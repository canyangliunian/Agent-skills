## MODIFIED Requirements

### Requirement: Provide multi-objective recommendation modes
系统 SHALL 至少支持以下推荐维度/模式：主题最匹配、最易发表、性价比，并保证输出可解释；同时系统 MUST 将“主题贴合候选集”作为所有模式的共同前置条件（参见 `topic-fit-gating` 能力）。

#### Scenario: Topic-fit mode
- **WHEN** 用户选择“主题匹配”模式（`mode=fit`）
- **THEN** 系统 MUST 先应用主题贴合候选集筛选，再在候选集内优先按主题相关性（贴合分）对期刊排序，并输出每个推荐的主题匹配解释字段（包含 `fit_score` 或等价指标）

#### Scenario: Ease-of-publication mode
- **WHEN** 用户选择“易发表”模式（`mode=easy`）
- **THEN** 系统 MUST 先应用主题贴合候选集筛选，再在候选集内使用可解释的代理指标对期刊排序，并在输出中展示这些代理指标（例如 `easy_score` 或等价字段）以及必要的风险提示（例如“仅为离线代理”）

#### Scenario: Value-for-money mode
- **WHEN** 用户选择“性价比”模式（`mode=value`）
- **THEN** 系统 MUST 先应用主题贴合候选集筛选，再在候选集内基于 AJG 等级与（如可用）分区/指标等信息形成排序，并输出可解释字段（例如 AJG 等级、`value_score` 的构成或等价信息）

## ADDED Requirements

### Requirement: Explain candidate gating and fallback in the output
系统 MUST 在推荐输出中解释“主题贴合候选集”的构造参数与可能发生的回退，以便用户理解推荐边界与不确定性。

#### Scenario: Output includes gating metadata
- **WHEN** 系统输出推荐报告
- **THEN** 输出 MUST 包含候选集元信息（例如：阈值/TopN、候选规模、是否触发回退与回退方式）

#### Scenario: Output explains when abstract is missing
- **WHEN** 用户未提供摘要或摘要过短
- **THEN** 输出 MUST 提示主题贴合判断的可信度降低，并建议补充摘要/引言或更详细的关键词信息

### Requirement: Output includes key per-journal explanation fields across modes
系统 MUST 在每条期刊推荐中包含关键解释字段，至少包括 `fit_score`，并按模式包含对应的 easy/value 代理指标，确保用户可对比与复核。

#### Scenario: Per-journal fields shown in Markdown tables
- **WHEN** 系统输出 Markdown 表格
- **THEN** 每条推荐 MUST 展示期刊基础信息（Field/Journal/AJG 等）以及 `fit_score`，并根据模式展示 `easy_score` 或 `value_score`（或等价字段）
