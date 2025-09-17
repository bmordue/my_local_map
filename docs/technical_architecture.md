# Technical Architecture

## System Overview

The Lumsden Tourist Map Generator is a Python-based application that creates high-quality printable maps by combining OpenStreetMap data with custom tourist information and topographic features.

## Core Components

### 1. Data Acquisition Layer
- **OpenStreetMap Integration**: Downloads OSM data via Overpass API for the specified bounding box
- **Elevation Data Processing**: Generates synthetic elevation data for contour line creation
- **Tourist Database**: SQLite database containing enhanced tourist information

### 2. Data Processing Layer
- **Shapefile Conversion**: Uses GDAL/OGR to convert OSM data to shapefiles
- **Contour Generation**: Creates contour lines from elevation data using GDAL tools
- **Data Enhancement**: Integrates custom tourist data with OSM features

### 3. Styling Layer
- **Mapnik XML Templates**: Defines visual styling for different map features
- **Dynamic Style Generation**: Substitutes variables in templates for customization
- **Multiple Themes**: Supports different visual styles for various use cases

### 4. Rendering Layer
- **Mapnik Engine**: Renders map using Mapnik library
- **Legend Generation**: Creates map legends for improved usability
- **Output Formats**: Generates high-resolution PNG images suitable for printing

## Technology Stack

### Core Technologies
- **Python 3.12+**: Main programming language
- **Mapnik**: Map rendering engine
- **GDAL/OGR**: Geospatial data processing tools
- **SQLite**: Lightweight database for tourist information

### Dependencies
- **Requests**: HTTP library for API interactions
- **Pillow**: Python Imaging Library for image processing
- **NumPy**: Numerical computing library

### Development Tools
- **pytest**: Testing framework
- **Nix**: Dependency management and development environment

## Data Flow

```
1. Configuration → 2. OSM Data Download → 3. Shapefile Conversion → 4. Elevation Processing
                                      ↓
                        5. Style Template Processing
                                      ↓
                        6. Map Rendering → 7. Legend Addition → 8. Output File
```

## File Structure

```
my_local_map/
├── config/                 # Configuration files
│   ├── areas.json          # Geographic area definitions
│   └── output_formats.json # Output format specifications
├── data/                   # Generated data files
│   ├── osm_data/           # Shapefiles from OSM data
│   └── enhanced_data/      # Tourist database and GeoJSON files
├── docs/                   # Documentation
├── icons/                  # Map symbol icons
├── styles/                 # Mapnik XML style templates
├── utils/                  # Utility modules
│   ├── config.py           # Configuration management
│   ├── data_processing.py  # Data processing functions
│   ├── style_builder.py    # Style generation utilities
│   └── legend.py           # Legend creation utilities
├── tests/                  # Test suite
├── map_generator.py        # Main application script
└── requirements.txt        # Python dependencies
```

## Key Design Principles

### 1. No Database Architecture
- Processes data directly from shapefiles
- Eliminates database setup and maintenance complexity
- Simplifies deployment and usage

### 2. Template-Based Styling
- Uses parameterized Mapnik XML templates
- Enables easy customization of visual appearance
- Supports multiple map themes

### 3. Modular Design
- Separate components for data processing, styling, and rendering
- Clear interfaces between components
- Easy to test and maintain

### 4. Configuration-Driven
- All geographic areas and output formats defined in JSON
- Easy to add new areas or modify existing ones
- Non-programmers can customize settings