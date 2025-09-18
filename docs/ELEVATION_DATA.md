Feature Proposal: Replace Synthetic DEM with Real Elevation Data
Overview
Currently, the Lumsden Tourist Map Generator uses a synthetic Digital Elevation Model (DEM) for hillshading and topographical relief. This proposal aims to replace the synthetic DEM with real elevation data, improving map accuracy and visual quality for users planning outdoor activities.

<!-- QUESTION: What is the exact structure and sample values for the hillshading configuration in config/areas.json? -->
<!-- SUGGESTION: Provide a JSON snippet in the documentation, e.g.:
"hillshading": {
  "enabled": true,
  "opacity": 0.4,
  "azimuth": 315,
  "altitude": 45,
  "z_factor": 1.0,
  "scale": 111120
}
Reference this format in both code and docs. -->

Product Requirements Document (PRD)
1. Objective
Goal: Integrate authentic elevation data (e.g., SRTM, EU-DEM, OS Terrain 50) into the map generation workflow, replacing the synthetic DEM.
Benefit: Enhanced realism and accuracy in hillshading, providing users with a more reliable representation of Lumsden’s terrain.
2. User Stories
As a tourist, I want the map’s hillshading to reflect actual terrain so I can better plan hikes and outdoor activities.
As a local resident, I want the map to show true elevation features for improved navigation and trip planning.
As a developer, I want the map generator to fetch and process real DEM data automatically, with minimal manual intervention.
3. Functional Requirements
3.1 Data Acquisition
Source: Use open-access elevation datasets (e.g., SRTM 1 arc-second, EU-DEM, OS Terrain 50).
Download: Automatically fetch DEM tiles covering the Lumsden area if not present locally.
Offline Mode: If download fails, fallback to synthetic DEM or notify the user.

<!-- QUESTION: How is the synthetic elevation generated? Is there a script or method, or should it be random/flat? Clarify the source and format. -->
<!-- SUGGESTION: Document the synthetic DEM generation method (e.g., flat raster, random, or simple gradient). Provide a reference to the script or function in map_generator.py that creates it. -->

3.2 Data Processing
Format: Convert raw DEM (GeoTIFF) to required projection and resolution for A3 output.
Clipping: Crop DEM to the map’s bounding box (8×12 km).
Hillshade Generation: Use gdaldem hillshade with user-configurable parameters (azimuth, altitude, opacity, z-factor, scale).

<!-- QUESTION: What are the precise instructions or a template for how the hillshade raster layer should be added to tourist_map_style.xml? -->
<!-- SUGGESTION: Add a sample Mapnik XML <RasterSymbolizer> block to the documentation and code comments, showing how to include hillshade.tif as a background layer. -->

3.3 Integration
Mapnik Layer: Integrate processed hillshade raster as a background layer in Mapnik style XML.
Configuration: Allow enabling/disabling real DEM via areas.json (e.g., "dem_source": "real" or "dem_source": "synthetic").

<!-- QUESTION: What should happen if GDAL or elevation data is missing? Should the map render without hillshading, or should it fail? -->
<!-- SUGGESTION: Implement graceful fallback: if GDAL or DEM is missing, log a warning and render the map without hillshading, using only vector layers. -->

3.4 Validation
Output: Ensure osm_data/elevation.tif and osm_data/hillshade.tif are generated from real DEM.
Visual: PNG output should show realistic terrain shading.
Fallback: If DEM unavailable, revert to synthetic DEM and log a warning.

<!-- QUESTION: How does the user enable/disable hillshading? Is it only via config/areas.json, or also via command-line arguments? -->
<!-- SUGGESTION: Primary control should be via config/areas.json, but optionally allow a command-line override (e.g., --hillshading on/off) for advanced users. Document both options. -->

4. Non-Functional Requirements
Performance: Map generation time should remain under 2 minutes, including DEM download.
Reliability: Graceful error handling for network or data issues.
Storage: DEM files cached locally for future runs.

1. Success Criteria
Accuracy: Hillshading matches real terrain features of Lumsden.
Output: All validation scenarios pass; PNG visually improved.
User Feedback: Positive feedback from users on terrain realism.

1. Implementation Plan
Research DEM sources and select best-fit for Lumsden area.
Update map_generator.py to support DEM download, processing, and integration.
Modify areas.json to allow DEM source selection.
Test with real DEM and validate outputs.
Document new workflow and troubleshooting steps.
Summary:
This feature will upgrade the Lumsden Tourist Map Generator to use real elevation data, delivering more accurate and visually appealing maps for all users.