## MODIFIED Requirements

### Requirement: Update flow is explicit
系统 MUST 仅在用户明确提出“更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据”等意图时才触发抓取更新流程。

#### Scenario: Explicit update intent triggers fetch
- **WHEN** 用户明确要求更新 AJG/ABS 数据库
- **THEN** 系统 MUST 执行抓取脚本并更新 `assets/data/` 中的数据文件与元数据

## ADDED Requirements

### Requirement: Skill package is relocatable (no hard-coded root paths)
系统 MUST 保证该 skill 包可被复制或移动到任意目录后仍可运行：脚本内部不得依赖某个固定工程根目录的硬编码绝对路径来定位同包脚本与 `assets/` 资源。

#### Scenario: Entrypoints infer skill root from __file__
- **WHEN** 用户以任意当前工作目录（CWD）运行 `scripts/abs_journal.py`、`scripts/abs_journal_recommend.py` 或 `scripts/ajg_fetch.py`
- **THEN** 脚本 MUST 基于 `__file__` 推断 skill 根目录，并据此定位同包脚本与默认 `assets/data/` 位置

#### Scenario: Docs use the delivered absolute path by default
- **WHEN** 用户复制 `SKILL.md` 或 `references/` 中的示例命令执行
- **THEN** 示例命令 MUST 指向实际交付目录（例如 `~/.agents/skills/abs-journal` 的绝对路径），不得指向历史旧工程目录
