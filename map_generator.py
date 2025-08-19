#!/usr/bin/env python3
"""
Lightweight A3 Tourist Map Generator for Lumsden, Aberdeenshire
Uses direct OSM file processing with GDAL/OGR - no database required
"""

import requests
import json
import os
import subprocess
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import math

# Map configuration
LUMSDEN_LAT = 57.3167
LUMSDEN_LON = -2.8833
MAP_SCALE = 25000

# A3 dimensions at 300 DPI
A3_WIDTH_MM = 297
A3_HEIGHT_MM = 420
DPI = 300
A3_WIDTH_PX = int(A3_WIDTH_MM / 25.4 * DPI)  # ~3508 pixels
A3_HEIGHT_PX = int(A3_HEIGHT_MM / 25.4 * DPI)  # ~4961 pixels

# Area coverage (8km x 12km for tourist planning)
BBOX_WIDTH_KM = 8
BBOX_HEIGHT_KM = 12

def calculate_bbox(center_lat, center_lon, width_km, height_km):
    """Calculate bounding box around center point"""
    lat_deg_per_km = 1 / 111.32
    lon_deg_per_km = 1 / (111.32 * abs(math.cos(math.radians(center_lat))))
    
    half_height_deg = (height_km / 2) * lat_deg_per_km
    half_width_deg = (width_km / 2) * lon_deg_per_km
    
    return {
        'south': center_lat - half_height_deg,
        'north': center_lat + half_height_deg,
        'west': center_lon - half_width_deg,
        'east': center_lon + half_width_deg
    }

def download_osm_data(bbox, output_file):
    """Download OSM data using Overpass API"""
    overpass_query = f"""
    [out:xml][timeout:300];
    (
      node({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
      way({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
      relation({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
      <;
    );
    (._;>;);
    out meta;
    """
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    print("Downloading OSM data from Overpass API...")
    response = requests.post(overpass_url, data=overpass_query, timeout=600)
    
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"OSM data saved to {output_file}")
        return True
    else:
        print(f"Failed to download OSM data: {response.status_code}")
        return False

def create_sample_tourist_data(bbox):
    """Create sample tourist data for Lumsden area to demonstrate enhanced map features"""
    print("Creating sample tourist data to demonstrate enhanced features...")
    
    output_dir = Path("enhanced_data")
    output_dir.mkdir(exist_ok=True)
    
    # Sample tourist points of interest for Lumsden area
    sample_pois = [
        {"name": "Lumsden Village Hall", "type": "tourism", "subtype": "information", "lat": 57.3167, "lon": -2.8833},
        {"name": "The Corgarff Arms", "type": "amenity", "subtype": "pub", "lat": 57.315, "lon": -2.885},
        {"name": "Lumsden Parish Church", "type": "amenity", "subtype": "place_of_worship", "lat": 57.318, "lon": -2.881},
        {"name": "Corgarff Castle", "type": "historic", "subtype": "castle", "lat": 57.335, "lon": -2.865},
        {"name": "River Don", "type": "waterway", "subtype": "river", "lat": 57.320, "lon": -2.870},
        {"name": "Lumsden Farm Shop", "type": "shop", "subtype": "farm", "lat": 57.314, "lon": -2.888},
        {"name": "Bellabeg Forest", "type": "natural", "subtype": "wood", "lat": 57.340, "lon": -2.850},
        {"name": "A944 Primary Route", "type": "highway", "subtype": "primary", "lat": 57.317, "lon": -2.883},
        {"name": "Lumsden Viewpoint", "type": "tourism", "subtype": "viewpoint", "lat": 57.330, "lon": -2.875},
        {"name": "Local B&B", "type": "tourism", "subtype": "guest_house", "lat": 57.312, "lon": -2.879},
        {"name": "Village Post Office", "type": "amenity", "subtype": "post_office", "lat": 57.316, "lon": -2.884},
        {"name": "Lumsden Primary School", "type": "amenity", "subtype": "school", "lat": 57.319, "lon": -2.882},
        {"name": "Golf Course", "type": "leisure", "subtype": "golf_course", "lat": 57.325, "lon": -2.890},
        {"name": "Walking Trail Start", "type": "highway", "subtype": "footway", "lat": 57.322, "lon": -2.878},
        {"name": "Local Parking", "type": "amenity", "subtype": "parking", "lat": 57.317, "lon": -2.883},
    ]
    
    # Create enhanced CSV files for different feature types
    with open(output_dir / "points_enhanced.csv", "w") as f:
        f.write("name,type,subtype,lat,lon\n")
        for poi in sample_pois:
            f.write(f"{poi['name']},{poi['type']},{poi['subtype']},{poi['lat']},{poi['lon']}\n")
    
    # Sample land use areas
    sample_landuse = [
        {"name": "Residential Area", "type": "landuse", "subtype": "residential"},
        {"name": "Agricultural Land", "type": "landuse", "subtype": "farmland"},
        {"name": "Forest Area", "type": "natural", "subtype": "wood"},
        {"name": "Grassland", "type": "natural", "subtype": "grassland"},
        {"name": "Commercial Zone", "type": "landuse", "subtype": "commercial"},
    ]
    
    with open(output_dir / "landuse_enhanced.csv", "w") as f:
        f.write("name,type,subtype\n")
        for area in sample_landuse:
            f.write(f"{area['name']},{area['type']},{area['subtype']}\n")
    
    print(f"✓ Created enhanced sample data in {output_dir}/")
    print(f"  - {len(sample_pois)} points of interest")
    print(f"  - {len(sample_landuse)} land use categories")
    
    return str(output_dir)

def convert_osm_to_shapefiles(osm_file):
    """Convert OSM data to shapefiles using ogr2ogr - no database needed!"""
    output_dir = Path("osm_data")
    
    # Check if shapefiles already exist
    required_layers = ['points', 'lines', 'multilinestrings', 'multipolygons']
    existing_shapefiles = []
    
    if output_dir.exists():
        for layer in required_layers:
            shp_file = output_dir / f"{layer}.shp"
            if shp_file.exists():
                existing_shapefiles.append(layer)
    
    # If all required shapefiles exist, skip conversion
    if len(existing_shapefiles) == len(required_layers):
        print("Using existing shapefiles (conversion not required)...")
        print(f"  Found all {len(required_layers)} layers: {existing_shapefiles}")
        return str(output_dir)
    
    # Need to convert - create directory and proceed
    print("Converting OSM data to shapefiles (no database required)...")
    output_dir.mkdir(exist_ok=True)
    
    # Check ogr2ogr version
    try:
        result = subprocess.run(["ogr2ogr", "--version"], capture_output=True, text=True, check=True)
        print(f"  Using GDAL/OGR version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  Error: Could not find or run 'ogr2ogr'. Is GDAL installed and in your PATH?")
        return None

    # First, let's see what layers are available in the OSM file
    print("  Inspecting OSM file for available layers...")
    try:
        result = subprocess.run(["ogrinfo", osm_file], 
                              capture_output=True, text=True, check=True)
        print("  Available layers:")
        for line in result.stdout.split('\n'):
            if 'Layer name:' in line:
                print(f"    {line.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"  Warning: Could not inspect OSM file: {e}")
    
    # OSM layers to extract (these are the standard OSM layer names)
    layers = {
        'points': 'points of interest, towns, etc.',
        'lines': 'roads, paths, boundaries', 
        'multilinestrings': 'complex routes',
        'multipolygons': 'land use, water bodies, buildings'
    }
    
    created_files = []
    
    for layer_name, description in layers.items():
        print(f"  Extracting {layer_name} ({description})...")
        output_file = output_dir / f"{layer_name}.shp"
        
        cmd = [
            "ogr2ogr",
            "-f", "ESRI Shapefile",
            "-overwrite",
            "--debug", "on",
            str(output_file),
            osm_file,
            layer_name
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if output_file.exists():
                print(f"    Created {output_file}")
                created_files.append(layer_name)
            else:
                print(f"    ⚠ Command succeeded but file not found: {output_file}")
                if result.stdout:
                    print(f"      ogr2ogr stdout:\n{result.stdout}")
                if result.stderr:
                    print(f"      ogr2ogr stderr:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"    Error creating {layer_name}:")
            print(f"      Command: {' '.join(cmd)}")
            print(f"      Stderr: {e.stderr.strip()}")
            print(f"      Stdout: {e.stdout.strip()}")

    print(f"  Successfully created {len(created_files)} shapefiles: {created_files}")
    
    # Verify files exist and show their info
    for layer in created_files:
        shp_file = output_dir / f"{layer}.shp"
        if shp_file.exists():
            try:
                result = subprocess.run(["ogrinfo", "-so", str(shp_file)], 
                                      capture_output=True, text=True, check=True)
                # Count features
                feature_count = 0
                for line in result.stdout.split('\n'):
                    if 'Feature Count:' in line:
                        feature_count = line.split(':')[1].strip()
                        break
                print(f"    {layer}: {feature_count} features")
            except:
                print(f"    {layer}: file exists but couldn't get info")
    
    return str(output_dir)

def create_mapnik_style(data_dir):
    """Use a Mapnik XML style file."""
    style_file = "tourist_map_style.xml"
    if not os.path.exists(style_file):
        print(f"Error: style file not found: {style_file}")
        return None
    print(f"Using external map style: {style_file}")
    return style_file


def _add_osm_layers_to_map(m, data_dir):
    """Add shapefile layers created from OSM into the map using styles from the XML."""
    import mapnik
    data_dir = str(Path(data_dir).resolve())

    # Ensure we use styles already defined by the XML
    required_styles = ["landuse", "water", "buildings", "roads_major", "roads_minor", "paths", "poi"]
    # Check if styles exist in the map
    style_names = []
    for style_name in required_styles:
        try:
            m.find_style(style_name)
            style_names.append(style_name)
        except RuntimeError:
            print(f"Warning: Style '{style_name}' not found in map XML")
    
    print(f"Found {len(style_names)} styles in map: {style_names}")

    # Note: We'll append to existing layers rather than clearing them
    # since m.layers is append-only in this Mapnik version

    wgs84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    # Polygons
    poly = os.path.join(data_dir, "multipolygons.shp")
    if os.path.exists(poly):
        lyr = mapnik.Layer("osm_multipolygons", wgs84)
        lyr.datasource = mapnik.Shapefile(file=poly)
        for sty in ("landuse", "water", "buildings"):
            if sty in style_names:
                lyr.styles.append(sty)
        m.layers.append(lyr)
    else:
        print(f"Note: missing shapefile: {poly}")

    # Lines
    lines = os.path.join(data_dir, "lines.shp")
    if os.path.exists(lines):
        lyr = mapnik.Layer("osm_lines", wgs84)
        lyr.datasource = mapnik.Shapefile(file=lines)
        for sty in ("roads_major", "roads_minor", "paths"):
            if sty in style_names:
                lyr.styles.append(sty)
        m.layers.append(lyr)
    else:
        print(f"Note: missing shapefile: {lines}")

    # Points
    pts = os.path.join(data_dir, "points.shp")
    if os.path.exists(pts):
        lyr = mapnik.Layer("osm_points", wgs84)
        lyr.datasource = mapnik.Shapefile(file=pts)
        if "poi" in style_names:
            lyr.styles.append("poi")
        m.layers.append(lyr)
    else:
        print(f"Note: missing shapefile: {pts}")

    print(f"Added {len(m.layers)} OSM layers to map from {data_dir}")


def render_map(style_file, bbox, output_file, data_dir):
    try:
        import mapnik
    except ImportError:
        print("Error: python-mapnik not available. Install with: pip install mapnik")
        return False

    print("Rendering A3 tourist map...")

    m = mapnik.Map(A3_WIDTH_PX, A3_HEIGHT_PX)
    mapnik.load_map(m, style_file)

    # Add the converted OSM shapefiles explicitly so paths are correct
    if data_dir:
        _add_osm_layers_to_map(m, data_dir)

    # Correctly reproject bbox from WGS84 to map SRS
    bbox_wgs84 = mapnik.Box2d(bbox['west'], bbox['south'], bbox['east'], bbox['north'])
    proj_wgs84 = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    proj_map = mapnik.Projection(m.srs)
    tx = mapnik.ProjTransform(proj_wgs84, proj_map)
    bbox_proj = tx.forward(bbox_wgs84)
    m.zoom_to_box(bbox_proj)

    mapnik.render_to_file(m, output_file, 'png')
    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"Map rendered successfully: {output_file} ({file_size_mb:.1f} MB)")
    return True

def main():
    print("Lumsden Tourist Map Generator")
    print("=" * 50)
    
    # Calculate area
    bbox = calculate_bbox(LUMSDEN_LAT, LUMSDEN_LON, BBOX_WIDTH_KM, BBOX_HEIGHT_KM)
    print(f"Centre: {LUMSDEN_LAT}, {LUMSDEN_LON}")
    print(f"Area: {BBOX_WIDTH_KM}×{BBOX_HEIGHT_KM}km")
    print(f"Scale: 1:{MAP_SCALE:,}")
    print()
    
    # Create sample enhanced data to demonstrate features
    print("🎨 Creating enhanced sample data...")
    enhanced_data_dir = create_sample_tourist_data(bbox)
    
    # Download OSM data
    osm_file = "lumsden_area.osm"
    if not Path(osm_file).exists():
        print("Downloading OpenStreetMap data...")
        if not download_osm_data(bbox, osm_file):
            return 1
    else:
        print(f"Using existing OSM data: {osm_file}")
    
    # Convert to shapefiles (no database!)
    print("\nConverting OSM data to shapefiles...")
    data_dir = convert_osm_to_shapefiles(osm_file)
    
    # Create map style
    print("\nCreating tourist map style...")
    style_file = create_mapnik_style(data_dir)
    if not style_file:
        return 1
    
    # Render map
    print(f"\nRendering A3 map ({A3_WIDTH_PX}×{A3_HEIGHT_PX} pixels)...")
    output_file = f"lumsden_tourist_map_A3.png"
    
    if render_map(style_file, bbox, output_file, data_dir=data_dir):
        print("\nSUCCESS!")
        print(f"Tourist map: {output_file}")
        print(f"Print size: A3 ({A3_WIDTH_MM}×{A3_HEIGHT_MM}mm at {DPI} DPI)")
        print(f"Perfect for planning day trips around Lumsden!")
        return 0
    else:
        print("\nMap rendering failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
