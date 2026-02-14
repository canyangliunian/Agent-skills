# 路径配置指南

oh-my-opencode-update skill 支持通过环境变量自定义所有路径，以适应不同的系统配置和部署场景。

## 环境变量

### OPENCODE_CONFIG_DIR

opencode 配置目录，也是 oh-my-opencode 的安装位置。

- **默认值**: `${HOME}/.config/opencode`
- **说明**: 包含 `package.json`、`node_modules/` 和配置文件（`opencode.json`、`oh-my-opencode.json`）
- **示例**:
  ```bash
  export OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
  export OPENCODE_CONFIG_DIR="/custom/config/opencode"
  ```

### OPENCODE_CACHE_DIR

缓存目录根目录。oh-my-opencode 会在此目录下创建 `oh-my-opencode` 子目录。

- **默认值**: `${HOME}/.cache`
- **说明**: oh-my-opencode 的缓存文件位置
- **示例**:
  ```bash
  export OPENCODE_CACHE_DIR="${HOME}/.cache"
  export OPENCODE_CACHE_DIR="/tmp/cache"
  ```

### OPENCODE_BIN

opencode 二进制文件的完整路径。

- **默认值**: `${HOME}/.opencode/bin/opencode`
- **说明**: opencode 命令行工具的位置。脚本会优先使用具备执行权限（可执行）的 `${OPENCODE_BIN}`；若该文件不存在或不可执行，则回退到 PATH 中的 `opencode`。
- **示例**:
  ```bash
  export OPENCODE_BIN="${HOME}/.opencode/bin/opencode"
  export OPENCODE_BIN="/usr/local/bin/opencode"
  ```

### BUN_INSTALL_TIMEOUT

bun 安装器超时时间（秒）。

- **默认值**: `300`
- **说明**: 使用 `bunx` 安装 oh-my-opencode 时的最大等待时间。如果网络较慢或需要安装较长时间，可以适当增加此值。
- **示例**:
  ```bash
  export BUN_INSTALL_TIMEOUT=600  # 10 分钟
  ```

## Bun 迁移说明

本 skill 现在使用官方推荐的 `bunx` 安装器，不再需要本地 node_modules 管理。

### 变化

- **不再需要**：npm、node 检查
- **新增要求**：bun 安装（`curl -fsSL https://bun.sh/install | bash`）
- **新增环境变量**：`BUN_INSTALL_TIMEOUT`（默认 300 秒）
- **新增选项**：`--force-cleanup`（跳过缓存清理确认）

### 迁移优势

1. **更快的安装速度**：bun 的包管理器比 npm 快数倍
2. **自动处理依赖**：`bunx` 会自动下载并缓存 oh-my-opencode 及其依赖
3. **简化环境**：无需本地 `node_modules/` 目录，减少磁盘占用
4. **更好的兼容性**：bun 兼容 Node.js 生态，确保与 oh-my-opencode 完全兼容

## 持久化配置

### 方法 1: Shell 配置文件（推荐）

将环境变量添加到你的 Shell 配置文件中，使其在每个新会话中自动生效：

**Bash** (`~/.bashrc` 或 `~/.bash_profile`):
```bash
# oh-my-opencode-update 配置
export OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
export OPENCODE_CACHE_DIR="${HOME}/.cache"
export OPENCODE_BIN="${HOME}/.opencode/bin/opencode"
```

**Zsh** (`~/.zshrc`):
```bash
# oh-my-opencode-update 配置
export OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
export OPENCODE_CACHE_DIR="${HOME}/.cache"
export OPENCODE_BIN="${HOME}/.opencode/bin/opencode"
```

**Fish** (`~/.config/fish/config.fish`):
```fish
# oh-my-opencode-update 配置
set -gx OPENCODE_CONFIG_DIR "$HOME/.config/opencode"
set -gx OPENCODE_CACHE_DIR "$HOME/.cache"
set -gx OPENCODE_BIN "$HOME/.opencode/bin/opencode"
```

添加后，重新加载配置文件或打开新的终端：
```bash
# Bash/Zsh
source ~/.bashrc  # 或 source ~/.zshrc

# Fish
source ~/.config/fish/config.fish
```

### 方法 2: 项目配置文件

在 skill 根目录（包含 SKILL.md 的目录）创建 `.env` 文件：

```bash
OPENCODE_CONFIG_DIR=${HOME}/.config/opencode
OPENCODE_CACHE_DIR=${HOME}/.cache
OPENCODE_BIN=${HOME}/.opencode/bin/opencode
```

然后在运行脚本前加载环境变量：

```bash
set -a  # 自动导出后续变量
source .env
set +a

# 现在运行脚本
bash scripts/oh_my_opencode_update.sh --apply --latest
```

### 方法 3: 一次性设置（临时）

仅在当前终端会话中设置：

```bash
export OPENCODE_CONFIG_DIR="/custom/path/to/config"
export OPENCODE_CACHE_DIR="/custom/path/to/cache"

bash scripts/oh_my_opencode_update.sh --apply --latest
```

## 验证配置

运行以下命令验证环境变量是否正确设置：

```bash
echo "OPENCODE_CONFIG_DIR: ${OPENCODE_CONFIG_DIR:-使用默认值}"
echo "OPENCODE_CACHE_DIR: ${OPENCODE_CACHE_DIR:-使用默认值}"
echo "OPENCODE_BIN: ${OPENCODE_BIN:-使用默认值}"

# 检查目录是否存在
echo ""
echo "目录检查:"
[ -d "${OPENCODE_CONFIG_DIR}" ] && echo "✓ OPENCODE_CONFIG_DIR 存在" || echo "✗ OPENCODE_CONFIG_DIR 不存在"
[ -d "${OPENCODE_CACHE_DIR}" ] && echo "✓ OPENCODE_CACHE_DIR 存在" || echo "✗ OPENCODE_CACHE_DIR 不存在"
[ -x "${OPENCODE_BIN}" ] && echo "✓ OPENCODE_BIN 可执行" || echo "✗ OPENCODE_BIN 不可执行或不存在"
```

## 常见配置场景

### 场景 1: 使用系统级安装

如果 opencode 安装在系统级别（如 `/usr/local/`）：

```bash
export OPENCODE_CONFIG_DIR="/usr/local/etc/opencode"
export OPENCODE_CACHE_DIR="/var/cache/opencode"
export OPENCODE_BIN="/usr/local/bin/opencode"
```

### 场景 2: 开发环境

在开发环境中使用临时配置：

```bash
export OPENCODE_CONFIG_DIR="${HOME}/dev/config/opencode"
export OPENCODE_CACHE_DIR="${HOME}/dev/cache"
export OPENCODE_BIN="${HOME}/dev/bin/opencode"
```

### 场景 3: Docker 容器

在 Docker 容器中运行：

```bash
export OPENCODE_CONFIG_DIR="/app/config"
export OPENCODE_CACHE_DIR="/app/cache"
export OPENCODE_BIN="/usr/local/bin/opencode"
```

## 故障排查

### 问题：脚本提示 "permission denied" 或权限错误

**解决方案**:
1. 检查 `OPENCODE_CONFIG_DIR` 的写权限
2. 如果目录不存在：脚本在 `--apply` 模式会自动创建；如创建失败再手动创建：
   ```bash
   mkdir -p "${OPENCODE_CONFIG_DIR}"
   ```
3. 确保当前用户对目录有写权限：
   ```bash
   ls -ld "${OPENCODE_CONFIG_DIR}"
   ```

### 问题：找不到 opencode 命令

**解决方案**:
1. 设置 `OPENCODE_BIN` 环境变量指向正确的 opencode 二进制路径，并确保该文件可执行（必要时 `chmod +x "${OPENCODE_BIN}"`）
2. 或者确保 opencode 在系统 PATH 中：
   ```bash
   which opencode
   ```

### 问题：找不到配置文件

**解决方案**:
1. 检查 `OPENCODE_CONFIG_DIR` 是否正确：
   ```bash
   ls "${OPENCODE_CONFIG_DIR}"
   ```
2. 确认 `opencode.json` 和 `oh-my-opencode.json` 文件存在
3. 如果不存在，可能需要重新初始化 opencode

### 问题：缓存清理失败

**解决方案**:
1. 检查 `OPENCODE_CACHE_DIR` 环境变量及其权限
2. 手动检查缓存目录：
   ```bash
   ls -la "${OPENCODE_CACHE_DIR}/oh-my-opencode"
   ```

## 环境变量优先级

1. 用户显式设置的环境变量（最高优先级）
2. 脚本中的默认值（通过 `: "${VAR:=default}"` 设定）

脚本使用 `: "${VAR:=default}"` 语法，这意味着：
- 如果变量已设置且非空：保持原值
- 如果变量未设置或为空：将其设置为默认值

例如：
```bash
: "${OPENCODE_CONFIG_DIR:=${HOME}/.config/opencode}"
```

这行代码的意思是：如果 `OPENCODE_CONFIG_DIR` 已设置且非空，使用它的值；否则将其设置为 `${HOME}/.config/opencode`。

> 备注：`${VAR:-default}` 只是在变量为空/未设置时“展开默认值”，不会写回变量；本脚本采用 `:=` 写回，便于后续统一引用。

## 最佳实践

1. **始终使用默认值**：除非有特殊需求，建议使用默认路径配置
2. **保持一致性**：确保所有环境变量指向一致的位置
3. **验证设置**：在运行脚本前，先验证环境变量是否正确
4. **文档化**：如果你为团队或 CI/CD 配置自定义路径，请记录在项目文档中
5. **测试**：首次使用自定义路径时，先用 `--dry-run` 参数测试

## 相关资源

- **主文档**: `SKILL.md` - oh-my-opencode-update 使用说明
- **脚本**: `scripts/oh_my_opencode_update.sh` - 升级脚本
- **规划**: `plan/task_plan.md` - 项目规划文档
