## MODIFIED Requirements

### Requirement: Hybrid guidance accuracy
The ABS-Journal SKILL.md SHALL describe the hybrid workflow as: export candidate pool → AI generate tri-mode JSON (fit/easy/value, each ≥ TopK with topic) → run `abs_ai_review.py --topk` → generate single Markdown report via `hybrid_report.py`, with fixed columns `序号 | 期刊名 | ABS星级 | 期刊主题`.

#### Scenario: Outdated single-mode guidance
- **WHEN** SKILL.md suggests仅 fit 或未要求三模式
- **THEN** update text to require fit/easy/value 同时输出并固定列。

### Requirement: Path defaults
The SKILL.md SHALL default to project-root-relative paths under `assets/` for candidate_pool, ai_output, and report examples, noting absolute paths only when necessary.

#### Scenario: Absolute path only examples
- **WHEN** SKILL.md示例只给绝对路径
- **THEN**补充相对路径示例并说明基准目录。

### Requirement: Consistent hard rules
Hard constraints in SKILL.md SHALL not contradict top-level AGENTS rules (e.g., prefer local data, no auto-update) and SHALL mirror the implemented scripts’ constraints.

#### Scenario: Conflicting rule
- **WHEN** SKILL.md allows skipping subset validation or omits rating_filter requirement
- **THEN** align it with actual script behavior and AGENTS hard constraints.
