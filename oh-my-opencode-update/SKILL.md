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

## 适用环境（本机固定路径）
- `opencode`：`/Users/lingguiwang/.opencode/bin/opencode`
- 依赖目录（oh-my-opencode 安装在这里）：`/Users/lingguiwang/.config/opencode`
- 配置文件：
  - `/Users/lingguiwang/.config/opencode/opencode.json`
  - `/Users/lingguiwang/.config/opencode/oh-my-opencode.json`
- 缓存目录（可选清理）：`/Users/lingguiwang/.cache/oh-my-opencode`

## 使用方式（脚本入口）
脚本：`/Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh`

### 1) Dry-run（推荐先跑）
```bash
bash /Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh --dry-run --latest
```

### 2) 实际执行：升级到 latest
```bash
bash /Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh --apply --latest
```

### 3) 实际执行：升级到指定版本
```bash
bash /Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh --apply --target-version 3.2.2
```

## 验收（必须做）
- `cd /Users/lingguiwang/.config/opencode && node node_modules/.bin/oh-my-opencode --version`
- `cd /Users/lingguiwang/.config/opencode && node node_modules/.bin/oh-my-opencode doctor`

## 常见问题（本机已遇到）
- `bunx ...` 报 `bun is unable to write files to tempdir: PermissionDenied`
  - 本技能默认不依赖 bunx；优先在依赖目录内使用 `bun remove/add`。
- `bun remove/add` 报无法写 `package.json`
  - 说明目录写权限/沙盒限制；需要提升权限执行。

