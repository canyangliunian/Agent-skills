## ADDED Requirements

### Requirement: Enforce tri-mode AI JSON schema
The AI output JSON SHALL contain top-level keys `fit`, `easy`, `value`, each mapped to an array of objects with `journal` and `topic`.

#### Scenario: Missing key
- **WHEN** the JSON omits the `value` key
- **THEN** validation SHALL fail and report the missing key.

### Requirement: Candidate pool subset validation
Each `journal` in AI output SHALL exist in the exported candidate pool `candidates[].journal`.

#### Scenario: Journal outside pool
- **WHEN** AI output includes a journal not present in the candidate pool
- **THEN** validation SHALL fail, listing the offending journal and mode.

### Requirement: Length meets TopK
Each mode array SHALL contain at least TopK entries (default 10 or user-specified).

#### Scenario: Short list
- **WHEN** `easy` contains fewer than TopK entries
- **THEN** validation SHALL fail and specify the shortfall.

### Requirement: Non-empty topic
Every entry SHALL include a non-empty `topic` string.

#### Scenario: Topic missing
- **WHEN** a row's `topic` is empty or whitespace
- **THEN** validation SHALL fail and report mode + index.
