# Task Plan: 规范化期刊推荐报告输出样式

## Goal
解决 abs-journal skill 在生成期刊推荐时输出样式混乱的问题（一会儿纯文字,一会儿表格），基于 /writing-skills 规范统一输出格式。

## Context
- **问题来源**: Session ID a12dd2fe-a5f9-4228-8219-9f935055f60e
- **当前状态**: 主报告文件 `reports/ai_report.md` 格式符合要求（固定表格输出）
- **核心问题**: Claude 在基于主报告文件向用户做推荐时，输出样式不一致（混合使用纯文字列表和表格）
- **需求**: 统一规范 Claude 的推荐输出样式，必要时创建模板文件

## Current Phase
Phase 2: 设计规范化方案 - COMPLETE
Phase 3: 实现规范化 - IN PROGRESS

## Phases

### Phase 1: 问题诊断与调研 ✅
**目标**: 明确样式混乱的具体场景和根本原因

- [x] 读取 /writing-skills 相关文档,理解其输出规范要求（未找到本地文档）
- [x] 分析 `hybrid_report.py` 当前的报告生成逻辑
- [x] 查看 abs-journal skill 的主入口文件 (`SKILL.md`),了解推荐流程
- [x] 识别样式混乱发生在哪个环节:
  - **根因**: SKILL.md 要求"期刊主题"列，hybrid_report.py 输出"Field"列
  - 不是样式混乱，而是列定义不同步
- [x] 记录具体的不一致案例：SKILL.md Line 64 vs hybrid_report.py Line 107

**Status**: complete
**完成时间**: 2026-02-08 03:30

### Phase 2: 设计规范化方案 ✅
**目标**: 设计统一的输出模板和规范

- [x] 基于调研结果，明确问题不在样式混乱，而在列定义不同步
- [x] 决策方案: **选择方案 A 路径 1** - 修改 `hybrid_report.py`，添加"期刊主题"列
  - 理由 1: AI 输出 JSON 中已有 topic 字段可直接使用
  - 理由 2: "期刊主题"比"Field"提供更多价值（AI 生成的针对性说明）
  - 理由 3: 符合混合流程设计初衷（AI 二次筛选补充推荐理由）
- [x] 明确新表格格式: 序号 | 期刊名 | ABS星级 | 期刊主题
- [x] 设计实施步骤:
  1. 修改 `render_table` 函数的表头和数据提取逻辑
  2. 从 AI 输出 JSON 的 topic 字段提取期刊主题
  3. 保留 Field 信息在"可追溯信息"区展示

**Status**: complete
**完成时间**: 2026-02-08 03:35

### Phase 3: 实现规范化
**目标**: 根据设计方案实施修改

- [ ] 如果选择方案 A: 修改 `hybrid_report.py`
  - [ ] 统一表格生成函数的格式
  - [ ] 添加输出格式验证逻辑
- [ ] 如果选择方案 B: 创建 `recommendation_template.md`
  - [ ] 定义标准的推荐报告结构
  - [ ] 提供示例填充说明
- [ ] 如果选择方案 C: 更新 `SKILL.md`
  - [ ] 添加"输出样式规范"章节
  - [ ] 明确 Claude 在推荐时应遵循的格式约束

**Status**: pending

### Phase 4: 测试验证
**目标**: 使用真实数据验证规范化效果

- [ ] 使用 Session a12dd2fe 的测试数据重新生成推荐
- [ ] 检查输出是否严格遵循统一格式
- [ ] 验证以下场景:
  - Easy/Medium/Hard 三段推荐的格式一致性
  - 可追溯信息的呈现格式
  - 补充说明的格式
- [ ] 对比修改前后的输出差异

**Status**: pending

### Phase 5: 文档更新
**目标**: 更新相关文档,确保规范可持续

- [ ] 更新 `README.md`,说明新的输出规范
- [ ] 在 `references/` 目录下创建输出样式指南文档
- [ ] 如果创建了模板文件,添加使用说明
- [ ] 更新 `SKILL.md` 的使用示例

**Status**: pending

## Key Questions
1. [待调研] /writing-skills 的具体规范要求是什么?
2. [待调研] 样式混乱发生在脚本生成阶段还是 Claude 二次呈现阶段?
3. [待决策] 应该采用哪种方案来规范输出（A/B/C）?
4. [待设计] 表格和列表的使用边界是什么?

## Decisions Made
| Decision | Rationale | Date |
|----------|-----------|------|
| 创建 plan/ 目录下的规划文件 | 符合 CLAUDE.md 的规范要求 | 2026-02-08 |

## Errors Encountered
| Error | Attempt | Resolution | Date |
|-------|---------|------------|------|
| (待记录) | - | - | - |

## Notes
- 根据用户反馈,当前主报告文件格式正确,问题主要在推荐呈现环节
- 需要平衡可读性和一致性,避免过度格式化导致信息传递效率降低
- 考虑是否需要针对不同推荐场景（快速推荐 vs 详细分析）使用不同模板
