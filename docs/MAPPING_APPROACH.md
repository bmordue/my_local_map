# Lumsden Tourist Map: Mapping Approach

This document describes the approach used to customize and enhance the Lumsden tourist map generator, with a focus on making the process repeatable for other mapping projects using OpenStreetMap (OSM), GDAL/OGR, and Mapnik.

## 1. Data Extraction and Preparation
- **Source:** OSM extract for the area of interest (e.g., `lumsden_area.osm`).
- **Conversion:** Use `ogr2ogr` (from GDAL) to convert OSM data to shapefiles for points, lines, multilinestrings, and multipolygons.
- **Environment:** Always use `nix-shell` with GDAL and Mapnik to ensure all dependencies are available and consistent.

## 2. Style Customization (Mapnik XML)
- **Base Style:** Start from a template Mapnik XML (e.g., `styles/tourist.xml`).
- **POI Expansion:**
  - Identify all OSM tags/features present in the data using `ogrinfo` and `ogr2ogr`.
  - Add new `<Rule>` blocks to the `poi` style for each desired feature (e.g., all `barrier=*`, `natural=peak`, `generator:*`, `man_made=mast`, `historic=*`, `memorial=*`, `artwork_type=*`, `tourism=*`, `heritage=*`, etc.).
  - Use generic or custom icons for new features as needed.
- **Labeling:**
  - Add a rule to the `poi_labels` style to label all POIs with a `name` attribute using `<TextSymbolizer>`.

## 3. Rendering
- **Mapnik Rendering:**
  - Use the enhanced style XML and shapefiles to render the map at the desired scale and extent.
  - All included POIs with a `name` will be labeled.

## 4. Validation
- **Visual Check:** Ensure all new features and labels appear as expected.
- **Repeatability:**
  - The approach is generic: after extracting OSM data and inspecting available tags, simply add or adjust style rules for any new project.
  - Use `nix-shell` for reproducible environments.

## 5. Example: Adding New POI Types
1. Inspect shapefile attributes:
   ```bash
   nix-shell -p gdal --run 'ogrinfo -so data/osm_data/points.shp points'
   ```
2. Add new rules to the Mapnik XML for any desired OSM tags.
3. Add a label rule for `[name]` if not already present.
4. Regenerate the map and validate output.

---
This workflow ensures that any OSM-based mapping project can be quickly customized to show additional features and labels, with a repeatable, environment-controlled process.
