# Progress Log（ABS-Journal：路径可移植化）

## 2026-02-05
- 初始化 `plan/` 目录与规划文件（task_plan/findings/progress）。
- 启动 Phase 1：准备扫描硬编码路径与入口点。
- 扫描发现硬编码路径主要集中在文档/示例命令；脚本中也有少量 docstring 示例与 1 处遗留变量（`abs_article_impl.py` 内 `SKILL_ROOT` 未定义）触发测试失败。
- 新增路径工具 `scripts/abs_paths.py`，通过环境变量覆盖 + 自动向上探测 `SKILL.md` 来解析 `skill_root/data_dir`。
- 运行 `python3 scripts/test_hybrid_flow.py` 通过（修复 `SKILL_ROOT` + mock AI 输出满足 TopK）。

## 2026-02-06
- 将三模式语义从 `easy/fit/value` 调整为投稿难度 `easy/medium/hard`，并统一 TopK 默认=10。
- 更新混合流程相关脚本：AI 输出校验与报告生成均改为检查 `easy/medium/hard` 三键。
- 更新文档与模板：`SKILL.md`、`references/abs_journal_recommend.md`、`scripts/ai_second_pass_template.md`。
- 自测通过：
  - `python3 scripts/test_recommendation_gating.py`
  - `python3 scripts/test_hybrid_flow.py`
- 根据用户新反馈增强“难度层次感”：在 `scripts/abs_journal.py` 为不同 `--mode` 默认注入星级过滤（easy=1,2；medium=2,3；hard=4,4*），用户显式传 `--rating_filter` 则覆盖默认。
- 用用户提供论文信息做一次端到端分层测试（不启用 hybrid；TopK=10；field=ECON）：
  - easy：输出命中星级分布：1×4 + 2×2（通过“混合比例”规则尝试引入 2，使 easy 不再全是 1；仍受主题贴合 gating 影响）
  - medium：输出命中星级分布：2×3 + 3×1（通过“混合比例”规则尝试引入 3，使 medium 不再全是 2；仍受主题贴合 gating 影响）
  - hard：在实现“TopK 不足回退”后，本例输出提升为 7 条（4*×2 + 4×5），但仍未补满 10；说明仅扩大 gating + 放宽星级一档仍可能不足，后续可继续考虑更激进回退（例如 hard 再放宽到 2，或允许跨领域/关闭 gating）。
- 方案A（参数体验）：明确 `--field` 不控制候选范围，仅作为论文领域标签/关键词配置；默认候选期刊 Field 范围由内置 5 个 Field 白名单决定（可用 `--field_scope` 覆盖）。更新了 README/SKILL/references 文档与 CLI help。
- 修复潜在严重误判：`parse_ajg_rating()` 对未知/空值不再默认映射为 4*，改为未评级（0）；报告中新增“未评级”分组（如出现）。
- 测试补充：新增 `--field_scope` 非法值应报错并打印可选 Field 列表的断言；并改为覆盖“不传 `--field_scope` 参数”的默认行为。
<!-- 
  WHAT: Your session log - a chronological record of what you did, when, and what happened.
  WHY: Answers "What have I done?" in the 5-Question Reboot Test. Helps you resume after breaks.
  WHEN: Update after completing each phase or encountering errors. More detailed than task_plan.md.
-->

## Session: [DATE]
<!-- 
  WHAT: The date of this work session.
  WHY: Helps track when work happened, useful for resuming after time gaps.
  EXAMPLE: 2026-01-15
-->

### Phase 1: [Title]
<!-- 
  WHAT: Detailed log of actions taken during this phase.
  WHY: Provides context for what was done, making it easier to resume or debug.
  WHEN: Update as you work through the phase, or at least when you complete it.
-->
- **Status:** in_progress
- **Started:** [timestamp]
<!-- 
  STATUS: Same as task_plan.md (pending, in_progress, complete)
  TIMESTAMP: When you started this phase (e.g., "2026-01-15 10:00")
-->
- Actions taken:
  <!-- 
    WHAT: List of specific actions you performed.
    EXAMPLE:
      - Created todo.py with basic structure
      - Implemented add functionality
      - Fixed FileNotFoundError
  -->
  -
- Files created/modified:
  <!-- 
    WHAT: Which files you created or changed.
    WHY: Quick reference for what was touched. Helps with debugging and review.
    EXAMPLE:
      - todo.py (created)
      - todos.json (created by app)
      - task_plan.md (updated)
  -->
  -

### Phase 2: [Title]
<!-- 
  WHAT: Same structure as Phase 1, for the next phase.
  WHY: Keep a separate log entry for each phase to track progress clearly.
-->
- **Status:** pending
- Actions taken:
  -
- Files created/modified:
  -

## Test Results
<!-- 
  WHAT: Table of tests you ran, what you expected, what actually happened.
  WHY: Documents verification of functionality. Helps catch regressions.
  WHEN: Update as you test features, especially during Phase 4 (Testing & Verification).
  EXAMPLE:
    | Add task | python todo.py add "Buy milk" | Task added | Task added successfully | ✓ |
    | List tasks | python todo.py list | Shows all tasks | Shows all tasks | ✓ |
-->
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
|      |       |          |        |        |

## Error Log
<!-- 
  WHAT: Detailed log of every error encountered, with timestamps and resolution attempts.
  WHY: More detailed than task_plan.md's error table. Helps you learn from mistakes.
  WHEN: Add immediately when an error occurs, even if you fix it quickly.
  EXAMPLE:
    | 2026-01-15 10:35 | FileNotFoundError | 1 | Added file existence check |
    | 2026-01-15 10:37 | JSONDecodeError | 2 | Added empty file handling |
-->
<!-- Keep ALL errors - they help avoid repetition -->
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
|           |       | 1       |            |

## 5-Question Reboot Check
<!-- 
  WHAT: Five questions that verify your context is solid. If you can answer these, you're on track.
  WHY: This is the "reboot test" - if you can answer all 5, you can resume work effectively.
  WHEN: Update periodically, especially when resuming after a break or context reset.
  
  THE 5 QUESTIONS:
  1. Where am I? → Current phase in task_plan.md
  2. Where am I going? → Remaining phases
  3. What's the goal? → Goal statement in task_plan.md
  4. What have I learned? → See findings.md
  5. What have I done? → See progress.md (this file)
-->
<!-- If you can answer these, context is solid -->
| Question | Answer |
|----------|--------|
| Where am I? | Phase X |
| Where am I going? | Remaining phases |
| What's the goal? | [goal statement] |
| What have I learned? | See findings.md |
| What have I done? | See above |

---
<!-- 
  REMINDER: 
  - Update after completing each phase or encountering errors
  - Be detailed - this is your "what happened" log
  - Include timestamps for errors to track when issues occurred
-->
*Update after completing each phase or encountering errors*
