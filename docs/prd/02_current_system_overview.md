# 2. Current System Overview

## 2.1 System Description
The current system generates printable A3 tourist maps (297×420mm at 300 DPI) for the Lumsden area using:
- OpenStreetMap data acquired via Overpass API
- Enhanced local tourism data stored in SQLite
- Synthetic elevation data for hillshading and contour generation
- Mapnik for map rendering
- GDAL/OGR for geospatial data processing

## 2.2 Key Features
- High-quality printable A3 maps
- Hillshading and contour line visualization
- Enhanced tourism data including attractions, accommodations, and activities
- SVG icon system for points of interest
- Template-based styling with Mapnik XML
- Reproducible development environment with Nix

## 2.3 Technology Stack
- Python 3.12
- Mapnik rendering engine
- GDAL/OGR geospatial tools
- SQLite database
- NumPy for elevation processing
- requests for HTTP operations
- Pillow for image processing

## 2.4 Current Limitations
- Limited to single geographic area (Lumsden)
- Synthetic elevation data only (no real DEM sources)
- Command-line only interface
- No web or mobile access
- No real-time information integration
- No route planning capabilities