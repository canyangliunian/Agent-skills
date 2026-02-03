# Findings & Decisions
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
- 新增 `README.md`（中文），用于介绍项目用途、目录结构与最小使用示例。
- README 示例默认使用绝对路径。
- README 需说明 help 上色策略：`NO_COLOR` 会强制禁色，强制彩色常用 `NO_COLOR= FORCE_COLOR=1 ...`。
- 使用 `pycli-color` 规范为 `scripts/compile.py` 与 `scripts/marker_extract.py` 的 argparse `-h/--help` 输出上色：
  - option token（以 `-` 开头）→ 青色 + 加粗（`\x1b[36;1m`）
  - metavar token（全大写或包含 `_`）→ 黄色 + 加粗（`\x1b[33;1m`）
  - 颜色策略：默认 auto（TTY 且 TERM != dumb）；存在 `NO_COLOR` 强制禁用；`FORCE_COLOR=1` 强制启用
  - 仅上色 help，不改变业务输出与参数语义

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
- 本环境常见默认存在 `NO_COLOR=1`，因此 README 中“强制彩色”应写成 `NO_COLOR= FORCE_COLOR=1 ...`。
- `scripts/compile.py` 使用 `parse_args()` 构造 `argparse.ArgumentParser`；参数里已有 `choices=`（如 `--engine`/`--bib`/`--build-mode`），但多数参数未设置 `metavar`。
- `scripts/marker_extract.py` 使用 `build_argparser()` 构造 `argparse.ArgumentParser`；已有位置参数 `input` 与多个 `choices=` 参数。
- 若不显式指定 `metavar`，help 中很多占位符不满足“全大写或含 `_`”规则，黄色高亮不明显，因此需要给关键参数补充 `metavar=`（仅影响 help 显示）。

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
| 每个脚本内置 `supports_color()/colorize()/ColorHelpFormatter` | 避免抽公共模块导致导入路径/复用决策；改动直观 |
| 仅给 `-h/--help` 上色 | 避免对脚本其它输出造成影响 |
| 为关键参数补充 `metavar=` | 确保黄色高亮可见且一致；不影响解析行为 |
| Python 3.10+ | 用户明确要求 |
| README 用中文 + 最小示例 | 符合默认中文与“简洁可复制”偏好 |
| README 示例用绝对路径 | 便于直接复制运行；避免路径歧义 |

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
- `/Users/lingguiwang/.agents/skills/pycli-color/scripts/demo_pycli_color.py`（可复制的 formatter 实现）
- `scripts/compile.py`
- `scripts/marker_extract.py`

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
