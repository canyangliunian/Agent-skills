## 1. Add References Docs For Core Entrypoints

- [x] 1.1 新增 `references/ajg_fetch.md`：用途、何时使用（显式更新才抓取）、环境变量、绝对路径示例、输出文件、常见错误与排查
- [x] 1.2 新增 `references/abs_journal_recommend.md`：用途、何时使用（默认本地推荐）、参数（mode/topk/field/ajg_csv）、数据依赖与常见错误

## 2. Wire References From SKILL.md

- [x] 2.1 更新 `SKILL.md` 的 References 列表，引用 `references/ajg_fetch.md` 与 `references/abs_journal_recommend.md`
- [x] 2.2 确认 `SKILL.md` 保持精简：脚本参数细节仅放在 references 中

## 3. Verification

- [x] 3.1 运行 `python3 scripts/ajg_fetch.py -h` 并核对 `references/ajg_fetch.md` 中参数一致
- [x] 3.2 运行 `python3 scripts/abs_journal.py recommend -h` 并核对 `references/abs_journal_recommend.md` 中参数一致
