# abs-journal Test Suite

This directory contains the test suite for the abs-journal skill.

## Test Structure

```
tests/
├── __init__.py
├── fixtures/           # Test fixtures
└── test_unit/
    ├── __init__.py
    └── test_abs_unit.py  # Unit tests
```

## Running Tests

### Run all tests
```bash
cd /Users/lingguiwang/Documents/Coding/LLM/Agent-skills/abs-journal
python3 -m pytest tests/ -v
```

### Run specific test class
```bash
python3 -m pytest tests/test_unit/test_abs_unit.py::TestSupportsColor -v
python3 -m pytest tests/test_unit/test_abs_unit.py::TestValidateNoOverlap -v
```

### Run specific test
```bash
python3 -m pytest tests/test_unit/test_abs_unit.py::TestValidateNoOverlap::test_normalizes_whitespace_in_journal_names -v
```

## Test Coverage

### Current Tests (16 tests)

#### TestSupportsColor (5 tests)
- ✅ `test_no_color_disables_color` - NO_COLOR=1 disables color
- ✅ `test_empty_term_disables_color` - Empty TERM disables color
- ✅ `test_dumb_term_disables_color` - TERM=dumb disables color
- ✅ `test_valid_term_enables_color` - Valid TERM enables color
- ✅ `test_force_color_conflict_behavior` - NO_COLOR takes precedence over FORCE_COLOR

#### TestValidateNoOverlap (9 tests)
- ✅ `test_no_overlap_valid_input` - Valid input with no overlaps
- ✅ `test_detects_overlap_between_buckets` - Detects overlap between buckets
- ✅ `test_allows_explicit_overlap` - meta.allow_overlap=True allows overlaps
- ✅ `test_handles_empty_buckets` - Empty buckets handled gracefully
- ✅ `test_handles_missing_buckets` - Missing buckets handled gracefully
- ❌ `test_normalizes_whitespace_in_journal_names` - **FAILS** (potential bug found!)
- ✅ `test_handles_none_input` - None input raises exception (expected)
- ✅ `test_handles_empty_string_journal` - Empty journal names skipped
- ✅ `test_handles_non_dict_items` - Non-dict items skipped

#### TestRenderReport (2 tests)
- ✅ `test_handles_none_gating_meta` - Placeholder test
- ✅ `test_renders_valid_gating_meta` - Placeholder test

### Test Results

```
========================= 1 failed, 15 passed in 0.03s ==========================
```

## Discovered Issues

### Bug: Whitespace Normalization in validate_no_overlap()

**Location**: `abs_ai_review.py:55`

**Problem**:
- Journal names with different internal whitespace are treated as different
- `"Journal  A"` (double space) vs `"Journal A"` (single space) are not detected as duplicates
- Only `.strip()` is applied, which only removes leading/trailing whitespace

**Test that exposes it**:
```python
ai_output = {
    "easy": [{"journal": "Journal  A", "topic": "topic 1"}],  # Double space
    "medium": [{"journal": "Journal A", "topic": "topic 2"}],  # Single space
    "hard": [],
}
# Current: No overlap detected (0 errors)
# Expected: Should detect overlap (1 error)
```

**Impact**:
- Users might accidentally submit the same journal with different whitespace
- Could lead to duplicate recommendations in different buckets

**Suggested Fix**:
Normalize whitespace in journal names:
```python
# In validate_no_overlap(), line 55
j = (it.get("journal") or "").strip()
# Change to:
import re
j = re.sub(r'\s+', ' ', (it.get("journal") or "")).strip()
```

## pytest Configuration

Configuration is in `pytest.ini` at the abs-journal skill root.

## Adding New Tests

1. Create test file in `tests/test_unit/`
2. Name file with `test_*.py` prefix
3. Name test functions with `test_` prefix
4. Use pytest fixtures for common setup

Example:
```python
class TestNewFeature:
    def test_normal_case(self):
        """Test description."""
        # Arrange
        input_data = "test"

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected_output
```

## Coverage Reports

Generate coverage report (after installing pytest-cov):
```bash
python3 -m pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```
