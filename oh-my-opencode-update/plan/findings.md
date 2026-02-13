# Findings & Decisions — oh-my-opencode-update 路径硬编码修复

## Session: 2026-02-09 (当前会话 - 路径硬编码修复)

### 修复目标
修复 oh-my-opencode-update skill 中的路径硬编码问题，使其可移植、可分享给其他人使用。

### 团队配置
- **团队名称**: oh-my-opencode-fix
- **团队文件**: `~/.claude/teams/oh-my-opencode-fix/config.json`
- **任务列表**: `~/.claude/tasks/oh-my-opencode-fix/`
- **工作目录**: `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update`

### 成员职责

| 成员 | Agent Type | 负责任务 | 关键点 |
|------|-----------|----------|--------|
| team-lead | general-purpose | #1, #7 | 团队协调、规划文档更新、报告生成 |
| path-fix-implementer | general-purpose | #2, #3, #4 | 修复脚本、更新 SKILL.md、创建配置文档 |
| scripts-reviewer | general-purpose | #5 | 使用 requesting-code-review 审核脚本 |
| reference-reviewer | general-purpose | #6 | 使用 writing-skills 审核文档 |

### 核心问题发现

#### 问题 1: SKILL.md 硬编码路径（第 16-39 行）

**现状**:
```markdown
## 适用环境（本机固定路径）
- `opencode`：`/Users/lingguiwang/.opencode/bin/opencode`
- 依赖目录（oh-my-opencode 安装在这里）：`/Users/lingguiwang/.config/opencode`
- 配置文件：
  - `/Users/lingguiwang/.config/opencode/opencode.json`
  - `/Users/lingguiwang/.config/opencode/oh-my-opencode.json`
- 缓存目录（可选清理）：`/Users/lingguiwang/.cache/oh-my-opencode`

## 使用方式（脚本入口）
脚本：`/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh`
```

**影响**:
- Skill 无法分享给其他人使用
- 路径硬编码特定用户（lingguiwang）
- 违反可移植性原则

**解决方案**: 使用环境变量语法 `${OPENCODE_CONFIG_DIR:-${HOME}/.config/opencode}`

---

#### 问题 2: 脚本示例命令使用绝对路径（第 27-38 行）

**现状**:
```bash
bash /Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh --dry-run --latest
```

**影响**:
- 无法从不同目录运行脚本
- 无法在不同位置安装 skill
- 用户无法直接复制执行示例命令

**解决方案**: 使用相对路径 `bash scripts/oh_my_opencode_update.sh`

---

#### 问题 3: 验收命令使用绝对路径（第 42-43 行）

**现状**:
```bash
cd /Users/lingguiwang/.config/opencode && node node_modules/.bin/oh-my-opencode --version
```

**影响**:
- 使用绝对路径，无法通过环境变量自定义
- 不符合环境变量使用模式

**解决方案**: 使用 `cd ${OPENCODE_CONFIG_DIR}`

---

#### 问题 4: 缺少环境变量配置文档

**现状**: 用户不知道如何自定义路径，缺少配置说明

**影响**: 用户遇到自定义路径需求时无法自行解决

**解决方案**: 创建 `references/paths_config.md` 详细说明环境变量配置

---

### 参考项目分析

#### ABS-Journal 项目路径处理方案

**文件**: `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/scripts/abs_paths.py`

**关键模式**:
```python
def _env_path(name: str) -> Optional[Path]:
    """从环境变量获取路径"""
    v = os.environ.get(name, "").strip()
    if not v:
        return None
    return Path(os.path.expanduser(v)).resolve()

def skill_root() -> Path:
    """动态解析 skill 根目录"""
    override = _env_path("ABS_JOURNAL_HOME")
    if override is not None:
        return override
    # 向上查找 SKILL.md
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "SKILL.md").is_file():
            return p
    return here.parent.parent.resolve()
```

**关键设计点**:
- 支持环境变量覆盖
- 动态查找 SKILL.md 确定根目录
- 使用 `Path.resolve()` 确保绝对路径

---

### Shell 脚本路径处理方案

对于 Bash 脚本，采用以下模式：

```bash
# 路径配置（优先使用环境变量，否则使用默认值）
: "${OPENCODE_CONFIG_DIR:=${HOME}/.config/opencode}"
: "${OPENCODE_CACHE_DIR:=${HOME}/.cache}"
: "${OPENCODE_BIN:=${HOME}/.opencode/bin/opencode}"

# 核心路径
CONFIG_DIR="${OPENCODE_CONFIG_DIR}"
OPENCODE_JSON="${CONFIG_DIR}/opencode.json"
OMO_JSON="${CONFIG_DIR}/oh-my-opencode.json"
OMO_CACHE="${OPENCODE_CACHE_DIR}/oh-my-opencode"
```

**关键设计点**:
- 使用 `${VAR:-default}` 语法提供默认值
- 支持环境变量覆盖
- 保持向后兼容性

---

### 环境变量命名规范

| 环境变量 | 默认值 | 用途 |
|---------|--------|------|
| `OPENCODE_CONFIG_DIR` | `${HOME}/.config/opencode` | opencode 配置目录（oh-my-opencode 安装位置） |
| `OPENCODE_CACHE_DIR` | `${HOME}/.cache` | 缓存目录根目录 |
| `OPENCODE_BIN` | `${OPENCODE_HOME}/bin/opencode` | opencode 二进制文件路径 |

**命名原则**:
- 使用 `OPENCODE_` 前缀避免与其他工具冲突
- 名称清晰表达用途
- 使用 `_DIR` 和 `_BIN` 后缀区分类型

---

### 可移植性检查清单

- [x] 识别 SKILL.md 硬编码路径问题
- [ ] SKILL.md 中移除所有硬编码用户路径
- [ ] 示例命令使用相对路径
- [ ] 支持环境变量自定义所有路径
- [ ] 提供环境变量配置文档
- [ ] 脚本能从 skill 任何安装位置运行
- [ ] 默认值使用 `${HOME}` 适配不同用户

---

### 历史审核记录

#### Session: 2026-02-09 (审核项目初始化)

**团队名称**: oh-my-opencode-audit

**审核结果**:

| 审核项 | 评分 | 状态 |
|--------|------|------|
| 文档审核 | B+ | 合格 |
| 脚本审核 | B- | 需修复 |

**综合评分**: B （存在中等优先级问题，需修复）

**当时已完成的修复**:
- 脚本中部分硬编码路径改为 `${HOME}` 变量
- SKILL.md 中的路径目录名修正（Skills → Agent-skills）

**遗留问题**:
- SKILL.md 仍包含完整的硬编码用户路径（第 16-39 行）
- 缺少环境变量配置文档
- 脚本示例命令仍使用绝对路径

---

### 项目资源

**核心文件**:
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/SKILL.md`
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh`

**修复记录**:
- `plan/task_plan.md` - 任务计划与进度
- `plan/findings.md` - 问题发现与决策（本文件）
- `plan/progress.md` - 会话日志
- `plan/fix_summary_report.md` - 修复完成报告（待生成）

---

## Session: 2026-02-10 (bun → npm 切换审核)

### 审核发现

#### 问题 1: SKILL.md 中残留 bun 相关说明（第 69-72 行）

**现状**:
```markdown
## 常见问题（本机已遇到）
- `bunx ...` 报 `bun is unable to write files to tempdir: PermissionDenied`
  - 本技能默认不依赖 bunx；优先在依赖目录内使用 `bun remove/add`。
- `bun remove/add` 报无法写 `package.json`
  - 说明目录写权限/沙盒限制；需要提升权限执行。
```

**影响**:
- 脚本已经改用 npm（第 147、149、174、176 行），但文档还在说 bun
- 用户会困惑为什么文档说 bun 但实际用的是 npm
- 常见问题部分已经过时，不再适用

**解决方案**:
- 删除或更新"常见问题"部分，改为 npm 相关的常见问题
- 或者说明"历史上使用过 bun，现已切换到 npm"

---

#### 问题 2: 脚本路径可移植性 ✅ 已解决

**验证结果**:
- ✅ 脚本使用 `SCRIPT_DIR` 和 `SKILL_ROOT` 动态解析路径（第 16-17 行）
- ✅ 支持环境变量覆盖所有路径（第 20-22 行）
- ✅ 日志目录优先使用 `${SKILL_ROOT}/plan`（第 50 行）
- ✅ 可以从任何位置运行脚本

**结论**: 路径可移植性问题已在之前会话中完全解决。

---

#### 问题 3: 脚本包管理器 ✅ 已使用 npm

**验证结果**:
- ✅ 第 147 行：`npm uninstall oh-my-opencode`
- ✅ 第 174 行：`npm install ${pkg}`
- ✅ 无任何 bun 命令残留

**结论**: 脚本已完全使用 npm，无需修改。

---

### 修复计划

| 问题 | 优先级 | 修复方案 | 状态 |
|------|--------|----------|------|
| SKILL.md 残留 bun 说明 | 高 | 更新"常见问题"部分为 npm 相关内容 | pending |
| 路径可移植性 | - | 已解决 ✅ | complete |
| 脚本包管理器 | - | 已使用 npm ✅ | complete |

---

## Session: 2026-02-13 (缓存清理分析)

### 分析目标

分析 `scripts/oh_my_opencode_update.sh` 脚本中第 262-288 行的缓存清理部分，以及相关文档，确定需要修改的具体位置。

### 当前脚本清理的缓存位置

#### 位置 1: oh-my-opencode 缓存目录

**路径**: `${OPENCODE_CACHE_DIR}/oh-my-opencode`
- **默认值**: `${HOME}/.cache/oh-my-opencode`
- **脚本行号**: 第 246-260 行
- **清理方式**: 单个目录清理，需要用户交互确认

**代码片段**:
```bash
echo "[5/7] Cache cleanup (optional)" | tee -a "${out}/log.txt"
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
fi
```

---

#### 位置 2: opencode 插件缓存目录

**路径**: `${OPENCODE_CACHE_DIR}/opencode/node_modules/oh-my-opencode*`
- **默认值**: `${HOME}/.cache/opencode/node_modules/oh-my-opencode*`
- **脚本行号**: 第 262-288 行
- **清理方式**: 使用 glob 模式 `oh-my-opencode*` 匹配所有相关缓存，需要用户交互确认

**代码片段**:
```bash
# Clean opencode plugin cache (where version info is read from)
# Use glob pattern to clean all oh-my-opencode related caches
local opencode_plugin_cache_dir="${OPENCODE_CACHE_DIR}/opencode/node_modules"
if [ -d "${opencode_plugin_cache_dir}" ]; then
  local found_cache=0
  for cache_path in "${opencode_plugin_cache_dir}"/oh-my-opencode*; do
    if [ -e "${cache_path}" ]; then
      found_cache=1
      echo "Found opencode plugin cache: ${cache_path}" | tee -a "${out}/log.txt}"
      if [ ${DRY_RUN} -eq 1 ]; then
        echo "DRY: rm -rf ${cache_path} (would ask confirmation)" | tee -a "${out}/log.txt"
      else
        if confirm "Delete opencode plugin cache ${cache_path}?"; then
          rm -rf "${cache_path}"
          echo "Deleted ${cache_path}" | tee -a "${out}/log.txt"
        else
          echo "Skipped deleting ${cache_path}" | tee -a "${out}/log.txt"
        fi
      fi
    fi
  done
  if [ ${found_cache} -eq 0 ]; then
    echo "No oh-my-opencode cache found in ${opencode_plugin_cache_dir}" | tee -a "${out}/log.txt"
  fi
fi
```

---

### 相关文档分析

#### SKILL.md

**提及缓存清理的位置**:

| 行号 | 内容摘要 |
|------|---------|
| 第 25 行 | `[5/7] Cache cleanup (optional)` - 执行流程表格中说明此步骤 |
| 第 56 行 | `~/.cache/oh-my-opencode` - 缓存目录说明 |
| 第 57 行 | `~/.cache/opencode/node_modules/oh-my-opencode*` - opencode 插件缓存 |

**执行流程表格**:

| 步骤 | 名称 | 说明 |
|------|------|------|
| [5/7] | Cache cleanup (optional) | 可选的缓存清理（需确认），包括 ~/.cache/oh-my-opencode 和 ~/.cache/opencode/node_modules/oh-my-opencode* |

#### references/paths_config.md

**提及缓存清理的位置**:

| 行号 | 内容摘要 |
|------|---------|
| 第 19-29 行 | `OPENCODE_CACHE_DIR` 环境变量说明 |
| 第 197-204 行 | "缓存清理失败"故障排查章节 |

---

### 文档与脚本一致性验证

| 验证项 | 文档说明 | 脚本实现 | 一致性 |
|--------|---------|---------|--------|
| 缓存目录 | `~/.cache/oh-my-opencode` | `${OPENCODE_CACHE_DIR}/oh-my-opencode` | ✅ 一致 |
| 插件缓存 | `~/.cache/opencode/node_modules/oh-my-opencode*` | glob 模式匹配 | ✅ 一致 |
| 交互确认 | 需确认 | `confirm()` 函数 | ✅ 一致 |
| 步骤编号 | [5/7] | `[5/7] Cache cleanup (optional)` | ✅ 一致 |

---

### 可能遗漏的缓存位置分析

| 缓存类型 | 位置 | 清理状态 | 原因 |
|---------|------|---------|------|
| oh-my-opencode 主缓存 | `${OPENCODE_CACHE_DIR}/oh-my-opencode` | ✅ 已清理 | - |
| opencode 插件缓存 | `${OPENCODE_CACHE_DIR}/opencode/node_modules/oh-my-opencode*` | ✅ 已清理 | - |
| npm 全局缓存 | `~/.npm` | ❌ 未清理 | 全局共享，不应每次升级都清理 |
| 配置目录 node_modules | `${OPENCODE_CONFIG_DIR}/node_modules` | ❌ 未清理 | npm uninstall 会清理，这是安装位置 |

**结论**: 无明显遗漏，当前实现已考虑所有需要清理的缓存位置。

---

### 设计优点

1. **使用 glob 模式**: `oh-my-opencode*` 可以匹配不同版本的缓存
2. **交互确认**: 每个缓存删除都需要用户确认，安全可靠
3. **dry-run 支持**: 可以预览将要删除的内容
4. **日志记录**: 所有操作都会记录到日志文件

---

### 潜在改进建议（非必需）

1. **添加缓存大小显示**: 在删除前显示缓存大小，帮助用户决策
2. **添加"全部确认"选项**: 避免多次确认，提高效率

---

### 分析结论

✅ **文档与脚本完全一致** - 无需修改

1. 当前脚本清理的缓存位置正确
2. 文档与脚本实现完全一致
3. 无明显遗漏的缓存位置
4. 设计合理，安全可靠

---

*Last updated: 2026-02-13*
