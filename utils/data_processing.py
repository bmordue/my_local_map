"""Geographic and data processing utilities"""

import math
import requests
import subprocess
from pathlib import Path


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


def convert_osm_to_shapefiles(osm_file):
    """Convert OSM data to shapefiles using ogr2ogr - no database needed!"""
    print("Converting OSM data to shapefiles (no database required)...")
    
    output_dir = Path("data/osm_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
            "-lco", "ALL_ATTRIBUTES=YES",
            "--debug", "on",
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
                if result.stdout:
                    print(f"      ogr2ogr stdout:\n{result.stdout}")
                if result.stderr:
                    print(f"      ogr2ogr stderr:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"    ⚠ Error creating {layer_name}:")
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