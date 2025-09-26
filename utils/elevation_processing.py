"""Elevation data processing and hillshading utilities"""

import math
import struct
import subprocess
from pathlib import Path


def calculate_elevation_bbox(bbox, buffer_km=1.0):
    """Calculate elevation data bounding box with buffer for hillshading"""
    # Add buffer to ensure good hillshading at edges
    lat_buffer = buffer_km / 111.0  # ~1 degree = 111 km
    lon_buffer = buffer_km / (
        111.0 * math.cos(math.radians((bbox["north"] + bbox["south"]) / 2.0))
    )  # Adjust for latitude

    return {
        "west": bbox["west"] - lon_buffer,
        "east": bbox["east"] + lon_buffer,
        "south": bbox["south"] - lat_buffer,
        "north": bbox["north"] + lat_buffer,
    }


def generate_contours(elevation_file, contours_file, interval=10):
    """Generate contour lines from elevation data using GDAL"""
    try:
        # Use gdal_contour to generate contour lines from elevation data
        cmd = [
            "gdal_contour",
            "-a",
            "elevation",  # Attribute name for elevation values
            "-i",
            str(interval),  # Contour interval
            str(elevation_file),
            str(contours_file),
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


def download_elevation_data(
    bbox, output_file, resolution=30, force_subprocess=False, dem_source="srtm"
):
    """
    Download elevation data for the given bounding box.
    Only supports real DEM sources - synthetic data generation removed.

    Args:
        bbox: Bounding box dictionary
        output_file: Path to output file
        resolution: Resolution in meters
        force_subprocess: Force use of subprocess (for testing)
        dem_source: Source of DEM data ("srtm", "aster", "os_terrain", "eu_dem")
        
    Returns:
        False - Real DEM data sources not yet implemented
    """
    print(f"📊 Attempting to download real elevation data from {dem_source}...")

    # Handle different DEM sources
    if dem_source == "srtm":
        return _download_srtm_elevation_data(bbox, output_file, resolution)
    elif dem_source in ["aster", "os_terrain", "eu_dem"]:
        print(f"❌ DEM source '{dem_source}' not yet implemented")
        print("❌ Real DEM data download functionality required")
        print("❌ Synthetic elevation data generation removed per requirements")
        return False
    else:
        print(f"❌ Unknown DEM source '{dem_source}'")
        print("❌ Supported sources: srtm, aster, os_terrain, eu_dem")
        print("❌ Synthetic elevation data generation removed")
        return False


def _download_srtm_elevation_data(bbox, output_file, resolution=30):
    """
    Download SRTM elevation data for the given bounding box.
    
    Real SRTM data implementation required - synthetic data generation removed.

    Args:
        bbox: Bounding box dictionary
        output_file: Path to output file
        resolution: Resolution in meters
    
    Returns:
        False - Real SRTM data download not implemented
    """
    try:
        # Calculate SRTM tile numbers (1 degree tiles)
        # SRTM tiles are named like NXXEYYY or NXXWYYY
        south_tile = int(math.floor(bbox["south"]))
        north_tile = int(math.floor(bbox["north"]))
        west_tile = int(math.floor(bbox["west"]))
        east_tile = int(math.floor(bbox["east"]))

        print(
            f"❌ SRTM data download not implemented for tiles: "
            f"lat {south_tile} to {north_tile}, lon {west_tile} to {east_tile}"
        )
        print("❌ Real DEM data sources (SRTM, ASTER, OS Terrain) required")
        print("❌ Synthetic elevation data generation has been removed")
        
        return False

    except Exception as e:
        print(f"❌ Error attempting SRTM data download: {e}")
        print("❌ Real DEM data sources required - synthetic fallback removed")
        return False


# Synthetic elevation data generation removed per issue requirements
# Real DEM data sources should be used instead


def generate_hillshade(dem_file, output_file, config):
    """Generate hillshade from DEM using GDAL"""
    try:
        cmd = [
            "gdaldem",
            "hillshade",
            str(dem_file),
            str(output_file),
            "-z",
            str(config.get("z_factor", 1.0)),
            "-s",
            str(config.get("scale", 111120)),
            "-az",
            str(config.get("azimuth", 315)),
            "-alt",
            str(config.get("altitude", 45)),
            "-of",
            "GTiff",
            "-co",
            "COMPRESS=LZW",
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
    hillshade_config = area_config.get("hillshading", {})
    contours_config = area_config.get("contours", {})
    elevation_config = area_config.get("elevation", {})

    # Check if either hillshading or contours are enabled
    hillshading_enabled = hillshade_config.get("enabled", False)
    contours_enabled = contours_config.get("enabled", False)

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

    # Get DEM source from configuration
    dem_source = elevation_config.get("source", "synthetic")

    # Download/generate elevation data
    if not download_elevation_data(elev_bbox, dem_file, dem_source=dem_source):
        return None

    # Generate hillshade if enabled
    hillshade_result = None
    if hillshading_enabled:
        if generate_hillshade(dem_file, hillshade_file, hillshade_config):
            hillshade_result = str(hillshade_file)

    # Generate contours if enabled
    contours_result = None
    if contours_enabled:
        interval = contours_config.get("interval", 10)
        if generate_contours(dem_file, contours_file, interval):
            contours_result = str(contours_file)

    return hillshade_result
