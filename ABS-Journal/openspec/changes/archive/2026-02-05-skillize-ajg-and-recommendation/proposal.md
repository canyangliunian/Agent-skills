## Why

当前仓库的功能已经具备“AJG/ABS 期刊目录抓取”和“基于本地 AJG 数据的投稿期刊推荐”，但目录结构与 skill 交付形态尚未统一：抓取脚本、推荐脚本、示例数据与说明分散在不同子目录中，不利于作为一个可复用、可部署的 skill 包长期维护与调用。需要将当前目录重构为一个标准 skill 形态（含 `scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`），并明确默认使用本地数据进行推荐，只有在用户明确要求时才更新 AJG 数据库。

## What Changes

- 将仓库根目录重构为单一 skill：`ABS-Journal`，并在根目录下形成标准结构：
  - `scripts/`：抓取 AJG 与推荐投稿期刊的可执行脚本
  - `references/`：仅在需要时加载的参考资料（数据字段说明、常见问题、工作流）
  - `assets/`：模板/示例输出等不需常驻上下文的资源
  - `SKILL.md`：skill 的触发条件与最小工作流（强调默认使用本地数据，除非明确要求更新）
  - `README.md`：人类可读的最小使用说明（绝对路径示例、环境变量、常见错误）
- 统一入口与默认策略：
  - 推荐默认使用现有本地 `data/` 中 AJG CSV 进行推荐；
  - 只有在用户明确说“更新/重新抓取/刷新 ABS(AJG) 数据库”时才触发抓取流程。
- 兼容性调整（可能为 **BREAKING**）：为配合 skill 结构，脚本路径、默认数据路径、以及示例文件位置可能发生变更，但会在 README/SKILL.md 中给出迁移说明。

## Capabilities

### New Capabilities

- `abs-skill-package`: 将当前仓库重构为可部署的单一 skill 包（目录结构、资源分层、SKILL.md 工作流、README 最小说明）。

### Modified Capabilities

- `ajg-fetch`: 将抓取脚本纳入 skill 的 `scripts/` 标准入口，并确保仅在用户明确要求更新数据时才运行抓取（默认不联网更新）。
- `journal-recommendation`: 将推荐脚本纳入 skill 的 `scripts/` 标准入口，并明确默认读取本地 AJG CSV 数据进行推荐。

## Impact

- 影响目录结构：根目录将新增/整理 `scripts/`、`references/`、`assets/`、`SKILL.md`、`README.md`，并可能移动/重命名现有文件（**BREAKING**）。
- 影响脚本入口：
  - 抓取：`scripts/ajg_fetch.py`（或等价命名）作为更新数据库入口
  - 推荐：`scripts/abs_recommend.py`（或整合现有推荐脚本）作为默认推荐入口
- 影响数据：继续使用本地 `data/` 作为默认数据来源；更新动作将写入元数据并可离线校验。

