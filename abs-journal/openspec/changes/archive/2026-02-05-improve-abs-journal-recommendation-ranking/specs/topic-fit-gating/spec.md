## ADDED Requirements

### Requirement: Generate topic-fit score for each candidate journal
系统 MUST 基于用户提供的论文信息（标题/摘要等）为每个候选期刊生成一个可解释、可复现的主题贴合分（`fit_score`）。

#### Scenario: Fit score computed from title only
- **WHEN** 用户仅提供论文标题（未提供摘要）
- **THEN** 系统 MUST 仍然计算 `fit_score`，并在输出解释中标注“信息不足导致贴合分不确定性更高”

#### Scenario: Fit score computed from title + abstract
- **WHEN** 用户提供论文标题与摘要
- **THEN** 系统 MUST 使用标题与摘要共同计算 `fit_score`，且该计算过程 MUST 完全离线（不依赖联网请求）

### Requirement: Gate all modes by a shared topic-fit candidate set
系统 MUST 先基于 `fit_score` 构造“主题贴合候选集”，并将该候选集作为 `fit/easy/value` 三种推荐模式的共同前置条件；未进入候选集的期刊 MUST NOT 出现在任何模式的最终推荐列表中。

#### Scenario: Non-matching journals excluded from easy/value
- **WHEN** 某期刊的 `fit_score` 低于候选集阈值（或未进入候选集 TopN）
- **THEN** 该期刊 MUST NOT 出现在 `easy` 或 `value` 模式的最终推荐结果中

#### Scenario: Candidate gating applied to fit mode
- **WHEN** 用户选择 `fit` 模式
- **THEN** 系统 MUST 仍然先应用候选集筛选，再在候选集内按贴合度进行排序

### Requirement: Provide a robust thresholding and fallback strategy
系统 MUST 提供稳健的候选集构造策略，使其在不同论文主题与文本长度下都能产出合理的候选规模，并在触发回退时给出明确提示。

#### Scenario: Candidate set too small triggers fallback
- **WHEN** 通过阈值的候选期刊数量小于用户请求的 `topk`（或小于预设最小候选数）
- **THEN** 系统 MUST 启用回退策略（例如降低阈值或扩大候选 TopN），并在输出中明确说明回退已发生以及采用的回退方式

#### Scenario: Candidate gating parameters are explicit in output
- **WHEN** 系统完成推荐计算
- **THEN** 输出 MUST 明确包含候选集参数信息（例如阈值/TopN、是否回退），以便用户理解“为何这些期刊被纳入”

### Requirement: Expose fit_score in recommendation output for explainability
系统 MUST 在最终推荐输出中展示每个期刊的 `fit_score`（或等价指标），以支持可解释性与调参迭代。

#### Scenario: Fit score present in Markdown table output
- **WHEN** 推荐以 Markdown 表格形式输出
- **THEN** 表格 MUST 包含贴合分列（例如 `FitScore` 或 `贴合分`），并可与 `easy/value` 的关键指标同时展示
