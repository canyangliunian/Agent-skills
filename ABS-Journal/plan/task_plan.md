# Task Plan：ABS-Journal 路径可移植化
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
  WHY: After 50+ tool calls, your original goals can get forgotten. This file keeps them fresh.
  WHEN: Create this FIRST, before starting any work. Update after each phase completes.
-->

## Goal
- 修复候选池 JSON 的星级分布：在 `easy/medium/hard` 各自允许的星级集合内，尽量实现 **1:1**（数量尽量均衡）；不够再按“同桶内相邻星级优先”补齐。
- 作用范围：仅影响 `--export_candidate_pool_json` 导出的候选池内容与其 `meta`；不改变 stdout 的推荐表输出与 CLI 参数语义。

## Non-goals
- 不联网更新 AJG 数据。
- 不改变评分函数、主题贴合 gating 策略的定义（仍按现有逻辑得到候选序列）。
- 不把“均衡”责任丢给 AI 提示词（提示词/文档可补充说明，但不作为主要约束手段）。

## Current Phase
<!-- 
  WHAT: Which phase you're currently working on (e.g., "Phase 1", "Phase 3").
  WHY: Quick reference for where you are in the task. Update this as you progress.
-->
Phase 4（更新说明与收尾）

## Phases
<!-- 
  WHAT: Break your task into 3-7 logical phases. Each phase should be completable.
  WHY: Breaking work into phases prevents overwhelm and makes progress visible.
  WHEN: Update status after completing each phase: pending → in_progress → complete
-->

### Phase 1: Requirements & Discovery（定位候选池导出逻辑）
<!-- 
  WHAT: Understand what needs to be done and gather initial information.
  WHY: Starting without understanding leads to wasted effort. This phase prevents that.
-->
- [x] 定位候选池导出逻辑（`scripts/abs_article_impl.py` / `scripts/abs_journal.py`）
- [x] 明确“1:1”的落点与补齐规则（候选池内均衡；同桶相邻星级补齐）
- **Status:** complete
<!-- 
  STATUS VALUES:
  - pending: Not started yet
  - in_progress: Currently working on this
  - complete: Finished this phase
-->

### Phase 2: Implementation（实现候选池星级均衡）
<!-- 
  WHAT: Decide how you'll approach the problem and what structure you'll use.
  WHY: Good planning prevents rework. Document decisions so you remember why you chose them.
-->
- [x] 在候选池导出前加入“按星级配额均衡采样”函数（尽量 1:1）
- [x] 写入候选池 `meta.rating_rebalance`（记录可用/选择/是否补齐/是否总量不足）
- [x] 保持现有 `--rating_filter` 语义：显式传入仍覆盖默认星级集合
- **Status:** complete

### Phase 3: Testing & Verification（最小自测）
<!-- 
  WHAT: Actually build/create/write the solution.
  WHY: This is where the work happens. Break into smaller sub-tasks if needed.
-->
- [x] 运行一次 `--hybrid --auto_ai ...` 生成三段候选池 JSON
- [x] 统计各候选池内允许星级分布，验证差值 <= 1（在总量足够时）
- [x] 覆盖不足场景：记录 `meta.rating_rebalance` 的补齐与不足标记正确
- **Status:** complete

### Phase 4: Delivery（更新说明）
<!-- 
  WHAT: Verify everything works and meets requirements.
  WHY: Catching issues early saves time. Document test results in progress.md.
-->
- [x] 更新 `references/abs_journal_recommend.md`（说明候选池会尽量均衡星级，并在 meta 记录）
- **Status:** complete

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


<!-- 旧任务已归档：此前关于“报告固定列”的计划不再适用本次目标 -->
