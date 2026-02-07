# Findings & Decisions（ABS-Journal：路径可移植化）
<!-- 
  WHAT: Your knowledge base for the task. Stores everything you discover and decide.
  WHY: Context windows are limited. This file is your "external memory" - persistent and unlimited.
  WHEN: Update after ANY discovery, especially after 2 view/browser/search operations (2-Action Rule).
-->

## Requirements
<!-- 
  WHAT: What the user asked for, broken down into specific requirements.
  WHY: Keeps requirements visible so you don't forget what you're building.
  WHEN: Fill this in during Phase 1 (Requirements & Discovery).
  EXAMPLE:
    - Command-line interface
    - Add tasks
    - List all tasks
    - Delete tasks
    - Python implementation
-->
<!-- Captured from user request -->
- 最终推荐报告呈现固定列改为：`序号 | 期刊名 | ABS星级 | Field`。
- 代码需要从开发目录复制到 `~/.agents/skills/abs-journal` 后仍可运行（路径不能写死）。
- 更换电脑/用户名/目录结构时无需改代码（通过“自动探测 + 可覆盖配置”实现）。
- 默认仍以“绝对路径”形式对外展示/日志输出，但这些绝对路径应由运行时解析得到，而非写进仓库。
- 三类难度需要更清晰的“星级层次感”：`easy` 推荐应主要来自星级 1–2；`medium` 来自 2–3；`hard` 来自 4–4*（星级允许重叠：2 同时属于 easy/medium；4 同时属于 hard）。
- 候选期刊的默认 Field 范围固定为 5 个 Field 白名单：`ECON, FINANCE, PUB SEC, REGIONAL STUDIES, PLANNING AND ENVIRONMENT, SOC SCI`（其中 `REGIONAL STUDIES, PLANNING AND ENVIRONMENT` 是一个整体 Field 名称）；如需只看某个领域，通过 `--field_scope` 显式覆盖。`--field` 仅作为论文领域标签/关键词配置，不控制候选范围。

## Observations
- 当前开发目录：`/Users/lingguiwang/Documents/Coding/LLM/Skills/ABS-Journal`。
- 目标安装目录：`~/.agents/skills/abs-journal`。
- 问题核心：脚本里存在硬编码的绝对路径（包含用户目录名），不可移植。

## Research Findings
<!-- 
  WHAT: Key discoveries from web searches, documentation reading, or exploration.
  WHY: Multimodal content (images, browser results) doesn't persist. Write it down immediately.
  WHEN: After EVERY 2 view/browser/search operations, update this section (2-Action Rule).
  EXAMPLE:
    - Python's argparse module supports subcommands for clean CLI design
    - JSON module handles file persistence easily
    - Standard pattern: python script.py <command> [args]
-->
<!-- Key discoveries during exploration -->
- 代码层面：多数脚本已通过 `__file__` 推导 `SKILL_ROOT`，但仍有残留“文档字符串里的绝对路径示例”以及少量硬编码/遗留变量引用（本次修复中遇到 `abs_article_impl.py` 的 `SKILL_ROOT` 未定义问题）。
- 文档层面：`README.md`、`SKILL.md`、`references/*.md`、`assets/*.md` 多处包含机器相关绝对路径（`/Users/...`），需要统一改成“相对路径（基准为项目根）”或“占位路径 + 环境变量说明”。
- 2026-02-07 用户反馈的工作流理解问题：Step1 已生成 easy/medium/hard 三类候选池，但后续校验/报告看起来没用上三池（见下方“混合流程候选池”条目）。

## 混合流程候选池（2026-02-07）
- 现象：在 `references/abs_journal_recommend.md` 的 Step 1 已生成 easy/medium/hard 三个候选池后，Step 3 的单次命令仍用 `--mode medium`，容易让人误以为“只跑了 medium / 没基于三池选”，且在离线 `--auto_ai` 路径下会导致子集校验失败（因为 medium/hard 的选择不在 easy 的候选池里）。
- 根因（代码）：`scripts/abs_journal.py --hybrid` 确实会导出三份候选池（`*_easy.json/*_medium.json/*_hard.json`），但 `scripts/abs_ai_review.py` 与 `scripts/hybrid_report.py` 的接口长期假设“单候选池”，从而无法对 easy/medium/hard 分 bucket 做 membership 校验与字段填充。
- 修复策略：离线 `--auto_ai` 生成 `ai_output.json` 时，把三份候选池嵌入 `candidate_pool_by_mode`；随后校验脚本允许把 `ai_output.json` 自己作为候选池来源；报告脚本也从 `candidate_pool_by_mode` 取对应 bucket 的候选信息来补齐 `ABS星级/Field`。

## Technical Decisions
<!-- 
  WHAT: Architecture and implementation choices you've made, with reasoning.
  WHY: You'll forget why you chose a technology or approach. This table preserves that knowledge.
  WHEN: Update whenever you make a significant technical choice.
  EXAMPLE:
    | Use JSON for storage | Simple, human-readable, built-in Python support |
    | argparse with subcommands | Clean CLI: python todo.py add "task" |
-->
<!-- Decisions made with rationale -->
| Decision | Rationale |
|----------|-----------|
|          |           |

## Issues Encountered
<!-- 
  WHAT: Problems you ran into and how you solved them.
  WHY: Similar to errors in task_plan.md, but focused on broader issues (not just code errors).
  WHEN: Document when you encounter blockers or unexpected challenges.
  EXAMPLE:
    | Empty file causes JSONDecodeError | Added explicit empty file check before json.load() |
-->
<!-- Errors and how they were resolved -->
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
<!-- 
  WHAT: URLs, file paths, API references, documentation links you've found useful.
  WHY: Easy reference for later. Don't lose important links in context.
  WHEN: Add as you discover useful resources.
  EXAMPLE:
    - Python argparse docs: https://docs.python.org/3/library/argparse.html
    - Project structure: src/main.py, src/utils.py
-->
<!-- URLs, file paths, API references -->
-

## Visual/Browser Findings
<!-- 
  WHAT: Information you learned from viewing images, PDFs, or browser results.
  WHY: CRITICAL - Visual/multimodal content doesn't persist in context. Must be captured as text.
  WHEN: IMMEDIATELY after viewing images or browser results. Don't wait!
  EXAMPLE:
    - Screenshot shows login form has email and password fields
    - Browser shows API returns JSON with "status" and "data" keys
-->
<!-- CRITICAL: Update after every 2 view/browser operations -->
<!-- Multimodal content must be captured as text immediately -->
-

---
<!-- 
  REMINDER: The 2-Action Rule
  After every 2 view/browser/search operations, you MUST update this file.
  This prevents visual information from being lost when context resets.
-->
*Update this file after every 2 view/browser/search operations*
*This prevents visual information from being lost*


## 2026-02-08：easy/medium/hard 星级过滤不一致问题（根因）

### 现象
- `/Users/lingguiwang/Documents/Coding/LLM/tests/abs_journal_reports/ai_report.md` 中三段（Easy/Medium/Hard）的“星级过滤”完全一致（都为 `2,3`），与预期分层（easy < medium < hard）不一致。

### 根因定位
- 代码侧已经实现默认分层：`scripts/abs_journal.py` 中 `DEFAULT_RATING_FILTER_BY_MODE = {easy: 1,2; medium: 2,3; hard: 4,4*}`，当 `--rating_filter` 留空时会按 mode 自动选择。
- 但文档/示例（`SKILL.md` 与 `references/abs_journal_recommend.md`）仍示范传入统一或不合理的 `--rating_filter`（如 `"1,2,3"` 或 hard 用 `"3,4,4*"`），会覆盖默认分层，导致 AI/用户照抄时出现“星级过滤不一致/不分层”。

### 修复方向
- 文档侧明确：混合流程要么不传 `--rating_filter`（留空=自动分层），要么分别为 easy/medium/hard 明确不同桶；并强调“显式传入会覆盖默认分层”。
- 需要同步修正文档与示例，并用本地离线用例验证生成的报告中三段 meta 的 `rating_filter` 分别为 `1,2` / `2,3` / `4,4*`。
