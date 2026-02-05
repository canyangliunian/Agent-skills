# Task Plan：ABS-Journal 路径可移植化
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
  WHY: After 50+ tool calls, your original goals can get forgotten. This file keeps them fresh.
  WHEN: Create this FIRST, before starting any work. Update after each phase completes.
-->

## Goal
- 将仓库内“写死的绝对路径”（尤其是从 `.../Skills/ABS-Journal` 复制到 `~/.agents/skills/abs-journal` 后会失效的路径）改造为“可移植/可配置”的路径解析方案。
- 目标：同一套代码既能在开发目录运行，也能复制到 `~/.agents/skills/abs-journal` 运行；更换电脑/用户名/目录结构时无需改代码。

## Non-goals
- 不改变现有业务逻辑（除路径解析、少量 CLI 参数/默认值）。
- 不做大规模重构（仅围绕路径与配置）。

## Current Phase
<!-- 
  WHAT: Which phase you're currently working on (e.g., "Phase 1", "Phase 3").
  WHY: Quick reference for where you are in the task. Update this as you progress.
-->
Phase 1（扫描硬编码路径与入口点）

## Phases
<!-- 
  WHAT: Break your task into 3-7 logical phases. Each phase should be completable.
  WHY: Breaking work into phases prevents overwhelm and makes progress visible.
  WHEN: Update status after completing each phase: pending → in_progress → complete
-->

### Phase 1: Requirements & Discovery（扫描硬编码路径）
<!-- 
  WHAT: Understand what needs to be done and gather initial information.
  WHY: Starting without understanding leads to wasted effort. This phase prevents that.
-->
- [ ] 汇总现有目录结构与运行入口
- [ ] 全仓扫描绝对路径/家目录写死/开发机路径
- [ ] 记录“必须可配置”的路径清单（脚本/数据/缓存/输出）
- **Status:** in_progress
<!-- 
  STATUS VALUES:
  - pending: Not started yet
  - in_progress: Currently working on this
  - complete: Finished this phase
-->

### Phase 2: Planning & Structure（路径策略设计）
<!-- 
  WHAT: Decide how you'll approach the problem and what structure you'll use.
  WHY: Good planning prevents rework. Document decisions so you remember why you chose them.
-->
- [ ] 定义统一路径解析函数（repo root / install root / data / cache）
- [ ] 约定环境变量覆盖（如 `ABS_JOURNAL_HOME` 等）
- [ ] 记录兼容策略（旧路径/默认行为）
- **Status:** pending

### Phase 3: Implementation（逐文件替换）
<!-- 
  WHAT: Actually build/create/write the solution.
  WHY: This is where the work happens. Break into smaller sub-tasks if needed.
-->
- [ ] 新增/改造 `scripts/` 下的路径工具模块
- [ ] 替换硬编码路径为统一工具函数调用
- [ ] 增加基础错误提示（找不到路径时给出可操作指引）
- **Status:** pending

### Phase 4: Testing & Verification（最小自测）
<!-- 
  WHAT: Verify everything works and meets requirements.
  WHY: Catching issues early saves time. Document test results in progress.md.
-->
- [ ] 在“开发目录”运行最小命令集
- [ ] 复制到 `~/.agents/skills/abs-journal` 后再跑一遍最小命令集（或模拟）
- [ ] 记录测试日志与差异
- **Status:** pending

### Phase 5: Delivery（文档与迁移说明）
<!-- 
  WHAT: Final review and handoff to user.
  WHY: Ensures nothing is forgotten and deliverables are complete.
-->
- [ ] Review all output files
- [ ] Ensure deliverables are complete
- [ ] Deliver to user
- **Status:** pending

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
