# CI Pipeline

## GitHub Actions Workflow

The CI pipeline (`.github/workflows/test.yml`) runs on:
- Every pull request to `main`/`master`
- Every push to `main`/`master`

## Test Matrix

Tests run on multiple Python versions:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Dependencies in CI

The CI environment installs:
- **System packages**: `gdal-bin`, `python3-mapnik`
- **Python packages**: `pytest`, `pytest-mock`, `pytest-cov`
- **Application dependencies**: `requests`