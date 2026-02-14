#!/usr/bin/env bash
set -euo pipefail

# oh-my-opencode-update
# - 默认升级到 latest
# - 也支持指定版本（例如 3.2.2）
# - 温和策略：任何关键步骤失败立刻停止（不自动扩大破坏范围）

MODE=""
DRY_RUN=0

# target: "latest" or a semver string
TARGET="latest"

# 路径配置：获取脚本所在目录和 skill 根目录
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

# 路径配置（优先使用环境变量，否则使用默认值）
: "${OPENCODE_CONFIG_DIR:=${HOME}/.config/opencode}"
: "${OPENCODE_CACHE_DIR:=${HOME}/.cache}"
: "${OPENCODE_BIN:=${HOME}/.opencode/bin/opencode}"

# timeout for bunx install (in seconds), 0 = no timeout
: "${BUN_INSTALL_TIMEOUT:=300}"

# 核心路径
CONFIG_DIR="${OPENCODE_CONFIG_DIR}"
OPENCODE_JSON="${CONFIG_DIR}/opencode.json"
OMO_JSON="${CONFIG_DIR}/oh-my-opencode.json"
OMO_CACHE="${OPENCODE_CACHE_DIR}/oh-my-opencode"
OPENCODE_OMO_CACHE="${OPENCODE_CACHE_DIR}/opencode/node_modules/oh-my-opencode"

usage() {
  cat <<'USAGE'
Usage:
  oh_my_opencode_update.sh --dry-run [--latest | --target-version X.Y.Z]
  oh_my_opencode_update.sh --apply   [--latest | --target-version X.Y.Z]

Options:
  --dry-run                 Print planned actions only
  --apply                   Perform actions (still asks before destructive deletes)
  --latest                  Upgrade to latest (default)
  --target-version X.Y.Z    Upgrade to a specific version

Notes:
  - Any failure stops immediately (no auto escalation).
  - Cache delete requires interactive confirmation.
USAGE
}

log_base_dir() {
  # 优先使用 skill 根目录下的 plan 文件夹
  if [ -d "${SKILL_ROOT}/plan" ]; then
    echo "${SKILL_ROOT}/plan"
  else
    echo "/tmp/oh-my-opencode-update"
  fi
}

confirm() {
  local prompt="$1"
  local ans=""
  if ! read -r -p "${prompt} [y/N] " ans; then
    return 1
  fi
  case "${ans}" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

# SHA256 checksum command (cross-platform)
SHA256_CMD=""
if command -v shasum &> /dev/null; then
  SHA256_CMD="shasum -a 256"
elif command -v openssl &> /dev/null; then
  SHA256_CMD="openssl dgst -sha256"
else
  SHA256_CMD="sha256sum"  # Linux (may not be available on some macOS)
fi

resolve_target_pkg() {
  # produce npm install argument
  if [ "${TARGET}" = "latest" ]; then
    echo "oh-my-opencode@latest"
  else
    echo "oh-my-opencode@${TARGET}"
  fi
}

main() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        MODE="dry-run"
        shift
        ;;
      --apply)
        MODE="apply"
        shift
        ;;
      --latest)
        TARGET="latest"
        shift
        ;;
      --target-version)
        TARGET="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown arg: $1" >&2
        usage
        exit 2
        ;;
    esac
  done

  if [ -z "${MODE}" ]; then
    usage
    exit 2
  fi

  local ts; ts="$(date '+%Y%m%d_%H%M%S')"
  local base; base="$(log_base_dir)"
  local out; out="${base}/run_${ts}"
  mkdir -p "${out}"

  local pkg; pkg="$(resolve_target_pkg)"

  echo "[oh-my-opencode-update] mode=${MODE} target=${TARGET} logdir=${out}"

  # [1/4] Prerequisites check
  echo "[1/4] Prerequisites check" | tee -a "${out}/log.txt"

  # Check bun
  if ! command -v bun &> /dev/null; then
    echo "ERROR: bun not found. Please install bun first." | tee -a "${out}/log.txt"
    echo "  Install: curl -fsSL https://bun.sh/install | bash" | tee -a "${out}/log.txt"
    exit 1
  fi
  echo "bun: $(bun --version)" | tee -a "${out}/log.txt"

  # Ensure config directory exists and is writable
  if [ ! -d "${CONFIG_DIR}" ]; then
    echo "WARN: Config directory does not exist: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    if [ ${DRY_RUN} -eq 1 ]; then
      echo "      DRY: would create it: mkdir -p ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    else
      mkdir -p "${CONFIG_DIR}" || {
        echo "ERROR: Failed to create config directory: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
        exit 1
      }
      echo "Created config directory: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    fi
  fi

  if [ -d "${CONFIG_DIR}" ] && [ ! -w "${CONFIG_DIR}" ]; then
    echo "ERROR: Config directory is not writable: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    echo "  Check permissions: ls -ld ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    echo "  Fix with: chmod u+w ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    exit 1
  fi

  echo "[2/4] Baseline" | tee -a "${out}/log.txt"
  echo "OPENCODE_BIN: ${OPENCODE_BIN}" | tee -a "${out}/log.txt"

  local opencode_cmd=""
  if [ -x "${OPENCODE_BIN}" ]; then
    opencode_cmd="${OPENCODE_BIN}"

    local opencode_bin_dir=""
    opencode_bin_dir="$(dirname "${OPENCODE_BIN}")"
    PATH="${opencode_bin_dir}:${PATH}"
    export PATH
    echo "PATH prepend: ${opencode_bin_dir}" | tee -a "${out}/log.txt"
  elif command -v opencode &> /dev/null; then
    opencode_cmd="$(command -v opencode)"
  fi

  if [ -n "${opencode_cmd}" ]; then
    echo "opencode: ${opencode_cmd}" | tee -a "${out}/log.txt"
    "${opencode_cmd}" --version | tee -a "${out}/log.txt" || true
  else
    echo "WARN: opencode command not found. Set OPENCODE_BIN or add opencode to PATH." | tee -a "${out}/log.txt"
  fi

  echo "[3/4] Backup configs" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: cp -a ${OPENCODE_JSON} ${out}/opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    echo "DRY: cp -a ${OMO_JSON} ${out}/oh-my-opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
  else
    if [ -f "${OPENCODE_JSON}" ]; then
      cp -a "${OPENCODE_JSON}" "${out}/opencode.json.${ts}.bak"
      ${SHA256_CMD} "${OPENCODE_JSON}" "${out}/opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    else
      echo "WARN: ${OPENCODE_JSON} not found, skipping backup" | tee -a "${out}/log.txt"
    fi

    if [ -f "${OMO_JSON}" ]; then
      cp -a "${OMO_JSON}" "${out}/oh-my-opencode.json.${ts}.bak"
      ${SHA256_CMD} "${OMO_JSON}" "${out}/oh-my-opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    else
      echo "WARN: ${OMO_JSON} not found, skipping backup" | tee -a "${out}/log.txt"
    fi
  fi

  echo "[4/7] Uninstall (gentle)" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm uninstall oh-my-opencode)" | tee -a "${out}/log.txt"
  else
    set +e
    (cd "${CONFIG_DIR}" && npm uninstall oh-my-opencode) 2>&1 | tee -a "${out}/log.txt"
    local uninstall_rc=${PIPESTATUS[0]}
    set -e

    if [ ${uninstall_rc} -ne 0 ]; then
      echo "WARN: npm uninstall failed (rc=${uninstall_rc})." | tee -a "${out}/log.txt"
      echo "      This is often OK if the package was not installed yet." | tee -a "${out}/log.txt"
      echo "      Continuing to installation step." | tee -a "${out}/log.txt"
    fi
  fi

  echo "[5/7] Cache cleanup (optional)" | tee -a "${out}/log.txt"
  if [ -d "${OMO_CACHE}" ]; then
    echo "Found cache dir: ${OMO_CACHE}" | tee -a "${out}/log.txt"
    if [ ${DRY_RUN} -eq 1 ]; then
      echo "DRY: rm -rf ${OMO_CACHE} (would ask confirmation)" | tee -a "${out}/log.txt"
    else
      if confirm "Delete cache dir ${OMO_CACHE}?"; then
        rm -rf "${OMO_CACHE}"
        echo "Deleted ${OMO_CACHE}" | tee -a "${out}/log.txt"
      else
        echo "Skipped deleting ${OMO_CACHE}" | tee -a "${out}/log.txt"
      fi
    fi
  else
    echo "No cache dir ${OMO_CACHE}" | tee -a "${out}/log.txt"
  fi

  # Clean opencode plugin cache (where version info is read from)
  # Use glob pattern to clean all oh-my-opencode related caches
  local opencode_plugin_cache_dir="${OPENCODE_CACHE_DIR}/opencode/node_modules"
  if [ -d "${opencode_plugin_cache_dir}" ]; then
    local found_cache=0
    for cache_path in "${opencode_plugin_cache_dir}"/oh-my-opencode*; do
      if [ -e "${cache_path}" ]; then
        found_cache=1
        echo "Found opencode plugin cache: ${cache_path}" | tee -a "${out}/log.txt"
        if [ ${DRY_RUN} -eq 1 ]; then
          echo "DRY: rm -rf ${cache_path} (would ask confirmation)" | tee -a "${out}/log.txt"
        else
          if confirm "Delete opencode plugin cache ${cache_path}?"; then
            rm -rf "${cache_path}"
            echo "Deleted ${cache_path}" | tee -a "${out}/log.txt"
          else
            echo "Skipped deleting ${cache_path}" | tee -a "${out}/log.txt"
          fi
        fi
      fi
    done
    if [ ${found_cache} -eq 0 ]; then
      echo "No oh-my-opencode cache found in ${opencode_plugin_cache_dir}" | tee -a "${out}/log.txt"
    fi
  else
    echo "No opencode plugin cache dir ${opencode_plugin_cache_dir}" | tee -a "${out}/log.txt"
  fi

  # Clean opencode package.json dependencies
  local opencode_pkg_json="${OPENCODE_CACHE_DIR}/opencode/package.json"
  if [ -f "${opencode_pkg_json}" ]; then
    echo "Found opencode package.json: ${opencode_pkg_json}" | tee -a "${out}/log.txt"

    # Check if oh-my-opencode dependency exists
    local has_omo=""
    has_omo=$(node -e "const pkg=require('${opencode_pkg_json}'); console.log(!!pkg.dependencies?.['oh-my-opencode'])" 2>/dev/null || echo "false")

    if [ "${has_omo}" = "true" ]; then
      echo "Found oh-my-opencode dependency in opencode package.json" | tee -a "${out}/log.txt"

      if [ ${DRY_RUN} -eq 1 ]; then
        echo "DRY: would delete oh-my-opencode dependency from ${opencode_pkg_json}" | tee -a "${out}/log.txt"
        echo "      Command: node -e \"const p=require('${opencode_pkg_json}'); delete p.dependencies['oh-my-opencode']; require('fs').writeFileSync('${opencode_pkg_json}', JSON.stringify(p, null, 2))\"" | tee -a "${out}/log.txt"
      else
        if confirm "Delete oh-my-opencode dependency from ${opencode_pkg_json}?"; then
          node -e "const p=require('${opencode_pkg_json}'); delete p.dependencies['oh-my-opencode']; require('fs').writeFileSync('${opencode_pkg_json}', JSON.stringify(p, null, 2))" | tee -a "${out}/log.txt"
          echo "Deleted oh-my-opencode dependency from ${opencode_pkg_json}" | tee -a "${out}/log.txt"
        else
          echo "Skipped deleting oh-my-opencode dependency from ${opencode_pkg_json}" | tee -a "${out}/log.txt"
        fi
      fi
    else
      echo "No oh-my-opencode dependency found in ${opencode_pkg_json}" | tee -a "${out}/log.txt"
    fi
  else
    echo "No opencode package.json: ${opencode_pkg_json}" | tee -a "${out}/log.txt"
  fi

  echo "[6/7] Install/Upgrade" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm install ${pkg} --save-exact)" | tee -a "${out}/log.txt"
    echo "DRY: fallback with --save-exact --ignore-scripts if postinstall hangs" | tee -a "${out}/log.txt"
  else
    local install_success=0
    local install_output=""

    # Try normal install first (with optional timeout)
    echo "Attempting npm install (timeout: ${NPM_INSTALL_TIMEOUT}s)..." | tee -a "${out}/log.txt"
    if [ -n "${TIMEOUT_CMD}" ] && [ "${NPM_INSTALL_TIMEOUT}" -gt 0 ]; then
      install_output=$(${TIMEOUT_CMD} "${NPM_INSTALL_TIMEOUT}" npm install "${pkg}" --save-exact --prefix "${CONFIG_DIR}" 2>&1) && install_success=1 || install_success=0
      echo "${install_output}" | tee -a "${out}/log.txt"
    else
      install_output=$( (cd "${CONFIG_DIR}" && npm install "${pkg}" --save-exact) 2>&1 ) && install_success=1 || install_success=0
      echo "${install_output}" | tee -a "${out}/log.txt"
    fi

    # If failed or timed out, try with --ignore-scripts
    if [ ${install_success} -eq 0 ]; then
      echo "WARN: npm install failed or timed out. Trying with --ignore-scripts..." | tee -a "${out}/log.txt"
      set +e
      (cd "${CONFIG_DIR}" && npm install "${pkg}" --save-exact --ignore-scripts) 2>&1 | tee -a "${out}/log.txt"
      local ignore_scripts_rc=${PIPESTATUS[0]}
      set -e

      if [ ${ignore_scripts_rc} -ne 0 ]; then
        echo "ERROR: npm install failed even with --ignore-scripts (rc=${ignore_scripts_rc}). Possible causes:" | tee -a "${out}/log.txt"
        echo "  1. Network issue - check internet connection" | tee -a "${out}/log.txt"
        echo "     Test: curl -I https://registry.npmjs.org/" | tee -a "${out}/log.txt"
        echo "  2. Permission issue - check directory permissions" | tee -a "${out}/log.txt"
        echo "     Check: ls -ld ${CONFIG_DIR}" | tee -a "${out}/log.txt"
        echo "  3. Registry issue - try using official registry:" | tee -a "${out}/log.txt"
        echo "     Fix: npm config set registry https://registry.npmjs.org/" | tee -a "${out}/log.txt"
        echo "  4. Disk space issue - check available space" | tee -a "${out}/log.txt"
        echo "     Check: df -h ${CONFIG_DIR}" | tee -a "${out}/log.txt"
        exit 20
      fi

      echo "INFO: Installation succeeded with --ignore-scripts" | tee -a "${out}/log.txt"
      echo "NOTE: Some optional dependencies may not be fully configured." | tee -a "${out}/log.txt"
    fi
  fi

  echo "[4/4] Verify" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: node ${CONFIG_DIR}/node_modules/.bin/oh-my-opencode --version" | tee -a "${out}/log.txt"
    echo "DRY: node ${CONFIG_DIR}/node_modules/.bin/oh-my-opencode doctor" | tee -a "${out}/log.txt"
  else
    (cd "${CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode --version) | tee -a "${out}/log.txt"
    (cd "${CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode doctor) | tee -a "${out}/log.txt" || true

    # Optional: record the resolved version from installed package.json
    if [ -f "${CONFIG_DIR}/node_modules/oh-my-opencode/package.json" ]; then
      node -e "const p=require('${CONFIG_DIR}/node_modules/oh-my-opencode/package.json'); console.log('resolved_version', p.version)" | tee -a "${out}/log.txt" || true
    fi
  fi

  echo "Done. Logs: ${out}" | tee -a "${out}/log.txt"
}

main "$@"
