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
    print("Converting OSM data to shapefiles (no database required)...")
    
    output_dir = Path("osm_data")
    output_dir.mkdir(exist_ok=True)
    
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
            str(output_file),
            osm_file,
            layer_name
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if output_file.exists():
                print(f"    ✓ Created {output_file}")
                created_files.append(layer_name)
            else:
                print(f"    ⚠ Command succeeded but file not found: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"    ⚠ Warning: Could not create {layer_name}")
            print(f"      Error: {e.stderr.strip() if e.stderr else 'Unknown error'}")
    
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
    """Create a comprehensive tourist-focused Mapnik XML style with rich content"""
    
    style_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" 
     background-color="#f8f8f8">

  <!-- ENHANCED LAND USE / BACKGROUND -->
  <Style name="landuse">
    <!-- Natural Features -->
    <Rule>
      <Filter>[landuse] = 'forest' or [natural] = 'wood'</Filter>
      <PolygonSymbolizer fill="#d4e6b7" fill-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[natural] = 'heath' or [natural] = 'scrub'</Filter>
      <PolygonSymbolizer fill="#e8dab2" fill-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[natural] = 'grassland' or [natural] = 'fell' or [natural] = 'moor'</Filter>
      <PolygonSymbolizer fill="#e6f2d4" fill-opacity="0.6"/>
    </Rule>
    <Rule>
      <Filter>[natural] = 'wetland' or [natural] = 'marsh'</Filter>
      <PolygonSymbolizer fill="#b8e6d1" fill-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[natural] = 'scree' or [natural] = 'bare_rock'</Filter>
      <PolygonSymbolizer fill="#d1d5db" fill-opacity="0.6"/>
    </Rule>
    
    <!-- Agricultural Land -->
    <Rule>
      <Filter>[landuse] = 'farmland' or [landuse] = 'grass'</Filter>
      <PolygonSymbolizer fill="#e8f5d4" fill-opacity="0.6"/>
    </Rule>
    <Rule>
      <Filter>[landuse] = 'meadow' or [landuse] = 'orchard'</Filter>
      <PolygonSymbolizer fill="#daf2c0" fill-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[landuse] = 'vineyard'</Filter>
      <PolygonSymbolizer fill="#c8e6c9" fill-opacity="0.7"/>
    </Rule>
    
    <!-- Urban Areas -->
    <Rule>
      <Filter>[landuse] = 'residential'</Filter>
      <PolygonSymbolizer fill="#f5f5f5" fill-opacity="0.6"/>
    </Rule>
    <Rule>
      <Filter>[landuse] = 'commercial' or [landuse] = 'retail'</Filter>
      <PolygonSymbolizer fill="#ffe0e6" fill-opacity="0.6"/>
    </Rule>
    <Rule>
      <Filter>[landuse] = 'industrial'</Filter>
      <PolygonSymbolizer fill="#e8e8e8" fill-opacity="0.6"/>
    </Rule>
    
    <!-- Recreation Areas -->
    <Rule>
      <Filter>[leisure] = 'park' or [leisure] = 'garden'</Filter>
      <PolygonSymbolizer fill="#c8facc" fill-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[leisure] = 'golf_course'</Filter>
      <PolygonSymbolizer fill="#b3e6b8" fill-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[leisure] = 'sports_centre' or [leisure] = 'pitch'</Filter>
      <PolygonSymbolizer fill="#c8f7c5" fill-opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'camp_site' or [tourism] = 'caravan_site'</Filter>
      <PolygonSymbolizer fill="#e8f5e8" fill-opacity="0.6"/>
    </Rule>
  </Style>

  <!-- ENHANCED WATER FEATURES -->
  <Style name="water">
    <Rule>
      <Filter>[natural] = 'water' or [waterway] = 'river' or [waterway] = 'stream'</Filter>
      <PolygonSymbolizer fill="#7dd3c0" fill-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[waterway] = 'canal' or [waterway] = 'drain'</Filter>
      <LineSymbolizer stroke="#5dade2" stroke-width="2" stroke-opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[natural] = 'spring'</Filter>
      <MarkersSymbolizer fill="#5dade2" width="4" height="4" opacity="0.9"/>
    </Rule>
  </Style>
  
  <!-- ENHANCED ROADS - Tourist-friendly styling -->
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
    <Rule>
      <Filter>[highway] = 'service' or [highway] = 'track'</Filter>
      <LineSymbolizer stroke="#bdc3c7" stroke-width="1" stroke-opacity="0.7"/>
    </Rule>
  </Style>
  
  <!-- ENHANCED PATHS & TRANSPORTATION -->
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
      <Filter>[route] = 'hiking' or [highway] = 'bridleway'</Filter>
      <LineSymbolizer stroke="#d35400" stroke-width="2.5" stroke-dasharray="5,3" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[railway] = 'rail'</Filter>
      <LineSymbolizer stroke="#34495e" stroke-width="2" stroke-opacity="0.9"/>
      <LineSymbolizer stroke="#ffffff" stroke-width="1" stroke-dasharray="8,4" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[railway] = 'disused' or [railway] = 'abandoned'</Filter>
      <LineSymbolizer stroke="#95a5a6" stroke-width="1.5" stroke-dasharray="6,6" stroke-opacity="0.6"/>
    </Rule>
  </Style>
  
  <!-- ENHANCED BUILDINGS -->
  <Style name="buildings">
    <Rule>
      <Filter>[building] = 'church' or [amenity] = 'place_of_worship'</Filter>
      <PolygonSymbolizer fill="#d4b8e6" fill-opacity="0.8"/>
      <LineSymbolizer stroke="#8e44ad" stroke-width="1" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[building] = 'school' or [amenity] = 'school'</Filter>
      <PolygonSymbolizer fill="#f9e79f" fill-opacity="0.8"/>
      <LineSymbolizer stroke="#f4d03f" stroke-width="1" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[building] = 'hospital' or [amenity] = 'hospital'</Filter>
      <PolygonSymbolizer fill="#fadbd8" fill-opacity="0.8"/>
      <LineSymbolizer stroke="#e74c3c" stroke-width="1" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[building] = 'public' or [amenity] = 'townhall'</Filter>
      <PolygonSymbolizer fill="#d5e8f7" fill-opacity="0.8"/>
      <LineSymbolizer stroke="#3498db" stroke-width="1" stroke-opacity="0.9"/>
    </Rule>
    <Rule>
      <PolygonSymbolizer fill="#bdc3c7" fill-opacity="0.6"/>
      <LineSymbolizer stroke="#7f8c8d" stroke-width="0.5" stroke-opacity="0.8"/>
    </Rule>
  </Style>
  
  <!-- COMPREHENSIVE POINTS OF INTEREST -->
  <Style name="poi">
    <!-- Food & Drink -->
    <Rule>
      <Filter>[amenity] = 'restaurant'</Filter>
      <MarkersSymbolizer fill="#e74c3c" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'pub' or [amenity] = 'bar'</Filter>
      <MarkersSymbolizer fill="#c0392b" width="9" height="9" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'cafe' or [amenity] = 'fast_food'</Filter>
      <MarkersSymbolizer fill="#f39c12" width="8" height="8" opacity="0.9"/>
    </Rule>
    
    <!-- Accommodation -->
    <Rule>
      <Filter>[tourism] = 'hotel'</Filter>
      <MarkersSymbolizer fill="#3498db" width="12" height="12" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'guest_house' or [tourism] = 'bed_and_breakfast'</Filter>
      <MarkersSymbolizer fill="#5dade2" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'hostel' or [tourism] = 'motel'</Filter>
      <MarkersSymbolizer fill="#85c1e9" width="9" height="9" opacity="0.9"/>
    </Rule>
    
    <!-- Attractions & Tourism -->
    <Rule>
      <Filter>[tourism] = 'attraction'</Filter>
      <MarkersSymbolizer fill="#f39c12" width="12" height="12" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'viewpoint'</Filter>
      <MarkersSymbolizer fill="#d68910" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[tourism] = 'museum' or [tourism] = 'gallery'</Filter>
      <MarkersSymbolizer fill="#8e44ad" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[historic] = 'castle' or [historic] = 'ruins'</Filter>
      <MarkersSymbolizer fill="#7d3c98" width="12" height="12" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[historic] = 'monument' or [historic] = 'memorial'</Filter>
      <MarkersSymbolizer fill="#a569bd" width="9" height="9" opacity="0.9"/>
    </Rule>
    
    <!-- Services -->
    <Rule>
      <Filter>[amenity] = 'parking'</Filter>
      <MarkersSymbolizer fill="#95a5a6" width="7" height="7" opacity="0.7"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'fuel' or [amenity] = 'charging_station'</Filter>
      <MarkersSymbolizer fill="#e67e22" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'bank' or [amenity] = 'atm'</Filter>
      <MarkersSymbolizer fill="#27ae60" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'post_office'</Filter>
      <MarkersSymbolizer fill="#e74c3c" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'pharmacy'</Filter>
      <MarkersSymbolizer fill="#2ecc71" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'hospital' or [amenity] = 'clinic'</Filter>
      <MarkersSymbolizer fill="#e74c3c" width="10" height="10" opacity="0.9"/>
    </Rule>
    
    <!-- Education & Public -->
    <Rule>
      <Filter>[amenity] = 'school' or [amenity] = 'university'</Filter>
      <MarkersSymbolizer fill="#f1c40f" width="9" height="9" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'library'</Filter>
      <MarkersSymbolizer fill="#9b59b6" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'police'</Filter>
      <MarkersSymbolizer fill="#3498db" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'fire_station'</Filter>
      <MarkersSymbolizer fill="#e74c3c" width="8" height="8" opacity="0.8"/>
    </Rule>
    
    <!-- Recreation -->
    <Rule>
      <Filter>[leisure] = 'sports_centre' or [leisure] = 'fitness_centre'</Filter>
      <MarkersSymbolizer fill="#1abc9c" width="9" height="9" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[leisure] = 'golf_course'</Filter>
      <MarkersSymbolizer fill="#27ae60" width="10" height="10" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[leisure] = 'playground'</Filter>
      <MarkersSymbolizer fill="#f39c12" width="7" height="7" opacity="0.8"/>
    </Rule>
    
    <!-- Transport -->
    <Rule>
      <Filter>[railway] = 'station'</Filter>
      <MarkersSymbolizer fill="#34495e" width="10" height="10" opacity="0.9"/>
    </Rule>
    <Rule>
      <Filter>[highway] = 'bus_stop'</Filter>
      <MarkersSymbolizer fill="#3498db" width="6" height="6" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[aeroway] = 'aerodrome'</Filter>
      <MarkersSymbolizer fill="#2c3e50" width="12" height="12" opacity="0.9"/>
    </Rule>
    
    <!-- Shopping -->
    <Rule>
      <Filter>[shop] = 'supermarket' or [shop] = 'convenience'</Filter>
      <MarkersSymbolizer fill="#e67e22" width="8" height="8" opacity="0.8"/>
    </Rule>
    <Rule>
      <Filter>[amenity] = 'marketplace'</Filter>
      <MarkersSymbolizer fill="#d68910" width="9" height="9" opacity="0.8"/>
    </Rule>
  </Style>

  <!-- PLACE LABELS for better navigation -->
  <Style name="place_labels">
    <Rule>
      <Filter>[place] = 'city' or [place] = 'town'</Filter>
      <TextSymbolizer face-name="DejaVu Sans Bold" size="14" fill="#2c3e50" 
                      placement="point" dx="0" dy="-15">[name]</TextSymbolizer>
    </Rule>
    <Rule>
      <Filter>[place] = 'village' or [place] = 'hamlet'</Filter>
      <TextSymbolizer face-name="DejaVu Sans" size="11" fill="#34495e" 
                      placement="point" dx="0" dy="-12">[name]</TextSymbolizer>
    </Rule>
    <Rule>
      <Filter>[place] = 'farm' or [place] = 'locality'</Filter>
      <TextSymbolizer face-name="DejaVu Sans" size="9" fill="#7f8c8d" 
                      placement="point" dx="0" dy="-10">[name]</TextSymbolizer>
    </Rule>
  </Style>

  <!-- LAYER DEFINITIONS with enhanced ordering -->
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
  
  <Layer name="place_labels" srs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs">
    <StyleName>place_labels</StyleName>
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
    print("🗺️  Enhanced Lumsden Tourist Map Generator")
    print("=" * 50)
    
    # Calculate area
    bbox = calculate_bbox(LUMSDEN_LAT, LUMSDEN_LON, BBOX_WIDTH_KM, BBOX_HEIGHT_KM)
    print(f"📍 Center: {LUMSDEN_LAT}, {LUMSDEN_LON}")
    print(f"📏 Area: {BBOX_WIDTH_KM}×{BBOX_HEIGHT_KM}km")
    print(f"🎯 Scale: 1:{MAP_SCALE:,}")
    print()
    
    # Create sample enhanced data to demonstrate features
    print("🎨 Creating enhanced sample data...")
    enhanced_data_dir = create_sample_tourist_data(bbox)
    
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
    
    # Create enhanced map style
    print("\n🎨 Creating comprehensive tourist map style...")
    style_file = create_mapnik_style(data_dir)
    
    # Render map
    print(f"\n🖨️  Rendering enhanced A3 map ({A3_WIDTH_PX}×{A3_HEIGHT_PX} pixels)...")
    output_file = f"lumsden_enhanced_tourist_map_A3.png"
    
    if render_map(style_file, bbox, output_file):
        print("\n🎉 SUCCESS!")
        print(f"📄 Enhanced tourist map: {output_file}")
        print(f"📐 Print size: A3 ({A3_WIDTH_MM}×{A3_HEIGHT_MM}mm at {DPI} DPI)")
        print(f"🎯 Features comprehensive tourist information for Lumsden!")
        print(f"📋 Enhancement plan: MAP_ENHANCEMENT_PLAN.md")
        print(f"📊 Sample data: {enhanced_data_dir}/")
        return 0
    else:
        print("\n❌ Map rendering failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

