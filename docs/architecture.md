# My Local Map - Comprehensive Documentation

## Overview

The "My Local Map" project is a Python-based system for generating high-quality, printable tourist maps for the Lumsden area of Aberdeenshire, Scotland. The system uses OpenStreetMap data combined with enhanced local tourism information to produce detailed A3 maps suitable for printing.

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
External APIs → Data Processing → Map Styling → Map Rendering → PNG Output
```

### Core Components

1. **Data Acquisition Layer**
   - Downloads OpenStreetMap data via Overpass API
   - Processes elevation data for hillshading and contour generation
   - Integrates enhanced tourism data from local database

2. **Data Processing Layer**
   - Converts OSM data to shapefiles using GDAL/OGR
   - Generates elevation data and hillshading
   - Creates contour lines from elevation data

3. **Styling Layer**
   - Template-based Mapnik XML style generation
   - Configurable styling with hillshading and contour support
   - Icon-based point of interest rendering

4. **Rendering Layer**
   - Mapnik-based map rendering
   - Legend generation and overlay
   - PNG output with specified dimensions

5. **Configuration Layer**
   - Geographic area configuration
   - Output format specifications
   - Feature enablement settings

## Technology Stack

### Core Technologies
- **Python 3.12+**: Main programming language
- **Mapnik**: Map rendering engine
- **GDAL/OGR**: Geospatial data processing and conversion
- **SQLite**: Enhanced tourism data storage
- **NumPy**: Elevation data processing

### Key Libraries
- **requests**: HTTP requests for OSM data download
- **Pillow**: Image processing for legend overlay
- **cairosvg**: SVG to PNG conversion for icons

### System Dependencies
- **GDAL/OGR tools**: Command-line geospatial data conversion
- **Mapnik rendering library**: High-quality map rendering

## Data Flow

1. **Configuration Loading**
   - Load area configuration (`config/areas.json`)
   - Load output format specifications (`config/output_formats.json`)

2. **Data Acquisition**
   - Download OSM data using Overpass API query
   - Generate synthetic elevation data (fallback when external DEM sources unavailable)
   - Load enhanced tourism data from SQLite database

3. **Data Processing**
   - Convert OSM data to shapefiles using `ogr2ogr`
   - Generate hillshade using `gdaldem hillshade`
   - Create contour lines using `gdal_contour`

4. **Map Styling**
   - Process Mapnik XML template with data paths and configuration
   - Enable/disable hillshading and contour layers based on configuration
   - Configure styling parameters (colors, widths, opacities)

5. **Map Rendering**
   - Load styled map in Mapnik
   - Set bounding box and projection transformation
   - Render to high-resolution PNG

6. **Post-Processing**
   - Generate and overlay map legend
   - Save final map as PNG with specified dimensions

## File Structure

```
/home/ben/Projects/mine/my_local_map/
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
├── lumsden_area.osm        # Source OSM data
├── map_generator.py        # Main map generation script
├── requirements.txt        # Python dependencies
├── shell.nix               # Nix development environment
└── README.md               # Project documentation
```

## Key Modules

### `map_generator.py` (Main Module)
The primary entry point that orchestrates the entire map generation process:
- Loads configuration
- Downloads and processes OSM data
- Generates elevation data and hillshading
- Creates Mapnik style
- Renders map to PNG
- Adds legend overlay

### `utils/config.py`
Handles configuration loading:
- Area configuration (center, coverage, scale)
- Output format specifications (A3, preview)
- Feature configurations (hillshading, contours)

### `utils/data_processing.py`
Manages OSM data processing:
- Bounding box calculation
- OSM data download from Overpass API
- OSM to shapefile conversion using OGR
- Elevation data generation
- Contour line generation

### `utils/elevation_processing.py`
Handles elevation data and hillshading:
- Synthetic elevation data generation
- Hillshade generation using GDAL
- Contour line generation

### `utils/style_builder.py`
Generates Mapnik XML styles:
- Template-based style generation
- Variable substitution for data paths
- Conditional layer inclusion based on data availability

### `utils/legend.py`
Creates map legends:
- Legend item definitions based on style
- Legend rendering and overlay onto map image

### `utils/create_enhanced_data.py`
Manages enhanced tourism data:
- SQLite database creation with tourism information
- Export to GeoJSON for mapping

## Map Styling System

The styling system uses Mapnik XML templates with variable substitution:

### Style Categories
1. **Land Use**: Forests, farmland, parks, nature reserves
2. **Water Features**: Rivers, streams, lakes, canals
3. **Transportation**: Roads (classified by type), paths, trails
4. **Buildings**: General building footprints
5. **Points of Interest**: Icons for various amenities
6. **Place Labels**: Hierarchical text for settlements
7. **Contour Lines**: Elevation representation
8. **Hillshading**: Topographic relief visualization

### Icon System
The system uses SVG icons for point features:
- Restaurants, accommodations, attractions
- Shops, services, transportation
- Natural features, emergency services

### Layer Ordering
1. Hillshade (background)
2. Contour lines
3. Land use and water features
4. Buildings
5. Roads (major to minor)
6. Paths and trails
7. Points of interest
8. Text labels (topmost)

## Configuration System

### Areas Configuration (`config/areas.json`)
Defines geographic parameters:
- Center coordinates
- Coverage area (width/height in km)
- Map scale
- Contour settings (interval, styling)
- Hillshading configuration (azimuth, altitude, opacity)
- Elevation data source

### Output Formats (`config/output_formats.json`)
Specifies output dimensions:
- A3 format (297×420mm at 300 DPI)
- Preview format (smaller for testing)

## Data Sources

### Primary Sources
1. **OpenStreetMap**: Base geographic data via Overpass API
2. **Enhanced Tourism Database**: Local tourism information
3. **Synthetic Elevation Data**: Topographic representation (fallback)

### Enhanced Data Categories
- Tourist attractions with ratings and details
- Accommodation options with amenities
- Dining venues with cuisine types
- Activities with booking requirements
- Walking trails with distances and waymarking

## Output Specifications

### Map Output
- **Format**: PNG image
- **Resolution**: 3507×4960 pixels (A3 at 300 DPI)
- **Print Size**: 297×420mm (standard A3)
- **Color Space**: RGBA with transparency support

### Style Output
- **Format**: Mapnik XML
- **Features**: 25+ style categories with 100+ individual rules
- **Customization**: Template-based with variable substitution

## Development Environment

The project provides a `shell.nix` file for reproducible development environments using Nix:
- Python 3.12 with required packages
- GDAL/OGR tools
- Mapnik rendering library
- All Python dependencies pre-installed

## Testing

The project includes pytest-based testing infrastructure:
- Unit tests for utility functions
- Integration tests for data processing
- Coverage reporting capabilities

This documentation provides a comprehensive overview of the My Local Map system, covering its architecture, components, data flow, and technology stack. The modular design allows for easy extension and customization for different geographic areas and mapping requirements.