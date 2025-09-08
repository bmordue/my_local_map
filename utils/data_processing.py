"""Geographic and data processing utilities"""

import math
import requests
import subprocess
import os
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


def download_elevation_data(bbox, output_file="elevation_data.tif"):
    """
    Download elevation data for the given bounding box using SRTM data
    For minimal implementation, creates a sample elevation dataset
    In production, this would download from USGS or similar sources
    """
    print("📊 Preparing elevation data for contour generation...")
    
    # For this implementation, we'll create a synthetic elevation dataset
    # based on the geographic location (Scotland Highlands have elevation)
    # This provides a working demonstration without external dependencies
    
    try:
        # Calculate approximate elevation based on distance from sea level
        # and typical Highland topography patterns
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lon = (bbox['east'] + bbox['west']) / 2
        
        # Create a simple elevation model using GDAL
        # This is a simplified approach for demonstration
        width = int((bbox['east'] - bbox['west']) * 111000 / 30)  # ~30m resolution
        height = int((bbox['north'] - bbox['south']) * 111000 / 30)  # ~30m resolution
        
        # Ensure minimum reasonable size
        width = max(width, 100)
        height = max(height, 100)
        
        # Create elevation data using gdal_translate and synthetic data
        temp_xyz = Path("temp_elevation.xyz")
        
        # Generate synthetic elevation data representing Highland topography
        with open(temp_xyz, 'w') as f:
            for y in range(height):
                for x in range(width):
                    # Map pixel coordinates to geographic coordinates
                    lon = bbox['west'] + (x / width) * (bbox['east'] - bbox['west'])
                    lat = bbox['south'] + ((height - y) / height) * (bbox['north'] - bbox['south'])
                    
                    # Generate realistic elevation for Scottish Highlands
                    # Base elevation increases with distance from coastline
                    base_elevation = 50 + (lat - 57.0) * 200  # Increase with latitude
                    
                    # Add topographic variation using simple math functions
                    variation = (
                        50 * math.sin(lon * 20) * math.cos(lat * 25) +
                        30 * math.sin(lon * 15) * math.sin(lat * 18) +
                        20 * math.cos(lon * 12) * math.cos(lat * 22)
                    )
                    
                    elevation = max(0, base_elevation + variation)
                    f.write(f"{lon} {lat} {elevation:.1f}\n")
        
        # Convert XYZ to GeoTIFF using GDAL
        cmd = [
            "gdal_translate",
            "-of", "GTiff",
            "-a_srs", "EPSG:4326",  # WGS84
            "-ot", "Float32",
            str(temp_xyz),
            str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Clean up temporary file
        temp_xyz.unlink(missing_ok=True)
        
        if Path(output_file).exists():
            print(f"✓ Created elevation data: {output_file}")
            return str(output_file)
        else:
            print("⚠ Elevation data creation failed")
            return None
            
    except Exception as e:
        print(f"⚠ Error creating elevation data: {e}")
        # Clean up on error
        Path("temp_elevation.xyz").unlink(missing_ok=True)
        return None


def generate_contour_lines(elevation_file, output_dir, interval=10):
    """
    Generate contour lines from elevation data using GDAL
    
    Args:
        elevation_file: Path to elevation raster (GeoTIFF)
        output_dir: Directory to save contour shapefiles
        interval: Contour interval in meters
    
    Returns:
        Path to contour shapefile or None if failed
    """
    print(f"📏 Generating contour lines (interval: {interval}m)...")
    
    if not Path(elevation_file).exists():
        print(f"⚠ Elevation file not found: {elevation_file}")
        return None
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    contour_file = output_dir / "contours.shp"
    
    try:
        # Use gdal_contour to generate contour lines
        cmd = [
            "gdal_contour",
            "-a", "elevation",  # Attribute name for elevation values
            "-i", str(interval),  # Contour interval
            "-f", "ESRI Shapefile",
            str(elevation_file),
            str(contour_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if contour_file.exists():
            # Get feature count for reporting
            try:
                info_result = subprocess.run(
                    ["ogrinfo", "-so", str(contour_file)], 
                    capture_output=True, text=True, check=True
                )
                feature_count = "unknown"
                for line in info_result.stdout.split('\n'):
                    if 'Feature Count:' in line:
                        feature_count = line.split(':')[1].strip()
                        break
                
                print(f"✓ Generated contour lines: {contour_file}")
                print(f"  Features: {feature_count} contour lines")
                print(f"  Interval: {interval}m")
                
                return str(contour_file)
            except:
                print(f"✓ Generated contour lines: {contour_file}")
                return str(contour_file)
        else:
            print("⚠ Contour generation completed but no output file found")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"⚠ Error generating contour lines:")
        print(f"  Command: {' '.join(cmd)}")
        error_msg = e.stderr.strip() if e.stderr else "No error details available"
        print(f"  Error: {error_msg}")
        return None
    except Exception as e:
        print(f"⚠ Unexpected error in contour generation: {e}")
        return None


def process_elevation_and_contours(bbox, data_dir, contour_interval=10, enable_contours=True):
    """
    Main function to handle elevation data and contour generation
    
    Args:
        bbox: Bounding box dictionary with north, south, east, west
        data_dir: Directory for output files
        contour_interval: Elevation interval for contour lines in meters
        enable_contours: Whether to generate contours
    
    Returns:
        Dictionary with paths to generated files or None if disabled/failed
    """
    if not enable_contours:
        print("📏 Contour generation disabled")
        return None
    
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    elevation_file = data_dir / "elevation_data.tif"
    
    # Download/generate elevation data
    if not elevation_file.exists():
        result = download_elevation_data(bbox, str(elevation_file))
        if not result:
            print("⚠ Could not obtain elevation data, skipping contours")
            return None
    else:
        print(f"📁 Using existing elevation data: {elevation_file}")
    
    # Generate contour lines
    contour_file = generate_contour_lines(str(elevation_file), str(data_dir), contour_interval)
    
    if contour_file:
        return {
            'elevation_file': str(elevation_file),
            'contour_file': contour_file,
            'interval': contour_interval
        }
    else:
        return None