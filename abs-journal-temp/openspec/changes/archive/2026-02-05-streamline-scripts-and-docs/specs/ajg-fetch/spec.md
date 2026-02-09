## MODIFIED Requirements

### Requirement: Output artifacts and naming contract
系统 SHALL 将抓取结果写入本地文件，并满足固定的文件命名契约，以便下游（推荐能力）稳定消费。

#### Scenario: Reference doc exists for ajg_fetch
- **WHEN** 用户需要抓取/更新 AJG 数据库或排查抓取失败
- **THEN** 系统 MUST 提供 `references/ajg_fetch.md`，包含环境变量、运行示例（绝对路径）、输出文件、常见失败与排查

