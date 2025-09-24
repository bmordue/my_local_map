# Test Coverage

Current test coverage: **85%**

| Module | Coverage | Missing Lines |
|--------|----------|---------------|
| map_generator.py | 97% | Entry point only |
| utils/config.py | 100% | Complete coverage |
| utils/data_processing.py | 78% | Error handling paths |
| utils/style_builder.py | 100% | Complete coverage |

Areas not covered are primarily error handling for external dependencies (mapnik, ogr2ogr) that are mocked in tests.