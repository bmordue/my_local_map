# My Local Map - Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the My Local Map codebase, including technical debt, workarounds, and real-world patterns. It serves as a reference for AI agents working on enhancements to this Python-based system for generating high-quality, printable tourist maps for the Lumsden area of Aberdeenshire, Scotland.

### Document Scope

Focused on areas relevant to: Enhancing the Lumsden Tourist Map Generator by fixing failing tests, improving elevation data integration, and expanding map content to create a comprehensive tourist information resource.

### Change Log

| Date   | Version | Description                 | Author    |
| ------ | ------- | --------------------------- | --------- |
| 2025-09-19 | 1.0     | Initial brownfield analysis | Winston (Architect) |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

- **Main Entry**: `map_generator.py`
- **Configuration**: `config/areas.json`, `config/output_formats.json`
- **Core Business Logic**: `utils/elevation_processing.py`, `utils/data_processing.py`, `utils/style_builder.py`
- **Data Models**: SQLite database in `data/lumsden_tourist.db`, GeoJSON exports in `data/`
- **Key Algorithms**: Elevation processing in `utils/elevation_processing.py`

### Enhancement Impact Areas

Based on the PRD and recent work, these files will be affected by future enhancements:
- `utils/elevation_processing.py` - Enhanced with real DEM sources
- `config/areas.json` - Will support multiple geographic areas
- `map_generator.py` - Will need to support area selection
- Various files in `styles/` - Will need updates for new features

## High Level Architecture

### Technical Summary

The My Local Map project is a Python-based system for generating printable A3 tourist maps using OpenStreetMap data enhanced with local tourism information. It currently covers an 8×12km area around Lumsden with over 25 map feature categories.

### Actual Tech Stack (from requirements.txt and shell.nix)

| Category  | Technology | Version | Notes                      |
| --------- | ---------- | ------- | -------------------------- |
| Runtime   | Python    | 3.12+   | Main programming language  |
| Framework | Mapnik    | -       | Map rendering engine       |
| Libraries | GDAL/OGR  | -       | Geospatial data processing |
| Database  | SQLite    | -       | Enhanced tourism data      |
| Libraries | NumPy     | -       | Elevation data processing  |
| Libraries | Requests  | -       | HTTP requests for OSM data |
| Libraries | Pillow    | -       | Image processing           |

### Repository Structure Reality Check

- Type: Simple repository (not monorepo)
- Package Manager: pip
- Notable: Configuration-driven approach with JSON files

## Source Tree and Module Organization

### Project Structure (Actual)

```text
my_local_map/
├── config/
│   ├── areas.json          # Geographic area configurations
│   └── output_formats.json # Output format specifications
├── data/                   # Generated data (git-ignored)
├── icons/                  # SVG icons for POIs
├── styles/                 # Mapnik XML style templates
├── utils/                  # Utility modules
│   ├── config.py           # Configuration management
│   ├── data_processing.py  # OSM data conversion and processing
│   ├── elevation_processing.py  # Elevation data and hillshading
│   ├── style_builder.py    # Mapnik style generation
│   ├── legend.py           # Legend generation
│   └── create_enhanced_data.py  # Tourism database creation
├── tests/                  # Test suite
├── lumsden_area.osm        # Source OSM data
├── map_generator.py        # Main map generation script
├── requirements.txt        # Python dependencies
├── shell.nix               # Nix development environment
└── README.md               # Project documentation
```

### Key Modules and Their Purpose

- **Map Generator**: `map_generator.py` - Main orchestration script that coordinates the entire map generation process
- **Configuration Management**: `utils/config.py` - Handles loading of area and output format configurations
- **Data Processing**: `utils/data_processing.py` - Manages OSM data processing including conversion to shapefiles
- **Elevation Processing**: `utils/elevation_processing.py` - Handles elevation data generation, hillshading and contours (recently enhanced)
- **Style Building**: `utils/style_builder.py` - Generates Mapnik XML styles from templates
- **Legend Generation**: `utils/legend.py` - Creates and overlays map legends
- **Enhanced Data Creation**: `utils/create_enhanced_data.py` - Manages tourism database and exports

## Data Models and APIs

### Data Models

Instead of duplicating, reference actual model files:

- **Tourism Database**: See `data/lumsden_tourist.db` (SQLite database)
- **GeoJSON Exports**: See `data/*.geojson` files
- **Configuration Models**: See `config/areas.json` and `config/output_formats.json`

### API Specifications

- **OpenStreetMap API**: Overpass API used for data download
- **No formal API specifications** - Direct integration with external services

## Technical Debt and Known Issues

### Critical Technical Debt

1. **Synthetic Elevation Data**: Currently using synthetic elevation data generation as a fallback instead of real DEM sources
2. **Limited Geographic Coverage**: Only supports a single geographic area (Lumsden)
3. **Configuration Limitations**: Hard-coded paths and limited configuration options
4. **Testing Gaps**: Recent fixes to failing tests indicate potential testing gaps in other areas

### Workarounds and Gotchas

- **Hillshading Disabled by Default**: In `config/areas.json`, hillshading is disabled by default but can be enabled
- **GDAL Dependency**: System requires GDAL/OGR tools to be installed for geospatial operations
- **Nix Shell Environment**: Development environment is managed through Nix for consistency
- **Subprocess Testing**: Recent test fixes required adding a `force_subprocess` parameter to properly test subprocess paths

## Integration Points and External Dependencies

### External Services

| Service  | Purpose  | Integration Type | Key Files                      |
| -------- | -------- | ---------------- | ------------------------------ |
| OpenStreetMap | Base geographic data | Overpass API | `utils/data_processing.py` |
| GDAL/OGR | Geospatial processing | Command-line tools | `utils/elevation_processing.py`, `utils/data_processing.py` |
| Mapnik | Map rendering | Python library | `map_generator.py` |

### Internal Integration Points

- **Configuration Loading**: JSON files loaded by `utils/config.py`
- **Data Flow**: OSM data → Shapefiles → Mapnik styling → PNG rendering
- **Legend Integration**: Legend overlay added to final PNG in `utils/legend.py`

## Development and Deployment

### Local Development Setup

1. Use nix-shell for consistent environment: `nix-shell`
2. Or manually install dependencies:
   - System dependencies: `sudo apt-get install gdal-bin python3-mapnik`
   - Python dependencies: `pip3 install -r requirements.txt`
3. Run the generator: `python3 map_generator.py`

### Build and Deployment Process

- **Build Command**: No specific build process, directly runnable
- **Deployment**: Copy files to target system with dependencies installed
- **Environments**: Development and production use same setup

## Testing Reality

### Current Test Coverage

- Unit Tests: 80 tests covering various functionality (pytest)
- Integration Tests: Limited, primarily in `tests/test_elevation_processing.py`
- E2E Tests: None beyond the main script execution

### Running Tests

```bash
pytest           # Runs all tests
pytest tests/test_elevation_processing.py  # Runs specific test file
```

Recent fixes addressed two failing tests in `test_elevation_processing.py`:
1. `test_download_elevation_data_failure` - ensuring function returns False when subprocess fails
2. `test_download_elevation_data_success` - ensuring subprocess is called when expected

## Enhancement Impact Analysis

Based on the PRD and recent work, future enhancements will affect:

### Files That Will Need Modification

- `map_generator.py` - Add support for area selection
- `config/areas.json` - Support multiple geographic areas
- `utils/elevation_processing.py` - Integrate real DEM sources like SRTM
- `styles/` - Update for new content categories
- `utils/data_processing.py` - Handle new data sources

### New Files/Modules Needed

- Additional configuration files for new areas
- New style templates for enhanced features
- Potentially new utility modules for new data sources

### Integration Considerations

- Will need to maintain backward compatibility with existing Lumsden configuration
- Must follow existing configuration-driven approach
- Should maintain the modular architecture pattern

## Appendix - Useful Commands and Scripts

### Frequently Used Commands

```bash
nix-shell        # Start development environment
python3 map_generator.py  # Generate map
pytest           # Run tests
pytest tests/test_elevation_processing.py  # Run specific tests
```

### Debugging and Troubleshooting

- **Logs**: Check console output for processing information
- **Debug Mode**: No specific debug mode, but verbose output during processing
- **Common Issues**: 
  - GDAL/OGR tools not installed
  - Missing Python dependencies
  - Incorrect configuration in JSON files