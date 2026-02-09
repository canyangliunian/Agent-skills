# LaTeX Skill - Test Suite

This directory contains the test suite for the latex skill.

## Test Structure

```
tests/
├── __init__.py
├── test_unit/
│   ├── __init__.py
│   └── test_compile_critical_bugs.py  # Critical bug detection tests
└── test_integration/                    # Future: integration tests
```

## Running Tests

### Run all tests
```bash
cd /Users/lingguiwang/Documents/Coding/LLM/Agent-skills/latex
python3 -m pytest tests/ -v
```

### Run specific test file
```bash
python3 -m pytest tests/test_unit/test_compile_critical_bugs.py -v
```

### Run specific test class
```bash
python3 -m pytest tests/test_unit/test_compile_critical_bugs.py::TestRequiresUnicodeEngine -v
```

### Run specific test
```bash
python3 -m pytest tests/test_unit/test_compile_critical_bugs.py::TestDeleteTmpdir::test_no_infinite_recursion -v
```

## Test Coverage

### Current Tests

#### `test_compile_critical_bugs.py`

**TestRequiresUnicodeEngine** (4 tests)
- ✅ `test_detects_ctex_class` - Tests ctex document class detection
- ✅ `test_detects_ctex_package` - Tests ctex package detection
- ✅ `test_detects_xecjk_package` - Tests xeCJK package detection
- ✅ `test_rejects_plain_latex` - Tests plain LaTeX rejection

**TestDeleteTmpdir** (3 tests)
- ❌ `test_no_infinite_recursion` - Tests for RecursionError (KNOWN BUG)
- ✅ `test_skips_non_tmp_directories` - Tests safety guards
- ✅ `test_handles_nonexistent_directory` - Tests error handling

### Known Issues

**Bug: RecursionError in `_delete_tmpdir()`**
- **Location**: `compile.py:559`
- **Cause**: Infinite recursion - function calls itself instead of `shutil.rmtree()`
- **Test**: `test_no_infinite_recursion` correctly fails with RecursionError
- **Status**: RED stage - waiting for fix (GREEN stage)

## TDD Workflow

This test suite follows Test-Driven Development (TDD) principles:

1. **RED**: Tests are written to fail, exposing bugs
2. **GREEN**: Minimal code changes to make tests pass
3. **REFACTOR**: Improve code quality while keeping tests green

### Current Status
- ✅ RED stage complete (Bug exposed)
- ⏳ GREEN stage pending (Bug fix needed)
- ⏳ REFACTOR stage pending

## Adding New Tests

1. Create test file in appropriate directory (`test_unit/` or `test_integration/`)
2. Name file with `test_` prefix
3. Name test functions with `test_` prefix
4. Run tests to verify

Example:
```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = "test"

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

## pytest Configuration

Configuration is in `pytest.ini` at the latex skill root.

## Coverage Reports

Generate coverage report (after installing pytest-cov):
```bash
python3 -m pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```
