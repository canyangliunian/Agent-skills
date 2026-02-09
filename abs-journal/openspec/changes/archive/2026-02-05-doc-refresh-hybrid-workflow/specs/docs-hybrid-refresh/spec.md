## ADDED Requirements

### Requirement: Documentation reflects hybrid-only workflow
系统 MUST 仅在文档中推荐混合模式工作流（脚本候选池 → AI 仅在候选池内筛选 → 子集校验 → 三段固定列报告），不得出现旧入口或纯脚本模式作为可用路径。

#### Scenario: Quick start shows hybrid commands
- **WHEN** 用户查看 SKILL.md 或 README 的“Quick Start/示例命令”
- **THEN** MUST 提供混合模式命令链：`scripts/abs_journal.py recommend --hybrid --export_candidate_pool_json ... [--ai_output_json ... --hybrid_report_md ...]`
- **AND THEN** 示例使用绝对路径并包含星级过滤、候选池导出、AI 输出、校验与报告步骤

#### Scenario: No legacy entrypoint mentioned
- **WHEN** 在文档中搜索 `abs_journal_recommend.py` 或“纯脚本模式”
- **THEN** 搜索结果 MUST 为空（允许在历史归档/变更描述中提到“已删除”但不作为可用路径）

### Requirement: References capture detailed hybrid workflow
系统 MUST 将混合模式的详细步骤（参数说明、三类星级过滤、AI 提示模板、子集校验、报告生成）集中在 references 文档中，主文档仅做触发与链接。

#### Scenario: References include full command chain
- **WHEN** 用户查看 `references/abs_journal_recommend.md`
- **THEN** 文档 MUST 包含：
  - 候选池导出命令（含 `--hybrid`、`--export_candidate_pool_json`、`--rating_filter`）
  - AI 输出 JSON 结构与模板位置
  - 子集校验命令（`abs_ai_review.py`）
  - 报告生成命令（`hybrid_report.py` 或 `abs_journal.py --hybrid_report_md ...`）

### Requirement: Writing-skills compliance for documentation
文档 MUST 遵循 writing-skills 原则：主文档精简、描述字段聚焦“何时使用”，避免在描述中嵌入流程细节；示例命令使用绝对路径且可直接运行。

#### Scenario: SKILL.md description is trigger-only
- **WHEN** 阅读 SKILL.md 的 description 与前几节
- **THEN** 描述 MUST 仅包含触发条件与核心约束，不展开完整流程；详细步骤通过 References 链接提供
