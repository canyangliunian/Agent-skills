## MODIFIED Requirements

### Requirement: Provide multi-objective recommendation modes
系统 SHALL 至少支持以下推荐维度/模式：主题最匹配、最易发表、性价比（或冲刺）；并保证输出可解释。系统 MUST 支持“脚本先生成候选池 → AI 二次筛选”的混合推荐流程：脚本负责候选池与基础排序信号，AI 仅在候选池内生成最终 TopK 与解释性字段。

#### Scenario: Hybrid workflow for fit mode
- **WHEN** 用户选择 `fit` 模式
- **THEN** 系统 MUST 先由脚本生成候选池（满足本地 AJG CSV、field、星级过滤等约束），再由 AI 在候选池内输出最终 TopK，并包含 `期刊主题` 字段

#### Scenario: Hybrid workflow for easy mode
- **WHEN** 用户选择 `easy` 模式
- **THEN** 系统 MUST 先由脚本生成候选池，再由 AI 在候选池内输出“更易投中”的 TopK，并包含 `期刊主题` 字段

#### Scenario: Hybrid workflow for value mode
- **WHEN** 用户选择 `value` 模式
- **THEN** 系统 MUST 先由脚本生成候选池，再由 AI 在候选池内输出“可冲刺”的 TopK，并包含 `期刊主题` 字段

## ADDED Requirements

### Requirement: Script SHALL export a candidate pool for AI review
系统 MUST 支持将脚本候选池以结构化格式导出，以便 AI 二次筛选。候选池条目 MUST 至少包含：期刊名、ABS/AJG 星级、field，以及用于排序/解释的基础字段（如 fit/easy/value 信号或其组成）。

#### Scenario: Candidate pool export is machine-readable
- **WHEN** 用户启用混合推荐流程
- **THEN** 系统 MUST 产生机器可读的候选池输出（例如 JSON），供 AI 稳定读取与校验“只从候选池选刊”

### Requirement: Final output MUST match fixed reporting columns
系统 MUST 将最终推荐结果输出为固定列结构，便于汇报与复制：
`序号 | 期刊名 | ABS星级 | 期刊主题`。

#### Scenario: Fixed columns for reporting
- **WHEN** 系统输出推荐清单
- **THEN** 输出 MUST 使用固定列结构，且三类（fit/easy/value）分别输出 TopK（默认 Top10）
