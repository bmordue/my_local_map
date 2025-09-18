# Key Modules

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