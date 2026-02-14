---
name: oh-my-opencode-update
description: Use when upgrading, reinstalling, or troubleshooting the oh-my-opencode plugin, especially when old caches, lockfiles, or permissions prevent the new version from taking effect.
---

# oh-my-opencode-update

面向唯一长期用户：凌贵旺（Guiwang Ling）。

## 核心目标
- **默认升级到最新版本（latest）**，并支持 **指定版本（pinned version）**。
- 先检查环境（bun/权限），再备份，再清理缓存（可选，删除前交互确认），最后使用官方安装器安装并验证。
- 关键步骤失败：**立刻停止**。例外：`--force-cleanup` 时不询问直接清理；`doctor` 失败不阻塞。

## 执行流程

脚本按以下顺序执行（共 4 步）：

| 步骤 | 名称 | 说明 |
|------|------|------|
| [1/4] | Prerequisites check | 检查 bun 版本及配置目录权限 |
| [2/4] | Baseline | 记录当前环境信息 |
| [3/4] | Backup + Cache cleanup | 备份配置文件并清理缓存 |
| [4/4] | Install/Upgrade | 使用官方安装器安装并验证 |

### [4/4] Install/Upgrade 详解

安装过程使用官方推荐的 `bunx` 安装器：

```bash
bunx oh-my-opencode@<version> install --no-tui
```

**关键特性**：
- `--no-tui`：非交互式模式，适合脚本自动化
- 官方安装器处理：插件注册、配置、认证步骤
- `@<version>`：指定版本，`@latest` 表示最新版

## 适用环境（可通过环境变量自定义）

### 默认路径
以下路径为默认值，可通过环境变量覆盖：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录 |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${HOME}/.opencode/bin/opencode` | opencode 二进制文件路径 |
| `BUN_INSTALL_TIMEOUT` | `300` | bunx 安装超时时间（秒），0 表示无超时 |

### 配置文件
- opencode 配置：`~/.config/opencode/opencode.json` （环境变量：`OPENCODE_CONFIG_DIR`）
- oh-my-opencode 配置：`~/.config/opencode/oh-my-opencode.json`
- 缓存目录：`~/.cache/oh-my-opencode`
- opencode 插件缓存（版本信息读取位置）：`~/.cache/opencode/node_modules/oh-my-opencode*`
- opencode package.json（依赖配置）：`~/.cache/opencode/package.json`

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

### 可选参数

| 参数 | 说明 |
|------|------|
| `--force-cleanup` | 强制清理缓存，不询问确认 |
| `--dry-run` | 仅显示将要执行的操作，不实际执行 |
| `--apply` | 实际执行升级操作 |
| `--latest` | 升级到最新版本 |
| `--target-version <version>` | 升级到指定版本 |

## 验收（必须做）
```bash
(cd "${OPENCODE_CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode --version)
(cd "${OPENCODE_CONFIG_DIR}" && node node_modules/.bin/oh-my-opencode doctor)
```

## 常见问题

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

### 历史说明
- 本 skill 早期版本使用 `npm` 进行包管理，现已切换到 `bunx` 以与官方推荐方式保持一致。

