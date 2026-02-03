# Task Plan: 修复 oh-my-opencode-update skill 规范（可被识别）

## Goal
让 `oh-my-opencode-update` 技能在你的技能系统中可被正确发现/触发：补齐 YAML frontmatter、规范化 description（触发条件）、并保持默认升级 latest + 支持指定版本；同时继续在 `plan/` 下维护记录文件。

## Current Phase
Phase 3

## Phases

### Phase 1: Discovery (skill detection rules)
- [x] 确认当前目录 skill 版本的 SKILL.md 缺少 YAML frontmatter
- [x] 明确技能系统的“发现路径”（你的环境扫描 `~/.config/opencode/skills` 指向的目录；现有 symlink 指向 `~/.agents/skills/...`）
- **Status:** complete

### Phase 2: Rewrite SKILL.md to spec
- [x] 写入 YAML frontmatter（仅 name/description）
- [x] description 只写触发条件（Use when...），不写流程
- [x] body 保留简体中文说明、绝对路径、默认 latest + 指定版本
- **Status:** complete

### Phase 3: Verify discovery
- [x] 校验 frontmatter 解析规则（本地脚本断言）
- [x] dry-run 验证脚本 latest 路径可运行
- [ ] （待你确认）在 opencode 实际对话中触发测试：说“使用 oh-my-opencode-update 升级到最新版本”
- **Status:** in_progress

