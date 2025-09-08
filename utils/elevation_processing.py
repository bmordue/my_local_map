"""Elevation data processing and hillshading utilities"""

import os
import subprocess
import tempfile
from pathlib import Path
import requests


def calculate_elevation_bbox(bbox, buffer_km=1.0):
    """Calculate elevation data bounding box with buffer for hillshading"""
    # Add buffer to ensure good hillshading at edges
    lat_buffer = buffer_km / 111.0  # ~1 degree = 111 km
    lon_buffer = buffer_km / (111.0 * abs(bbox['north'] + bbox['south']) / 2.0)  # Adjust for latitude
    
    return {
        'west': bbox['west'] - lon_buffer,
        'east': bbox['east'] + lon_buffer,
        'south': bbox['south'] - lat_buffer,
        'north': bbox['north'] + lat_buffer
    }


def download_elevation_data(bbox, output_file, resolution=30):
    """
    Download elevation data for the given bounding box.
    For production use, this would connect to real elevation data sources.
    For now, creates a synthetic DEM for demonstration.
    """
    print(f"📊 Generating elevation data for hillshading...")
    
    # Create synthetic elevation data (since we can't access external DEM sources in sandbox)
    # This creates a simple elevation model based on distance from center
    try:
        # Create a simple synthetic DEM using gdal_translate and VRT
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lon = (bbox['west'] + bbox['east']) / 2
        
        width = max(100, int((bbox['east'] - bbox['west']) * 111120 / resolution))  # approximate meters
        height = max(100, int((bbox['north'] - bbox['south']) * 111120 / resolution))
        
        # Create a temporary raw binary file with synthetic elevation data
        temp_dir = Path(output_file).parent
        temp_raw = temp_dir / "temp_elevation.raw"
        
        # Generate synthetic elevation as binary data
        import struct
        with open(temp_raw, 'wb') as f:
            for j in range(height):
                for i in range(width):
                    # Normalize coordinates to 0-1 range
                    x_norm = i / width if width > 1 else 0.5
                    y_norm = j / height if height > 1 else 0.5
                    
                    # Simple elevation model: higher in the center, lower at edges
                    dist_from_center = ((x_norm - 0.5) ** 2 + (y_norm - 0.5) ** 2) ** 0.5
                    elevation = 100 + (200 * (1 - min(1.0, dist_from_center * 2)))  # 100-300m elevation
                    
                    # Write as 32-bit float
                    f.write(struct.pack('f', elevation))
        
        # Create VRT to describe the raw data
        vrt_content = f'''<VRTDataset rasterXSize="{width}" rasterYSize="{height}">
  <SRS>EPSG:4326</SRS>
  <GeoTransform>{bbox['west']},{(bbox['east']-bbox['west'])/width},0,{bbox['north']},0,{(bbox['south']-bbox['north'])/height}</GeoTransform>
  <VRTRasterBand dataType="Float32" band="1">
    <SimpleSource>
      <SourceFilename relativeToVRT="1">temp_elevation.raw</SourceFilename>
      <SourceBand>1</SourceBand>
      <SourceProperties RasterXSize="{width}" RasterYSize="{height}" DataType="Float32"/>
    </SimpleSource>
  </VRTRasterBand>
</VRTDataset>'''
        
        temp_vrt = temp_dir / "temp_elevation.vrt"
        with open(temp_vrt, 'w') as f:
            f.write(vrt_content)
        
        # Convert VRT to GeoTIFF
        cmd = [
            'gdal_translate',
            '-of', 'GTiff',
            '-co', 'COMPRESS=LZW',
            str(temp_vrt),
            str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Could not generate elevation data: {result.stderr}")
            return False
        
        # Clean up temp files
        temp_raw.unlink(missing_ok=True)
        temp_vrt.unlink(missing_ok=True)
        
        print(f"✓ Generated synthetic elevation data: {output_file}")
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
    """Main function to process elevation data and generate hillshade"""
    hillshade_config = area_config.get('hillshading', {})
    
    if not hillshade_config.get('enabled', False):
        print("📊 Hillshading disabled in configuration")
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
    
    # Download/generate elevation data
    if not download_elevation_data(elev_bbox, dem_file):
        return None
    
    # Generate hillshade
    if not generate_hillshade(dem_file, hillshade_file, hillshade_config):
        return None
    
    return str(hillshade_file)