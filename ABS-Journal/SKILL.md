---
name: ABS-Journal
description: Use when a user asks to fetch/update the ABS/AJG journal guide database, or to recommend target journals for a paper using local AJG data, especially when the user mentions ABS/AJG, AJG CSV, journal ranking, or wants “fit/easy/value” submission recommendations.
---

# ABS-Journal

## Core Rules (Non-Negotiable)

- 默认推荐 **只使用本地 AJG CSV**（`assets/data/ajg_<year>_journals_core_custom.csv`），不得自动联网更新。
- 只有当用户明确提出 **更新/重新抓取/刷新/更新数据库/更新ABS(AJG)数据** 时，才运行抓取脚本更新 `assets/data/`。
- 抓取登录凭据仅通过环境变量 `AJG_EMAIL` / `AJG_PASSWORD` 提供；不要在文件中写入明文密码。
- 命令行示例默认使用绝对路径。

## Quick Start

### A) 推荐投稿期刊（默认本地数据）

```bash
python3 /Users/lingguiwang/Documents/Coding/LLM/09ABS/scripts/abs_journal_recommend.py \
  --title "你的论文标题" \
  --abstract "你的摘要（可选）" \
  --mode fit \
  --topk 20
```

### B) 更新 AJG/ABS 数据库（仅在用户明确要求时）

```bash
export AJG_EMAIL="lingguiwang@yeah.net"
export AJG_PASSWORD="你的密码"

python3 /Users/lingguiwang/Documents/Coding/LLM/09ABS/scripts/ajg_fetch.py \
  --outdir /Users/lingguiwang/Documents/Coding/LLM/09ABS/assets/data
```

## Workflow

1) 解析用户意图：
   - 若用户只说“推荐投稿期刊/帮我选期刊”，走 **推荐流程**（不更新）。
   - 若用户明确说“更新/重新抓取/刷新数据库”，走 **更新+（可选）推荐流程**。
2) 推荐流程：
   - 读取本地 AJG CSV，按 `--mode` 输出 Markdown 推荐报告。
   - 若本地数据缺失：提示用户先明确“更新数据库”，或手动提供 AJG CSV 的绝对路径。
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
