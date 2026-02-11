# Task Plan: oh-my-opencode-update 全面审核与修复

## Goal
1. **包管理器切换**：将所有 `bun` 命令改为 `npm`（bun 在依赖解析时卡住）
2. **路径可移植性审核**：确保脚本能从任何位置运行，自动找到 skill 根目录
3. **文档一致性审核**：确保 SKILL.md 和 references/ 文档与脚本实现一致

## Current Phase
Phase 6: 审核完成 (complete)

## Phases

### Phase 1: 脚本审核
- [x] 审核 scripts/oh_my_opencode_update.sh
- [x] 检查 bun 命令使用情况
- [x] 验证路径可移植性
- **Status:** complete

### Phase 2: 文档审核
- [x] 审核 SKILL.md 路径说明
- [x] 审核 references/paths_config.md
- [x] 检查文档与实现一致性
- **Status:** complete

### Phase 3: 文档修复
- [x] 更新 SKILL.md "常见问题"部分
- [x] 移除过时的 bun 说明
- [x] 添加 npm 相关内容
- **Status:** complete

### Phase 4: 最终报告
- [x] 生成审核报告
- [x] 更新规划文档
- [x] 完成所有任务
- **Status:** complete

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
