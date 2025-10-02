# Quality Validation System for Lumsden Tourist Map Generator

This document describes the comprehensive quality validation system implemented in Phase 2 of the project roadmap.

## Overview

The quality validation system provides automated data quality checking for tourist map data, ensuring accuracy, completeness, and consistency across multiple data sources.

## Features Implemented

### 1. Coordinate Validation
- **Geographic bounds checking**: Ensures all coordinates fall within the map area
- **Coordinate format validation**: Supports lat/lon, GeoJSON, and other coordinate formats
- **Invalid coordinate detection**: Identifies coordinates outside valid ranges (-90°/90° lat, -180°/180° lon)
- **Out-of-bounds warnings**: Flags data points outside the map coverage area

### 2. Attribute Completeness Validation
- **Required field checking**: Configurable required fields per data type (accommodation, dining, attractions, etc.)
- **Empty field detection**: Identifies missing or empty required attributes
- **Data type specific rules**: Different validation rules for different POI categories
- **Completeness metrics**: Calculates percentage of complete records

### 3. Temporal Data Validation
- **Opening hours validation**: Supports multiple formats (dictionary, string, special cases)
- **Time format checking**: Validates HH:MM time formats and time ranges
- **Seasonal information**: Validates seasonal availability descriptions
- **Special cases**: Handles "closed", "24/7", "varies", etc.

### 4. Cross-Reference Validation
- **Multi-source comparison**: Compares data across different sources for consistency
- **Name-based matching**: Fuzzy matching for similar business/location names
- **Location-based matching**: Identifies the same location from different sources using coordinates
- **Conflict detection**: Flags inconsistencies in contact info, types, locations, etc.
- **Distance tolerance**: Configurable tolerance for coordinate differences (default: 100m)

## System Architecture

```
Data Sources → Quality Validators → Validation Results → Quality Report
     ↓               ↓                      ↓               ↓
  GeoJSON    CoordinateValidator    ValidationResult    JSON Report
  Enhanced   AttributeValidator     Error/Warning       Summary
  Data       TemporalValidator      Statistics          Recommendations
             CrossReferenceValidator
```

### Core Components

#### ValidationResult
Container for validation results with:
- Pass/fail status
- Error and warning messages
- Statistics (counts, percentages)
- Detailed error information

#### CoordinateValidator
- Validates geographic coordinates
- Checks bounds and format
- Supports multiple coordinate formats
- Configurable map boundaries

#### AttributeValidator
- Validates data completeness
- Configurable required fields per data type
- Supports custom validation rules
- Calculates completeness metrics

#### TemporalValidator
- Validates opening hours and seasonal data
- Flexible time format support
- Handles special cases (closed, 24/7, etc.)
- Regex-based time validation

#### CrossReferenceValidator
- Compares data across sources
- Name and location-based matching
- Conflict detection and reporting
- Distance-based tolerance

#### QualityValidationReport
- Generates comprehensive reports
- JSON and console output
- Automated recommendations
- Summary statistics

## Usage

### Standalone Validation

Run comprehensive validation on all data sources:

```bash
python3 utils/run_quality_validation.py
```

This will:
1. Load enhanced data from `enhanced_data/` directory
2. Run all validation checks
3. Generate detailed report in `validation_reports/`
4. Display summary with recommendations

### Integration with Map Generator

Enable quality validation during map generation:

```bash
ENABLE_QUALITY_VALIDATION=1 python3 map_generator.py
```

### Programmatic Usage

```python
from utils.quality_validation import validate_data_quality

# Define data sources
data_sources = {
    'attractions': [...],
    'accommodation': [...],
    'dining': [...]
}

# Define map boundaries
bbox = {
    'south': 57.26,
    'north': 57.37,
    'west': -2.95,
    'east': -2.82
}

# Run validation
report = validate_data_quality(data_sources, bbox, output_dir="reports")

# Check results
if any(not result.passed for result in report.results):
    print("Quality issues found!")
else:
    print("All quality checks passed!")
```

## Configuration

### Required Fields by Data Type

Default required fields configuration:

```python
required_fields = {
    'accommodation': ['name', 'type', 'contact'],
    'dining': ['name', 'cuisine_type', 'contact'],
    'attraction': ['name', 'description', 'type'],
    'activity': ['name', 'description', 'duration'],
    'trail': ['name', 'distance', 'difficulty']
}
```

### Cross-Reference Tolerance

Default distance tolerance for location matching: 100 meters

Can be customized when creating CrossReferenceValidator:

```python
validator = CrossReferenceValidator()
validator.tolerance_meters = 50  # More strict
```

## Quality Metrics

The system tracks comprehensive quality metrics:

### Coordinate Validation
- Total items processed
- Valid coordinates count
- Invalid coordinates count
- Out-of-bounds warnings

### Attribute Validation
- Total items processed
- Complete items count
- Incomplete items count
- Completeness percentage

### Temporal Validation
- Items with temporal data
- Valid temporal data count
- Invalid temporal data count
- Items without temporal data

### Cross-Reference Validation
- Total comparisons made
- Matches found
- Conflicts detected
- Missing references
- Match percentage

## Output Reports

### Console Output
Real-time validation progress with:
- ✓/✗ Status indicators
- Item counts and statistics
- Error and warning summaries
- Overall quality status
- Actionable recommendations

### JSON Report
Detailed structured report containing:
- Validation summary (pass/fail counts, error totals)
- Individual validation results with details
- Statistics and metrics
- Generated timestamp
- Automated recommendations

Example report structure:
```json
{
  "validation_summary": {
    "total_checks": 12,
    "passed_checks": 10,
    "failed_checks": 2,
    "total_errors": 5,
    "total_warnings": 3,
    "overall_status": "FAILED"
  },
  "validation_details": [...],
  "generated_at": "2024-09-16T17:21:45.123456",
  "recommendations": [...]
}
```

## Error Handling

The validation system is designed to be robust:

- **Graceful degradation**: Continues validation even if some checks fail
- **Error isolation**: Problems in one validator don't affect others
- **Detailed error reporting**: Specific error messages with context
- **Safe defaults**: Handles missing or malformed data appropriately

## Testing

Comprehensive test suite covering:

### Unit Tests (31 test cases)
- ValidationResult functionality
- Each validator component
- Error conditions and edge cases
- Configuration handling

### Integration Tests
- End-to-end validation workflows
- File I/O operations
- Report generation
- Error scenarios

Run tests:
```bash
python3 -m pytest tests/test_quality_validation.py -v
```

## Performance

The validation system is optimized for performance:

- **Memory efficient**: Processes data in streams where possible
- **Fast validation**: Optimized algorithms for coordinate and attribute checking
- **Minimal dependencies**: Only requires standard library + existing project deps
- **Configurable scope**: Can validate specific data types or run comprehensive checks

## Integration with Existing Systems

### Setup Validation
Quality validation is integrated into the existing setup validation:

```bash
python3 utils/system_validation.py
```

Now includes quality validation system checks.

### Map Generation Pipeline
Optional integration with map generation process:

- Set `ENABLE_QUALITY_VALIDATION=1` environment variable
- Runs validation on enhanced data before map rendering
- Continues map generation even if quality issues found
- Logs quality status in map generation output

## Future Enhancements

Potential improvements for Phase 3:

### Advanced Validation Rules
- Custom validation plugins
- Business rule validation (e.g., opening hours logic)
- External data source integration
- Real-time validation APIs

### Enhanced Reporting
- HTML report generation
- Visual quality dashboards
- Trend analysis over time
- Integration with monitoring systems

### Performance Optimization
- Parallel validation processing
- Incremental validation for large datasets
- Caching of validation results
- Database integration for large-scale validation

### Machine Learning Integration
- Anomaly detection in data patterns
- Automated data correction suggestions
- Quality score prediction
- Pattern-based validation rules

## Best Practices

### Data Preparation
1. **Standardize formats**: Use consistent coordinate and temporal formats
2. **Complete required fields**: Ensure all mandatory attributes are populated
3. **Validate sources**: Cross-check data from multiple sources
4. **Document data sources**: Track data provenance for quality assurance

### Validation Workflows
1. **Run early and often**: Validate data as soon as it's available
2. **Automated integration**: Include validation in CI/CD pipelines
3. **Monitor trends**: Track quality metrics over time
4. **Act on recommendations**: Address quality issues promptly

### Quality Monitoring
1. **Set quality thresholds**: Define acceptable error/warning levels
2. **Regular audits**: Schedule periodic comprehensive validations
3. **Quality gates**: Block deployment if critical quality issues found
4. **Stakeholder reporting**: Share quality status with relevant teams

## Troubleshooting

### Common Issues

#### Import Errors
```
ModuleNotFoundError: No module named 'utils.quality_validation'
```
**Solution**: Ensure you're running from the project root directory.

#### Missing Data Files
```
⚠️  Enhanced data directory not found: enhanced_data
```
**Solution**: The system will generate sample data for testing. For production, ensure enhanced data files are present.

#### Validation Failures
Multiple validation errors can indicate:
- Data quality issues that need attention
- Incorrect validation configuration
- Missing required fields in data sources

Review the detailed error messages and recommendations in the generated report.

### Getting Help

1. **Check logs**: Review console output for specific error details
2. **Examine reports**: Look at generated JSON reports for comprehensive details
3. **Run individual validators**: Test specific validators with known good data
4. **Check test suite**: Run tests to ensure system integrity

```bash
# Test specific validator
python3 -c "
from utils.quality_validation import CoordinateValidator
validator = CoordinateValidator({'south': 57.0, 'north': 58.0, 'west': -3.0, 'east': -2.0})
result = validator.validate_coordinates([{'lat': 57.5, 'lon': -2.5}])
print(f'Passed: {result.passed}')
"

# Run validation tests
python3 -m pytest tests/test_quality_validation.py::TestCoordinateValidator -v
```

This comprehensive quality validation system ensures that the Lumsden Tourist Map Generator maintains high data quality standards, supporting the project's goal of creating reliable and accurate tourist maps.