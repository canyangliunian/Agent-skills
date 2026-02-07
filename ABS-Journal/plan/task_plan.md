# Task Plan：ABS-Journal 路径可移植化
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
  WHY: After 50+ tool calls, your original goals can get forgotten. This file keeps them fresh.
  WHEN: Create this FIRST, before starting any work. Update after each phase completes.
-->

## Goal
- 将最终推荐报告的呈现方式改为：`序号 | 期刊名 | ABS星级 | Field`（用于 hybrid_report.md 等最终输出）。
- 要求：不改变推荐/候选池/校验逻辑，仅调整最终报告的固定列与顺序。

## Non-goals
- 不联网更新 AJG 数据、不改评分/筛选/候选池/子集校验逻辑。
- 不改命令行参数语义（仅必要时新增/调整报告列说明）。

## Current Phase
<!-- 
  WHAT: Which phase you're currently working on (e.g., "Phase 1", "Phase 3").
  WHY: Quick reference for where you are in the task. Update this as you progress.
-->
Phase 2（修复混合流程三候选池贯通）

## Phases
<!-- 
  WHAT: Break your task into 3-7 logical phases. Each phase should be completable.
  WHY: Breaking work into phases prevents overwhelm and makes progress visible.
  WHEN: Update status after completing each phase: pending → in_progress → complete
-->

### Phase 1: Requirements & Discovery（定位报告生成逻辑）
<!-- 
  WHAT: Understand what needs to be done and gather initial information.
  WHY: Starting without understanding leads to wasted effort. This phase prevents that.
-->
- [ ] 确认最终报告由哪个脚本生成（`scripts/hybrid_report.py`）
- [ ] 确认当前报告列顺序与字段映射来源（期刊名/星级/Field）
- **Status:** complete
<!-- 
  STATUS VALUES:
  - pending: Not started yet
  - in_progress: Currently working on this
  - complete: Finished this phase
-->

### Phase 2: Implementation（修改报告固定列）
<!-- 
  WHAT: Decide how you'll approach the problem and what structure you'll use.
  WHY: Good planning prevents rework. Document decisions so you remember why you chose them.
-->
- [x] 修复混合流程：AI 二次筛选/子集校验/报告生成必须基于 Step1 生成的 easy/medium/hard 三候选池
- [x] 保持对“单候选池”输入的兼容（历史用法不破坏）
- **Status:** complete

### Phase 3: Testing & Verification（最小自测）
<!-- 
  WHAT: Actually build/create/write the solution.
  WHY: This is where the work happens. Break into smaller sub-tasks if needed.
-->
- [x] 运行一次 `--hybrid --auto_ai --ai_report_md ...` 生成报告（TopK=2 即可）
- [x] 检查 `reports/ai_report.md` 三段的 `ABS星级/Field` 是否均能填充
- **Status:** complete

### Phase 4: Delivery（更新说明）
<!-- 
  WHAT: Verify everything works and meets requirements.
  WHY: Catching issues early saves time. Document test results in progress.md.
-->
- [ ] 更新 `references/abs_journal_recommend.md`（如有列说明）
- [ ] 更新 `assets/recommendation_example.md`（如有固定列示例）
- **Status:** pending

<!-- Phase 5 removed: merged into Phase 4 -->

## Key Questions
<!-- 
  WHAT: Important questions you need to answer during the task.
  WHY: These guide your research and decision-making. Answer them as you go.
  EXAMPLE: 
    1. Should tasks persist between sessions? (Yes - need file storage)
    2. What format for storing tasks? (JSON file)
-->
1. [Question to answer]
2. [Question to answer]

## Decisions Made
<!-- 
  WHAT: Technical and design decisions you've made, with the reasoning behind them.
  WHY: You'll forget why you made choices. This table helps you remember and justify decisions.
  WHEN: Update whenever you make a significant choice (technology, approach, structure).
  EXAMPLE:
    | Use JSON for storage | Simple, human-readable, built-in Python support |
-->
| Decision | Rationale |
|----------|-----------|
|          |           |

## Errors Encountered
<!-- 
  WHAT: Every error you encounter, what attempt number it was, and how you resolved it.
  WHY: Logging errors prevents repeating the same mistakes. This is critical for learning.
  WHEN: Add immediately when an error occurs, even if you fix it quickly.
  EXAMPLE:
    | FileNotFoundError | 1 | Check if file exists, create empty list if not |
    | JSONDecodeError | 2 | Handle empty file case explicitly |
-->
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
<!-- 
  REMINDERS:
  - Update phase status as you progress: pending → in_progress → complete
  - Re-read this plan before major decisions (attention manipulation)
  - Log ALL errors - they help avoid repetition
  - Never repeat a failed action - mutate your approach instead
-->
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
