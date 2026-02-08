---
name: oh-my-opencode-update
description: Use when upgrading, reinstalling, or troubleshooting the oh-my-opencode plugin for opencode (OpenCode), especially when old caches/lockfiles/permissions cause the new version not to take effect; supports upgrading to latest or a pinned version with backup and verification.
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

## 常见问题（本机已遇到）
- `bunx ...` 报 `bun is unable to write files to tempdir: PermissionDenied`
  - 本技能默认不依赖 bunx；优先在依赖目录内使用 `bun remove/add`。
- `bun remove/add` 报无法写 `package.json`
  - 说明目录写权限/沙盒限制；需要提升权限执行。

