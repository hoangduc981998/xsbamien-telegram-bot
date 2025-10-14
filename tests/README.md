# 🧪 Tests Documentation

This directory contains unit tests for the XS Ba Miền Telegram Bot.

## 📁 Structure

```
tests/
├── __init__.py           # Package initialization
├── conftest.py           # Pytest fixtures and shared test utilities
├── test_keyboards.py     # Tests for keyboard generation functions
└── README.md            # This file
```

## 🎯 Test Coverage

### Current Tests

#### `test_keyboards.py`
Tests for keyboard generation functions in `app/ui/keyboards.py`:

- **`TestGetScheduleTodayKeyboard`** - Tests for `get_schedule_today_keyboard()`
  - ✅ Weekday conversion (all 7 days)
  - ✅ All provinces shown (no limit)
  - ✅ 2-column layout
  - ✅ Back button presence
  - ✅ Display name truncation
  - ✅ Callback data format
  - ✅ Province grouping by region order (MB → MT → MN)

- **`TestGetTodayScheduleActions`** - Tests for `get_today_schedule_actions()`
  - ✅ Weekday conversion (all 7 days)
  - ✅ Navigation buttons presence
  - ✅ All provinces shown (no limit)
  - ✅ 2-column layout
  - ✅ Display name truncation
  - ✅ Callback data format
  - ✅ Province/navigation button ordering
  - ✅ Province grouping by region order (MB → MT → MN)
  - ✅ Edge case: Thursday with 7 provinces

## 🚀 Running Tests

### Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_keyboards.py
```

### Run Specific Test Class

```bash
pytest tests/test_keyboards.py::TestGetScheduleTodayKeyboard
```

### Run Specific Test Method

```bash
pytest tests/test_keyboards.py::TestGetScheduleTodayKeyboard::test_weekday_conversion
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run with Coverage for Specific Module

```bash
pytest --cov=app.ui.keyboards --cov-report=term-missing
```

## 📊 Test Fixtures

Located in `conftest.py`:

### `mock_datetime`
Mock `datetime.now()` to test different weekdays.

**Usage:**
```python
def test_example(mock_datetime):
    with patch('app.ui.keyboards.datetime') as mock_dt:
        mock_dt.now.return_value = mock_datetime(0)  # Monday
        # ... test code
```

### `expected_provinces_by_day`
Dictionary mapping Python weekday to expected province codes.

**Usage:**
```python
def test_example(expected_provinces_by_day):
    monday_provinces = expected_provinces_by_day[0]
    # Expected: ["MB", "THTH", "PHYE", "TPHCM", "DOTH", "CAMA"]
```

## 🎨 Test Patterns

### Testing Weekday Conversion

The most critical test is the weekday conversion from Python's format to SCHEDULE format:

```python
@pytest.mark.parametrize("python_weekday,schedule_day", [
    (0, 1),  # Monday → schedule day 1
    (1, 2),  # Tuesday → schedule day 2
    # ... etc
])
def test_weekday_conversion(self, python_weekday, schedule_day):
    with patch('app.ui.keyboards.datetime') as mock_dt:
        mock_dt.now.return_value.weekday.return_value = python_weekday
        # Test logic
```

**Why this matters:**
- Python: Monday=0, Tuesday=1, ..., Sunday=6
- SCHEDULE: Sunday=0, Monday=1, ..., Saturday=6
- Conversion: `schedule_day = (weekday + 1) % 7`

### Testing Button Layout

Verify 2-column layout:
```python
for row in keyboard.inline_keyboard[:-1]:  # Exclude last row
    assert len(row) <= 2
```

### Testing Button Data

Extract and verify province codes:
```python
province_codes = []
for row in keyboard.inline_keyboard[:-1]:
    for button in row:
        if button.callback_data.startswith("province_"):
            province_codes.append(button.callback_data.replace("province_", ""))
```

## 📈 Coverage Goals

- **Target:** ≥ 90% coverage for `app/ui/keyboards.py`
- **Current:** Run `pytest --cov=app.ui.keyboards` to check

## 🔍 Debugging Tests

### Run with Print Statements

```bash
pytest -s tests/test_keyboards.py
```

### Run with PDB Debugger

```bash
pytest --pdb
```

### Show All Test Output

```bash
pytest -vv
```

## 🎯 Best Practices

1. **Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **Single Assertion Focus**: One concept per test when possible
4. **Use Fixtures**: Reuse common setup via fixtures
5. **Parametrize**: Test multiple scenarios with `@pytest.mark.parametrize`
6. **Mock External Dependencies**: Use `patch()` for datetime, API calls, etc.

## 🐛 Common Issues

### Issue: Import Errors

**Solution:** Ensure the project root is in PYTHONPATH:
```bash
export PYTHONPATH=/path/to/xsbamien-telegram-bot:$PYTHONPATH
pytest
```

### Issue: Tests Pass Locally But Fail in CI

**Solution:** Check for:
- Timezone differences
- Environment variables
- File path differences

### Issue: Flaky Tests

**Solution:** 
- Ensure proper mocking
- Avoid time-dependent logic without mocking
- Use fixtures for consistent state

## 📝 Adding New Tests

1. Create test file in `tests/` with `test_` prefix
2. Create test class with `Test` prefix
3. Create test methods with `test_` prefix
4. Use fixtures from `conftest.py`
5. Run tests: `pytest tests/your_test.py`

Example:
```python
# tests/test_example.py
import pytest

class TestExample:
    def test_something(self):
        assert True
```

## 🔄 Continuous Integration

Tests are automatically run on:
- Every push to main branch
- Every pull request
- Before deployment

## 📞 Support

For questions or issues with tests:
- Check this README
- Review existing tests for patterns
- Open an issue on GitHub
