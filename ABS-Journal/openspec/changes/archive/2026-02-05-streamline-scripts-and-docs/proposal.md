## Why

当前仓库已是单一 skill（`ABS-Journal`），但 `scripts/` 与 `references/` 的使用说明仍可进一步“对齐真实工作流”：在不误删关键脚本（离线校验/统一入口）的前提下，明确哪些脚本是核心入口（抓取与推荐），并为核心入口提供对应的 reference 文档，便于 skill 在对话中更稳定、可重复地指导用户使用。

## What Changes

- 明确脚本分层：
  - **核心入口**：`scripts/ajg_fetch.py`（更新 AJG/ABS 数据库）、`scripts/abs_journal_recommend.py`（默认本地推荐）
  - **辅助但保留**：`scripts/abs_journal.py`（统一控制流入口）、`scripts/ajg_verify_outputs.py`（离线校验）、`scripts/abs_article_impl.py`（推荐实现）
- 在 `references/` 下新增/完善两份核心入口的说明文档：
  - `references/ajg_fetch.md`：抓取脚本用法、envvars、输出文件、常见错误与排查
  - `references/abs_journal_recommend.md`：推荐入口用法、模式（easy/fit/value）、数据依赖与常见错误
- 更新 `SKILL.md` 引用上述 references，保证渐进式加载与更可控的指导。

## Capabilities

### New Capabilities

<!-- 无新增 capability。本次为文档与入口分层的整理。 -->

### Modified Capabilities

- `ajg-fetch`: 增补 reference 文档以稳定指导抓取更新流程。
- `journal-recommendation`: 增补 reference 文档以稳定指导本地推荐流程。
- `abs-skill-package`: 明确脚本分层，并在 `SKILL.md` 中引用对应 reference。

## Impact

- 影响文档：新增 `references/*.md`，并修改 `SKILL.md` 的 references 指向。
- 不改变核心代码逻辑：不移除离线校验与统一入口脚本，仅做“入口明确 + 文档补齐”。

