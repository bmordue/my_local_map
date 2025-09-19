# Data Flow

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