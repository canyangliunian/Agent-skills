## MODIFIED Requirements

### Requirement: Progressive disclosure in SKILL.md
系统 SHALL 保持 `SKILL.md` 精简，只包含触发条件与最小工作流，并将较重的字段说明/FAQ/脚本参数细节放入 `references/` 或 `assets/`，并在 `SKILL.md` 中以链接方式引用。

#### Scenario: Script-specific docs live in references
- **WHEN** 需要指导用户如何使用 `scripts/ajg_fetch.py` 或 `scripts/abs_journal.py`
- **THEN** 系统 MUST 在 `references/` 下提供对应的脚本说明文档，并在 `SKILL.md` 的 References 区域引用它们
