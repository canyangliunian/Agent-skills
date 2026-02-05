## Purpose

定义基于本地 AJG 目录数据进行投稿期刊推荐的能力契约：输入论文信息、读取 AJG 数据文件、支持不同推荐模式，并输出可解释的结构化推荐结果。
## Requirements
### Requirement: Accept structured manuscript input
系统 SHALL 接收用户提供的论文信息作为输入，并支持“最少信息可用”的场景（例如仅题目/摘要）。

#### Scenario: Minimal input (title only)
- **WHEN** 用户仅提供论文题目
- **THEN** 系统 MUST 仍然生成推荐结果，并在解释中说明信息不足带来的不确定性

#### Scenario: Rich input (title + abstract + intro)
- **WHEN** 用户提供题目、摘要与引言（或全文片段）
- **THEN** 系统 MUST 将这些信息用于提升主题匹配与筛选准确度

### Requirement: Consume AJG dataset outputs
系统 SHALL 以本地 AJG 数据文件作为主要数据来源，并要求数据输入满足明确的文件/字段契约。

#### Scenario: Default AJG CSV path under assets/data
- **WHEN** 用户未显式指定 AJG CSV 路径
- **THEN** 系统 MUST 默认读取 `assets/data/ajg_<year>_journals_core_custom.csv`（实际年份以本地最新可用文件为准）

### Requirement: Provide multi-objective recommendation modes
系统 SHALL 至少支持以下推荐维度/模式：主题最匹配、最易发表、性价比（如 ABS 等级较高但分区较低等），并保证输出可解释。

#### Scenario: Topic-fit mode
- **WHEN** 用户选择“主题匹配”模式
- **THEN** 系统 MUST 优先按主题相关性对候选期刊排序，并输出每个推荐的主题匹配解释字段

#### Scenario: Ease-of-publication mode
- **WHEN** 用户选择“易发表”模式
- **THEN** 系统 MUST 使用可解释的代理指标（例如较低门槛/更宽投稿范围/历史接受度等，具体以实现为准）进行排序，并说明采用了哪些信号

#### Scenario: Value-for-money mode
- **WHEN** 用户选择“性价比”模式
- **THEN** 系统 MUST 基于 AJG 等级与（如可用）分区/指标等信息形成排序，并输出“性价比”解释字段

### Requirement: Recommendation output schema
系统 SHALL 输出结构化的推荐结果，包含期刊标识信息、排序分数/依据、以及可解释说明，便于封装为 skill 或后续写表格报告。

#### Scenario: Reference doc exists for recommend entrypoint
- **WHEN** 用户需要基于本地 AJG CSV 推荐投稿期刊
- **THEN** 系统 MUST 提供 `references/abs_journal_recommend.md`，包含推荐入口用法、模式（easy/fit/value）、数据依赖与常见错误

