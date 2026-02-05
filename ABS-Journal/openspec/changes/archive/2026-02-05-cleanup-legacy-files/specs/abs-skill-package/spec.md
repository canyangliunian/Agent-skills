## MODIFIED Requirements

### Requirement: Repository root matches skill package layout
系统 MUST 保持仓库根目录为单一 skill 包 `ABS-Journal` 的固定结构：`scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`。

#### Scenario: Skill layout exists at repository root
- **WHEN** 用户查看仓库根目录
- **THEN** MUST 能看到 `scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`

#### Scenario: Local AJG data lives under assets
- **WHEN** skill 需要承载本地 AJG 数据文件（CSV/JSON/JSONL/meta）
- **THEN** 系统 MUST 将这些数据存放在 `assets/data/` 下，而不是根目录 `data/`

### Requirement: Default recommendation uses local AJG data
系统 MUST 默认使用本地已有 AJG CSV 数据进行推荐，不得在用户未明确要求时自动触发网络更新。

#### Scenario: Recommend uses assets data directory by default
- **WHEN** 用户请求推荐且未指定 `--ajg_csv/--data_dir` 覆盖路径
- **THEN** 系统 MUST 默认从 `assets/data/` 中读取 AJG CSV

