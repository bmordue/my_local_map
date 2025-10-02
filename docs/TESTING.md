# Testing Guide for Lumsden Tourist Map Generator

This document describes the comprehensive testing infrastructure for the Lumsden Tourist Map Generator project.

## Testing Overview

The project now includes a complete testing suite with:
- **Unit tests** for all utility functions
- **Integration tests** for the main application workflow
- **GitHub Actions CI pipeline** for automated testing
- **Code coverage reporting**

## Test Structure

```
tests/
├── __init__.py
├── test_config.py           # Configuration utilities tests
├── test_data_processing.py  # Geographic and data processing tests
├── test_style_builder.py    # Style generation tests
└── test_integration.py      # End-to-end integration tests
```

## Running Tests

### Prerequisites

Install testing dependencies:
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing -v

# Run specific test files
python -m pytest tests/test_config.py -v
python -m pytest tests/test_integration.py -v
```

### Test Categories

Tests are marked with categories:
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, test workflows)

Run specific categories:
```bash
# Run only unit tests
python -m pytest -m unit -v

# Run only integration tests  
python -m pytest -m integration -v
```

## Test Coverage

Current test coverage: **85%**

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| map_generator.py | 97% | Entry point only |
| utils/config.py | 100% | Complete coverage |
| utils/data_processing.py | 78% | Error handling paths |
| utils/style_builder.py | 100% | Complete coverage |

Areas not covered are primarily error handling for external dependencies (mapnik, ogr2ogr) that are mocked in tests.

## CI Pipeline

### GitHub Actions Workflow

The CI pipeline (`.github/workflows/test.yml`) runs on:
- Every pull request to `main`/`master`
- Every push to `main`/`master`

### Test Matrix

Tests run on multiple Python versions:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### Dependencies in CI

The CI environment installs:
- **System packages**: `gdal-bin`, `python3-mapnik`
- **Python packages**: `pytest`, `pytest-mock`, `pytest-cov`
- **Application dependencies**: `requests`

## Test Strategy

### Unit Tests

Test individual functions in isolation with mocked dependencies:

```python
@pytest.mark.unit
def test_calculate_bbox_basic(self):
    """Test basic bounding box calculation"""
    bbox = calculate_bbox(57.3167, -2.8833, 8, 12)
    assert isinstance(bbox, dict)
    assert 'south' in bbox
    # ... more assertions
```

### Integration Tests

Test complete workflows with all external dependencies mocked:

```python
@pytest.mark.integration  
def test_main_with_mocked_dependencies(self):
    """Test main function with all dependencies mocked"""
    with patch('map_generator.load_area_config') as mock_load_area:
        # Setup mocks...
        result = map_generator.main()
        assert result == 0
```

### Mocking Strategy

External dependencies are mocked to ensure tests:
- Run in any environment (without mapnik/GDAL installed)
- Are fast and reliable (no network calls)
- Focus on testing our code logic

Key mocked components:
- **mapnik** module (for map rendering)
- **requests** calls (for OSM data download)
- **subprocess** calls (for ogr2ogr)
- **file operations** (for configuration and output)

## Validation

### Manual Validation

Run the validation script to check basic functionality:
```bash
python utils/system_validation.py
```

This tests:
- Module imports
- Configuration loading  
- Basic data processing functions

### Code Quality

The CI pipeline also includes:
- **Black** formatting checks
- **isort** import sorting
- **flake8** linting (PEP8 compliance)

Run locally:
```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code (PEP8 compliance)
./check_flake8.sh
# Or run flake8 directly
flake8 .
```

## Testing Best Practices

### Writing New Tests

1. **Unit tests** for new utility functions
2. **Integration tests** for new workflows
3. **Mock external dependencies** appropriately
4. **Use descriptive test names** and docstrings
5. **Test both success and failure paths**

### Example Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Test new feature functionality"""
    
    @pytest.mark.unit
    def test_new_function_success(self):
        """Test successful execution of new function"""
        # Arrange
        # Act  
        # Assert
        
    @pytest.mark.unit
    def test_new_function_error_handling(self):
        """Test error handling in new function"""
        # Test error conditions
```

## Troubleshooting Tests

### Common Issues

1. **Import errors**: Ensure you're running from the project root
2. **Mock not working**: Check that you're patching the right module path
3. **Tests slow**: Ensure external dependencies are properly mocked

### Debugging Tests

```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Run single test with debugging
python -m pytest tests/test_config.py::TestConfigUtilities::test_load_area_config_success -v -s

# Drop into debugger on failure
python -m pytest tests/ --pdb
```

## Future Testing Enhancements

Potential improvements:
- **End-to-end tests** with real (small) OSM data
- **Performance tests** for large areas
- **Visual regression tests** for map output
- **Property-based testing** for geographic calculations
- **Integration with external data sources**