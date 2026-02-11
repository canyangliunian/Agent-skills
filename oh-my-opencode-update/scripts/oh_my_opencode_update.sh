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

  echo "[1/6] Baseline" | tee -a "${out}/log.txt"
  echo "opencode: $(command -v opencode)" | tee -a "${out}/log.txt"
  opencode --version | tee -a "${out}/log.txt" || true

  echo "[2/6] Backup configs" | tee -a "${out}/log.txt"
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

  echo "[3/6] Uninstall (gentle)" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm uninstall oh-my-opencode)" | tee -a "${out}/log.txt"
  else
    (cd "${CONFIG_DIR}" && npm uninstall oh-my-opencode) | tee -a "${out}/log.txt" || {
      echo "ERROR: gentle uninstall failed. Stop (no auto escalation)." | tee -a "${out}/log.txt"
      exit 10
    }
  fi

  echo "[4/6] Cache cleanup (optional)" | tee -a "${out}/log.txt"
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

  echo "[5/6] Install/Upgrade" | tee -a "${out}/log.txt"
  if [ ${DRY_RUN} -eq 1 ]; then
    echo "DRY: (cd ${CONFIG_DIR} && npm install ${pkg})" | tee -a "${out}/log.txt"
  else
    (cd "${CONFIG_DIR}" && npm install "${pkg}") | tee -a "${out}/log.txt" || {
      echo "ERROR: install/upgrade failed. Stop (no auto switch to npm)." | tee -a "${out}/log.txt"
      exit 20
    }
  fi

  echo "[6/6] Verify" | tee -a "${out}/log.txt"
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
