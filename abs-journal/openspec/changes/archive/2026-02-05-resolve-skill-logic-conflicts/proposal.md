## Why

现有 SKILL.md（特别是 AGENTS 顶层规则与 ABS-Journal SKILL.md）在路径使用、流程顺序、输出格式等方面与 `scripts/` 与 `references/` 的实际实现存在偏差或未同步，导致运行流程与文档指引不一致，容易误导使用者。

## What Changes

- 梳理并修复 SKILL.md 中与脚本/参考文档的冲突（如绝对/相对路径要求、三模式固定列输出、候选池与 AI 校验顺序）。
- 统一 SKILL.md 对混合流程的描述，使之与 `scripts/abs_journal.py`、`scripts/abs_ai_review.py`、`scripts/hybrid_report.py` 以及 `references/abs_journal_recommend.md` 保持一致。
- 明确路径约定：默认相对项目根使用 `assets/`；仅在明确要求时使用绝对路径。
- 补充/纠正示例命令与约束，避免旧流程（单模式、缺列）被误用。

## Capabilities

### New Capabilities
- `skill-consistency-check`: 定义检查与维护 SKILL 文档与脚本/参考文档一致性的流程与要求。

### Modified Capabilities
- `abs-journal-skill-doc`: 更新 ABS-Journal 相关 SKILL.md 中的流程说明与参数要求，使其与最新脚本/文档一致。

## Impact

- 文档：`SKILL.md`（相关技能）、`references/abs_journal_recommend.md`、任何引用旧路径或旧流程的段落。
- 代码：不改动核心脚本逻辑，仅在必要处补充说明或小修文字以消除冲突。
