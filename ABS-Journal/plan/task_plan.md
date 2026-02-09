# Task Plan: 审阅和修复 ABS-Journal 技能规范

## Goal
使用 `/writing-skills` 的流程规范，全面审阅当前 `abs-journal` 技能，修复技能名称大小写问题，并检查其他潜在问题。

## Context
- **任务来源**: 用户要求使用 `/writing-skills` 规范审阅当前技能
- **核心问题**: SKILL.md 中的 `name: ABS-Journal` 使用了大写，需要改为小写 `abs-journal`
- **审阅方式**: 创建 agent team（非 subagent）进行标准化审阅
- **审阅范围**:
  - 技能元数据（name, description）
  - 文档结构和内容
  - 代码实现
  - 测试覆盖
  - 引用文档一致性

## Current Phase
✅ Phase 6: 验证和测试 - 已完成

**所有阶段已完成！**

## Phases

### Phase 1: 准备和探索
**目标**: 了解 `/writing-skills` 规范，探索当前技能结构

**任务**:
- ✅ 读取 `/writing-skills` 技能规范文档
- ✅ 理解技能审阅的标准流程和检查清单
- ✅ 探索当前 `abs-journal` 技能的完整结构
- ✅ 列出所有需要审阅的文件清单
- ✅ 记录当前已知问题（name 大小写）

**Status**: ✅ complete

### Phase 2: 创建审阅团队
**目标**: 创建专门的 agent team 进行标准化审阅

**任务**:
- ✅ 设计团队结构和角色分工
- ✅ 创建审阅团队（使用 TeamCreate）
- ✅ 分配审阅任务给不同的 agent
- ✅ 建立审阅检查清单

**Status**: ✅ complete

### Phase 3: 执行审阅
**目标**: 团队协作完成全面审阅

**任务**:
- ✅ 元数据审阅（name, description, 触发条件）
- ✅ 文档结构审阅（SKILL.md, README.md, references/）
- ✅ 代码实现审阅（scripts/, 命名规范, 错误处理）
- ✅ 测试覆盖审阅（tests/, 测试完整性）
- ✅ 一致性审阅（文档与代码的一致性）
- ✅ 用户体验审阅（Quick Start, 错误提示, 示例）

**Status**: ✅ complete

**审阅结果**:
- 总计发现 19 个问题
- Critical: 2个，High: 7个，Medium: 6个，Low: 4个

### Phase 4: 汇总问题和制定修复方案
**目标**: 整理审阅发现的所有问题，制定修复计划

**任务**:
- ✅ 汇总所有审阅发现的问题
- ✅ 按优先级分类（Critical, High, Medium, Low）
- ✅ 制定修复方案和顺序
- ✅ 评估修复影响范围
- ✅ 获取用户确认

**Status**: ✅ complete

### Phase 5: 执行修复
**目标**: 按计划修复所有问题

**任务**:
- ✅ 修复 Critical 级别问题（2个）
- ✅ 修复 High 级别问题（7个）
- ⏳ 修复 Medium 级别问题（待后续迭代）
- ⏳ 修复 Low 级别问题（待后续迭代）
- ✅ 更新相关文档

**Status**: ✅ complete（Critical + High 全部完成）

### Phase 6: 验证和测试
**目标**: 验证所有修复是否正确

**任务**:
- ✅ 验证技能元数据格式正确
- ✅ 测试技能触发条件
- ✅ 运行现有测试套件
- ✅ 验证文档一致性
- ✅ 生成审阅报告

**Status**: ✅ complete

**测试结果**:
- ✅ test_hybrid_flow.py - 通过
- ✅ test_recommendation_gating.py - 通过
- ✅ test_hybrid_requires_export.py - 通过
- ✅ 所有测试通过率：100%

### Phase 5: 执行修复
**目标**: 按计划修复所有问题

**任务**:
- [ ] 修复 Critical 级别问题（如 name 大小写）
- [ ] 修复 High 级别问题
- [ ] 修复 Medium 级别问题
- [ ] 修复 Low 级别问题（可选）
- [ ] 更新相关文档

**Status**: pending

### Phase 6: 验证和测试
**目标**: 验证所有修复是否正确

**任务**:
- [ ] 验证技能元数据格式正确
- [ ] 测试技能触发条件
- [ ] 运行现有测试套件
- [ ] 验证文档一致性
- [ ] 生成审阅报告

**Status**: pending

## Key Questions
1. [待调研] `/writing-skills` 规范的具体审阅流程是什么？
2. [待调研] 技能命名规范是什么？（全小写？kebab-case？）
3. [待确认] 除了 name 大小写，还有哪些潜在问题？
4. [待决策] 是否需要向后兼容旧的技能名称？
5. [待确认] 审阅团队应该包含哪些角色？

## Decisions Made
| Decision | Rationale | Date |
|----------|-----------|------|
| 使用 agent team 而非 subagent | 用户明确要求，且适合标准化审阅流程 | 2026-02-10 |
| 使用 plan/ 目录管理规划文件 | 符合 CLAUDE.md 规范要求 | 2026-02-10 |

## Errors Encountered
| Error | Attempt | Resolution | Date |
|-------|---------|------------|------|
| (待记录) | - | - | - |

## Notes
- 当前已知问题：SKILL.md 第2行 `name: ABS-Journal` 应改为 `name: abs-journal`
- 需要检查是否有其他地方引用了大写的技能名称
- 审阅应该全面，不仅限于已知问题
- 修复后需要确保技能仍然可以正常工作
