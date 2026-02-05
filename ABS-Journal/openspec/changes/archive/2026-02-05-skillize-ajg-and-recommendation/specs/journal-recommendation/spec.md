## MODIFIED Requirements

### Requirement: Consume AJG dataset outputs
系统 SHALL 以本地 AJG 数据文件作为主要数据来源，并要求数据输入满足明确的文件/字段契约。

#### Scenario: Use local AJG CSV by default
- **WHEN** 用户请求推荐投稿期刊且本地 AJG CSV 可用
- **THEN** 系统 MUST 读取本地 AJG CSV 生成推荐，且不得在未明确要求时触发抓取更新

#### Scenario: Missing AJG data provides fix guidance
- **WHEN** 本地 AJG CSV 缺失或不可读
- **THEN** 系统 MUST 给出明确错误信息，并提示“如需更新请明确提出更新/重新抓取”或先运行抓取脚本

