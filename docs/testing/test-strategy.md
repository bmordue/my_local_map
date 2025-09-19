# Test Strategy

## Unit Tests

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

## Integration Tests

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

## Mocking Strategy

External dependencies are mocked to ensure tests:
- Run in any environment (without mapnik/GDAL installed)
- Are fast and reliable (no network calls)
- Focus on testing our code logic

Key mocked components:
- **mapnik** module (for map rendering)
- **requests** calls (for OSM data download)
- **subprocess** calls (for ogr2ogr)
- **file operations** (for configuration and output)