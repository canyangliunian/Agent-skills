# abs-skill-package Specification

## Purpose
TBD - created by archiving change skillize-ajg-and-recommendation. Update Purpose after archive.
## Requirements
### Requirement: Repository root matches skill package layout
系统 MUST 保持仓库根目录为单一 skill 包 `ABS-Journal` 的固定结构：`scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`。

#### Scenario: Skill layout exists at repository root
- **WHEN** 用户查看仓库根目录
- **THEN** MUST 能看到 `scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`

#### Scenario: Local AJG data lives under assets
- **WHEN** skill 需要承载本地 AJG 数据文件（CSV/JSON/JSONL/meta）
- **THEN** 系统 MUST 将这些数据存放在 `assets/data/` 下，而不是根目录 `data/`

### Requirement: Progressive disclosure in SKILL.md
系统 SHALL 保持 `SKILL.md` 精简，只包含触发条件与最小工作流，并将较重的字段说明/FAQ/脚本参数细节放入 `references/` 或 `assets/`，并在 `SKILL.md` 中以链接方式引用。

#### Scenario: Script-specific docs live in references
- **WHEN** 需要指导用户如何使用 `scripts/ajg_fetch.py` 或混合模式推荐入口 `scripts/abs_journal.py`
- **THEN** 系统 MUST 在 `references/` 下提供对应的脚本说明文档，并在 `SKILL.md` 的 References 区域引用它们

### Requirement: Default recommendation uses local AJG data
系统 MUST 默认使用本地已有 AJG CSV 数据进行推荐，不得在用户未明确要求时自动触发网络更新。

#### Scenario: Recommend uses assets data directory by default
- **WHEN** 用户请求推荐且未指定 `--ajg_csv/--data_dir` 覆盖路径
- **THEN** 系统 MUST 默认从 `assets/data/` 中读取 AJG CSV

### Requirement: Update flow is explicit
系统 MUST 仅在用户明确提出“更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据”等意图时才触发抓取更新流程。

#### Scenario: Explicit update intent triggers fetch
- **WHEN** 用户明确要求更新 AJG/ABS 数据库
- **THEN** 系统 MUST 执行抓取脚本并更新 `assets/data/` 中的数据文件与元数据

### Requirement: Skill package is relocatable (no hard-coded root paths)
系统 MUST 保证该 skill 包可被复制或移动到任意目录后仍可运行：脚本内部不得依赖某个固定工程根目录的硬编码绝对路径来定位同包脚本与 `assets/` 资源。

#### Scenario: Entrypoints infer skill root from __file__
- **WHEN** 用户以任意当前工作目录（CWD）运行 `scripts/abs_journal.py` 或 `scripts/ajg_fetch.py`
- **THEN** 脚本 MUST 基于 `__file__` 推断 skill 根目录，并据此定位同包脚本与默认 `assets/data/` 位置

#### Scenario: Docs use the delivered absolute path by default
- **WHEN** 用户复制 `SKILL.md` 或 `references/` 中的示例命令执行
- **THEN** 示例命令 MUST 指向实际交付目录（例如 `~/.agents/skills/abs-journal` 的绝对路径），不得指向历史旧工程目录
