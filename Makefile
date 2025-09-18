.PHONY: lint test fix check clean

# Lint all Python files
lint:
	ruff check .

# Automatically fix linting issues
fix:
	ruff check . --fix

# Run tests
test:
	pytest

# Run both linting and tests
check: lint test

# Clean cache files
clean:
	rm -rf .ruff_cache __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Help
help:
	@echo "Available commands:"
	@echo "  lint   - Check for linting issues"
	@echo "  fix    - Automatically fix linting issues"
	@echo "  test   - Run tests"
	@echo "  check  - Run both linting and tests"
	@echo "  clean  - Remove cache files"