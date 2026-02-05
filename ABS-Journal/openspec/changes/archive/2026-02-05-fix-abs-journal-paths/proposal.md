## Why

当前 `ABS-Journal` skill 已被复制到 `~/.agents/skills/abs-journal` 作为真实交付形态，但 `SKILL.md` / `references/` / `assets/` 以及部分 `scripts/` 仍残留旧工程目录（例如 `/Users/lingguiwang/Documents/Coding/LLM/09ABS`）的硬编码绝对路径，导致迁移后文档示例不可用、入口脚本可能直接运行失败。需要将这些路径引用迁移为新位置，并消除脚本中的目录硬编码以提升可移植性。

## What Changes

- 将文档与示例命令中旧绝对路径统一更新为 `~/.agents/skills/abs-journal` 的绝对路径（面向“默认绝对路径”使用习惯）。
- 将脚本内硬编码的 repo/skill 根目录与默认数据文件路径改为基于 `__file__` 推断 `SKILL_ROOT`，避免未来再次复制/移动时失效。
- 调整抓取脚本的 `progress.md/findings.md` 写入位置，不再写入旧工程目录，改为写入 skill 自身目录下的 `plan/`（并自动创建）。
- 保持核心行为不变：推荐默认只读本地 `assets/data/`；仅在显式 `--update` 或用户明确“更新数据库”意图时联网抓取。

## Capabilities

### New Capabilities

- （无）

### Modified Capabilities

- `abs-skill-package`: 文档与脚本示例的默认绝对路径从旧工程目录迁移到 `~/.agents/skills/abs-journal`，并要求脚本路径不依赖固定工程根目录（迁移可用性）。

## Impact

- 受影响文件类型：`SKILL.md`、`references/*.md`、`assets/*.md`、`scripts/*.py`。
- 受影响代码路径：入口脚本（如 `scripts/abs_journal.py`）、推荐实现默认 CSV 路径（`scripts/abs_article_impl.py`）、抓取脚本日志输出（`scripts/ajg_fetch.py`）。
- 依赖/外部系统：无新增依赖；联网抓取行为仍由显式触发控制。
