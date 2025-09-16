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
        print("✓ Legend added successfully")
    else:
        print("⚠ Legend could not be added (continuing without legend)")
    
    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"✓ Map rendered successfully: {output_file} ({file_size_mb:.1f} MB)")
    return True

def main():
    print("🗺️  Lightweight Lumsden Tourist Map Generator")
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
    print(f"📍 Center: {area_config['center']['lat']}, {area_config['center']['lon']}")
    print(f"📏 Area: {area_config['coverage']['width_km']}×{area_config['coverage']['height_km']}km")
    print(f"🎯 Scale: 1:{area_config['scale']:,}")
    print()
    
    # Ensure data directory exists for shapefiles and output
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # OSM file should be at repository root according to coding guidelines  
    osm_file = Path("lumsden_area.osm")
    if not osm_file.exists():
        print("📡 Downloading OpenStreetMap data...")
        if not download_osm_data(bbox, str(osm_file)):
            return 1
    else:
        print(f"📁 Using existing OSM data: {osm_file}")
    
    # Convert to shapefiles (no database!)
    print("\n🔄 Converting OSM data to shapefiles...")
    osm_data_dir = convert_osm_to_shapefiles(str(osm_file))
    
    # Process elevation data and generate contours if enabled
    print("\n📏 Processing elevation data and contours...")
    contour_config = area_config.get("contours", {})
    contour_data = process_elevation_and_contours(
        bbox, 
        osm_data_dir,
        contour_interval=contour_config.get("interval", 10),
        enable_contours=contour_config.get("enabled", True)
    )
    
    if contour_data:
        print(f"✓ Contour lines generated with {contour_data['interval']}m intervals")
    else:
        print("⚠ Contour generation skipped or failed")

    # Process elevation data for hillshading if enabled
    hillshade_file = process_elevation_for_hillshading(bbox, area_config, osm_data_dir)
    hillshade_available = hillshade_file is not None
    
    # Run quality validation on enhanced data (optional)
    quality_validation_enabled = os.environ.get('ENABLE_QUALITY_VALIDATION', '').lower() in ('1', 'true', 'yes')
    if quality_validation_enabled:
        print("\n🔍 Running data quality validation...")
        try:
            from utils.quality_validation import validate_data_quality
            import json
            
            # Load enhanced data if available for validation
            enhanced_data_path = Path("enhanced_data")
            if enhanced_data_path.exists():
                data_sources = {}
                geojson_files = {
                    'tourist_attractions': 'tourist_attractions.geojson',
                    'accommodation': 'accommodation.geojson', 
                    'dining': 'dining.geojson',
                    'activities': 'activities.geojson',
                    'walking_trails': 'walking_trails.geojson'
                }
                
                for source_name, filename in geojson_files.items():
                    file_path = enhanced_data_path / filename
                    if file_path.exists():
                        try:
                            with open(file_path, 'r') as f:
                                geojson_data = json.load(f)
                                features = geojson_data.get('features', [])
                                data_list = []
                                
                                for feature in features:
                                    item = feature.get('properties', {}).copy()
                                    geom = feature.get('geometry', {})
                                    if geom.get('type') == 'Point':
                                        coords = geom.get('coordinates', [])
                                        if len(coords) >= 2:
                                            item['lon'] = coords[0]
                                            item['lat'] = coords[1]
                                    data_list.append(item)
                                
                                if data_list:
                                    data_sources[source_name] = data_list
                        except Exception as e:
                            print(f"⚠️  Warning: Could not load {filename} for validation: {e}")
                
                if data_sources:
                    validation_report = validate_data_quality(data_sources, bbox)
                    failed_checks = sum(1 for r in validation_report.results if not r.passed)
                    if failed_checks > 0:
                        print(f"⚠️  Quality validation found {failed_checks} issues (continuing with map generation)")
                    else:
                        print("✓ All data quality checks passed")
                else:
                    print("ℹ️  No enhanced data found for quality validation")
            else:
                print("ℹ️  Enhanced data directory not found - skipping quality validation")
        except ImportError:
            print("⚠️  Quality validation not available (utils.quality_validation not found)")
        except Exception as e:
            print(f"⚠️  Quality validation failed: {e}")
    
    # Create map style
    print("\n🎨 Creating tourist map style...")
    style_file = create_mapnik_style(osm_data_dir, area_config, hillshade_available)
    
    # Render map
    print(f"\n🖨️  Rendering A3 map ({width_px}×{height_px} pixels)...")
    output_file = data_dir / "lumsden_tourist_map_A3.png"
    
    if render_map(style_file, bbox, str(output_file), width_px, height_px):
        print("\n🎉 SUCCESS!")
        print(f"📄 Tourist map: {output_file}")
        print(f"📐 Print size: A3 ({output_format['width_mm']}×{output_format['height_mm']}mm at {output_format['dpi']} DPI)")
        print(f"🎯 Perfect for planning day trips around Lumsden!")
        return 0
    else:
        print("\n❌ Map rendering failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

