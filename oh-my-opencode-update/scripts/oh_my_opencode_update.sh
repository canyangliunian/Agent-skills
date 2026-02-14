#!/usr/bin/env bash
set -euo pipefail

# oh-my-opencode-update
# - 默认升级到 latest
# - 也支持指定版本（例如 3.2.2）
# - 使用官方推荐的 bunx 安装器
# - 温和策略：任何关键步骤失败立刻停止（不自动扩大破坏范围）

MODE=""
DRY_RUN=0
FORCE_CLEANUP=0

# target: "latest" or a semver string
TARGET="latest"

# Subscription parameters
CLAUDE=""
GEMINI=""
COPILOT=""

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
  oh_my_opencode_update.sh --dry-run [--latest | --target-version X.Y.Z] [--force-cleanup] --claude <value> --gemini <value> --copilot <value>
  oh_my_opencode_update.sh --apply   [--latest | --target-version X.Y.Z] [--force-cleanup] --claude <value> --gemini <value> --copilot <value>

Options:
  --dry-run                 Print planned actions only
  --apply                   Perform actions (still asks before destructive deletes unless --force-cleanup)
  --latest                  Upgrade to latest (default)
  --target-version X.Y.Z    Upgrade to a specific version
  --force-cleanup           Skip confirmation for cache deletion
  --claude <value>          Claude 订阅: no, yes, max20 (必需)
  --gemini <value>          Gemini 集成: no, yes (必需)
  --copilot <value>         GitHub Copilot 订阅: no, yes (必需)

Notes:
  - Any failure stops immediately (no auto escalation).
  - Cache delete requires interactive confirmation unless --force-cleanup is set.
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

  # Skip confirmation if FORCE_CLEANUP is set
  if [ ${FORCE_CLEANUP} -eq 1 ]; then
    echo "[FORCE] ${prompt}" | tee -a "${out}/log.txt"
    return 0
  fi

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
  # produce bunx install command argument
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
      --force-cleanup)
        FORCE_CLEANUP=1
        shift
        ;;
      --claude)
        CLAUDE="$2"
        shift 2
        ;;
      --gemini)
        GEMINI="$2"
        shift 2
        ;;
      --copilot)
        COPILOT="$2"
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

  # [1/4] Prepare
  echo "[1/4] Prepare (prerequisites & baseline)" | tee -a "${out}/log.txt"

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

  echo "[2/4] Backup configs" | tee -a "${out}/log.txt"
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

  echo "[3/4] Cache cleanup (optional)" | tee -a "${out}/log.txt"
  if [ -d "${OMO_CACHE}" ]; then
    local cache_size=""
    cache_size=$(du -sh "${OMO_CACHE}" 2>/dev/null | cut -f1)
    echo "Found cache dir: ${OMO_CACHE} (${cache_size})" | tee -a "${out}/log.txt"
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
        local cache_size=""
        cache_size=$(du -sh "${cache_path}" 2>/dev/null | cut -f1)
        echo "Found opencode plugin cache: ${cache_path} (${cache_size})" | tee -a "${out}/log.txt"
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

  echo "[4/4] Install/Upgrade via official installer" | tee -a "${out}/log.txt"

  # Validate required subscription parameters
  if [ -z "${CLAUDE}" ] && [ -z "${GEMINI}" ] && [ -z "${COPILOT}" ]; then
    echo "ERROR: At least one subscription option is required (--claude, --gemini, or --copilot)." | tee -a "${out}/log.txt"
    echo "  Usage: bunx oh-my-opencode install --no-tui --claude=<no|yes|max20> --gemini=<no|yes> --copilot=<no|yes>" | tee -a "${out}/log.txt"
    exit 1
  fi

  # Build install command with subscription parameters
  local install_args="--no-tui"
  if [ -n "${CLAUDE}" ]; then
    install_args="${install_args} --claude=${CLAUDE}"
  fi
  if [ -n "${GEMINI}" ]; then
    install_args="${install_args} --gemini=${GEMINI}"
  fi
  if [ -n "${COPILOT}" ]; then
    install_args="${install_args} --copilot=${COPILOT}"
  fi

  local install_cmd="bunx ${pkg} install ${install_args}"

  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: ${install_cmd}" | tee -a "${out}/log.txt"
  else
    set +e
    local install_output=""
    local install_rc=0

    # Execute with optional timeout
    if [ "${BUN_INSTALL_TIMEOUT}" -gt 0 ]; then
      if command -v timeout &> /dev/null; then
        install_output=$(timeout "${BUN_INSTALL_TIMEOUT}" ${install_cmd} 2>&1) && install_rc=0 || install_rc=$?
      elif command -v gtimeout &> /dev/null; then
        install_output=$(gtimeout "${BUN_INSTALL_TIMEOUT}" ${install_cmd} 2>&1) && install_rc=0 || install_rc=$?
      else
        # No timeout available, run without timeout
        install_output=$(${install_cmd} 2>&1) && install_rc=0 || install_rc=$?
      fi
    else
      install_output=$(${install_cmd} 2>&1) && install_rc=0 || install_rc=$?
    fi
    set -e

    echo "${install_output}" | tee -a "${out}/log.txt"

    if [ ${install_rc} -ne 0 ]; then
      echo "ERROR: bunx install failed (rc=${install_rc})." | tee -a "${out}/log.txt"
      echo "  Possible causes:" | tee -a "${out}/log.txt"
      echo "  1. Network issue - check internet connection" | tee -a "${out}/log.txt"
      echo "     Test: curl -I https://registry.npmjs.org/" | tee -a "${out}/log.txt"
      echo "  2. Bun/bunx issue - check installation" | tee -a "${out}/log.txt"
      echo "     Test: bunx --version" | tee -a "${out}/log.txt"
      echo "  3. Version not found - verify target version" | tee -a "${out}/log.txt"
      echo "     Test: bun pm ls oh-my-opencode" | tee -a "${out}/log.txt"
      exit 2
    fi

    echo "INFO: Installation completed successfully." | tee -a "${out}/log.txt"
  fi

  echo "[4/4] Verify installation" | tee -a "${out}/log.txt"

  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: grep -q 'oh-my-opencode' ${OPENCODE_JSON}" | tee -a "${out}/log.txt"
    echo "DRY: test -f ${OMO_JSON}" | tee -a "${out}/log.txt"
  else
    local verify_rc=0

    # Check plugin registration
    if [ -f "${OPENCODE_JSON}" ]; then
      if grep -q '"oh-my-opencode"' "${OPENCODE_JSON}" 2>/dev/null; then
        echo "[OK] Plugin registered in opencode.json" | tee -a "${out}/log.txt"
      else
        echo "[WARN] Plugin not found in opencode.json" | tee -a "${out}/log.txt"
        verify_rc=1
      fi
    else
      echo "[WARN] opencode.json not found: ${OPENCODE_JSON}" | tee -a "${out}/log.txt"
      verify_rc=1
    fi

    # Check config file existence
    if [ -f "${OMO_JSON}" ]; then
      echo "[OK] Config file exists: ${OMO_JSON}" | tee -a "${out}/log.txt"
    else
      echo "[WARN] Config file not found: ${OMO_JSON}" | tee -a "${out}/log.txt"
    fi

    # Optional: run opencode doctor (non-blocking)
    if command -v opencode &> /dev/null; then
      echo "Running opencode doctor..." | tee -a "${out}/log.txt"
      opencode doctor 2>&1 | tee -a "${out}/log.txt" || echo "[WARN] opencode doctor had issues" | tee -a "${out}/log.txt"
    fi

    exit ${verify_rc}
  fi

  echo "Done. Logs: ${out}" | tee -a "${out}/log.txt"
}

main "$@"
