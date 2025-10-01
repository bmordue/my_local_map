# My Local Map - Tourist Map Generator

A Python-based tourist map generator that creates high-quality A3 printable maps for multiple areas across Aberdeenshire using OpenStreetMap data. The application uses GDAL/OGR for data processing and Mapnik for rendering, with extensive testing infrastructure and CI/CD workflows.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Project Overview

### Supported Geographic Areas
The application supports **11 geographic areas** in Aberdeenshire, configured in `config/areas.json`:
- Lumsden, Balmoral Castle, Crathes Castle, Dunnottar Castle
- Cairngorms National Park, Fraserburgh, Peterhead, Huntly  
- Stonehaven, Lochnagar, Ythan Estuary

### Key Features
- **Multi-area support**: Generate maps for any configured area
- **High-quality output**: A3 printable maps (3507×4960 pixels at 300 DPI)
- **Advanced styling**: 25+ feature categories with comprehensive visual design
- **Hillshading & contours**: Topographical visualization with configurable parameters
- **Enhanced tourism data**: Local attractions, accommodations, dining, activities
- **Robust testing**: Comprehensive test suite with CI/CD automation
- **Quality validation**: Data validation system with configurable rules

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
sudo apt install -y python3-mapnik gdal-bin python3-pip libmapnik-dev mapnik-utils

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install -r requirements-test.txt  # For testing

# Verify installations
python3 -c "import mapnik; print('mapnik version:', mapnik.mapnik_version())"
ogr2ogr --version
python3 -c "import requests; print('requests OK')"
python3 -c "from PIL import Image; print('Pillow OK')"
python3 -c "import pytest; print('pytest available')"
```

### Build and Run
- **Build process**: No build step required - this is a Python application with modules
- **Run for specific area**: `python3 map_generator.py lumsden`
- **Run with default area**: `python3 map_generator.py` (uses Lumsden)
- **Run with verbose logging**: `python3 map_generator.py lumsden -v` or `python3 map_generator.py lumsden --verbose`
- **Available areas**: lumsden, balmoral_castle, crathes_castle, dunnottar_castle, cairngorms_national_park, fraserburgh, peterhead, huntly, stonehaven, lochnagar, ythan_estuary
- **Execution time**: Takes approximately 1-2 seconds per area. NEVER CANCEL builds under 60 seconds.
- **Timeout recommendation**: Set 120+ seconds timeout for any test runs to account for variations

### Logging Framework
**IMPORTANT**: This project uses Python's standard logging framework, not print() statements.

#### Using Logging in Code
```python
import logging

# Get logger for your module
logger = logging.getLogger(__name__)

# Log at different levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for potential issues")
logger.error("Error messages for failures")

# The logging system automatically handles emoji formatting
logger.info("🗺️ Map generation started")  # Emoji preserved
logger.error("Failed to process data")  # Automatically gets ❌ emoji
logger.warning("Data quality is low")  # Automatically gets ⚠️ emoji
```

#### Logging Best Practices
- **NEVER use print()** - Always use logging instead
- **Use appropriate log levels**: DEBUG for detailed info, INFO for normal messages, WARNING for potential issues, ERROR for failures
- **Get module logger**: Always use `logger = logging.getLogger(__name__)` at module level
- **Preserve emoji style**: Continue using emoji in messages for better readability (e.g., "🗺️", "✓", "📍")
- **Verbose mode**: Use the `-v` flag for debug-level logging during development
- **Structured messages**: Keep messages clear and actionable

#### Logging Configuration
The logging framework is configured in `utils/logging_config.py` and provides:
- Colored console output with emoji support
- Configurable log levels (INFO, DEBUG, WARNING, ERROR)
- Custom formatter that preserves existing emoji style
- Verbose mode via command-line flag (`-v` or `--verbose`)

#### Examples
```bash
# Normal output (INFO level)
python3 map_generator.py lumsden

# Verbose output (DEBUG level)
python3 map_generator.py lumsden -v

# Run utility scripts with proper logging
python3 utils/system_validation.py
```

### Testing and Quality Assurance
**CRITICAL**: This project has comprehensive testing infrastructure. ALWAYS run tests after changes:

1. **Run all tests**: `python3 -m pytest tests/ -v`
2. **Run with coverage**: `python3 -m pytest tests/ --cov=. --cov-report=term-missing`
3. **Run specific test**: `python3 -m pytest tests/test_integration.py -v`
4. **Quality validation**: `python3 utils/run_quality_validation.py`
5. **System validation**: `python3 utils/system_validation.py`

### Linting and Code Quality
The project uses automated linting with CI/CD integration:

1. **Format code**: `black .`
2. **Sort imports**: `isort .`
3. **Check formatting**: `black --check --diff .`
4. **Run linter**: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`

### Validation Scenarios
**CRITICAL**: After making any changes, ALWAYS run these validation steps:

1. **Syntax validation**: `python3 -m py_compile map_generator.py`
2. **Run tests**: `python3 -m pytest tests/ -v`
3. **Full application test**: `python3 map_generator.py lumsden`
4. **Verify output files**:
   ```bash
   ls -la lumsden_tourist_map_A3.png tourist_map_style.xml osm_data/
   file lumsden_tourist_map_A3.png  # Should show: PNG image data, 3507 x 4960
   ```
5. **Clean run test**: Remove generated files and run again:
   ```bash
   rm -f *_tourist_map_A3.png tourist_map_style.xml
   rm -rf osm_data/
   python3 map_generator.py --area lumsden
   ```

### Testing Changes
- **Automated testing**: Run `python3 -m pytest tests/` for comprehensive test coverage
- **Manual validation**: Always run the complete map generation process after changes
- **Expected outputs**:
  - `{area}_tourist_map_A3.png` - 3507×4960 pixel PNG image (~79KB)
  - `tourist_map_style.xml` - Mapnik XML style definition (~5.5KB)
  - `osm_data/` directory containing 4+ shapefiles and elevation data
- **Validation time**: Complete validation takes under 5 seconds
- **Visual verification**: Generated PNG should be a valid map image of specified area

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
map_generator.py          # Main application script with area support
shell.nix                # Nix environment configuration (recommended)  
lumsden_area.osm         # Pre-downloaded OpenStreetMap data (~6MB)
pyproject.toml           # Python project configuration
requirements.txt         # Core Python dependencies
requirements-test.txt    # Testing dependencies
.github/workflows/       # CI/CD automation
```

### Modular Architecture
```
utils/                   # Utility modules (NEW modular structure)
├── config.py           # Configuration management
├── data_processing.py  # OSM data conversion and processing
├── elevation_processing.py  # Elevation data and hillshading
├── style_builder.py    # Mapnik style generation
├── legend.py           # Legend generation
└── create_enhanced_data.py  # Tourism database creation

config/                 # Configuration files
├── areas.json          # 11 geographic area configurations  
└── output_formats.json # Output format specifications (A3, preview)

tests/                  # Comprehensive test suite (14 test files)
├── test_integration.py # Full workflow integration tests
├── test_config.py      # Configuration validation tests
├── test_data_processing.py # Data processing tests
└── ... (11 more test files)
```

### Generated Files (Not in Git)
```
{area}_tourist_map_A3.png     # Final A3 map output for specified area
tourist_map_style.xml         # Mapnik style definition
osm_data/                     # Shapefile directory
  ├── points.{shp,dbf,prj,shx}
  ├── lines.{shp,dbf,prj,shx}
  ├── multilinestrings.{shp,dbf,prj,shx}
  ├── multipolygons.{shp,dbf,prj,shx}
  ├── elevation.tif           # Elevation data for hillshading
  └── hillshade.tif          # Generated hillshade raster
enhanced_data/                # Tourism data (when enabled)
  ├── lumsden_tourist.db      # SQLite database
  └── *.geojson              # Various tourism datasets
```

### Core Configuration
Located in `config/areas.json` with 11+ areas:
- **Center coordinates**: Lat/Lon for each geographic area
- **Coverage area**: Width/height in kilometers per area
- **Map scale**: Typically 1:25,000 for tourist planning (1:50,000 for large areas)
- **A3 output**: 297×420mm at 300 DPI (3507×4960 pixels)
- **Hillshading configuration**: Per-area enable/disable with visual parameters
- **Contour settings**: Interval and styling for topographic features
- **Data sources**: OSM file paths and elevation sources

### Hillshading Feature
The map generator supports configurable hillshading to enhance topographical visualization:

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

### Making Code Changes
1. **Edit**: Modify relevant Python files (`map_generator.py`, `utils/*.py`)
2. **Syntax check**: `python3 -m py_compile {filename}`
3. **Run tests**: `python3 -m pytest tests/test_{relevant}.py -v`
4. **Lint code**: `black . && isort . && flake8 .`
5. **Test**: `python3 map_generator.py lumsden`
6. **Validate**: Check all output files are generated correctly

### Environment Setup (Nix recommended)
- Use `nix-shell` for a reproducible environment with all dependencies
- If Nix is unavailable, follow manual setup instructions above
- **Always activate environment before development work**

### CI/CD Integration
The project has automated GitHub Actions workflows:
- **Test workflow** (`.github/workflows/test.yml`): Runs on all PRs and pushes
  - Multi-Python version testing (3.12)
  - Full test suite with coverage reporting
  - Linting with black, isort, flake8
  - System dependency installation (mapnik, GDAL)
- **Map generation workflow**: Generates sample maps on PRs

### Adding New Geographic Areas
1. **Edit** `config/areas.json` with new area configuration:
   ```json
   "new_area": {
     "center": {"lat": XX.XXXX, "lon": -X.XXXX},
     "coverage": {"width_km": 8, "height_km": 12},
     "scale": 25000,
     "name": "New Area, Aberdeenshire",
     "osm_file": "data/new_area.osm",
     "contours": {"enabled": false, ...},
     "hillshading": {"enabled": true, ...}
   }
   ```
2. **Test**: `python3 map_generator.py new_area`
3. **Add tests**: Update `tests/test_config.py` with new area validation

### Debugging Common Issues
- **Import errors**: Ensure environment is activated (`nix-shell`) or dependencies installed
- **Permission errors**: Use sudo for apt install commands
- **Network timeouts**: Use offline mode with existing OSM files
- **Empty shapefiles**: Normal for some areas - check the OSM data coverage
- **Test failures**: Run individual test files to isolate issues
- **Linting errors**: Use `black .` and `isort .` to auto-format code

## Performance Expectations

### Timing Benchmarks
- **Fresh run** (with cache): ~1-2 seconds per area
- **Clean run** (no cache): ~1-2 seconds per area  
- **OSM download** (when needed): 5-60 seconds (network dependent)
- **Full test suite**: ~10-30 seconds depending on system
- **Total worst case**: Under 2 minutes including fresh OSM download

### File Sizes
- **Input**: lumsden_area.osm (~6MB, contains multiple areas)
- **Output PNG**: ~79KB (3507×4960 pixels) per area
- **Style XML**: ~5.5KB (shared across areas)
- **Shapefiles**: ~18-50KB total (varies by OSM data density per area)
- **Test artifacts**: Minimal, cleaned automatically

## Testing Infrastructure

**IMPORTANT**: This project has comprehensive testing, unlike earlier versions.

### Test Categories
- **Unit tests**: Individual function and module testing (`test_*.py`)
- **Integration tests**: Full workflow testing (`test_integration.py`)
- **Configuration tests**: Area and format validation (`test_config.py`)
- **Quality validation**: Data validation system (`test_quality_validation.py`)

### Running Tests
- **All tests**: `python3 -m pytest tests/ -v`
- **Specific category**: `python3 -m pytest tests/test_integration.py -v`
- **With coverage**: `python3 -m pytest tests/ --cov=. --cov-report=term-missing`
- **Failed tests only**: `python3 -m pytest tests/ --lf`

### Test Configuration
- **pytest configuration**: `pyproject.toml` (markers, coverage settings)
- **Test requirements**: `requirements-test.txt`
- **CI integration**: `.github/workflows/test.yml`

## Troubleshooting

### Common Error Patterns
1. **ModuleNotFoundError: No module named 'mapnik'**
   - Solution: Use `nix-shell` or `sudo apt install -y python3-mapnik libmapnik-dev`
   
2. **ogr2ogr: command not found**
   - Solution: Use `nix-shell` or `sudo apt install -y gdal-bin`
   
3. **ConnectionError: overpass-api.de**
   - Solution: Use offline mode with existing OSM file
   - Command: `git checkout HEAD -- lumsden_area.osm`

4. **Empty output image**
   - Check OSM data: `ls -la lumsden_area.osm` (should be ~6MB)
   - Verify shapefiles: `ls -la osm_data/` (should have 16+ files)
   - Try different area: `python3 map_generator.py stonehaven`

5. **Test failures**
   - Run individual test: `python3 -m pytest tests/test_integration.py -v -s`
   - Check dependencies: `python3 -c "import mapnik, requests, pytest; print('All OK')"`
   - Clean test environment: `rm -rf osm_data/ *.png *.xml`

6. **Linting errors**
   - Auto-format: `black .`
   - Fix imports: `isort .`
   - Check syntax: `flake8 . --select=E9,F63,F7,F82`

### Quick Diagnostic Commands
```bash
# Check dependencies
python3 -c "import mapnik, requests, pytest; print('All OK')"
which ogr2ogr

# Check repository state
git status
ls -la *.osm *.png *.xml

# List available areas
python3 -c "import json; areas = json.load(open('config/areas.json')); print('Available areas:', ', '.join(areas.keys()))"

# Full clean test with specific area
rm -rf osm_data/ *.png *.xml && python3 map_generator.py lumsden

# Run quick test suite
python3 -m pytest tests/test_config.py -v
```

### GitHub Actions Troubleshooting
- **Workflow failures**: Check `.github/workflows/test.yml` for dependency issues
- **Coverage issues**: Tests may pass locally but fail in CI due to missing dependencies
- **Timeout issues**: Increase timeout in workflow if map generation takes longer than expected

## Map Generator Output Reference

### Expected Console Output (Updated)
```
🗺️  My Local Map Generator - Multi-Area Support
==================================================
📍 Area: Lumsden, Aberdeenshire (57.3167, -2.8833)
📏 Coverage: 8×12km
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
- Tests pass: `python3 -m pytest tests/ -v` (exit code 0)
- Linting passes: `black --check .` and `flake8 .` (exit code 0)

### Command Line Options
```bash
python3 map_generator.py --help           # Show all options
python3 map_generator.py lumsden          # Generate map for specific area
python3 map_generator.py                  # Default to Lumsden area

# List available areas with Python
python3 -c "import json; areas = json.load(open('config/areas.json')); print('Available areas:', ', '.join(areas.keys()))"
```

## Best Practices for Contributors

### Before Making Changes
1. **Read documentation**: Check `docs/` directory for architectural details
2. **Run tests**: `python3 -m pytest tests/ -v` to ensure starting point is clean
3. **Check code quality**: `black --check .` and `flake8 .`
4. **Understand area configuration**: Review `config/areas.json` structure

### During Development
1. **Write tests first**: Add test cases for new functionality
2. **Test multiple areas**: Don't just test with Lumsden
3. **Follow code style**: Use `black .` and `isort .` for formatting
4. **Validate configurations**: Ensure changes work with all 12+ areas

### Before Submitting Changes
1. **Full test suite**: `python3 -m pytest tests/ --cov=. --cov-report=term-missing`
2. **Multiple area validation**: Test with different geographic areas
3. **Clean run test**: Remove all generated files and run fresh
4. **CI check**: Ensure GitHub Actions will pass (similar environment to CI)

<tool_calling>
You have the capability to call multiple tools in a single response. For maximum efficiency, whenever you need to perform multiple independent operations, ALWAYS invoke all relevant tools simultaneously rather than sequentially. Especially when exploring repository, reading files, viewing directories, validating changes or replying to comments.
</tool_calling>