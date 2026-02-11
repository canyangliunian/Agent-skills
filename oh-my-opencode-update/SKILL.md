---
name: oh-my-opencode-update
description: Use when upgrading, reinstalling, or troubleshooting the oh-my-opencode plugin, especially when old caches, lockfiles, or permissions prevent the new version from taking effect.
---

# oh-my-opencode-update

面向唯一长期用户：凌贵旺（Guiwang Ling）。

## 核心目标
- **默认升级到最新版本（latest）**，并支持 **指定版本（pinned version）**。
- 先备份，再温和卸载，再清理缓存（删除前二次确认），最后安装并验证。
- 任何关键步骤失败：**立刻停止**（不自动扩大破坏范围）。

## 适用环境（可通过环境变量自定义）

### 默认路径
以下路径为默认值，可通过环境变量覆盖：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录（oh-my-opencode 安装位置） |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${HOME}/.opencode/bin/opencode` | opencode 二进制文件路径 |

### 配置文件
- opencode 配置：`${OPENCODE_CONFIG_DIR}/opencode.json`
- oh-my-opencode 配置：`${OPENCODE_CONFIG_DIR}/oh-my-opencode.json`
- 缓存目录：`${OPENCODE_CACHE_DIR}/oh-my-opencode`

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
cd ${OPENCODE_CONFIG_DIR}
node node_modules/.bin/oh-my-opencode --version
node node_modules/.bin/oh-my-opencode doctor
```

## 常见问题

### npm 相关问题
- `npm install` 报权限错误
  - 检查 `${OPENCODE_CONFIG_DIR}` 的写权限
  - 确保当前用户对目录有写权限：`ls -ld "${OPENCODE_CONFIG_DIR}"`
- `npm uninstall` 失败
  - 可能是 `package.json` 或 `node_modules` 权限问题
  - 检查目录权限或使用 `sudo`（不推荐，优先修复目录权限）

### 历史说明
- 本 skill 早期版本使用 `bun` 作为包管理器，现已切换到 `npm` 以提高兼容性和稳定性

