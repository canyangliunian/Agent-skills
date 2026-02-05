## ADDED Requirements

### Requirement: Source-of-truth alignment
SKILL 文档的流程、参数、输出格式和路径描述 SHALL align with the implemented behavior in `scripts/` 和 `references/`（以项目内文件为准）。

#### Scenario: Detect conflict
- **WHEN** a SKILL.md instruction contradicts `scripts/abs_journal.py` or `references/abs_journal_recommend.md`
- **THEN** the SKILL SHALL be updated to match the actual script/reference behavior.

### Requirement: Path convention clarity
Default examples SHALL use project-root-relative paths under `assets/`, and only use absolute paths when explicitly justified.

#### Scenario: Example command
- **WHEN** providing sample commands in SKILL.md
- **THEN** paths SHALL be relative (e.g., `assets/...`) unless a note states absolute path is required.

### Requirement: Hybrid flow completeness
SKILL.md SHALL require tri-mode (fit/easy/value) outputs with fixed columns `序号 | 期刊名 | ABS星级 | 期刊主题`, matching script-generated reports.

#### Scenario: Missing mode in guidance
- **WHEN** SKILL.md omits easy/value or suggests单模式
- **THEN** the SKILL SHALL be corrected to mandate all three modes simultaneously.
