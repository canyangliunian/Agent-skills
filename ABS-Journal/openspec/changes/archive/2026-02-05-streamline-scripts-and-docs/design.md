## Context

仓库当前以根目录 skill（`ABS-Journal`）方式交付，核心工作流由 `SKILL.md` 驱动：默认基于本地 `assets/data/` 推荐投稿期刊，只有用户明确要求更新数据库时才运行 `scripts/ajg_fetch.py`。

目前 `references/` 已包含数据契约与排查文档，但缺少两份“脚本级别”的使用说明，导致未来 skill 指导用户时需要反复从脚本源码中提取参数/示例，且容易遗漏关键约束（默认不更新、envvars、输出目录等）。

本次变更的重点是“入口明确 + 文档补齐”：
- 明确 `scripts/` 脚本分层（核心入口 vs 辅助保留）
- 为两个核心入口脚本增加对应 `references/*.md` 说明文档
- 更新 `SKILL.md` 的 references 指向，保持渐进式加载

## Goals / Non-Goals

**Goals:**
- 在 `references/` 下新增两份脚本文档：
  - `references/ajg_fetch.md`
  - `references/abs_journal_recommend.md`
- 两份文档均包含：用途、何时使用、最小命令示例（绝对路径）、关键参数、常见错误与排查、与 skill 默认策略（不自动更新）的关系。
- 更新 `SKILL.md` 的 “References (Load Only If Needed)” 列表，使其可按需加载到这两份脚本文档。
- 不移除离线校验/统一入口脚本（`ajg_verify_outputs.py`、`abs_journal.py`）。

**Non-Goals:**
- 不改变抓取与推荐算法逻辑（只做文档与引用整理）。
- 不对脚本进行大规模重命名或拆分（保持现有入口稳定）。

## Decisions

1) **脚本分层以“用户入口”为准**
- 决策：将 `scripts/ajg_fetch.py` 与 `scripts/abs_journal_recommend.py` 定义为“核心入口”，其余为“辅助但保留”。
- 理由：用户最常用的两个动作就是“更新数据（显式）”与“推荐（默认本地）”；其他脚本服务于控制流或校验，不应被误删。

2) **reference 文档定位为“可复制命令 + 约束解释”**
- 决策：`references/*.md` 不写长叙述，优先提供可复制命令、参数表、失败模式与修复动作。
- 理由：减少对话指导时的上下文成本，并提高可复现性。

3) **SKILL.md 保持精简，重内容下沉到 references**
- 决策：SKILL.md 只保留工作流分支与指向 references；脚本参数细节放到 `references/ajg_fetch.md` 与 `references/abs_journal_recommend.md`。

## Risks / Trade-offs

- [文档与脚本参数不一致导致误导] → 在 apply 阶段从脚本 `-h/--help` 中提取参数并写入文档；变更脚本参数时必须同步更新 references。
- [用户误用更新流程导致频繁抓取] → 文档与 SKILL.md 均强调“只有明确要求更新才抓取”，并建议优先使用本地数据推荐。

