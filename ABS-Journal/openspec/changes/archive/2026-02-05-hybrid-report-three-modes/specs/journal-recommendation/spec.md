## MODIFIED Requirements

### Requirement: Hybrid report generation
The system SHALL generate a Markdown report for hybrid mode that now includes all three recommendation modes (fit, easy, value) in one file when `--hybrid_report_md` is provided.

#### Scenario: Three-mode report produced
- **WHEN** the user supplies `--hybrid --export_candidate_pool_json <path> --ai_output_json <path> --hybrid_report_md <path>`
- **THEN** the resulting report SHALL contain separate sections for fit, easy, and value, each with TopK rows and fixed columns.
