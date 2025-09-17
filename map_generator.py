#!/usr/bin/env python3
"""
Lightweight A3 Tourist Map Generator for Lumsden, Aberdeenshire
Uses configuration-driven approach for maximum flexibility
"""

import os
from pathlib import Path
from utils.config import load_area_config, load_output_format, calculate_pixel_dimensions
from utils.style_builder import build_mapnik_style
from utils.data_processing import calculate_bbox, download_osm_data, convert_osm_to_shapefiles, process_elevation_and_contours
from utils.legend import MapLegend, add_legend_to_image
from utils.elevation_processing import process_elevation_for_hillshading
#from utils.download_icons import download_icons # not needed - icons are already present

# Configuration will be loaded dynamically

def create_mapnik_style(data_dir, area_config, hillshade_available=False):
    """Create a tourist-focused Mapnik XML style using template"""
    style_file = build_mapnik_style("tourist", data_dir, area_config, hillshade_available)
    print(f"Created tourist-focused map style: {style_file}")
    return style_file

def render_map(style_file, bbox, output_file, width_px, height_px):
    """Render the map using Mapnik"""
    try:
        import mapnik
    except ImportError:
        print("Error: python-mapnik not available. Install with: pip install mapnik")
        return False
    
    print("Rendering A3 tourist map...")
    
    # Create map
    m = mapnik.Map(width_px, height_px)
    mapnik.load_map(m, style_file)
    
    # Set bounding box
    # The bounding box from the script is in WGS84 (lat/lon)
    bbox_wgs84 = mapnik.Box2d(bbox['west'], bbox['south'], bbox['east'], bbox['north'])
    
    # The map projection is Mercator, so we need to transform the bbox
    proj_wgs84 = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    proj_merc = mapnik.Projection(m.srs)
    transform = mapnik.ProjTransform(proj_wgs84, proj_merc)
    
    bbox_merc = transform.forward(bbox_wgs84)
    m.zoom_to_box(bbox_merc)
    
    # Render base map
    mapnik.render_to_file(m, output_file, 'png')
    
    # Create and add legend
    print("Adding map legend...")
    legend = MapLegend()
    legend_data = legend.render_to_map(m)
    
    # Add legend overlay to the image
    if add_legend_to_image(output_file, legend_data):
        print("Legend added successfully")
    else:
        print("Legend could not be added (continuing without legend)")
    
    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"Map rendered successfully: {output_file} ({file_size_mb:.1f} MB)")
    return True

def main():
    print("Lightweight Lumsden Tourist Map Generator")
#    print("Downloading icons...")
#    download_icons()
#    print("=" * 50)
    
    # Load configuration
    area_config = load_area_config("lumsden")
    output_format = load_output_format("A3")
    width_px, height_px = calculate_pixel_dimensions(output_format)

    # Calculate area
    bbox = calculate_bbox(
        area_config["center"]["lat"], 
        area_config["center"]["lon"], 
        area_config["coverage"]["width_km"], 
        area_config["coverage"]["height_km"]
    )
    print(f"Center: {area_config['center']['lat']}, {area_config['center']['lon']}")
    print(f"Area: {area_config['coverage']['width_km']}×{area_config['coverage']['height_km']}km")
    print(f"Scale: 1:{area_config['scale']:,}")
    print()

    # Ensure data directory exists for shapefiles and output
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Determine OSM file path (configurable, default to data/lumsden_area.osm)
    osm_file_path = area_config.get("osm_file", "data/lumsden_area.osm")
    osm_file = Path(osm_file_path)
    if not osm_file.exists():
        print(f"OSM file not found at {osm_file}. Downloading...")
        if not download_osm_data(bbox, str(osm_file)):
            return 1
    else:
        print(f"Using OSM data: {osm_file}")
    
    # Convert to shapefiles (no database!)
    print("\nConverting OSM data to shapefiles...")
    osm_data_dir = convert_osm_to_shapefiles(str(osm_file))
    
    # Process elevation data and generate contours if enabled
    print("\nProcessing elevation data and contours...")
    contour_config = area_config.get("contours", {})
    contour_data = process_elevation_and_contours(
        bbox, 
        osm_data_dir,
        contour_interval=contour_config.get("interval", 10),
        enable_contours=contour_config.get("enabled", True)
    )
    
    if contour_data:
        print(f"Contour lines generated with {contour_data['interval']}m intervals")
    else:
        print("Contour generation skipped or failed")

    # Process elevation data for hillshading if enabled
    hillshade_file = process_elevation_for_hillshading(bbox, area_config, osm_data_dir)
    hillshade_available = hillshade_file is not None
    
    # Create map style
    print("\nCreating tourist map style...")
    style_file = create_mapnik_style(osm_data_dir, area_config, hillshade_available)
    
    # Render map
    print(f"\nRendering A3 map ({width_px}×{height_px} pixels)...")
    output_file = data_dir / "lumsden_tourist_map_A3.png"
    
    if render_map(style_file, bbox, str(output_file), width_px, height_px):
        print("\nSUCCESS!")
        print(f"Tourist map: {output_file}")
        print(f"Print size: A3 ({output_format['width_mm']}×{output_format['height_mm']}mm at {output_format['dpi']} DPI)")
        print(f"Perfect for planning day trips around Lumsden!")
        return 0
    else:
        print("\nMap rendering failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

