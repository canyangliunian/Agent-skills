## MODIFIED Requirements

### Requirement: Recommendation output schema
系统 SHALL 输出结构化的推荐结果，包含期刊标识信息、排序分数/依据、以及可解释说明，便于封装为 skill 或后续写表格报告。

#### Scenario: Reference doc exists for recommend entrypoint
- **WHEN** 用户需要基于本地 AJG CSV 推荐投稿期刊
- **THEN** 系统 MUST 提供 `references/abs_journal_recommend.md`，包含推荐入口用法、模式（easy/fit/value）、数据依赖与常见错误

