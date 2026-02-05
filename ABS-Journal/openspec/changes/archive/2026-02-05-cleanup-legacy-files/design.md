## Context

仓库当前已按 `ABS-Journal` skill 形态完成核心能力落地：抓取脚本在 `scripts/ajg_fetch.py`，推荐脚本实现与入口在 `scripts/abs_article_impl.py`、`scripts/abs_journal_recommend.py` / `scripts/abs_journal.py`，并通过 `SKILL.md` 明确“默认本地推荐、显式更新才抓取”。

但仍存在两类“新版本不需要的旧内容”：
1) 资源位置不统一：本地 AJG 数据目前在 `data/`，而本 skill 的资源承载目录应为 `assets/`（便于打包、分发与示例管理）。
2) 脚本与杂项文件冗余：`scripts/` 目录可能存在未被当前 skill 工作流引用的脚本；以及 `.DS_Store`、`__pycache__` 等垃圾文件。

本次变更目标是在不破坏既有功能前提下，做一次“保留清单驱动”的清理，并在执行任何破坏性操作（删除/覆盖/大规模移动）前提供明确清单并二次确认。

## Goals / Non-Goals

**Goals:**
- 将 `data/` 中全部数据迁移到 `assets/` 下（例如 `assets/data/`），并更新脚本/文档的默认路径引用。
- 以当前 skill 实际工作流为依据，识别 `scripts/` 中“未使用脚本”，给出删除清单并在确认后删除。
- 清理常见垃圾文件：`.DS_Store`、`__pycache__/`、`*.pyc`。
- 保持核心功能可用：
  - 推荐默认不联网：仍可在迁移后基于本地 AJG CSV 输出推荐报告；
  - 显式更新才抓取：抓取脚本仍能写入指定目录（默认目录更新为新的 assets 数据目录）。

**Non-Goals:**
- 不改变推荐算法逻辑与抓取策略本身（仅调整路径与清理冗余）。
- 不引入新的外部依赖或发布体系。
- 不在本轮做“数据瘦身/抽样”或丢弃文件：按用户要求迁移 `data/` 的**全部内容**。

## Decisions

1) **数据迁移目标位置：`assets/data/`**
- 决策：将 `data/*` 迁移到 `assets/data/*`（保留原文件名），并将默认数据目录从 `.../data` 改为 `.../assets/data`。
- 理由：符合“assets 承载本地资源”的约定；便于后续 skill 打包与分发。
- 备选方案：直接把 `data/` 改名为 `assets/`。不采用，会污染 assets 语义且不利于区分示例资产与数据资产。

2) **删除脚本的判定依据：是否被当前 skill 入口引用**
- 决策：以 `SKILL.md`、`README.md`、以及入口脚本（`scripts/abs_journal.py`、`scripts/abs_journal_recommend.py`）为“引用源”，凡未被引用且不属于必要的底层实现/校验工具，列入“候选删除清单”。
- 理由：严格以功能为准，避免主观误删。
- 规则：任何候选删除必须先输出清单并获得确认后执行（遵守破坏性操作确认要求）。

3) **迁移与清理的验证策略**
- 决策：迁移后至少做三类验证：
  - 离线校验：运行 `scripts/ajg_verify_outputs.py` 指向新数据目录；
  - 推荐冒烟：运行推荐入口指向新 CSV；
  - 更新流程冒烟：在显式 `--update` 下，抓取输出落在新数据目录（缺失 envvars 时应给出可操作提示并非零退出）。

## Risks / Trade-offs

- [硬编码绝对路径导致迁移后失效] → 全库搜索 `/Users/lingguiwang/Documents/Coding/LLM/09ABS/data` 并统一替换为新路径；同时保留 `--data_dir/--ajg_csv` 参数覆盖能力。
- [误删脚本导致功能回归] → 先给出“候选删除清单 + 引用证据”，确认后再删；删除后立即运行冒烟验证。
- [迁移数据文件较大导致操作耗时] → 采用原地移动（同一磁盘）并在迁移前后核对文件数量与关键文件存在性。

