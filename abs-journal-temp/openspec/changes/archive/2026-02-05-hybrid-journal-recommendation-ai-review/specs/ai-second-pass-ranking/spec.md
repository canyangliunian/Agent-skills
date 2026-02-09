## ADDED Requirements

### Requirement: AI second-pass MUST select only from script candidate pool
系统 MUST 在脚本生成的候选池（candidate pool）范围内执行 AI 二次筛选；AI 输出的每一个推荐期刊 MUST 能在候选池中找到精确匹配条目，且系统 MUST NOT 输出任何候选池之外的期刊。

#### Scenario: Candidate pool constraint enforced
- **WHEN** AI 二次筛选产生一条推荐结果
- **THEN** 系统 MUST 校验该期刊存在于候选池中；若不存在，系统 MUST 报错或要求重新生成（不得悄悄替换为其他期刊）

#### Scenario: No directory-external journals
- **WHEN** 用户请求推荐结果
- **THEN** 系统 MUST 仅从本地 AJG CSV 生成候选池并进行推荐，AI MUST NOT 引入 AJG CSV 未包含的期刊名称

### Requirement: AI output SHALL include journal topic for each recommendation
系统 MUST 为每条推荐输出一个“期刊主题”字段，用于解释该期刊与论文主题的匹配关系；该字段 MUST 是保守、解释性的短描述，避免对期刊政策/审稿周期等不可验证事实作出断言。

#### Scenario: Topic field present and short
- **WHEN** 系统输出推荐清单
- **THEN** 每条推荐 MUST 包含 `期刊主题`，且该描述 MUST 为 1–2 句的短文本（便于汇报复制）

### Requirement: Structured report format for fit/easy/value
系统 MUST 分别为 `fit/easy/value` 三类输出 TopK（默认 Top10），并使用固定列结构：
`序号 | 期刊名 | ABS星级 | 期刊主题`。

#### Scenario: Fit list output schema
- **WHEN** 用户请求 `fit` 推荐
- **THEN** 系统 MUST 输出按主题贴合排序的 TopK，并严格使用固定列结构

#### Scenario: Easy list output schema
- **WHEN** 用户请求 `easy` 推荐
- **THEN** 系统 MUST 在主题贴合候选池约束下输出“更易发表”TopK，并严格使用固定列结构

#### Scenario: Value list output schema
- **WHEN** 用户请求 `value` 推荐
- **THEN** 系统 MUST 在主题贴合候选池约束下输出“可冲刺”TopK，并严格使用固定列结构

### Requirement: Candidate pool and gating metadata SHALL be traceable
系统 SHOULD 在报告中包含候选池的可追溯信息（例如：候选池规模、来源 AJG CSV 路径/年份、以及候选池生成参数），以支持复现与对比。

#### Scenario: Traceability metadata included
- **WHEN** 系统输出推荐报告
- **THEN** 输出 SHOULD 包含候选池元信息（候选池规模与来源文件标识）
