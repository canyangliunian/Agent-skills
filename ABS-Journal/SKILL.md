---
name: ABS-Journal
description: Use when a user asks to recommend target journals via a hybrid ABS/AJG workflow (script candidate pool then AI selection with subset validation), or explicitly asks to fetch/update the AJG/ABS journal guide database.
---

# ABS-Journal

## Core Rules

- 默认推荐 **只使用本地 AJG CSV**（`assets/data/ajg_<year>_journals_core_custom.csv`），不得自动联网更新。
- 只有当用户明确提出 **更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据** 时，才运行抓取脚本更新 `assets/data/`。
- 抓取登录凭据仅通过环境变量 `AJG_EMAIL` / `AJG_PASSWORD` 提供；不要在文件中写入明文密码。
- 命令行示例默认使用 **项目根相对路径（assets/）**，仅在用户明确要求时使用绝对路径并注明基准。
- 推荐流程为：脚本导出主题贴合候选池 → AI 仅在候选池内二次筛选 → 子集校验 → 三段固定列报告。

## Quick Start

### A) 校验 AI 输出并生成最终报告（固定列三段 Top10）

```bash
python3 scripts/abs_journal.py \
  recommend \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 10 \
  --rating_filter "1,2,3" \
  --hybrid \
  --export_candidate_pool_json "assets/candidate_pool_fit.json" \
  --ai_output_json "assets/ai_output.json" \
  --hybrid_report_md "assets/hybrid_report.md"
```

### B) 更新 AJG/ABS 数据库（仅在用户明确要求时）

```bash
export AJG_EMAIL="你的账号"
export AJG_PASSWORD="你的密码"

python3 scripts/ajg_fetch.py \
  --outdir "$(pwd)/assets/data"
```

## Workflow

1) 解析用户意图：
   - 若用户只说“推荐投稿期刊/帮我选期刊”，走 **混合推荐流程**（不更新）。
   - 若用户明确说“更新/重新抓取/刷新数据库”，走 **更新+（可选）推荐流程**。
2) 混合推荐流程：
   - 读取本地 AJG CSV → 先构造“主题贴合候选池”并导出 JSON（满足 field/星级过滤等约束）。
   - AI **只能在候选池内** 输出三类 TopK（fit/easy/value），并为每条补充 `期刊主题`（解释性摘要）。
   - 脚本做 **候选池子集校验**（禁止候选池外期刊）；通过后生成固定列 Markdown 报告：
     `序号 | 期刊名 | ABS星级 | 期刊主题`。
3) 更新流程：
   - 检查 `AJG_EMAIL/AJG_PASSWORD` 是否存在；缺失则给出可复制的 export 提示。
   - 运行抓取脚本写入 `assets/data/`。
   - （可选）运行离线校验脚本确认输出契约。

## References (Load Only If Needed)

- 抓取/更新 AJG 数据库（显式触发才运行）：`references/ajg_fetch.md`
- 投稿期刊推荐（默认本地数据）：`references/abs_journal_recommend.md`
- AJG 数据输出契约与离线校验：`references/ajg_data_contract.md`
- 常见失败排查（gate/验证码/环境变量）：`references/troubleshooting.md`
- 推荐输出示例：`assets/recommendation_example.md`
