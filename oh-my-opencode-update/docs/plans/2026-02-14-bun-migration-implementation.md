# Bun Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use @superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `oh-my-opencode-update` 脚本从 npm 包管理器切换到 bunx（官方推荐安装方式）

**Architecture:** 脚本简化为 4 步流程：[1/4] Bun 检查 → [2/4] 备份配置 → [3/4] 缓存清理 + 调用官方安装器 → [4/4] 验证。核心变化是移除所有 npm/node_modules 相关逻辑，改用 `bunx oh-my-opencode@<version> install --no-tui` 命令。

**Tech Stack:** Bash (兼容 macOS/Linux), bunx (官方安装器), opencode CLI

---

## Prerequisites

在开始实施前，确保 bun 已安装：
```bash
curl -fsSL https://bun.sh/install | bash
```

---

## Task 1: 替换前置检查为 Bun 检查

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:146-184`

**Step 1: 识别需要修改的代码段**

当前代码（第 146-163 行）：
```bash
# [1/7] Prerequisites check
echo "[1/7] Prerequisites check" | tee -a "${out}/log.txt"

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
```

**Step 2: 替换为 Bun 检查逻辑**

新代码（替换第 146-163 行）：
```bash
# [1/4] Prerequisites check
echo "[1/4] Prerequisites check" | tee -a "${out}/log.txt"

# Check bun
if ! command -v bun &> /dev/null; then
  echo "ERROR: bun not found. Please install bun first." | tee -a "${out}/log.txt"
  echo "  Install: curl -fsSL https://bun.sh/install | bash" | tee -a "${out}/log.txt"
  exit 1
fi
echo "bun: $(bun --version)" | tee -a "${out}/log.txt"
```

**Step 3: 更新步骤标签和日志**

搜索并替换所有 `[x/7]` 为 `[x/4]`：
- 使用 `sed` 或手动编辑替换
- 第 146 行：`[1/7]` → `[1/4]`
- 第 186 行：`[2/7]` → `[2/4]`
- 第 209 行：`[3/7]` → `[3/4]`
- 第 364 行：`[7/7]` → `[4/4]`

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 替换前置检查为 Bun 并更新步骤编号"
```

---

## Task 2: 移除 npm 特定的环境变量和超时处理

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:70-79, 320-362`

**Step 1: 移除 NPM_INSTALL_TIMEOUT 环境变量**

删除第 70-79 行：
```bash
# timeout for npm install (in seconds), 0 = no timeout
: "${NPM_INSTALL_TIMEOUT:=120}"

# Check if timeout command is available
TIMEOUT_CMD=""
if command -v timeout &> /dev/null; then
  TIMEOUT_CMD="timeout"
elif command -v gtimeout &> /dev/null; then
  TIMEOUT_CMD="gtimeout"  # macOS with coreutils
fi
```

**Step 2: 添加 BUN_INSTALL_TIMEOUT 环境变量**

在环境变量配置区域（第 22 行后）添加：
```bash
# timeout for bunx install (in seconds), 0 = no timeout
: "${BUN_INSTALL_TIMEOUT:=300}"
```

**Step 3: 测试变量设置**

运行以下命令验证：
```bash
# 设置测试值
export BUN_INSTALL_TIMEOUT=300

# 验证默认值（未设置时）
unset BUN_INSTALL_TIMEOUT
bash -c 'echo "${BUN_INSTALL_TIMEOUT:-default}"'  # 应输出: default
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 移除 npm 超时处理，添加 bun 超时支持"
```

---

## Task 3: 更新 resolve_target_pkg 函数

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:91-98`

**Step 1: 识别当前函数**

当前代码（第 91-98 行）：
```bash
resolve_target_pkg() {
  # produce npm install argument
  if [ "${TARGET}" = "latest" ]; then
    echo "oh-my-opencode@latest"
  else
    echo "oh-my-opencode@${TARGET}"
  fi
}
```

**Step 2: 更新注释并保持逻辑**

更新注释以反映 bunx 用途：
```bash
resolve_target_pkg() {
  # produce bunx install command argument
  if [ "${TARGET}" = "latest" ]; then
    echo "oh-my-opencode@latest"
  else
    echo "oh-my-opencode@${TARGET}"
  fi
}
```

**Step 3: 测试函数**

```bash
source scripts/oh_my_opencode_update.sh
TARGET=latest
echo "$(resolve_target_pkg)"  # 应输出: oh-my-opencode@latest

TARGET=3.2.2
echo "$(resolve_target_pkg)"  # 应输出: oh-my-opencode@3.2.2
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 更新 resolve_target_pkg 注释以反映 bunx 用途"
```

---

## Task 4: 移除 Uninstall 步骤

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:229-243`

**Step 1: 识别 Uninstall 代码块**

当前代码（第 229-243 行）：
```bash
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
```

**Step 2: 删除整个 Uninstall 步骤**

删除第 229-243 行（包含 `[4/7] Uninstall` 部分）

**Step 3: 验证脚本仍可执行**

```bash
bash -n scripts/oh_my_opencode_update.sh --help
# 应输出 usage 信息，无语法错误
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 移除 Uninstall 步骤（官方安装器自行管理）"
```

---

## Task 5: 更新缓存清理步骤序号和增强大小显示

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:245-318`

**Step 1: 更新步骤标签**

将 `[5/7]` 改为 `[3/4]`：
- 第 245 行：`echo "[5/7] Cache cleanup (optional)"` → `echo "[3/4] Cache cleanup (optional)"`

**Step 2: 添加缓存目录大小显示**

在 `if [ -d "${OMO_CACHE}" ]` 之前添加大小检查：

```bash
# Show cache size if directory exists
if [ -d "${OMO_CACHE}" ]; then
  local omo_size
  omo_size=$(du -sh "${OMO_CACHE}" 2>/dev/null | cut -f1 || echo "unknown")
  echo "Cache size: ${omo_size}" | tee -a "${out}/log.txt"
fi
```

**Step 3: 对 opencode plugin cache 也添加大小显示**

在第 264 行后添加：
```bash
# Show plugin cache size
if [ -d "${opencode_plugin_cache_dir}" ]; then
  local plugin_size
  plugin_size=$(du -sh "${opencode_plugin_cache_dir}" 2>/dev/null | cut -f1 || echo "unknown")
  echo "Plugin cache size: ${plugin_size}" | tee -a "${out}/log.txt"
fi
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "feat: 更新缓存清理步骤序号并添加大小显示"
```

---

## Task 6: 添加 --force-cleanup 选项支持

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:10, 31-47, 58-68`

**Step 1: 添加 FORCE_CLEANUP 变量**

在第 10 行 `DRY_RUN=0` 后添加：
```bash
FORCE_CLEANUP=0
```

**Step 2: 更新 usage 函数添加新选项**

修改第 31-47 行的 usage 函数，添加 `--force-cleanup` 说明：
```bash
usage() {
  cat <<'USAGE'
Usage:
  oh_my_opencode_update.sh --dry-run [--latest | --target-version X.Y.Z] [--force-cleanup]
  oh_my_opencode_update.sh --apply   [--latest | --target-version X.Y.Z] [--force-cleanup]

Options:
  --dry-run                 Print planned actions only
  --apply                   Perform actions (still asks before destructive deletes unless --force-cleanup)
  --latest                  Upgrade to latest (default)
  --target-version X.Y.Z    Upgrade to a specific version
  --force-cleanup           Skip confirmation for cache deletion

Notes:
  - Any failure stops immediately (no auto escalation).
  - Cache delete requires interactive confirmation unless --force-cleanup is set.
USAGE
}
```

**Step 3: 添加命令行参数解析**

在第 100-130 行的参数解析循环中添加 `--force-cleanup` 处理：
```bash
--force-cleanup)
  FORCE_CLEANUP=1
  shift
  ;;
```

**Step 4: 修改 confirm 函数支持强制模式**

修改第 58-68 行的 confirm 函数：
```bash
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
```

**Step 5: 测试 --force-cleanup 选项**

```bash
# 测试 dry-run
bash scripts/oh_my_opencode_update.sh --dry-run --latest --force-cleanup

# 验证 usage 中显示新选项
bash scripts/oh_my_opencode_update.sh --help | grep force-cleanup
```

**Step 6: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "feat: 添加 --force-cleanup 选项支持"
```

---

## Task 7: 替换 Install/Upgrade 步骤为 bunx 调用

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:320-362`

**Step 1: 识别当前 Install 代码**

当前代码（第 320-362 行，约 40 行复杂的 npm 安装逻辑）

**Step 2: 替换为简单的 bunx 调用**

替换整个 `[6/7] Install/Upgrade` 步骤（第 320-362 行）为：
```bash
echo "[4/4] Install/Upgrade via official installer" | tee -a "${out}/log.txt"
local install_cmd="bunx ${pkg} install --no-tui"

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
```

**Step 3: 测试 bunx 命令**

```bash
# 测试 bunx 可用性
bunx --version

# 测试包查询（不安装）
bun pm ls oh-my-opencode
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 替换 npm install 为 bunx 官方安装器"
```

---

## Task 8: 简化 Verify 步骤

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:364-376`

**Step 1: 识别当前 Verify 代码**

当前代码（第 364-376 行）检查本地 node_modules 中的 oh-my-opencode

**Step 2: 替换为简化的验证逻辑**

替换整个 `[7/7] Verify` 步骤（第 364-376 行）为：
```bash
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
```

**Step 4: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "refactor: 简化验证步骤，检查插件注册而非本地 node_modules"
```

---

## Task 9: 更新 SKILL.md 文档

**Files:**
- Modify: `SKILL.md:1-149`

**Step 1: 更新执行流程表格**

查找并更新 `## 执行流程` 表格（约第 14-28 行）：

| 步骤 | 名称 | 说明 |
|------|------|------|
| [1/4] | Prerequisites check | 检查 bun 版本及配置目录权限 |
| [2/4] | Baseline | 记录当前环境信息 |
| [3/4] | Backup + Cache cleanup | 备份配置文件并清理缓存 |
| [4/4] | Install/Upgrade | 使用官方安装器安装并验证 |

**Step 2: 更新 `[6/7] Install/Upgrade` 部分**

删除 `[6/7] Install/Upgrade` 详解部分（约第 29-39 行），替换为：

```markdown
### [4/4] Install/Upgrade 详解

安装过程使用官方推荐的 `bunx` 安装器：

```bash
bunx oh-my-opencode@<version> install --no-tui
```

**关键特性**：
- `--no-tui`：非交互式模式，适合脚本自动化
- 官方安装器处理：插件注册、配置、认证步骤
- `@<version>`：指定版本，`@latest` 表示最新版
```

**Step 3: 更新默认路径表格环境变量说明**

在 `## 适用环境` 部分更新表格，添加 bun 相关变量：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录 |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${HOME}/.opencode/bin/opencode` | opencode 二进制文件路径 |
| `BUN_INSTALL_TIMEOUT` | `300` | bunx 安装超时时间（秒），0 表示无超时 |

**Step 4: 更新 `## 常见问题` 部分**

替换 npm 相关问题为 bun 相关：

```markdown
### 前置检查失败
- **bun 未安装**
  - 安装 bun：`curl -fsSL https://bun.sh/install | bash`
- **配置目录无写权限**
  - 检查权限：`ls -ld "${OPENCODE_CONFIG_DIR}"`
  - 修复权限：`chmod u+w "${OPENCODE_CONFIG_DIR}"`

### bunx 相关问题
- **bunx 执行失败**
  - 检查网络：`curl -I https://registry.npmjs.org/`
  - 检查 bunx：`bunx --version`
  - 验证版本：`bun pm ls oh-my-opencode`
- **postinstall 脚本卡住**
  - 官方安装器自处理，不依赖脚本的超时控制
  - 可通过 `BUN_INSTALL_TIMEOUT` 调整超时时间

### 历史说明
- 本 skill 早期版本使用 `npm` 进行包管理，现已切换到 `bunx` 以与官方推荐方式保持一致。
```

**Step 5: 移除或更新版本控制方案部分**

删除或简化 `## 版本控制方案` 部分（约第 120-149 行），因为官方安装器自行管理版本。

**Step 6: 提交更改**

```bash
git add SKILL.md
git commit -m "docs: 更新 SKILL.md 反映 bun 迁移"
```

---

## Task 10: 更新脚本头部注释

**Files:**
- Modify: `scripts/oh_my_opencode_update.sh:1-7`

**Step 1: 更新脚本描述**

修改第 1-7 行的头部注释：
```bash
#!/usr/bin/env bash
set -euo pipefail

# oh-my-opencode-update
# - 默认升级到 latest
# - 也支持指定版本（例如 3.2.2）
# - 使用官方推荐的 bunx 安装器
# - 温和策略：任何关键步骤失败立刻停止（不自动扩大破坏范围）
```

**Step 2: 提交更改**

```bash
git add scripts/oh_my_opencode_update.sh
git commit -m "docs: 更新脚本头部注释说明 bunx 安装器"
```

---

## Task 11: 测试完整流程（Dry-run）

**Files:**
- Test: `scripts/oh_my_opencode_update.sh`

**Step 1: 运行 Dry-run 测试**

```bash
bash scripts/oh_my_opencode_update.sh --dry-run --latest
```

**Expected Output:**
- 模式：`mode=dry-run`
- 目标：`target=latest`
- 4 个步骤全部显示为 DRY 模式
- 日志文件创建

**Step 2: 验证 Dry-run 输出**

检查输出是否包含：
- `[1/4] Prerequisites check`
- `[2/4] Baseline`
- `[3/4] Cache cleanup (optional)`
- `[4/4] Install/Upgrade via official installer`

**Step 3: 测试指定版本 Dry-run**

```bash
bash scripts/oh_my_opencode_update.sh --dry-run --target-version 3.2.2
```

验证显示 `target=3.2.2`。

---

## Task 12: 测试完整流程（Apply 模式 - 需要备份数据）

**Files:**
- Test: `scripts/oh_my_opencode_update.sh`

**⚠️ WARNING**: 此步骤会修改系统配置，请确保已备份重要数据。

**Step 1: 准备测试环境**

```bash
# 备份当前配置（如果存在）
[ -f ~/.config/opencode/opencode.json ] && cp ~/.config/opencode/opencode.json /tmp/opencode.json.backup
[ -f ~/.config/opencode/oh-my-opencode.json ] && cp ~/.config/opencode/oh-my-opencode.json /tmp/oh-my-opencode.json.backup
```

**Step 2: 运行 Apply 模式（latest）**

```bash
bash scripts/oh_my_opencode_update.sh --apply --latest
```

**Expected Output:**
- bun 检查通过
- 配置备份完成
- 缓存清理（询问确认）
- bunx 安装执行
- 验证完成

**Step 3: 运行 Apply 模式（指定版本）**

```bash
bash scripts/oh_my_opencode_update.sh --apply --target-version 3.2.2
```

**Step 4: 测试 --force-cleanup 选项**

```bash
bash scripts/oh_my_opencode_update.sh --apply --latest --force-cleanup
```

验证缓存清理跳过确认。

**Step 5: 验证安装结果**

```bash
# 检查插件是否注册
grep "oh-my-opencode" ~/.config/opencode/opencode.json

# 检查配置文件
cat ~/.config/opencode/oh-my-opencode.json

# 运行 doctor
opencode doctor
```

**Step 6: 恢复备份（如需要）**

```bash
# 如果测试失败，恢复备份
[ -f /tmp/opencode.json.backup ] && cp /tmp/opencode.json.backup ~/.config/opencode/opencode.json
[ -f /tmp/oh-my-opencode.json.backup ] && cp /tmp/oh-my-opencode.json.backup ~/.config/opencode/oh-my-opencode.json
```

---

## Task 13: 更新 references/paths_config.md

**Files:**
- Modify: `references/paths_config.md`

**Step 1: 添加 bun 相关说明**

在适当位置添加：

```markdown
## Bun 迁移说明

本 skill 现在使用官方推荐的 `bunx` 安装器，不再需要本地 node_modules 管理。

### 变化

- 不再需要：npm、node 检查
- 新增要求：bun 安装（`curl -fsSL https://bun.sh/install | bash`）
- 新增环境变量：`BUN_INSTALL_TIMEOUT`（默认 300 秒）
```

**Step 2: 提交更改**

```bash
git add references/paths_config.md
git commit -m "docs: 添加 bun 迁移说明到 paths_config.md"
```

---

## Task 14: 最终代码审查和清理

**Files:**
- Review: `scripts/oh_my_opencode_update.sh`, `SKILL.md`

**Step 1: 代码风格检查**

检查并确保：
- 所有步骤标签使用 `[x/4]` 格式
- 没有遗留的 `npm`、`node_modules`、`NPM_INSTALL_TIMEOUT` 引用
- 错误消息使用 `[OK]`、`[WARN]`、`[ERROR]`、`[INFO]` 前缀

**Step 2: 功能完整性检查**

使用 @pr-review-toolkit:review-pr 或手动检查：
- 环境变量正确性
- dry-run 模式不执行实际操作
- apply 模式正确执行所有步骤
- --force-cleanup 跳过确认
- 验证步骤正确检查插件注册

**Step 3: 提交最终更改**

```bash
git add scripts/oh_my_opencode_update.sh SKILL.md
git commit -m "refactor: 最终代码审查和清理"
```

---

## Task 15: 更新 plan/task_plan.md（如需要）

**Files:**
- Modify: `plan/task_plan.md`

**Step 1: 添加完成记录**

在适当位置添加迁移完成记录：

```markdown
## Phase 7: Bun 迁移（完成）

- [x] 将包管理器从 npm 切换到 bunx
- [x] 简化流程为 4 步
- [x] 添加 --force-cleanup 选项
- [x] 更新所有文档

**Status:** complete
```

**Step 2: 提交更改**

```bash
git add plan/task_plan.md
git commit -m "docs: 记录 Bun 迁移完成状态"
```

---

## Task 16: 推送到远程仓库

**Files:**
- Git: remote

**Step 1: 查看待推送的提交**

```bash
git log --oneline --graph --all
```

**Step 2: 推送到远程**

```bash
git push origin main
```

**Step 3: 验证远程仓库**

访问 GitHub 验证提交已推送：
https://github.com/<your-username>/<your-repo>/commits/main

---

## 测试检查清单

完成后，确保以下测试通过：

- [ ] `--help` 显示正确用法和所有选项
- [ ] `--dry-run --latest` 输出所有步骤但不执行
- [ ] `--dry-run --target-version X.Y.Z` 显示指定版本
- [ ] `--apply --latest` 成功执行安装
- [ ] `--apply --target-version X.Y.Z` 安装指定版本
- [ ] `--apply --latest --force-cleanup` 跳过缓存确认
- [ ] bun 未安装时正确提示安装命令
- [ ] 缓存目录显示大小信息
- [ ] 验证步骤检查插件注册
- [ ] 退出码正确返回（0=成功，1=检查失败，2=安装失败）

---

## 参考资源

- 设计文档：`docs/plans/2026-02-14-bun-migration-design.md`
- 官方安装文档：https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/refs/heads/master/docs/guide/installation.md
- Bun 官方文档：https://bun.sh/docs
- oh-my-opencode GitHub：https://github.com/code-yeongyu/oh-my-opencode
