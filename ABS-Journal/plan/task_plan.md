# Task Plan：ABS-Journal 候选池 1:1 星级均衡问题诊断与修复

## Goal
- 诊断并修复候选池 JSON 星级分布不满足 1:1 的问题
- 根因：显式传入 `--rating_filter` 后，某些星级可能没有足够期刊满足主题贴合条件

## 当前问题发现（修复前）
- Easy 模式：`--rating_filter 1,2`，但可用星级分布为 `{"1": 0, "2": 106}`
- Medium 模式：`--rating_filter 2,3`，但可用星级分布为 `{"2": 0, "3": 53}`
- 结果：无法实现 1:1 均衡，因为低星级没有可用期刊
- `ideal_balanced_pool_size = 0`（由 min(0, 106) 计算得出）

## 根因分析
1. **显式 `--rating_filter` 覆盖默认分层逻辑**
2. **主题贴合 gating 后，某些星级完全被过滤掉**
3. **代码中 `rebalance_by_rating_quota` 正确处理了这种情况，但结果就是无法 1:1**

## Current Phase
All phases complete

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
