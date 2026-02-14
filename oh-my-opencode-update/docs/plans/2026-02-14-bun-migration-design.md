# oh-my-opencode-update Bun 迁移设计

**日期**: 2026-02-14
**用户**: 凌贵旺 (Guiwang Ling)
**目标**: 将包管理器从 npm 切换到 bunx（官方推荐方式）

---

## 设计概述

将 `oh-my-opencode-update` 脚本从基于 npm 的本地安装切换到使用官方推荐的 `bunx` 安装器。核心变化是**完全交给官方安装器处理所有安装逻辑**，脚本只负责环境准备、缓存清理和结果验证。

## 架构变化

### 流程对比

| 步骤 | 新方案（4 步） | 当前方案（7 步） | 变化 |
|------|----------------|------------------|------|
| [1/4] | Bun 检查 | npm/node 检查 | 包管理器切换 |
| [2/4] | 备份配置 | 备份配置 | 不变 |
| [3/4] | 缓存清理 + 调用官方安装器 | 温和卸载 + 缓存清理 | **核心变化** |
| [4/4] | 验证 | 安装 + 验证 | 简化 |

### 核心命令

```bash
# 升级到最新版本
bunx oh-my-opencode@latest install --no-tui

# 升级到指定版本
bunx oh-my-opencode@<version> install --no-tui
```

**关键参数说明**：
- `--no-tui`: 非交互式模式，适合脚本自动化
- `@<version>`: 指定版本，`@latest` 表示最新版

### 版本支持

脚本继续支持两个版本指定方式：

| 脚本参数 | 实际执行的命令 |
|-----------|--------------|
| `--latest` | `bunx oh-my-opencode@latest install --no-tui` |
| `--target-version 3.2.2` | `bunx oh-my-opencode@3.2.2 install --no-tui` |

---

## 缓存清理逻辑

### 清理目标

1. `~/.cache/oh-my-opencode/` - oh-my-opencode 主缓存目录
2. `~/.cache/opencode/node_modules/oh-my-opencode*` - opencode 插件缓存（glob 模式）
3. `~/.cache/opencode/package.json` - 移除 oh-my-opencode 依赖

### 执行流程

```
[3/4] 缓存清理
├── 检测缓存目录是否存在
├── 显示每个目录的大小（du -sh）
├── Dry-run: 显示将被删除的路径
├── Apply: 逐个确认后删除（交互式）
└── 清理 package.json 依赖（存在时）
```

### 增强功能

- **大小显示**: 显示每个缓存目录的大小，帮助用户判断
- **清理日志**: 记录删除了哪些文件
- **强制清理**: `--force-cleanup` 选项跳过所有确认

### 环境变量兼容

- `OPENCODE_CACHE_DIR` 继续生效
- 清理逻辑使用该变量，保持可配置性

---

## 错误处理和诊断

### 前置检查

| 检查项 | 失败处理 |
|---------|----------|
| `bun` 是否安装 | 立即退出，提示安装命令 |
| `bunx` 是否可用 | 立即退出，提示安装 bun |
| `opencode` 是否安装 | WARN 提示，不阻塞 |
| 配置目录是否可写 | 立即退出，提示修复命令 |

### 错误场景处理

| 错误类型 | 处理方式 |
|-----------|----------|
| `bun` 未安装 | 退出并提示: `curl -fsSL https://bun.sh/install \| bash` |
| `bunx` 执行失败 | 输出完整错误 + 诊断建议 |
| `opencode` 未安装 | WARN 提示，继续执行 |
| 配置目录不可写 | 退出并提示: `chmod u+w <dir>` |

### 诊断功能

- 显示 bun 版本: `bun --version`
- 显示目标包信息（可选）: `bun pm ls oh-my-opencode`
- 失败时提供诊断步骤:
  1. 检查网络: `curl -I https://registry.npmjs.org/`
  2. 检查 bunx: `bunx --version`
  3. 验证版本: `bun pm ls oh-my-opencode`

### 退出码设计

| 退出码 | 含义 |
|-------|------|
| 0 | 成功 |
| 1 | 前置检查失败 |
| 2 | 安装失败 |
| 3 | 验证失败 |

---

## 命令行接口

### 使用方式

```bash
# Dry-run（预览）
bash scripts/oh_my_opencode_update.sh --dry-run --latest
bash scripts/oh_my_opencode_update.sh --dry-run --target-version 3.2.2

# Apply（执行）
bash scripts/oh_my_opencode_update.sh --apply --latest
bash scripts/oh_my_opencode_update.sh --apply --target-version 3.2.2

# 强制清理（可选）
bash scripts/oh_my_opencode_update.sh --apply --latest --force-cleanup
```

### 选项说明

| 选项 | 说明 |
|------|------|
| `--dry-run` | 仅显示将要执行的操作，不实际执行 |
| `--apply` | 实际执行操作 |
| `--latest` | 升级到最新版本（默认） |
| `--target-version X.Y.Z` | 升级到指定版本 |
| `--force-cleanup` | 跳过所有确认，直接清理缓存 |

### 新增选项说明

**`--force-cleanup`**: 强制清理模式
- 不使用时：逐个询问每个缓存目录是否删除
- 使用时：直接删除所有缓存，适用于 CI/CD 或无人值守场景

---

## 验证逻辑

### 验证步骤

```bash
# 1. 检查插件是否注册
grep -q "oh-my-opencode" ~/.config/opencode/opencode.json

# 2. 检查配置文件是否存在
test -f ~/.config/opencode/oh-my-opencode.json

# 3. 运行官方验证（不阻塞）
opencode doctor || echo "WARN: opencode doctor 失败"
```

### 日志输出

- 彩色状态标识: `[OK]`、`[WARN]`、`[ERROR]`
- 步骤进度: `[1/4]`、`[2/4]`、`[3/4]`、`[4/4]`
- 日志文件: `plan/run_<timestamp>/log.txt`

---

## 环境变量

### 支持的环境变量

| 变量 | 默认值 | 说明 |
|------|---------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录 |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${HOME}/.opencode/bin/opencode` | opencode 二进制路径 |
| `BUN_INSTALL_TIMEOUT` | `300` | bunx 超时时间（秒） |

### 持久化配置

保持现有方式：
- Shell 配置文件（`~/.bashrc`、`~/.zshrc` 等）
- 项目 `.env` 文件

详见 `references/paths_config.md`。

---

## 关键移除项

以下功能在 bun 迁移后不再需要：

| 功能 | 原因 |
|------|------|
| `npm uninstall` | 官方安装器自行管理安装 |
| `npm install --save-exact` | 改用 `bunx` 调用安装器 |
| `--ignore-scripts` 处理 | 官方安装器自处理 postinstall |
| `NPM_INSTALL_TIMEOUT` | 改用 `BUN_INSTALL_TIMEOUT` |
| node_modules 管理 | 官方安装器自行处理 |

---

## 实现检查清单

- [ ] 创建新脚本 `scripts/oh_my_opencode_update.sh`（基于 bun）
- [ ] 更新 `SKILL.md` 文档
- [ ] 更新 `references/paths_config.md`（如有需要）
- [ ] 测试 `--dry-run` 模式
- [ ] 测试 `--apply --latest` 模式
- [ ] 测试 `--apply --target-version X.Y.Z` 模式
- [ ] 测试 `--force-cleanup` 选项
- [ ] 验证环境变量兼容性
- [ ] 更新 plan/task_plan.md（如需要）
