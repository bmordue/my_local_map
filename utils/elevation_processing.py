"""Elevation data processing and hillshading utilities"""

import math
import struct
import subprocess
from pathlib import Path


def calculate_elevation_bbox(bbox, buffer_km=1.0):
    """Calculate elevation data bounding box with buffer for hillshading"""
    # Add buffer to ensure good hillshading at edges
    lat_buffer = buffer_km / 111.0  # ~1 degree = 111 km
    lon_buffer = buffer_km / (111.0 * math.cos(math.radians((bbox['north'] + bbox['south']) / 2.0)))  # Adjust for latitude
    
    return {
        'west': bbox['west'] - lon_buffer,
        'east': bbox['east'] + lon_buffer,
        'south': bbox['south'] - lat_buffer,
        'north': bbox['north'] + lat_buffer
    }


def generate_contours(elevation_file, contours_file, interval=10):
    """Generate contour lines from elevation data using GDAL"""
    try:
        # Use gdal_contour to generate contour lines from elevation data
        cmd = [
            'gdal_contour',
            '-a', 'elevation',  # Attribute name for elevation values
            '-i', str(interval),  # Contour interval
            str(elevation_file),
            str(contours_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Generated contours: {contours_file}")
            return True
        else:
            print(f"⚠ Warning: Failed to generate contours: {result.stderr}")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: gdal_contour command failed: {e}")
        return False
    except FileNotFoundError:
        print("⚠ Warning: gdal_contour not available")
        return False


def download_elevation_data(bbox, output_file, resolution=30):
    """
    Download elevation data for the given bounding box.
    For production use, this would connect to real elevation data sources.
    For now, creates a synthetic DEM for demonstration.
    """
    print("📊 Generating elevation data for hillshading...")
    
    # Create synthetic elevation data (since we can't access external DEM sources in sandbox)
    # This creates a simple elevation model based on distance from center
    try:
        # Try to use GDAL Python bindings first
        try:
            from osgeo import gdal, osr
            use_gdal_python = True
        except ImportError:
            use_gdal_python = False
        
        # Create a simple synthetic DEM
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lon = (bbox['west'] + bbox['east']) / 2
        
        width = max(100, int((bbox['east'] - bbox['west']) * 111120 * math.cos(math.radians(center_lat)) / resolution))
        height = max(100, int((bbox['north'] - bbox['south']) * 111120 / resolution))
        
        if use_gdal_python:
            # Use GDAL Python bindings - create elevation data with basic Python lists
            elevation_data = []
            for j in range(height):
                row = []
                for i in range(width):
                    # Normalize coordinates to 0-1 range
                    x_norm = i / width if width > 1 else 0.5
                    y_norm = j / height if height > 1 else 0.5
                    
                    # Simple elevation model: higher in the center, lower at edges
                    dist_from_center = ((x_norm - 0.5) ** 2 + (y_norm - 0.5) ** 2) ** 0.5
                    elevation = 100 + (200 * (1 - min(1.0, dist_from_center * 2)))  # 100-300m elevation
                    row.append(elevation)
                elevation_data.append(row)
            
            # Create GeoTIFF file directly
            driver = gdal.GetDriverByName('GTiff')
            ds = driver.Create(str(output_file), width, height, 1, gdal.GDT_Float32,
                              options=['COMPRESS=LZW'])
            
            if ds is None:
                print("Warning: Could not create elevation GeoTIFF file")
                return False
            
            # Set geotransform
            geotransform = [
                bbox['west'],                           # x origin (top left)
                (bbox['east'] - bbox['west']) / width,  # x pixel size
                0,                                      # x rotation
                bbox['north'],                          # y origin (top left) 
                0,                                      # y rotation
                (bbox['south'] - bbox['north']) / height # y pixel size (negative)
            ]
            ds.SetGeoTransform(geotransform)
            
            # Set projection to WGS84
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            ds.SetProjection(srs.ExportToWkt())
            
            # Write elevation data row by row
            band = ds.GetRasterBand(1)
            for j, row in enumerate(elevation_data):
                band.WriteRaster(0, j, width, 1, struct.pack('f' * width, *row))
            band.SetNoDataValue(-9999)
            
            # Close dataset
            ds = None
            
            print(f"Generated synthetic elevation data: {output_file}")
            return True
        else:
            # Fallback: create a simple grayscale image and convert to GeoTIFF
            from PIL import Image
            
            # Create elevation as grayscale image
            img_data = []
            for j in range(height):
                for i in range(width):
                    # Normalize coordinates to 0-1 range
                    x_norm = i / width if width > 1 else 0.5
                    y_norm = j / height if height > 1 else 0.5
                    
                    # Simple elevation model: convert to grayscale (0-255)
                    dist_from_center = ((x_norm - 0.5) ** 2 + (y_norm - 0.5) ** 2) ** 0.5
                    elevation = 100 + (200 * (1 - min(1.0, dist_from_center * 2)))  # 100-300m elevation
                    gray_value = int((elevation - 100) / 200 * 255)  # normalize to 0-255
                    img_data.append(gray_value)
            
            # Create grayscale image
            temp_dir = Path(output_file).parent
            temp_png = temp_dir / "temp_elevation.png"
            
            img = Image.new('L', (width, height))
            img.putdata(img_data)
            img.save(temp_png)
            
            # Convert to GeoTIFF using gdal_translate
            cmd = [
                'gdal_translate',
                '-of', 'GTiff',
                '-a_srs', 'EPSG:4326',
                '-a_ullr', str(bbox['west']), str(bbox['north']), str(bbox['east']), str(bbox['south']),
                '-co', 'COMPRESS=LZW',
                str(temp_png),
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            temp_png.unlink(missing_ok=True)
            
            if result.returncode != 0:
                print(f"Warning: Could not generate elevation data: {result.stderr}")
                return False
            
            print(f"Generated synthetic elevation data: {output_file}")
            return True
        
    except Exception as e:
        print(f"Warning: Could not generate elevation data: {e}")
        return False


def generate_hillshade(dem_file, output_file, config):
    """Generate hillshade from DEM using GDAL"""
    try:
        cmd = [
            'gdaldem', 'hillshade',
            str(dem_file),
            str(output_file),
            '-z', str(config.get('z_factor', 1.0)),
            '-s', str(config.get('scale', 111120)),
            '-az', str(config.get('azimuth', 315)),
            '-alt', str(config.get('altitude', 45)),
            '-of', 'GTiff',
            '-co', 'COMPRESS=LZW'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error generating hillshade: {result.stderr}")
            return False
        
        print(f"✓ Generated hillshade: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error generating hillshade: {e}")
        return False


def process_elevation_for_hillshading(bbox, area_config, data_dir):
    """Main function to process elevation data and generate hillshade and contours"""
    hillshade_config = area_config.get('hillshading', {})
    contours_config = area_config.get('contours', {})
    
    # Check if either hillshading or contours are enabled
    hillshading_enabled = hillshade_config.get('enabled', False)
    contours_enabled = contours_config.get('enabled', False)
    
    if not (hillshading_enabled or contours_enabled):
        print("📊 Hillshading and contours disabled in configuration")
        return None
    
    print("📊 Processing elevation data for hillshading...")
    
    # Create data directory if needed
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    
    # Calculate buffered bbox for elevation data
    elev_bbox = calculate_elevation_bbox(bbox)
    
    # File paths
    dem_file = data_path / "elevation.tif"
    hillshade_file = data_path / "hillshade.tif"
    contours_file = data_path / "contours.shp"
    
    # Download/generate elevation data
    if not download_elevation_data(elev_bbox, dem_file):
        return None
    
    # Generate hillshade if enabled
    hillshade_result = None
    if hillshading_enabled:
        if generate_hillshade(dem_file, hillshade_file, hillshade_config):
            hillshade_result = str(hillshade_file)
    
    # Generate contours if enabled
    contours_result = None
    if contours_enabled:
        interval = contours_config.get('interval', 10)
        if generate_contours(dem_file, contours_file, interval):
            contours_result = str(contours_file)
    
    return hillshade_result