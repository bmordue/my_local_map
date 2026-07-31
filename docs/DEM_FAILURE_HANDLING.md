# DEM Data Failure Handling - Implementation Documentation

## Overview

The map generator now implements immediate failure when Digital Elevation Model (DEM) data is not present and cannot be downloaded, and when synthetic fallback is disabled in the configuration.

## Key Changes

### 1. Enhanced `download_elevation_data` Function

The function now raises a `RuntimeError` instead of silently returning `False` when:
- Real DEM data download fails from all sources
- `allow_synthetic_fallback` is set to `false` in configuration

**Previous behavior:**
```python
if not success and allow_synthetic_fallback:
    return _create_synthetic_dem_fallback(bbox, output_file, resolution)
return success  # Could return False silently
```

**New behavior:**
```python
if not success:
    if allow_synthetic_fallback:
        return _create_synthetic_dem_fallback(bbox, output_file, resolution)
    else:
        raise RuntimeError(
            f"DEM data download failed from '{dem_source}' source and synthetic fallback is disabled. "
            f"Either enable synthetic fallback or ensure network connectivity to DEM data sources."
        )
```

### 2. Exception Propagation Through Pipeline

The exception is now properly propagated through the data processing pipeline:

1. `download_elevation_data` → raises `RuntimeError`
2. `process_elevation_for_hillshading` → catches and re-raises with context
3. `process_data_pipeline` → catches and returns failure status
4. `main` → exits with error code 1

### 3. Configuration Control

Areas can now be configured to either allow or disallow synthetic fallback:

```json
{
  "elevation": {
    "source": "srtm",
    "resolution": 30,
    "allow_synthetic_fallback": false  // Fails immediately if DEM unavailable
  }
}
```

## Demonstration Areas

### Lumsden (Fallback Enabled)
- Configuration: `"allow_synthetic_fallback": true`
- Behavior: Falls back to synthetic DEM when real data unavailable
- Result: ✅ **Succeeds** with warning about synthetic data

### Balmoral Castle (Fallback Disabled)
- Configuration: `"allow_synthetic_fallback": false`
- Behavior: Fails immediately when real DEM data unavailable
- Result: ❌ **Fails** with clear error message

## Error Messages

When DEM download fails and fallback is disabled, users see:

```
❌ Failed to download real DEM data from 'srtm' source
❌ Synthetic fallback is disabled in configuration
❌ Cannot proceed without elevation data
❌ Critical DEM data failure: DEM data download failed from 'srtm' source and synthetic fallback is disabled. Either enable synthetic fallback or ensure network connectivity to DEM data sources.
```

## Testing

### Unit Tests
- `test_download_elevation_data_with_fallback_disabled`: Verifies RuntimeError is raised
- `test_download_elevation_data_with_fallback_enabled`: Verifies synthetic fallback works
- `test_process_elevation_for_hillshading_dem_failure`: Verifies exception propagation

### Integration Testing
- `test_dem_failure.py`: Comprehensive test script demonstrating both scenarios
- Real area testing: Lumsden vs Balmoral Castle behavior comparison

## Usage Scenarios

### Production Deployment
Set `"allow_synthetic_fallback": false` to ensure maps only use real elevation data:
- Prevents generation of maps with artificial elevation data
- Forces addressing of network/authentication issues
- Ensures data quality standards

### Development/Testing
Set `"allow_synthetic_fallback": true` to allow continued development:
- Works in offline environments
- Useful for CI/CD pipelines
- Enables testing without external dependencies

## Migration Guide

### For Existing Configurations
- **No change required** - default behavior maintains `allow_synthetic_fallback: true`
- Maps continue to work with synthetic fallback
- Add explicit `false` setting only when strict DEM requirements needed

### For New Deployments
- Consider setting `allow_synthetic_fallback: false` for production
- Ensure proper network connectivity to DEM sources
- Test DEM availability in target deployment environment

## Error Handling Best Practices

1. **Check configuration**: Verify `allow_synthetic_fallback` setting matches requirements
2. **Network connectivity**: Ensure access to DEM data sources (SRTM, ASTER, etc.)
3. **Authentication**: Some DEM sources require API keys or authentication
4. **Fallback strategy**: Consider hybrid approach with different settings per environment

## Benefits

1. **Predictable behavior**: No silent failures with synthetic data
2. **Data quality assurance**: Ensures maps use real elevation data when required
3. **Clear error messages**: Actionable feedback for configuration issues
4. **Flexible configuration**: Per-area control over DEM requirements
5. **Backward compatibility**: Existing configurations continue to work
