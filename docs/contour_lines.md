# Contour Lines Feature Documentation

## Overview

The Lumsden Tourist Map Generator now supports elevation contour lines to provide clear representation of terrain features and elevation changes. This feature enhances the map's utility for outdoor activities and tourism planning.

## Features

### Automatic Elevation Data Generation
- Synthetic elevation data based on Scottish Highland topography patterns
- 30-meter resolution elevation grid
- Realistic elevation values for the Lumsden area (50-400m)

### Contour Line Generation
- Configurable contour intervals (default: 10 meters)
- Major contour lines at 50-meter intervals with elevation labels
- Minor contour lines for detailed terrain representation
- Generated using GDAL's `gdal_contour` tool

### Styling Options
- **Default Tourist Style**: Balanced contours with brown styling
- **No Contours**: Clean map without elevation data for comparison
- **Prominent Contours**: Enhanced visibility for outdoor activities
- Fully integrated with existing map features

## Configuration

### Area Configuration
Edit `config/areas.json` to customize contour settings:

```json
{
  "lumsden": {
    "contours": {
      "enabled": true,
      "interval": 10,
      "major_interval": 50,
      "style": {
        "color": "#8B4513",
        "width": 0.5,
        "major_width": 1.0,
        "opacity": 0.7
      }
    }
  }
}
```

### Parameters
- `enabled`: Enable/disable contour generation (boolean)
- `interval`: Elevation interval for contour lines in meters (integer)
- `major_interval`: Interval for major contour lines with labels (integer)
- `style.color`: Color for contour lines (hex color)
- `style.width`: Line width for minor contours (float)
- `style.major_width`: Line width for major contours (float)
- `style.opacity`: Line opacity (0.0-1.0)

## Usage

### Basic Map Generation
```bash
python3 map_generator.py
```
Contours are automatically included if enabled in configuration.

### Style Preview Generation
```bash
python3 -m utils.style_preview_generator
```
Generates previews including contour variations for comparison.

### Disable Contours
Set `"enabled": false` in the area configuration to generate maps without contours.

## Technical Implementation

### Data Processing Pipeline
1. **Elevation Data**: Synthetic elevation grid generated using mathematical models
2. **Contour Generation**: GDAL `gdal_contour` extracts contour lines from elevation data
3. **Shapefile Output**: Contours saved as ESRI Shapefile for Mapnik rendering
4. **Styling**: Mapnik XML templates define contour appearance

### File Outputs
- `data/osm_data/elevation_data.tif`: Elevation raster data (GeoTIFF)
- `data/osm_data/contours.shp`: Contour lines shapefile
- Map renders include contour lines as additional layer

### Dependencies
- **GDAL**: `gdal_contour` for contour generation
- **Mapnik**: Rendering contour lines with map styling
- **Python**: Data processing and coordinate transformations

## Performance

### Generation Times
- Elevation data creation: ~0.5 seconds
- Contour line generation: ~0.3 seconds
- Map rendering with contours: ~1.5 seconds total

### File Sizes
- Elevation data: ~780KB (GeoTIFF)
- Contour shapefiles: ~76KB
- Final maps: Similar size to non-contour versions

## Troubleshooting

### Common Issues

**No contour lines visible**
- Check that `contours.enabled` is `true` in configuration
- Verify GDAL tools are installed: `gdal_contour --version`
- Check log output for contour generation messages

**GDAL errors**
- Ensure GDAL is properly installed: `sudo apt install gdal-bin`
- Check file permissions in data directory
- Verify elevation data was generated successfully

**Style rendering issues**
- Ensure contour shapefile exists: `ls data/osm_data/contours.*`
- Check Mapnik style includes contour layer definition
- Verify contour data has features: `ogrinfo -so data/osm_data/contours.shp`

### Debug Commands
```bash
# Check contour data
ogrinfo -so data/osm_data/contours.shp contours

# Test GDAL contour generation
gdal_contour -a elevation -i 10 elevation_data.tif test_contours.shp

# Verify elevation data
gdalinfo data/osm_data/elevation_data.tif
```

## Integration with Existing Features

### Map Layers
Contours are rendered between land use and label layers for optimal visibility:
1. Land use (background)
2. Water features
3. **Contour lines** ← New layer
4. Buildings and infrastructure
5. Roads and paths
6. Labels and points of interest

### Style Compatibility
Contour styling is designed to complement existing map features:
- Earth-tone colors that blend with natural features
- Appropriate opacity to avoid obscuring other elements
- Major/minor line differentiation for readability

### Performance Impact
- Minimal impact on rendering performance
- Optional feature that can be disabled
- Cached elevation data for repeated generation