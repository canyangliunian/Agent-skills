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
- `/Users/lingguiwang/Documents/Coding/LLM/tests/abs_journal_reports/ai_report.md` 中三段（Easy/Medium/Hard）的"星级过滤"完全一致（都为 `2,3`），与预期分层（easy < medium < hard）不一致。

### 根因定位
- 代码侧已经实现默认分层：`scripts/abs_journal.py` 中 `DEFAULT_RATING_FILTER_BY_MODE = {easy: 1,2; medium: 2,3; hard: 4,4*}`，当 `--rating_filter` 留空时会按 mode 自动选择。
- 但文档/示例（`SKILL.md` 与 `references/abs_journal_recommend.md`）仍示范传入统一或不合理的 `--rating_filter`（如 `"1,2,3"` 或 hard 用 `"3,4,4*"`），会覆盖默认分层，导致 AI/用户照抄时出现"星级过滤不一致/不分层"。

### 修复方向
- 文档侧明确：混合流程要么不传 `--rating_filter`（留空=自动分层），要么分别为 easy/medium/hard 明确不同桶；并强调"显式传入会覆盖默认分层"。
- 需要同步修正文档与示例，并用本地离线用例验证生成的报告中三段 meta 的 `rating_filter` 分别为 `1,2` / `2,3` / `4,4*`。


## 2026-02-08：Session 5ad953f2 候选池 1:1 不满足问题（根因分析）

### 现象
- 用户报告：Session `5ad953f2-7372-4b89-9799-095f41eaf279` 跑出来的候选池结果依然不满足 1:1
- 分析候选池 JSON `rating_rebalance` meta：
  - Easy: `allowed_ratings=["1","2"]`, `available_by_rating={"1":0,"2":106}`, `selected_by_rating={"1":0,"2":106}`
  - Medium: `allowed_ratings=["2","3"]`, `available_by_rating={"2":0,"3":53}`, `selected_by_rating={"2":0,"3":53}`
  - Hard: `allowed_ratings=["4","4*"]`, `available_by_rating={"4":21,"4*":6}`, `selected_by_rating={"4":21,"4*":6}`
  - `ideal_balanced_pool_size: 0`（所有模式都是 0）

### 根因定位
1. **显式传入 `--rating_filter`**：用户命令中使用了 `--rating_filter 1,2` 等参数，覆盖了默认的分层逻辑
2. **主题贴合 gating 后低星级被完全过滤**：
   - Easy 模式：星级 1 的期刊（共 700 本候选）经过主题贴合 gating 后，没有任何期刊满足条件
   - Medium 模式：星级 2 的期刊同样被完全过滤
   - 原因：论文主题（"test"，ECON 领域）可能与低星级期刊的主题范围匹配度低
3. **代码逻辑正确但结果无奈**：
   - `ideal_balanced_pool_size = k * min(available_by_rating.values())`
   - 当某星级可用量为 0 时，ideal_balanced_pool_size 就是 0
   - 均衡逻辑 `rebalance_by_rating_quota` 处理了这种情况（返回所有可用期刊），但无法实现 1:1

### 代码实现确认
- `scripts/abs_article_impl.py:703-869` 的 `rebalance_by_rating_quota` 函数逻辑正确
- 函数正确计算了 `available_by_rating`、`selected_by_rating`
- 当某个星级无可用期刊时，会返回所有可用期刊（满足"不够再补"的兜底策略）

### 修复方案选项
| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A. 调整 gating 策略 | 在主题贴合 gating 时，确保各星级都有足够候选 | 根本解决问题 | 可能降低推荐质量（主题贴合度） |
| B. 扩大候选池范围 | 增加 `candidate_topn` 参数，让更多期刊参与均衡 | 简单 | 不能解决根本问题 |
| C. 跨相邻星级补充 | 已实现的"同桶内相邻星级优先"补齐逻辑 | 已实现，无代价 | 但当前场景下没有相邻低星级可用 |
| D. 文档说明 | 说明 1:1 的前提条件和限制 | 无需改代码 | 不能解决用户实际需求 |
| E. 分两阶段均衡 | 先按主题 gating 再按星级均衡，扩大搜索范围 | 更全面 | 复杂度高 |

### 建议方案
- 短期：文档说明 + 建议用户使用不传 `--rating_filter` 的默认分层
- 中期：考虑调整 gating 策略，在主题贴合时给予低星级期刊更多机会
- 验证：检查 `--hybrid --auto_ai` 流程中是否传入了显式 `--rating_filter` 参数


## 完整问题链路分析（2026-02-08）

### 流程回顾
1. `--hybrid` 模式下，`abs_journal.py` 为每个 mode 生成候选池：
   - Easy: `--rating_filter "1,2"` (默认)
   - Medium: `--rating_filter "2,3"` (默认)
   - Hard: `--rating_filter "4,4*"` (默认)
2. `abs_article_impl.py` 的处理流程：
   - Phase 1 gating: 在所有 Field 范围（约 700 本）内按 fit_score 排序，取 TopN（默认 80）
   - 按 rating_filter 过滤星级
   - Phase 2 fallback: 如果过滤后 < TopK（10 本），扩大 candidate_topn 到 200
   - 再次按 rating_filter 过滤
   - 星级均衡采样（`rebalance_by_rating_quota`）

### 根因分析
- 主题贴合 gating 是"跨星级统一排序"的
- 低星级期刊（1, 2）的平均主题贴合度较低，在 TopN 中很少或没有
- Phase 2 扩大候选池到 200 后，仍然没有足够的低星级期刊
- 导致：
  - Easy: `available_by_rating = {"1": 0, "2": 106}`
  - Medium: `available_by_rating = {"2": 0, "3": 53}`
  - Hard: `available_by_rating = {"4": 21, "4*": 6}` (分布 21:6，非 1:1)

### 代码逻辑确认
- `rebalance_by_rating_quota` 函数逻辑正确
- 正确计算了 `ideal_balanced_pool_size = k * min(available_by_rating.values()) = 0`
- 正确处理了"某星级无可用期刊"的情况（返回所有可用期刊）
- 问题不在均衡逻辑，而在输入数据

### 修复方案

#### 方案 A：按星级分层 gating（已实现）
修改 `gate_by_topic_fit` 函数：
1. 按 rating_filter 分组期刊（按星级）
2. 在每个星级内分别进行主题贴合 gating
3. 确保每个星级都有足够候选（默认各星级至少 20 本）
4. 合并各星级的 gated 结果后，再进行评分排序

**优点**：从根本上解决问题，确保各星级都有候选
**缺点**：需要修改核心逻辑，可能增加计算时间

**实现详情**：
- 扩展 `GatingMeta` dataclass，添加 `per_rating_stats` 字段
- 修改 `gate_by_topic_fit` 函数，支持按星级分层 gating（V2）
- 添加 `_gate_by_topic_fit_per_rating` 函数，在每个星级内分别进行主题贴合排序
- 添加 `_rating_sort_key` 辅助函数，用于星级排序
- 更新 `build_ranked` 调用，传入 `rating_filter` 参数
- 更新 `candidate_pool_to_dict` 函数，输出 `per_rating_stats`

#### 方案 B：扩大 gating 候选池（备选）
进一步扩大 Phase 2 的 candidate_topn：
- 从 200 扩大到更大值（如 500 或 1000）
- 增加计算时间，但不保证能解决根本问题

**优点**：改动小，风险低
**缺点**：不保证解决问题，可能浪费计算资源

#### 方案 C：文档说明（兜底）
说明 1:1 的前提条件和限制：
- 1:1 的前提：各星级必须有足够期刊满足主题贴合条件
- 如果某星级无可用期刊，候选池将无法实现 1:1 均衡
- 建议用户：
  - 调整主题关键词（`--field`、`--abstract`）
  - 接受当前分布（meta 中会记录 `insufficient_total_candidates: true`）

**优点**：无代码风险
**缺点**：不解决根本问题


## 实现结果（2026-02-08）

### 方案 A 实现：按星级分层 gating

**代码变更**：
1. `scripts/abs_article_impl.py`:
   - 导入 `field` 函数（`from dataclasses import dataclass, field`）
   - 扩展 `GatingMeta` dataclass，添加 `per_rating_stats: Dict[str, int]` 字段
   - 修改 `gate_by_topic_fit` 函数签名，添加 `rating_filter` 参数
   - 添加 `_gate_by_topic_fit_per_rating` 辅助函数
   - 添加 `_rating_sort_key` 辅助函数
   - 更新 `build_ranked` 调用，传入 `rating_filter` 参数
   - 更新 `candidate_pool_to_dict` 函数，输出 `per_rating_stats`

### 验证结果

**测试命令**：
```bash
python3 scripts/abs_journal.py recommend \
  --title "test" \
  --mode medium \
  --topk 10 \
  --hybrid \
  --export_candidate_pool_json "reports/test_candidate_pool.json"
```

**候选池星级分布（修复后）**：
| Mode | Gating 策略 | per-rating 统计 | 可用量 | 实际选中 | ideal_balanced_pool_size |
|------|-------------|------------------|--------|---------|------------------------|
| Easy | `topn-per-rating` | `{'1': 80, '2': 80}` | `{'1': 80, '2': 80}` | 160 ✅ |
| Medium | `topn-per-rating` | `{'2': 80, '3': 80}` | `{'2': 80, '3': 80}` | 160 ✅ |
| Hard | `topn-per-rating` | `{'4': 41, '4*': 15}` | `{'4': 41, '4*': 15}` | 30 ✅ |

**对比（修复前 → 修复后）**：
| Mode | ideal_balanced_pool_size | 可用量分布 | per-rating 统计 |
|------|------------------------|----------|------------------|
| Easy | 0 → 160 ✅ | `{"1": 0, "2": 106}` → `{"1": 80, "2": 80}` | 无 → `{'1': 80, '2': 80}` |
| Medium | 0 → 160 ✅ | `{"2": 0, "3": 53}` → `{"2": 80, "3": 80}` | 无 → `{'2': 80, '3': 80}` |
| Hard | 0 → 30 ✅ | `{"4": 21, "4*": 6}` → `{"4": 41, "4*": 15}` | 无 → `{'4': 41, '4*': 15}` |

**结论**：
- ✅ 按星级分层 gating 成功确保各星级都有足够候选
- ✅ `ideal_balanced_pool_size` 从 0 提升到实际值
- ✅ Easy/Medium 模式实现完美 1:1 均衡
- ✅ Hard 模式接近 1:1（受限于可用量：4 星级 41 本，4* 星级 15 本）
