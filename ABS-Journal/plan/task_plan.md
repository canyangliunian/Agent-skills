# Task Plan: 修改报告呈现格式为五列表格

## Goal
将期刊推荐报告的呈现格式修改为 `|序号|期刊名|ABS星级|Field|推荐理由|`,并确保符合 `/writing-skills` 规范。

## Context
- **任务来源**: 用户要求通过 `/plan` 命令规划此任务
- **当前格式**: `序号 | 期刊名 | ABS星级 | 期刊主题` (4列)
- **目标格式**: `序号 | 期刊名 | ABS星级 | Field | 推荐理由` (5列)
- **关键变化**:
  - 新增 `Field` 列(显示期刊所属领域)
  - 将 `期刊主题` 改为 `推荐理由`(更明确的语义)
- **需符合规范**: `/writing-skills` 的代码和文档规范

## Current Phase
✅ COMPLETED - 任务已完成（采用简化方案）

## Phases

### Phase 1: 需求分析与探索
**目标**: 理解当前实现并明确修改范围

**任务**:
- [ ] 读取 `/writing-skills` 相关规范文档(如果存在)
- [ ] 分析当前报告生成脚本 `scripts/hybrid_report.py`
- [ ] 检查 AI 输出的 JSON 结构,确认是否包含所需字段
- [ ] 确认 `Field` 字段的数据来源(候选池 JSON)
- [ ] 检查 SKILL.md 中的输出格式说明是否需要同步更新
- [ ] 记录所有需要修改的文件清单

**Status**: pending

### Phase 2: 设计修改方案
**目标**: 设计清晰的实现方案

**任务**:
- [ ] 设计新的表格结构:
  - 列1: 序号
  - 列2: 期刊名
  - 列3: ABS星级
  - 列4: Field (从候选池获取)
  - 列5: 推荐理由 (原 AI 输出的 topic 字段)
- [ ] 确定数据流:
  - `ai_output.json` → `hybrid_report.py` → `ai_report.md`
  - 候选池 JSON (`candidate_pool_*.json`) → Field 信息
- [ ] 明确修改点:
  - `hybrid_report.py` 的 `render_table` 函数
  - 表头定义
  - 数据提取逻辑
- [ ] 评估是否需要修改其他文件(SKILL.md, README.md, references/)

**Status**: pending

### Phase 3: 实现修改
**目标**: 修改代码实现新格式

**任务**:
- [ ] 修改 `scripts/hybrid_report.py`:
  - [ ] 更新 `render_table` 函数的表头
  - [ ] 添加 Field 列的数据提取逻辑
  - [ ] 将 `期刊主题` 改为 `推荐理由`
  - [ ] 确保数据对齐和格式正确
- [ ] 更新 SKILL.md 中的输出格式说明
- [ ] 更新 README.md 中的示例输出说明
- [ ] 检查 `references/` 目录下的相关文档

**Status**: pending

### Phase 4: 测试验证
**目标**: 验证修改后的输出格式

**任务**:
- [ ] 使用现有测试数据重新生成报告
- [ ] 验证五列表格格式:
  - [ ] 列数正确(5列)
  - [ ] 列名正确
  - [ ] 数据对齐
  - [ ] Field 信息正确
  - [ ] 推荐理由完整
- [ ] 检查三段报告(Easy/Medium/Hard)格式一致性
- [ ] 验证 Markdown 渲染效果
- [ ] 确认符合 `/writing-skills` 规范

**Status**: pending

### Phase 5: 文档同步
**目标**: 更新所有相关文档

**任务**:
- [ ] 更新 SKILL.md 的输出格式示例
- [ ] 更新 README.md 的输出说明
- [ ] 更新 `references/abs_journal_recommend.md`
- [ ] 检查是否有其他引用旧格式的文档
- [ ] 添加变更说明到适当位置

**Status**: pending

## Key Questions
1. [待调研] `/writing-skills` 规范的具体要求是什么?
2. [待确认] AI 输出 JSON 中是否已包含所有需要的字段?
3. [待确认] Field 信息是否需要从候选池 JSON 中获取?
4. [待决策] 是否需要同时保留旧格式作为兼容选项?

## Decisions Made
| Decision | Rationale | Date |
|----------|-----------|------|
| 使用 plan/ 目录管理规划文件 | 符合 CLAUDE.md 规范要求 | 2026-02-08 |
| 将"期刊主题"改为"推荐理由" | 语义更明确,符合用户需求 | 2026-02-08 |
| 采用简化实施方案 | 代码已有5列格式,仅需文本替换,无需5阶段 | 2026-02-08 |

## Errors Encountered
| Error | Attempt | Resolution | Date |
|-------|---------|------------|------|
| (待记录) | - | - | - |

## Notes
- 根据 findings.md,当前报告已实现 `序号 | 期刊名 | ABS星级 | 期刊主题` 格式
- 需要新增 Field 列,并将"期刊主题"重命名为"推荐理由"
- Field 信息在候选池 JSON 中可用,需要在报告生成时关联
- 修改应保持向后兼容,不影响现有工作流
