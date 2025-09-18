# Architecture

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