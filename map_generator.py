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
        way({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        relation({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
        <;
    );
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

def convert_osm_to_shapefiles(osm_file):
    """Convert OSM data to shapefiles using ogr2ogr - no database needed!"""
    print("Converting OSM data to shapefiles (no database required)...")
    
    output_dir = Path("osm_data")
    output_dir.mkdir(exist_ok=True)
    
    # OSM layers to extract
    layers = {
        'points': 'points of interest, towns, etc.',
        'lines': 'roads, paths, boundaries',
        'multilinestrings': 'complex routes',
        'multipolygons': 'land use, water bodies, buildings'
    }
    
    for layer_name, description in layers.items():
        print(f"  Extracting {layer_name} ({description})...")
        output_file = output_dir / layer_name
        
        cmd = [
            "ogr2ogr",
            "-f", "ESRI Shapefile",
            "-overwrite",
            str(output_file),
            osm_file,
            layer_name
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"    ✓ Created {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"    ⚠ Warning: Could not create {layer_name}: {e.stderr}")
    
    return str(output_dir)

def create_mapnik_style(data_dir):
    """Create a tourist-focused Mapnik XML style"""
    
    style_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" 
     background-color="#f8f8f8">

  <!-- LAND USE / BACKGROUND -->
  <Style name="landuse">
    <Rule>
      <Filter>[landuse] = 'forest' or [natural] = 'wood'</Filter>
      <PolygonSymbolizer fill="#d4e6b7" fill-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[landuse] = 'farmland' or [landuse] = 'grass'</Filter>
      <PolygonSymbolizer fill="#e8f5d4" fill-opacity="0.6"/>
    </Rule>
    <Rule>
      <Filter>[leisure] = 'park' or [leisure] = 'garden'</Filter>
      <PolygonSymbolizer fill="#c8facc" fill-opacity="0.8"/>
    </Rule>
  </Style>

  <!-- WATER -->
  <Style name="water">
    <Rule>
      <Filter>[natural] = 'water' or [waterway] = 'river' or [waterway] = 'stream'</Filter>
      <PolygonSymbolizer fill="#7dd3c0" fill-opacity="0.8"/>
    </Rule>
  </Style>
  
  <!-- ROADS - Tourist-friendly styling -->
  <Style name="roads_major">
    <Rule>
      <Filter>[highway] = 'motorway'</Filter>
      <LineSymbolizer stroke="#e74c3c" stroke-width="4" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[highway] = 'trunk' or [highway] = 'primary'</Filter>
      <LineSymbolizer stroke="#f39c12" stroke-width="3" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[highway] = 'secondary'</Filter>
      <LineSymbolizer stroke="#f1c40f" stroke-width="2.5" stroke-opacity="0.8"/>
    </Rule>
  </Style>
  
  <Style name="roads_minor">
    <Rule>
      <Filter>[highway] = 'tertiary' or [highway] = 'unclassified'</Filter>
      <LineSymbolizer stroke="#ffffff" stroke-width="2" stroke-opacity="0.9"/>
      <LineSymbolizer stroke="#34495e" stroke-width="1.5" stroke-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[highway] = 'residential'</Filter>
      <LineSymbolizer stroke="#ecf0f1" stroke-width="1.5" stroke-opacity="0.8"/>
    </Rule>
  </Style>
  
  <!-- PATHS & TOURIST ROUTES - Emphasized for planning -->
  <Style name="paths">
    <Rule>
      <Filter>[highway] = 'footway' or [highway] = 'path'</Filter>
      <LineSymbolizer stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="3,2" stroke-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[highway] = 'cycleway'</Filter>
      <LineSymbolizer stroke="#27ae60" stroke-width="2" stroke-dasharray="4,2" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[route] = 'hiking'</Filter>
      <LineSymbolizer stroke="#d35400" stroke-width="2.5" stroke-dasharray="5,3" stroke-opacity="0.9"/>
    </Rule>
  </Style>
  
  <!-- BUILDINGS -->
  <Style name="buildings">
    <Rule>
      <PolygonSymbolizer fill="#bdc3c7" fill-opacity="0.6"/>
      <LineSymbolizer stroke="#7f8c8d" stroke-width="0.5" stroke-opacity="0.8"/>
    </Rule>
  </Style>
  
  <!-- POINTS OF INTEREST - Tourist focused -->
  <Style name="poi">
    <Rule>
      <Filter>[amenity] = 'restaurant' or [amenity] = 'pub' or [amenity] = 'cafe'</Filter>
      <PointSymbolizer fill="#e74c3c" width="8" height="8" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'hotel' or [tourism] = 'guest_house'</Filter>
      <PointSymbolizer fill="#3498db" width="8" height="8" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'attraction' or [tourism] = 'viewpoint'</Filter>
      <PointSymbolizer fill="#f39c12" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'parking'</Filter>
      <PointSymbolizer fill="#95a5a6" width="6" height="6" opacity="0.7"/>
    </Rule>
  </Style>

  <!-- LAYER DEFINITIONS -->
  <Layer name="landuse" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>landuse</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/multipolygons</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="water" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>water</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/multipolygons</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="buildings" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>buildings</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/multipolygons</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="roads_major" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>roads_major</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/lines</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="roads_minor" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>roads_minor</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/lines</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="paths" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>paths</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/lines</Parameter>
    </Datasource>
  </Layer>
  
  <Layer name="poi" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>poi</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">{data_dir}/points</Parameter>
    </Datasource>
  </Layer>

</Map>'''
    
    style_file = "tourist_map_style.xml"
    with open(style_file, 'w') as f:
        f.write(style_xml)
    
    print(f"Created tourist-focused map style: {style_file}")
    return style_file

def render_map(style_file, bbox, output_file):
    """Render the map using Mapnik"""
    try:
        import mapnik
    except ImportError:
        print("Error: python-mapnik not available. Install with: pip install mapnik")
        return False
    
    print("Rendering A3 tourist map...")
    
    # Create map
    m = mapnik.Map(A3_WIDTH_PX, A3_HEIGHT_PX)
    mapnik.load_map(m, style_file)
    
    # Set bounding box
    bbox_proj = mapnik.Box2d(bbox['west'], bbox['south'], bbox['east'], bbox['north'])
    m.zoom_to_box(bbox_proj)
    
    # Render
    mapnik.render_to_file(m, output_file, 'png')
    
    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"✓ Map rendered successfully: {output_file} ({file_size_mb:.1f} MB)")
    return True

def main():
    print("🗺️  Lightweight Lumsden Tourist Map Generator")
    print("=" * 50)
    
    # Calculate area
    bbox = calculate_bbox(LUMSDEN_LAT, LUMSDEN_LON, BBOX_WIDTH_KM, BBOX_HEIGHT_KM)
    print(f"📍 Center: {LUMSDEN_LAT}, {LUMSDEN_LON}")
    print(f"📏 Area: {BBOX_WIDTH_KM}×{BBOX_HEIGHT_KM}km")
    print(f"🎯 Scale: 1:{MAP_SCALE:,}")
    print()
    
    # Download OSM data
    osm_file = "lumsden_area.osm"
    if not Path(osm_file).exists():
        print("📡 Downloading OpenStreetMap data...")
        if not download_osm_data(bbox, osm_file):
            return 1
    else:
        print(f"📁 Using existing OSM data: {osm_file}")
    
    # Convert to shapefiles (no database!)
    print("\n🔄 Converting OSM data to shapefiles...")
    data_dir = convert_osm_to_shapefiles(osm_file)
    
    # Create map style
    print("\n🎨 Creating tourist map style...")
    style_file = create_mapnik_style(data_dir)
    
    # Render map
    print(f"\n🖨️  Rendering A3 map ({A3_WIDTH_PX}×{A3_HEIGHT_PX} pixels)...")
    output_file = f"lumsden_tourist_map_A3.png"
    
    if render_map(style_file, bbox, output_file):
        print("\n🎉 SUCCESS!")
        print(f"📄 Tourist map: {output_file}")
        print(f"📐 Print size: A3 ({A3_WIDTH_MM}×{A3_HEIGHT_MM}mm at {DPI} DPI)")
        print(f"🎯 Perfect for planning day trips around Lumsden!")
        return 0
    else:
        print("\n❌ Map rendering failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
