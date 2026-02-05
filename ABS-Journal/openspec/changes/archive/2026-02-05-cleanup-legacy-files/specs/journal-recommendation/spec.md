## MODIFIED Requirements

### Requirement: Consume AJG dataset outputs
系统 SHALL 以本地 AJG 数据文件作为主要数据来源，并要求数据输入满足明确的文件/字段契约。

#### Scenario: Default AJG CSV path under assets/data
- **WHEN** 用户未显式指定 AJG CSV 路径
- **THEN** 系统 MUST 默认读取 `assets/data/ajg_<year>_journals_core_custom.csv`（实际年份以本地最新可用文件为准）

