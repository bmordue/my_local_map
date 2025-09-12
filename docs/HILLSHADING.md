# Hillshading Feature Documentation

## Overview

The Lumsden Tourist Map Generator now includes configurable hillshading to enhance topographical visualization. This feature overlays hillshade effects based on elevation data, improving the map's appearance and usability for users needing to interpret terrain.

## Configuration

Hillshading is configured per area in the `config/areas.json` file. Add a `hillshading` section to any area configuration:

```json
{
  "lumsden": {
    "center": { "lat": 57.3167, "lon": -2.8833 },
    "coverage": { "width_km": 8, "height_km": 12 },
    "scale": 25000,
    "name": "Lumsden, Aberdeenshire",
    "hillshading": {
      "enabled": true,
      "opacity": 0.4,
      "azimuth": 315,
      "altitude": 45,
      "z_factor": 1.0,
      "scale": 111120
    }
  }
}
```

### Configuration Parameters

- **enabled** (boolean): Enable or disable hillshading for this area
- **opacity** (float, 0.0-1.0): Transparency of the hillshade layer (0.4 recommended)
- **azimuth** (integer, 0-360): Light source direction in degrees (315 = northwest)
- **altitude** (integer, 0-90): Light source elevation angle (45 degrees recommended)
- **z_factor** (float): Vertical exaggeration factor (1.0 = no exaggeration)
- **scale** (integer): Scale factor for lat/lon coordinates (111120 = meters per degree)

## Technical Implementation

### Elevation Data Processing

The hillshading feature uses GDAL tools to process elevation data:

1. **Elevation Data Generation**: Creates synthetic elevation model for demonstration
2. **Hillshade Calculation**: Uses `gdaldem hillshade` to generate relief visualization
3. **Mapnik Integration**: Incorporates hillshade as background raster layer

### File Structure

When hillshading is enabled, additional files are generated:

```
data/osm_data/
├── elevation.tif    # Digital elevation model (DEM)
└── hillshade.tif   # Calculated hillshade raster
```

### Processing Pipeline

1. Calculate elevation bounding box with buffer for edge effects
2. Generate or download elevation data (currently synthetic for demo)
3. Create hillshade using GDAL algorithms
4. Integrate hillshade layer into Mapnik style template
5. Render as background layer with specified opacity

## Dependencies

### Required Tools

- **GDAL/OGR**: For elevation data processing and hillshade generation
- **gdaldem**: Command-line tool for terrain analysis (part of gdal-bin)
- **Mapnik**: For raster layer rendering with transparency

### Installation

```bash
# Ubuntu/Debian
sudo apt install gdal-bin

# Verify installation
gdaldem --help
```

## Visual Effects

### Rendering Order

Hillshading is rendered as the first (background) layer in the following order:

1. **Hillshade layer** (background relief)
2. Land use polygons (forests, farmland, etc.)
3. Water features
4. Buildings and infrastructure
5. Roads and paths
6. Points of interest
7. Labels and text

### Styling Properties

- **Blend mode**: Multiply (darkens underlying features)
- **Scaling**: Bilinear interpolation for smooth appearance
- **Transparency**: Configurable opacity to avoid obscuring map features

## Production Considerations

### Real Elevation Data

For production use, replace the synthetic elevation generation with real DEM sources:

- **SRTM**: Global 30m/90m resolution elevation data
- **ASTER GDEM**: Global 30m resolution digital elevation model
- **Local DEMs**: Higher resolution data from national mapping agencies
- **OpenTopography**: Academic access to high-resolution elevation data

### Performance Optimization

- Cache elevation data locally to avoid repeated downloads
- Pre-process hillshades for common map areas
- Use appropriate resolution for target map scale
- Consider tiled processing for large areas

### Data Sources Integration

```python
def download_elevation_data(bbox, output_file):
    """
    Production implementation would integrate with:
    - NASA SRTM via USGS Earth Explorer
    - ASTER GDEM via NASA Earthdata
    - National elevation APIs
    - OpenTopography web services
    """
    pass
```

## Error Handling

The hillshading feature includes graceful fallback behavior:

- **Elevation data unavailable**: Map renders without hillshading
- **GDAL tools missing**: Warning message, continues without hillshading
- **Processing failures**: Detailed error messages, fallback to flat rendering

## Examples

### Default Configuration (Recommended)

```json
"hillshading": {
  "enabled": true,
  "opacity": 0.4,
  "azimuth": 315,
  "altitude": 45,
  "z_factor": 1.0,
  "scale": 111120
}
```

### High Contrast Relief

```json
"hillshading": {
  "enabled": true,
  "opacity": 0.6,
  "azimuth": 270,
  "altitude": 30,
  "z_factor": 2.0,
  "scale": 111120
}
```

### Subtle Background Relief

```json
"hillshading": {
  "enabled": true,
  "opacity": 0.2,
  "azimuth": 315,
  "altitude": 60,
  "z_factor": 0.5,
  "scale": 111120
}
```

## Testing

The hillshading feature includes comprehensive test coverage:

- Unit tests for elevation processing functions
- Integration tests for style generation
- Configuration validation tests
- Error handling and fallback tests

Run tests:

```bash
python3 -m pytest tests/test_elevation_processing.py -v
```

## Future Enhancements

Potential improvements for production deployment:

- **Contour lines**: Add elevation contours as vector layers
- **Terrain analysis**: Slope, aspect, and terrain ruggedness indices
- **Multi-resolution**: Adaptive detail based on map scale
- **Real-time data**: Integration with live elevation services
- **User customization**: Runtime configuration of hillshade parameters