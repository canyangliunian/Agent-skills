## 1. Inventory & Safety

- [x] 1.1 在交付目录（`/Users/lingguiwang/.agents/skills/abs-journal`）内搜索旧前缀（`/Users/lingguiwang/Documents/Coding/LLM/09ABS`）并确认无残留（含 scripts/docs/examples；不要求清理 openspec/archive 历史记录）
- [x] 1.2 确认 `assets/data/ajg_2024_journals_core_custom.csv` 在交付目录存在，或文档明确如何用 `--ajg_csv` 覆盖

## 2. Docs Path Migration

- [x] 2.1 更新 `SKILL.md` Quick Start 的示例命令为 `~/.agents/skills/abs-journal` 的绝对路径
- [x] 2.2 更新 `references/ajg_fetch.md` 示例命令与校验命令路径为新交付目录
- [x] 2.3 更新 `references/abs_journal_recommend.md` 与 `assets/recommendation_example.md` 的示例命令与默认数据路径说明
- [x] 2.4 更新 `references/ajg_data_contract.md` 的离线校验示例路径为新交付目录

## 3. Script Relocatability (No Hard-coded Roots)

- [x] 3.1 将 `scripts/abs_journal.py` 中的根目录定位改为基于 `__file__` 推断 `SKILL_ROOT`，并确保 `--data_dir` 默认指向 `SKILL_ROOT/assets/data`
- [x] 3.2 将推荐入口脚本定位改为基于 `__file__` 推断 `SKILL_ROOT`（以 `scripts/abs_journal.py` 为主）
- [x] 3.3 将 `scripts/abs_article_impl.py` 的 `DEFAULT_AJG_CSV` 改为 `SKILL_ROOT/assets/data/...`，避免固定工程路径

## 4. Fetch Logging Location

- [x] 4.1 将 `scripts/ajg_fetch.py` 的 `progress.md/findings.md` 输出默认写入 `SKILL_ROOT/plan/`（可用 env `ABS_JOURNAL_PLAN_DIR` 覆盖），并在该目录不可写时回退写入 `/tmp/abs-journal-plan/`

## 5. Minimal Verification

- [x] 5.1 运行 `python3 scripts/abs_journal.py -h`、`python3 scripts/ajg_fetch.py -h`、`python3 scripts/abs_article_impl.py -h` 确认入口可用
- [x] 5.2 运行一次本地推荐（例如 `python3 scripts/abs_article_impl.py --title "test" --topk 1`）确认默认数据路径可读取且能输出结果
