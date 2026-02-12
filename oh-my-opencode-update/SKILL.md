---
name: oh-my-opencode-update
description: Use when upgrading, reinstalling, or troubleshooting the oh-my-opencode plugin, especially when old caches, lockfiles, or permissions prevent the new version from taking effect.
---

# oh-my-opencode-update

面向唯一长期用户：凌贵旺（Guiwang Ling）。

## 核心目标
- **默认升级到最新版本（latest）**，并支持 **指定版本（pinned version）**。
- 先检查环境（npm/node/权限），再备份，再温和卸载，再清理缓存（删除前交互确认），最后安装并验证。
- 关键步骤失败：**立刻停止**。例外：温和卸载失败只记录 WARN 并继续；`doctor` 失败不阻塞。

## 执行流程

脚本按以下顺序执行（共 7 步）：

| 步骤 | 名称 | 说明 |
|------|------|------|
| [1/7] | Prerequisites check | 检查 npm、node 版本及配置目录权限（必要时自动创建配置目录） |
| [2/7] | Baseline | 记录当前环境信息 |
| [3/7] | Backup configs | 备份 opencode.json 和 oh-my-opencode.json |
| [4/7] | Uninstall (gentle) | 温和卸载旧版本（失败仅 WARN 并继续） |
| [5/7] | Cache cleanup (optional) | 可选的缓存清理（需确认），包括 ~/.cache/oh-my-opencode 和 ~/.cache/opencode/node_modules/oh-my-opencode* |
| [6/7] | Install/Upgrade | 安装新版本（支持超时回退） |
| [7/7] | Verify | 验证安装结果（doctor 失败不阻塞） |

### [6/7] Install/Upgrade 详解

安装过程采用双重策略：

1. **首次尝试**：正常 `npm install --save-exact`（在 `timeout`/`gtimeout` 可用时带超时保护）
2. **自动回退**：若失败或超时，自动使用 `--save-exact --ignore-scripts` 重试

**关键特性**：
- `--save-exact`：确保安装精确版本，避免 npm 自动添加 `^` 导致版本升级
- 超时保护（在 `timeout`/`gtimeout` 可用时）：防止 `postinstall` 脚本卡住

## 适用环境（可通过环境变量自定义）

### 默认路径
以下路径为默认值，可通过环境变量覆盖：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录（oh-my-opencode 安装位置） |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${HOME}/.opencode/bin/opencode` | opencode 二进制文件路径（优先使用可执行文件，否则回退 PATH） |
| `NPM_INSTALL_TIMEOUT` | `120` | npm install 超时时间（秒），`0` 表示无超时 |

### 配置文件
- opencode 配置：`~/.config/opencode/opencode.json` （环境变量：`OPENCODE_CONFIG_DIR`）
- oh-my-opencode 配置：`~/.config/opencode/oh-my-opencode.json`
- 缓存目录：`~/.cache/oh-my-opencode`
- opencode 插件缓存（版本信息读取位置）：`~/.cache/opencode/node_modules/oh-my-opencode*`

### 自定义路径（可选）
```bash
export OPENCODE_CONFIG_DIR="/custom/config/opencode"
export OPENCODE_CACHE_DIR="/custom/cache"
```

更多配置说明请参见 `references/paths_config.md`。

## 使用方式

脚本位置：`${SKILL_ROOT}/scripts/oh_my_opencode_update.sh`

其中 `${SKILL_ROOT}` 为 skill 根目录（包含 SKILL.md 的目录）。

### 1) Dry-run（推荐先跑）
```bash
# 从 skill 根目录运行
bash scripts/oh_my_opencode_update.sh --dry-run --latest
```

### 2) 实际执行：升级到 latest
```bash
bash scripts/oh_my_opencode_update.sh --apply --latest
```

### 3) 实际执行：升级到指定版本
```bash
bash scripts/oh_my_opencode_update.sh --apply --target-version 3.2.2
```

## 验收（必须做）
```bash
(cd "${OPENCODE_CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode --version)
(cd "${OPENCODE_CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode doctor)
```

## 常见问题

### 前置检查失败
- **npm 或 node 未安装**
  - 安装 Node.js：https://nodejs.org/
- **配置目录无写权限**
  - 检查权限：`ls -ld "${OPENCODE_CONFIG_DIR}"`
  - 修复权限：`chmod u+w "${OPENCODE_CONFIG_DIR}"`

### npm 相关问题
- **npm install 失败**
  - 脚本会自动输出诊断建议，常见原因：
    1. 网络问题 - 检查网络连接
    2. 权限问题 - 检查目录权限
    3. Registry 问题 - 尝试官方 registry
    4. 磁盘空间不足
- **npm uninstall 失败**
  - 可能是包未安装（首次安装时正常）
  - 可能是权限或 lock 文件问题，按脚本提示修复
  - 脚本会继续进入安装步骤（gentle）
- **postinstall 脚本卡住**
  - 脚本会自动处理：超时后使用 `--ignore-scripts` 重试
  - 可通过 `NPM_INSTALL_TIMEOUT` 调整超时时间
  - macOS 用户需安装 coreutils：`brew install coreutils`（提供 `gtimeout`）

### 历史说明
- 本 skill 早期版本使用 `bun` 作为包管理器，现已切换到 `npm` 以提高兼容性和稳定性

