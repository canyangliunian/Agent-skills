## ADDED Requirements

### Requirement: Repository root matches skill package layout
系统 MUST 将仓库根目录重构为单一 skill 包 `ABS-Journal`，并在根目录下提供固定结构：`scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`。

#### Scenario: Skill layout exists at repository root
- **WHEN** 用户查看仓库根目录
- **THEN** MUST 能看到 `scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`

### Requirement: Progressive disclosure in SKILL.md
系统 SHALL 保持 `SKILL.md` 精简，只包含触发条件与最小工作流，并将较重的字段说明/FAQ/示例输出放入 `references/` 或 `assets/`。

#### Scenario: Heavy reference is moved out of SKILL.md
- **WHEN** 需要解释 AJG 数据字段含义或展示长示例输出
- **THEN** MUST 将内容放到 `references/` / `assets/`，并在 `SKILL.md` 中给出指向

### Requirement: Default recommendation uses local AJG data
系统 MUST 默认使用本地已有 AJG CSV 数据进行推荐，不得在用户未明确要求时自动触发网络更新。

#### Scenario: Recommend without update intent
- **WHEN** 用户仅提供论文信息并请求推荐投稿期刊（未提“更新/重新抓取/刷新/更新数据库”等意图）
- **THEN** 系统 MUST 直接读取本地 AJG CSV 生成推荐，不运行抓取更新流程

### Requirement: Update flow is explicit
系统 MUST 仅在用户明确提出“更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据”等意图时才触发抓取更新流程。

#### Scenario: Explicit update intent triggers fetch
- **WHEN** 用户明确要求更新 AJG/ABS 数据库
- **THEN** 系统 MUST 执行抓取脚本并更新 `data/` 中的数据文件与元数据

