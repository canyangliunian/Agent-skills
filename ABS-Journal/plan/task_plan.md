# Task Plan：混合推荐报告中"每类期刊没有 1:1 匹配"问题诊断

## Goal
- 诊断用户反馈的"每类里面没有 1:1 匹配"问题（参考 Session ID: 95643038-114b-4aee-b7fd-05c5535a547）
- 明确问题是指"候选池星级分布"还是"最终推荐报告的分类呈现"
- 提供针对性的修复方案

## 问题澄清（2026-02-08 03:00）

### 用户反馈
- "依然每类里面没有 1:1"
- 提供测试数据：关于中美贸易战、农业关税的 RCT 研究论文

### 可能的理解维度
1. **候选池星级分布**：已通过"按星级分层 gating"修复，当前测试显示 Easy/Medium 完美 1:1
2. **最终推荐报告分类**：用户可能期望在"综合评分、影响力、实证方法、跨学科视角、政策导向"五个类别中每类都有 1:1 高度匹配的期刊

### 测试结果（2026-02-08）
使用提供的测试数据运行 `--hybrid` 流程：

**候选池星级分布（已修复）**：
- Easy: `{"1": 80, "2": 80}` → selected `{"1": 75, "2": 75}` ✅ 1:1
- Medium: `{"2": 80, "3": 80}` → selected `{"2": 75, "3": 75}` ✅ 1:1
- Hard: `{"4": 41, "4*": 15}` → selected `{"4": 35, "4*": 15}` ⚠️ 约 2:1（受限于可用量）

**最终推荐报告呈现**：
- 当前报告只按难度分段（Easy/Medium/Hard），没有按"综合评分、影响力、实证方法、跨学科、政策"五类分组
- 如果用户期望的是这五类分组，则需要重新设计推荐逻辑

## Current Phase
Phase 3: 审核最终推荐输出是否 1:1 - IN PROGRESS

## 需求澄清（2026-02-08 03:10）
用户关键问题：**候选池内部实现了 1:1，但最终推荐输出是否也是 1:1？**

这是两个不同阶段：
1. **候选池阶段**（已验证 ✅）：Easy/Medium 的候选池 JSON 内部星级分布为 1:1
2. **最终推荐阶段**（待审核 ❓）：从候选池中选出 TopK 推荐给用户时，是否保持 1:1？

## Phases

### Phase 1: 问题确认与需求澄清
- [x] 使用测试数据运行 `--hybrid` 流程
- [x] 读取候选池 JSON 文件分析星级分布
- [x] 明确用户期望的"1:1"含义
- **Status:** complete

### Phase 2: 完成诊断与总结
- [x] 分析 Hard 模式 4* 不足的根本原因
- [x] 确认是否有进一步优化空间
- [x] 提供初步诊断报告
- **Status:** complete

### Phase 3: 审核最终推荐输出
- [x] 读取推荐报告（`reports/ai_report.md`）
- [x] 统计 Easy/Medium/Hard 三段的推荐期刊星级分布
- [x] 对比"候选池 1:1" vs "推荐输出 1:1"
- [x] 定位推荐选择逻辑（`build_ranked` 函数）
- [x] 确认需要在推荐阶段也实施 1:1 均衡
- **Status:** complete
- **发现**：候选池虽然是 1:1，但最终推荐全是高星级（Easy 全是 2 星，Medium 全是 3 星，Hard 全是 4 星）

### Phase 4: 实施推荐阶段 1:1 均衡（方案 A）
- [x] 修复 `picked_names` 变量未定义的 bug
- [x] 让 `--hybrid` 模式默认启用 `exact_rating_balance`
- [x] 修改 `pick_unique` 函数，实现星级均衡采样逻辑
- [x] 使用测试数据验证修复效果（所有模式完美 1:1）
- [x] 检查边界情况（实现了回退策略）
- **Status:** complete

## 验证结果（2026-02-08 03:13）
- Easy Top10: 5×1星 + 5×2星 ✅ 完美 1:1
- Medium Top10: 5×2星 + 5×3星 ✅ 完美 1:1
- Hard Top10: 5×4星 + 5×4* ✅ 完美 1:1

## 最终状态
**所有 Phases 已完成** ✅

## Phases

### Phase 1: 问题诊断与方案设计
- [x] 分析候选池 JSON 的 `rating_rebalance` meta 数据
- [x] 确认问题：显式传入 `--rating_filter` 后，某些星级因主题贴合 gating 被完全过滤
- [x] 分析完整链路：
  - Phase 1 gating: 跨星级统一按 fit_score 排序，取 TopN（默认 80）
  - Phase 2 fallback: 扩大到 200 后仍无低星级期刊
  - 根因: 低星级期刊的平均主题贴合度较低，TopN 中被完全过滤
- [x] 设计修复方案（方案 A：按星级分层 gating）
- **Status:** complete

### Phase 2: 实现修复（方案 A：按星级分层 gating）
- [x] 扩展 `GatingMeta` dataclass，添加 `per_rating_stats` 字段
- [x] 修改 `gate_by_topic_fit` 函数，支持按星级分层 gating（V2）
- [x] 添加 `_gate_by_topic_fit_per_rating` 函数，在每个星级内分别进行主题贴合排序
- [x] 添加 `_rating_sort_key` 辅助函数，用于星级排序
- [x] 更新 `build_ranked` 调用，传入 `rating_filter` 参数
- [x] 更新 `candidate_pool_to_dict` 函数，输出 `per_rating_stats`
- **Status:** complete

### Phase 3: 验证测试
- [x] 运行完整混合流程，验证候选池星级分布接近 1:1
- [x] 检查 `ideal_balanced_pool_size > 0`
  - Easy: 160 (从 0 → 160)
  - Medium: 160 (从 0 → 160)
  - Hard: 30 (从 0 → 30)
- [x] 验证 per-rating 统计正确输出
  - Easy: {'1': 80, '2': 80} - 完美 1:1
  - Medium: {'2': 80, '3': 80} - 完美 1:1
  - Hard: {'4': 41, '4*': 15} - 接近 1:1（受限于可用量）
- **Status:** complete

### Phase 4: 文档更新
- [x] 更新 `references/abs_journal_recommend.md` 说明新的 gating 策略
- **Status:** complete

## Key Questions
1. [已解决] 如何确保各星级都有足够候选？→ 按星级分层进行主题贴合 gating
2. [已解决] 如何记录各星级的候选数量？→ GatingMeta.per_rating_stats

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 按星级分层 gating（方案 A）| 根本解决问题，确保各星级都有候选 |
| 扩展 GatingMeta 数据结构| 记录各星级的候选数量，便于调试和验证 |
| 兼容原有 V1 逻辑| 如果不传 rating_filter，使用原有统一排序策略 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| NameError: name 'field' is not defined | 1 | 添加 `from dataclasses import dataclass, field` |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
- Never repeat a failed action - mutate your approach instead
