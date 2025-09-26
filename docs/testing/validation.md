# Validation

## Manual Validation

Run the validation script to check basic functionality:
```bash
python validate_setup.py
```

This tests:
- Module imports
- Configuration loading  
- Basic data processing functions

## Code Quality

The CI pipeline also includes:
- **Black** formatting checks
- **isort** import sorting
- **flake8** linting

Run locally:
```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .
```