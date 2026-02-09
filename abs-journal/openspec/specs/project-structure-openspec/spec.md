## Purpose

定义本项目采用 OpenSpec 进行规范化管理时的目录结构、示例写法与默认安全策略（非破坏性），确保脚本与数据产出可复用、可验证、可演进。

## Requirements

### Requirement: OpenSpec-first project organization
系统 SHALL 以 OpenSpec 的 capabilities/specs/tasks 工件为中心组织项目演进，并确保变更流程可追踪。

#### Scenario: Change artifacts exist and are up to date
- **WHEN** 项目进行一次重要功能变更或重构
- **THEN** 系统 MUST 在 `openspec/changes/<change>/` 下维护 proposal/design/specs/tasks 等工件，且工件状态可由 `openspec status` 正确反映

### Requirement: Stable directories for data and scripts
系统 SHALL 约定稳定的目录结构以承载脚本与数据输出，降低用户运行与迁移成本。

#### Scenario: Default directories present
- **WHEN** 用户克隆仓库并准备运行抓取或推荐流程
- **THEN** 项目 MUST 提供清晰的脚本目录（如 `scripts/`）与数据目录（如 `data/`）的约定与用途说明（可由后续文档/README 实现）

### Requirement: Absolute paths by default in usage examples
系统 SHALL 在使用示例与运行说明中默认使用绝对路径，避免因工作目录变化导致运行失败或误写文件。

#### Scenario: Usage examples use absolute paths
- **WHEN** 提供命令行示例（如抓取脚本的 `--outdir`）
- **THEN** 示例 MUST 使用绝对路径或明确说明相对路径的 base 目录

### Requirement: Non-destructive by default
系统 SHALL 避免默认执行可能破坏用户数据的操作（覆盖/删除），并在需要时提供显式确认或安全策略。

#### Scenario: Existing output files present
- **WHEN** 输出目录中已存在同名输出文件
- **THEN** 系统 MUST 采取非破坏性策略（例如失败退出、写入新文件名、或要求显式 `--overwrite` 参数；以实现与后续设计为准），并给出明确提示
