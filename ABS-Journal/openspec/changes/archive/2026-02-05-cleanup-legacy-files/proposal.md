## Why

当前目录已重构为单一 skill（`ABS-Journal`），但仍存在旧版本遗留文件与冗余结构（例如多余脚本、旧数据目录位置不符合“assets/为资源承载”的约定）。需要在不破坏 skill 核心功能（抓取 AJG/ABS、基于本地数据推荐投稿期刊、默认不更新数据库）的前提下，清理不再需要的旧文件，并把本地数据资源迁移到更合适的位置，降低维护成本与误用风险。

## What Changes

- 以“保留清单”为准清理仓库：保留 `assets/`、`openspec/`、`Pha1.md`、`README.md`、`references/`、`scripts/`、`SKILL.md`，其余内容删除或迁移（可能为 **BREAKING**）。
- 迁移 `data/` 中全部内容到 `assets/` 下（作为本 skill 的本地资源数据），并更新脚本/文档中的默认路径引用。
- 根据当前 skill 的功能（抓取/推荐/默认本地推荐、显式更新才抓取）识别并删除 `scripts/` 下不再需要的脚本；所有删除操作将提供清单并需要确认后执行。
- 清理典型垃圾文件（如 `.DS_Store`、`__pycache__/`、`*.pyc`）以保持仓库整洁（如存在）。

## Capabilities

### New Capabilities

<!-- 无新增 capability。本次为结构清理与资源迁移。 -->

### Modified Capabilities

- `abs-skill-package`: 调整 skill 资源承载位置（`data/` → `assets/`）并清理旧文件结构，保持根目录 skill 形态更纯净。
- `ajg-fetch`: 更新默认输出/读取路径引用，以匹配数据迁移后的新位置；保持“显式更新才抓取”的策略不变。
- `journal-recommendation`: 更新默认本地 AJG CSV 的路径引用，以匹配数据迁移后的新位置；保持默认不更新策略不变。

## Impact

- 目录结构影响：`data/` 目录将被移除或转为空壳，数据迁移至 `assets/`（**BREAKING**：硬编码绝对路径的脚本/文档需同步更新）。
- 脚本影响：`scripts/` 下可能删除冗余脚本；推荐/抓取/控制流入口必须保持可用。
- 数据影响：本地数据全部迁移；需要确保离线校验与推荐冒烟仍可通过。

