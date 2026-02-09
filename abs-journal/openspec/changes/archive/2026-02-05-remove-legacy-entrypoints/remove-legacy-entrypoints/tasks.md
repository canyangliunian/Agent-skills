## 1. 删除旧入口与脚本清理

- [x] 1.1 删除 `scripts/abs_journal_recommend.py`
- [x] 1.2 全仓库搜索 `abs_journal_recommend.py`，将剩余引用替换为混合模式入口 `scripts/abs_journal.py recommend --hybrid ...`

## 2. 文档与示例一致性

- [x] 2.1 更新 `SKILL.md` / `README.md` / `assets/recommendation_example.md`：仅保留混合模式命令链（候选池 JSON → AI 输出 → 校验 → 固定列报告）
- [x] 2.2 更新 `references/abs_journal_recommend.md`：明确混合模式为唯一推荐路径，包含绝对路径示例

## 3. OpenSpec 规格与归档引用清理

- [x] 3.1 更新 `openspec/specs/**`：移除旧入口引用，改为混合模式入口（保持规格一致）
- [x] 3.2 更新 `openspec/changes/archive/**`：移除旧入口引用，改为混合模式入口（保持归档一致）

## 4. 离线验证

- [x] 4.1 运行 `python3 -m py_compile` 校验脚本可导入（重点：`scripts/abs_journal.py`、`scripts/abs_article_impl.py`、`scripts/abs_ai_review.py`、`scripts/hybrid_report.py`）
- [x] 4.2 运行一次最小混合流程：导出候选池 JSON，并确保 `rg "abs_journal_recommend.py"` 为 0
