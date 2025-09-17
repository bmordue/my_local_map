# Lumsden Tourist Map Generator

A Python-based tourist map generator for Lumsden, Aberdeenshire that creates A3 printable maps using OpenStreetMap data. The application uses GDAL/OGR for data processing and Mapnik for high-quality map rendering.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Install Dependencies

**Recommended: Use Nix for environment setup**

```bash
nix-shell  # Enters reproducible environment with all dependencies
python3 map_generator.py
```

**If Nix is unavailable, use manual setup:**

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-mapnik gdal-bin python3-pip

# Install Python dependencies
pip3 install -r requirements.txt

# Verify installations
python3 -c "import mapnik; print('mapnik version:', mapnik.mapnik_version())"
ogr2ogr --version
python3 -c "import requests; print('requests OK')"
python3 -c "from PIL import Image; print('Pillow OK')"
```

### Build and Run
- **Build process**: No build step required - this is a single Python script
- **Run the application**: `python3 map_generator.py`
- **Execution time**: Takes approximately 1 second. NEVER CANCEL builds under 60 seconds.
- **Timeout recommendation**: Set 120+ seconds timeout for any test runs to account for variations

### Validation Scenarios
**CRITICAL**: After making any changes, ALWAYS run these validation steps:

1. **Syntax validation**: `python3 -m py_compile map_generator.py`
2. **Full application test**: `python3 map_generator.py`
3. **Verify output files**:
   ```bash
   ls -la lumsden_tourist_map_A3.png tourist_map_style.xml osm_data/
   file lumsden_tourist_map_A3.png  # Should show: PNG image data, 3507 x 4960
   ```
4. **Clean run test**: Remove generated files and run again:
   ```bash
   rm -f lumsden_tourist_map_A3.png tourist_map_style.xml
   rm -rf osm_data/
   python3 map_generator.py
   ```

### Testing Changes
- **Manual validation**: Always run the complete map generation process after changes
- **Expected outputs**:
  - `lumsden_tourist_map_A3.png` - 3507×4960 pixel PNG image (~79KB)
  - `tourist_map_style.xml` - Mapnik XML style definition (~5.5KB)
  - `osm_data/` directory containing 4 shapefiles (points, lines, multilinestrings, multipolygons)
- **Validation time**: Complete validation takes under 2 seconds
- **Visual verification**: Generated PNG should be a valid map image of Lumsden area

## Network Dependencies and Limitations

### OSM Data Download
- **Online mode**: Downloads fresh data from `overpass-api.de` when `lumsden_area.osm` is missing
- **Offline mode**: Uses pre-downloaded `lumsden_area.osm` file (included in repository)
- **Sandboxed environments**: External downloads will FAIL in GitHub Codespaces and similar environments
- **Workaround**: The repository includes `lumsden_area.osm` (~1MB) so the application works offline

### Network Failure Handling
If you see connection errors to `overpass-api.de`:
```bash
# Restore the pre-downloaded OSM file
git checkout HEAD -- lumsden_area.osm
```

## Repository Structure

### Key Files
```
map_generator.py     # Main application script
shell.nix           # Nix environment configuration (recommended)
lumsden_area.osm    # Pre-downloaded OpenStreetMap data (~1MB)
.gitignore          # Excludes osm_data/ and __pycache__/
```

### Generated Files (Not in Git)
```
lumsden_tourist_map_A3.png    # Final A3 map output
tourist_map_style.xml         # Mapnik style definition
osm_data/                     # Shapefile directory
  ├── points.{shp,dbf,prj,shx}
  ├── lines.{shp,dbf,prj,shx}
  ├── multilinestrings.{shp,dbf,prj,shx}
  ├── multipolygons.{shp,dbf,prj,shx}
  ├── elevation.tif           # Elevation data for hillshading
  └── hillshade.tif          # Generated hillshade raster
```

### Core Constants and Configuration
Located in `config/areas.json`:
- `LUMSDEN_LAT = 57.3167`, `LUMSDEN_LON = -2.8833` - Map center coordinates
- `MAP_SCALE = 25000` - 1:25,000 scale for tourist planning
- `BBOX_WIDTH_KM = 8`, `BBOX_HEIGHT_KM = 12` - Coverage area
- A3 output: 297×420mm at 300 DPI (3507×4960 pixels)
- **Hillshading configuration**: Enable/disable topographical relief visualization

### Hillshading Feature
The map generator now supports configurable hillshading to enhance topographical visualization:

#### Configuration
Add hillshading configuration to `config/areas.json`:
```json
"hillshading": {
  "enabled": true,        // Enable/disable hillshading
  "opacity": 0.4,        // Hillshade opacity (0.0-1.0)
  "azimuth": 315,        // Light source azimuth (0-360 degrees)
  "altitude": 45,        // Light source altitude (0-90 degrees)
  "z_factor": 1.0,       // Vertical exaggeration factor
  "scale": 111120        // Scale factor for lat/lon (meters per degree)
}
```

#### Technical Implementation
- Uses GDAL/OGR tools for elevation data processing and hillshade generation
- Synthetic elevation model for demonstration (in production, would use real DEM data)
- Hillshade rendered as background layer with configurable transparency
- Graceful fallback when elevation data unavailable

#### Dependencies
- Requires `gdaldem` tool (part of gdal-bin package)
- Elevation data processing uses GDAL raster capabilities
- Hillshade integrated as Mapnik raster layer

## Development Workflow

### Code Changes
1. **Edit**: Modify `map_generator.py`
2. **Syntax check**: `python3 -m py_compile map_generator.py`
3. **Test**: `python3 map_generator.py`
4. **Validate**: Check all output files are generated correctly

### Environment Setup (Nix recommended)
- Use `nix-shell` for a reproducible environment with all dependencies
- If Nix is unavailable, follow manual setup instructions above

### Debugging Common Issues
- **Import errors**: Ensure environment is activated (`nix-shell`) or python3-mapnik and gdal-bin are installed
- **Permission errors**: Use sudo for apt install commands
- **Network timeouts**: Use offline mode with existing lumsden_area.osm
- **Empty shapefiles**: Normal for some areas - check the OSM data coverage

## Performance Expectations

### Timing Benchmarks
- **Fresh run** (with cache): ~0.9 seconds
- **Clean run** (no cache): ~0.9 seconds  
- **OSM download** (when needed): 5-60 seconds (network dependent)
- **Total worst case**: Under 2 minutes including fresh OSM download

### File Sizes
- **Input**: lumsden_area.osm (~1MB)
- **Output PNG**: ~79KB (3507×4960 pixels)
- **Style XML**: ~5.5KB
- **Shapefiles**: ~18KB total (varies by OSM data density)

## No Testing Infrastructure
- **No unit tests**: This project has no existing test framework
- **No linting setup**: No configured Python linters (pylint, flake8, etc.)
- **No CI/CD**: No GitHub Actions workflows
- **Manual testing only**: Rely on the validation scenarios above

## Troubleshooting

### Common Error Patterns
1. **ModuleNotFoundError: No module named 'mapnik'**
   - Solution: Use `nix-shell` or `sudo apt install -y python3-mapnik`
   
2. **ogr2ogr: command not found**
   - Solution: Use `nix-shell` or `sudo apt install -y gdal-bin`
   
3. **ConnectionError: overpass-api.de**
   - Solution: Use offline mode with existing OSM file
   - Command: `git checkout HEAD -- lumsden_area.osm`

4. **Empty output image**
   - Check OSM data: `ls -la lumsden_area.osm` (should be ~1MB)
   - Verify shapefiles: `ls -la osm_data/` (should have 16 files)

### Quick Diagnostic Commands
```bash
# Check dependencies
python3 -c "import mapnik, requests; print('All OK')"
which ogr2ogr

# Check repository state
git status
ls -la *.osm *.png *.xml

# Full clean test
rm -rf osm_data/ *.png *.xml && python3 map_generator.py
```

## Map Generator Output Reference

### Expected Console Output
```
🗺️  Lightweight Lumsden Tourist Map Generator
==================================================
📍 Center: 57.3167, -2.8833
📏 Area: 8×12km
🎯 Scale: 1:25,000

📁 Using existing OSM data: lumsden_area.osm

🔄 Converting OSM data to shapefiles...
[... conversion progress ...]

🎨 Creating tourist map style...
Created tourist-focused map style: tourist_map_style.xml

🖨️  Rendering A3 map (3507×4960 pixels)...
Rendering A3 tourist map...
✓ Map rendered successfully: lumsden_tourist_map_A3.png (0.1 MB)

🎉 SUCCESS!
📄 Tourist map: lumsden_tourist_map_A3.png
📐 Print size: A3 (297×420mm at 300 DPI)
🎯 Perfect for planning day trips around Lumsden!
```

### Success Criteria
- Exit code: 0
- PNG file: Valid image, ~79KB
- No error messages or tracebacks
- All emoji indicators show ✓ symbols