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

# 核心路径
CONFIG_DIR="${OPENCODE_CONFIG_DIR}"
OPENCODE_JSON="${CONFIG_DIR}/opencode.json"
OMO_JSON="${CONFIG_DIR}/oh-my-opencode.json"
OMO_CACHE="${OPENCODE_CACHE_DIR}/oh-my-opencode"

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
  read -r -p "${prompt} [y/N] " ans
  case "${ans}" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

# timeout for npm install (in seconds), 0 = no timeout
: "${NPM_INSTALL_TIMEOUT:=120}"

# Check if timeout command is available
TIMEOUT_CMD=""
if command -v timeout &> /dev/null; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout &> /dev/null; then
  TIMEOUT_CMD="gtimeout"  # macOS with coreutils
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

  # [0/7] Prerequisites check
  echo "[0/7] Prerequisites check" | tee -a "${out}/log.txt"

  # Check npm
  if ! command -v npm &> /dev/null; then
    echo "ERROR: npm not found. Please install Node.js and npm first." | tee -a "${out}/log.txt"
    echo "  Download: https://nodejs.org/" | tee -a "${out}/log.txt"
    exit 1
  fi
  echo "npm: $(npm --version)" | tee -a "${out}/log.txt"

  # Check node
  if ! command -v node &> /dev/null; then
    echo "ERROR: node not found. Please install Node.js first." | tee -a "${out}/log.txt"
    echo "  Download: https://nodejs.org/" | tee -a "${out}/log.txt"
    exit 1
  fi
  echo "node: $(node --version)" | tee -a "${out}/log.txt"

  # Check config directory exists and is writable
  if [ ! -d "${CONFIG_DIR}" ]; then
    echo "WARN: Config directory does not exist: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    echo "      Will attempt to create it during installation." | tee -a "${out}/log.txt"
  elif [ ! -w "${CONFIG_DIR}" ]; then
    echo "ERROR: Config directory is not writable: ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    echo "  Check permissions: ls -ld ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    echo "  Fix with: chmod u+w ${CONFIG_DIR}" | tee -a "${out}/log.txt"
    exit 1
  fi

  echo "[1/7] Baseline" | tee -a "${out}/log.txt"
  echo "opencode: $(command -v opencode)" | tee -a "${out}/log.txt"
  opencode --version | tee -a "${out}/log.txt" || true

  echo "[2/7] Backup configs" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: cp -a ${OPENCODE_JSON} ${out}/opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    echo "DRY: cp -a ${OMO_JSON} ${out}/oh-my-opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
  else
    if [ -f "${OPENCODE_JSON}" ]; then
      cp -a "${OPENCODE_JSON}" "${out}/opencode.json.${ts}.bak"
      shasum -a 256 "${OPENCODE_JSON}" "${out}/opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    else
      echo "WARN: ${OPENCODE_JSON} not found, skipping backup" | tee -a "${out}/log.txt"
    fi

    if [ -f "${OMO_JSON}" ]; then
      cp -a "${OMO_JSON}" "${out}/oh-my-opencode.json.${ts}.bak"
      shasum -a 256 "${OMO_JSON}" "${out}/oh-my-opencode.json.${ts}.bak" | tee -a "${out}/log.txt"
    else
      echo "WARN: ${OMO_JSON} not found, skipping backup" | tee -a "${out}/log.txt"
    fi
  fi

  echo "[3/7] Uninstall (gentle)" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm uninstall oh-my-opencode)" | tee -a "${out}/log.txt"
  else
    (cd "${CONFIG_DIR}" && npm uninstall oh-my-opencode) 2>&1 | tee -a "${out}/log.txt" || {
      echo "ERROR: npm uninstall failed. Possible causes:" | tee -a "${out}/log.txt"
      echo "  1. Package not installed - this is OK for first-time installation" | tee -a "${out}/log.txt"
      echo "  2. Permission issue - check directory permissions" | tee -a "${out}/log.txt"
      echo "     Fix: ls -ld ${CONFIG_DIR}" | tee -a "${out}/log.txt"
      echo "  3. Lock file issue - try: rm -f ${CONFIG_DIR}/package-lock.json" | tee -a "${out}/log.txt"
      exit 10
    }
  fi

  echo "[4/7] Cache cleanup (optional)" | tee -a "${out}/log.txt"
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

  echo "[5/7] Install/Upgrade" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm install ${pkg})" | tee -a "${out}/log.txt"
    echo "DRY: fallback with --ignore-scripts if postinstall hangs" | tee -a "${out}/log.txt"
  else
    local install_success=0
    local install_output=""

    # Try normal install first (with optional timeout)
    echo "Attempting npm install (timeout: ${NPM_INSTALL_TIMEOUT}s)..." | tee -a "${out}/log.txt"
    if [ -n "${TIMEOUT_CMD}" ] && [ "${NPM_INSTALL_TIMEOUT}" -gt 0 ]; then
      install_output=$(${TIMEOUT_CMD} "${NPM_INSTALL_TIMEOUT}" npm install "${pkg}" --prefix "${CONFIG_DIR}" 2>&1) && install_success=1 || install_success=0
      echo "${install_output}" | tee -a "${out}/log.txt"
    else
      install_output=$((cd "${CONFIG_DIR}" && npm install "${pkg}") 2>&1) && install_success=1 || install_success=0
      echo "${install_output}" | tee -a "${out}/log.txt"
    fi

    # If failed or timed out, try with --ignore-scripts
    if [ ${install_success} -eq 0 ]; then
      echo "WARN: npm install failed or timed out. Trying with --ignore-scripts..." | tee -a "${out}/log.txt"
      (cd "${CONFIG_DIR}" && npm install "${pkg}" --ignore-scripts) 2>&1 | tee -a "${out}/log.txt" || {
        echo "ERROR: npm install failed even with --ignore-scripts. Possible causes:" | tee -a "${out}/log.txt"
        echo "  1. Network issue - check internet connection" | tee -a "${out}/log.txt"
        echo "     Test: curl -I https://registry.npmjs.org/" | tee -a "${out}/log.txt"
        echo "  2. Permission issue - check directory permissions" | tee -a "${out}/log.txt"
        echo "     Check: ls -ld ${CONFIG_DIR}" | tee -a "${out}/log.txt"
        echo "  3. Registry issue - try using official registry:" | tee -a "${out}/log.txt"
        echo "     Fix: npm config set registry https://registry.npmjs.org/" | tee -a "${out}/log.txt"
        echo "  4. Disk space issue - check available space" | tee -a "${out}/log.txt"
        echo "     Check: df -h ${CONFIG_DIR}" | tee -a "${out}/log.txt"
        exit 20
      }
      echo "INFO: Installation succeeded with --ignore-scripts" | tee -a "${out}/log.txt"
      echo "NOTE: Some optional dependencies may not be fully configured." | tee -a "${out}/log.txt"
    fi
  fi

  echo "[6/7] Verify" | tee -a "${out}/log.txt"
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
