# Findings & Decisions — oh-my-opencode-update

## Requirements
- 使用 $planning-with-files 持久记录：`plan/task_plan.md`, `plan/findings.md`, `plan/progress.md`
- 备份：`~/.config/opencode/opencode.json` 与 `~/.config/opencode/oh-my-opencode.json`
- 温和卸载（失败即停止，不自动扩大范围）
- 默认升级到 **latest**，同时支持 **指定版本**
- 技能必须符合“可被系统识别”的规范（YAML frontmatter + 正确命名 + 目录结构）

## Key Findings (原因定位：为什么你识别不到 skill)
- 你当前工作目录的 `SKILL.md` **没有 YAML frontmatter**（缺少 `---\nname: ...\ndescription: ...\n---`），这会导致技能发现机制无法从元数据中识别与触发。
- 解决方案：按 `writing-skills`/`skill-creator` 规范重写 `SKILL.md`：
  - frontmatter 只包含 `name` 与 `description`
  - `name` 只能包含字母/数字/连字符（hyphens）
  - `description` 只写“Use when...”触发条件，不写流程细节

## Decisions
| Decision | Rationale |
|----------|-----------|
| name = oh-my-opencode-update | 已约定的技能名，且符合 hyphens 规范 |
| 默认 target = latest | 避免锁死版本，适配未来升级 |
| 保留 --target-version | 支持可复现 pinned 版本升级 |
| 日志优先写入 ./plan | 你要求持续维护 plan/ 下 md 文件 |

## Resources
- Working skill draft (current repo copy):
  - `/Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/SKILL.md`
  - `/Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/scripts/oh_my_opencode_update.sh`
- Plan logs:
  - `/Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/plan/task_plan.md`
  - `/Users/lingguiwang/Documents/Coding/LLM/Skills/oh-my-opencode-update/plan/progress.md`

