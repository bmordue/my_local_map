# Running Tests

## Prerequisites

Install testing dependencies:
```bash
pip install -r requirements-test.txt
```

## Run All Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing -v

# Run specific test files
python -m pytest tests/test_config.py -v
python -m pytest tests/test_integration.py -v
```

## Test Categories

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