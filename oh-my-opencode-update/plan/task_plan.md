# Task Plan: oh-my-opencode-update 路径硬编码修复

## Goal
修复 oh-my-opencode-update skill 中的路径硬编码问题，使其可移植、可分享给其他人使用。创建 Agent Team 进行项目审核。

## Current Phase
Phase 7: 团队解散 (完成)

## Phases

### Phase 1: 团队创建与任务规划
- [x] 创建 oh-my-opencode-fix 团队
- [x] 定义团队成员：team-lead, path-fix-implementer, reference-reviewer, scripts-reviewer
- [x] 创建任务列表（7 个任务）
- [x] 设置任务依赖关系
- [x] 更新规划文档
- **Status:** complete

### Phase 2: 路径修复实施
- [x] 修复脚本路径硬编码 (scripts/oh_my_opencode_update.sh)
- [x] 更新 SKILL.md 使用环境变量语法
- [x] 创建 references/paths_config.md 配置文档
- **Status:** complete

### Phase 3: 脚本审核
- [x] scripts-reviewer 使用 requesting-code-review 审核脚本
- [x] 验证路径解析逻辑正确性
- [x] 检查无硬编码路径残留
- **Status:** complete

### Phase 4: 文档审核
- [x] reference-reviewer 使用 writing-skills 审核文档
- [x] 检查 SKILL.md 环境变量说明清晰度
- [x] 检查 paths_config.md 完整性
- **Status:** complete

### Phase 5: 文档更新与报告
- [x] 更新 task_plan.md
- [x] 更新 findings.md
- [x] 更新 progress.md
- [x] 生成 fix_summary_report.md
- **Status:** complete

### Phase 6: 团队解散
- [ ] 所有任务完成确认
- [ ] 通知团队成员
- [ ] 使用 TeamDelete 清理资源
- **Status:** pending

## Team Members

| 成员 | Agent Type | 职责 | 状态 |
|------|-----------|------|------|
| team-lead | general-purpose | 团队协调、规划、记录 | 活跃 |
| path-fix-implementer | general-purpose | 实现路径修复 | 待命 |
| reference-reviewer | general-purpose | 审核文档 | 待命 |
| scripts-reviewer | general-purpose | 审核脚本 | 待命 |

## Task List

| 任务 ID | 负责人 | 描述 | 状态 | 依赖 |
|---------|--------|------|------|------|
| #1 | team-lead | 创建 plan/ 目录和规划文档 | completed | 无 |
| #2 | path-fix-implementer | 修复脚本路径硬编码 | completed | #1 |
| #3 | path-fix-implementer | 更新 SKILL.md 使用环境变量语法 | completed | #2 |
| #4 | path-fix-implementer | 创建 references/paths_config.md | completed | #2 |
| #5 | scripts-reviewer | 审核修复后的脚本 | completed | #2 |
| #6 | reference-reviewer | 审核 SKILL.md 和 paths_config.md | completed | #3, #4 |
| #7 | team-lead | 更新规划文档，生成修复报告 | completed | #5, #6 |

## Key Issues to Address

1. **SKILL.md 硬编码路径**（第 16-39 行）：包含完整的用户路径，不可移植
2. **脚本路径硬编码**：虽然已改为 `${HOME}`，但 SKILL.md 示例仍为绝对路径
3. **缺少环境变量配置文档**：用户不知道如何自定义路径
4. **脚本位置**：示例命令使用绝对路径，无法从不同位置运行

## Solution Approach

采用三层路径解析策略：
1. **环境变量优先**：用户可通过环境变量自定义所有路径
2. **动态解析**：脚本运行时自动计算相对于 skill 根目录的位置
3. **默认值回退**：使用 `${VAR:-default}` 语法提供合理的默认值

## Key Files

### 需要修改的文件
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh`
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/SKILL.md`

### 需要创建的文件
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/oh-my-opencode-update/references/paths_config.md`

### 参考文件
- `/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/scripts/abs_paths.py`

## Decisions Made

1. **环境变量命名**：使用 `OPENCODE_` 前缀避免冲突
2. **路径示例**：使用相对路径（如 `bash scripts/oh_my_opencode_update.sh`）
3. **文档位置**：配置文档放在 `references/paths_config.md`
