## Context

- 多个 SKILL.md（尤其 ABS-Journal、AGENTS 顶层规则）与 `scripts/` 和 `references/` 的现状不一致（路径、流程顺序、输出格式）。
- 目标：以 `scripts/` 和 `references/` 的行为为准，矫正 SKILL.md 的指引与约束，避免用户误用。
- 约束：不改核心脚本逻辑；优先文档/技能文件调整；路径默认相对项目根。

## Goals / Non-Goals

**Goals:**
- 识别并列出 SKILL.md 与实际流程的冲突点（路径、流程、输出格式、必选参数）。
- 更新相关 SKILL.md，使其与 `scripts/abs_journal.py`、`scripts/abs_ai_review.py`、`scripts/hybrid_report.py` 以及 `references/abs_journal_recommend.md` 一致。
- 明确路径约定：默认相对项目根使用 `assets/`。

**Non-Goals:**
- 不调整脚本功能或算法。
- 不变更数据源或混合流程逻辑。

## Decisions

1) **以脚本与 reference 为真源**：所有流程描述、示例命令、路径要求以 `scripts/` 和 `references/abs_journal_recommend.md` 为准。
2) **路径默认相对**：示例路径采用项目根下 `assets/`；如需绝对路径，显式说明。
3) **混合流程输出强调三模式固定列**：SKILL.md 明确要求 fit/easy/value 同时 10 条、表头固定、缺少即报错。
4) **校验顺序与参数**：先导出候选池 → AI 输出 → `abs_ai_review.py --topk` 校验 → `hybrid_report.py` 生成单文件报告。

## Risks / Trade-offs

- 风险：旧习惯用户仍用绝对路径或单模式；缓解：在 SKILL.md 中突出相对路径与三模式要求。
- 风险：遗漏其他技能引用旧流程；缓解：检查与 ABS-Journal 直接相关的 SKILL.md/AGENTS 片段。
