## MODIFIED Requirements

### Requirement: Output artifacts and naming contract
系统 SHALL 将抓取结果写入本地文件，并满足固定的文件命名契约，以便下游（推荐能力）稳定消费。

#### Scenario: Default output directory points to assets/data
- **WHEN** 用户未显式指定数据目录的约定位置（以本 skill 默认配置为准）
- **THEN** 系统 MUST 将抓取输出写入 `assets/data/`（或允许脚本参数覆盖，但默认文档与工作流以 `assets/data/` 为准）

