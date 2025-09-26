# Troubleshooting Tests

## Common Issues

1. **Import errors**: Ensure you're running from the project root
2. **Mock not working**: Check that you're patching the right module path
3. **Tests slow**: Ensure external dependencies are properly mocked

## Debugging Tests

```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Run single test with debugging
python -m pytest tests/test_config.py::TestConfigUtilities::test_load_area_config_success -v -s

# Drop into debugger on failure
python -m pytest tests/ --pdb
```