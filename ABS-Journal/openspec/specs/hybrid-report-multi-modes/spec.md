## Purpose

统一输出混合流程的三难度（easy/medium/hard）投稿推荐报告，确保固定列格式与完整性。

## Requirements

### Requirement: Generate unified tri-mode report
The system SHALL produce a single Markdown file containing three sections (easy, medium, hard), each listing TopK journals (default 10) derived from the AI-filtered candidate pool.

#### Scenario: Report generated with full modes
- **WHEN** user runs `abs_journal.py recommend --hybrid --hybrid_report_md <path> --export_candidate_pool_json <path> --ai_output_json <path>`
- **THEN** the output Markdown SHALL contain three titled sections (Easy, Medium, Hard) each with a table of TopK entries.

### Requirement: Fixed column layout
Each mode section table SHALL use the exact header `| 序号 | 期刊名 | ABS星级 | 期刊主题 |` and rows numbered sequentially from 1.

#### Scenario: Table columns rendered
- **WHEN** the report is generated
- **THEN** every mode table SHALL include four columns with the specified header and maintain ordering.

### Requirement: Mode completeness validation
The system SHALL fail with a clear error if any of the three difficulty buckets is missing or provides fewer than TopK items.

#### Scenario: Missing bucket
- **WHEN** AI output JSON lacks the `medium` key
- **THEN** the command SHALL exit non-zero and indicate the missing bucket.

#### Scenario: Insufficient rows
- **WHEN** a bucket contains fewer than TopK entries
- **THEN** the command SHALL exit non-zero and specify which bucket is short.

### Requirement: Topic presence
Each output row SHALL include a non-empty `topic` string describing why the journal fits the paper.

#### Scenario: Empty topic
- **WHEN** any row in AI output has an empty `topic`
- **THEN** the command SHALL exit non-zero pointing to that mode and row index.
