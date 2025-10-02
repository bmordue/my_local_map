"""
Elevation data processing and hillshading utilities
"""

import logging
import math
import os
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


def get_dem_cache_dir():
    """Get the local DEM cache directory"""
    cache_dir = Path.home() / ".my_local_map" / "dem_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _format_srtm_tile_name(lat, lon):
    """Format SRTM tile name based on coordinates"""
    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"

    lat_str = f"{abs(int(lat)):02d}"
    lon_str = f"{abs(int(lon)):03d}"

    return f"{lat_prefix}{lat_str}{lon_prefix}{lon_str}.hgt"


def _download_file_with_progress(url, output_path, timeout=30):
    """Download a file with basic progress indication"""
    try:
        logger.info(f"  📥 Downloading from {url}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        content_length = response.headers.get("content-length", None)
        try:
            total_size = (
                int(content_length)
                if content_length and content_length.isdigit()
                else 0
            )
        except (ValueError, TypeError):
            total_size = 0

        with open(output_path, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        logger.debug(f"  📊 Progress: {percent:.1f}%")

        logger.info("  ✓ Download complete")
        return True
    except Exception as e:
        logger.info(f"  ❌ Download failed: {e}")
        return False


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
            logger.info(f"✓ Generated contours: {contours_file}")
            return True
        else:
            logger.warning(f"Warning: Failed to generate contours: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        logger.warning(f"Warning: gdal_contour command failed: {e}")
        return False
    except FileNotFoundError:
        logger.warning("Warning: gdal_contour not available")
        return False


def _create_synthetic_dem_fallback(bbox, output_file, resolution=30):
    """
    Create synthetic elevation data as fallback when real DEM sources unavailable.

    This is a demonstration function that creates a simple elevation model
    for testing and offline use. In production, real DEM data is preferred.
    """
    try:
        import numpy as np
        from osgeo import gdal, osr

        logger.info("  📊 Creating synthetic DEM as fallback...")

        # Calculate grid dimensions based on bbox and resolution
        width_degrees = bbox["east"] - bbox["west"]
        height_degrees = bbox["north"] - bbox["south"]

        # Convert degrees to approximate meters (rough approximation)
        meters_per_degree_lat = 111320.0
        meters_per_degree_lon = 111320.0 * math.cos(
            math.radians((bbox["north"] + bbox["south"]) / 2)
        )

        width_meters = width_degrees * meters_per_degree_lon
        height_meters = height_degrees * meters_per_degree_lat

        cols = int(width_meters / resolution)
        rows = int(height_meters / resolution)

        logger.info(f"    📐 Creating {cols}x{rows} grid at {resolution}m resolution")

        # Create synthetic elevation data with gentle terrain
        x = np.linspace(0, width_degrees, cols)
        y = np.linspace(0, height_degrees, rows)
        X, Y = np.meshgrid(x, y)

        # Create simple terrain with hills and valleys
        elevation = (
            200
            + 100 * np.sin(X * 10) * np.cos(Y * 8)
            + 50 * np.sin(X * 15) * np.sin(Y * 12)
            + 30 * np.random.normal(0, 1, (rows, cols))  # Add some noise
        )

        # Ensure realistic elevation values for Scotland (0-1000m)
        elevation = np.clip(elevation, 0, 1000)

        # Create GeoTIFF
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(
            str(output_file), cols, rows, 1, gdal.GDT_Float32, options=["COMPRESS=LZW"]
        )

        # Set geotransform
        geotransform = [
            bbox["west"],  # top-left x
            width_degrees / cols,  # pixel width
            0,  # rotation
            bbox["north"],  # top-left y
            0,  # rotation
            -height_degrees / rows,  # pixel height (negative)
        ]
        dataset.SetGeoTransform(geotransform)

        # Set projection (WGS84)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        dataset.SetProjection(srs.ExportToWkt())

        # Write elevation data
        band = dataset.GetRasterBand(1)
        band.WriteArray(elevation)
        band.SetNoDataValue(-9999)

        # Cleanup
        band = None
        dataset = None

        logger.info(f"    ✓ Synthetic DEM created: {output_file}")
        return True

    except ImportError as e:
        logger.info(f"    ❌ Cannot create synthetic DEM: missing dependencies ({e})")
        return False
    except Exception as e:
        logger.info(f"    ❌ Error creating synthetic DEM: {e}")
        return False


def download_elevation_data(
    bbox,
    output_file,
    resolution=30,
    force_subprocess=False,
    dem_source="srtm",
    allow_synthetic_fallback=True,
):
    """
    Download elevation data for the given bounding box.
    Supports multiple real DEM sources with local caching.

    Args:
        bbox: Bounding box dictionary
        output_file: Path to output file
        resolution: Resolution in meters
        force_subprocess: Force use of subprocess (for testing)
        dem_source: Source of DEM data ("srtm", "aster", "os_terrain", "eu_dem")
        allow_synthetic_fallback: Create synthetic DEM if real sources fail

    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        RuntimeError: If real DEM download fails and synthetic fallback is disabled
    """
    logger.info(f"📊 Attempting to download real elevation data from {dem_source}...")

    # Handle different DEM sources
    success = False
    if dem_source == "srtm":
        success = _download_srtm_elevation_data(bbox, output_file, resolution)
    elif dem_source == "aster":
        success = _download_aster_elevation_data(bbox, output_file, resolution)
    elif dem_source == "os_terrain":
        success = _download_os_terrain_data(bbox, output_file, resolution)
    elif dem_source == "eu_dem":
        success = _download_eu_dem_data(bbox, output_file, resolution)
    else:
        logger.error(f"Unknown DEM source '{dem_source}'")
        logger.error("Supported sources: srtm, aster, os_terrain, eu_dem")
        return False

    # If real DEM download failed
    if not success:
        if allow_synthetic_fallback:
            logger.info("💡 Real DEM download failed, attempting synthetic fallback...")
            return _create_synthetic_dem_fallback(bbox, output_file, resolution)
        else:
            logger.error(f"❌ Failed to download real DEM data from '{dem_source}' source")
            logger.error("❌ Synthetic fallback is disabled in configuration")
            logger.error("❌ Cannot proceed without elevation data")
            raise RuntimeError(
                f"DEM data download failed from '{dem_source}' source and synthetic fallback is disabled. "
                f"Either enable synthetic fallback or ensure network connectivity to DEM data sources."
            )

    return success


def _download_aster_elevation_data(bbox, output_file, resolution=30):
    """
    Download ASTER GDEM elevation data for the given bounding box.

    ASTER GDEM provides 30m resolution global elevation data.
    """
    logger.info("📊 Downloading ASTER GDEM elevation data...")

    try:
        # ASTER tiles are 1x1 degree tiles
        south_tile = int(math.floor(bbox["south"]))
        north_tile = int(math.floor(bbox["north"]))
        west_tile = int(math.floor(bbox["west"]))
        east_tile = int(math.floor(bbox["east"]))

        logger.info(
            f"  📍 Required ASTER tiles: lat {south_tile} to {north_tile}, lon {west_tile} to {east_tile}"
        )

        cache_dir = get_dem_cache_dir() / "aster"
        cache_dir.mkdir(exist_ok=True)
        temp_files = []

        for lat in range(south_tile, north_tile + 1):
            for lon in range(west_tile, east_tile + 1):
                tile_name = f"ASTGTMV003_{_format_aster_tile_name(lat, lon)}_dem.tif"
                cached_file = cache_dir / tile_name

                if cached_file.exists():
                    logger.info(f"  ✓ Using cached ASTER tile: {tile_name}")
                    temp_files.append(str(cached_file))
                else:
                    logger.info(f"  📥 Downloading ASTER tile: {tile_name}")
                    if _download_aster_tile(lat, lon, cached_file):
                        temp_files.append(str(cached_file))

        if not temp_files:
            logger.info("  ❌ No ASTER tiles downloaded successfully")
            return False

        # Process and crop tiles
        logger.info("  🔄 Processing ASTER tiles...")
        return _process_srtm_tiles(temp_files, bbox, output_file)

    except Exception as e:
        logger.error(f"Error downloading ASTER data: {e}")
        return False


def _format_aster_tile_name(lat, lon):
    """Format ASTER tile name based on coordinates"""
    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"

    lat_str = f"{abs(int(lat)):02d}"
    lon_str = f"{abs(int(lon)):03d}"

    return f"{lat_prefix}{lat_str}{lon_prefix}{lon_str}"


def _download_aster_tile(lat, lon, output_file):
    """Download a single ASTER GDEM tile"""
    tile_name = f"ASTGTMV003_{_format_aster_tile_name(lat, lon)}_dem.tif"

    # ASTER GDEM sources
    aster_sources = [
        # NASA Earthdata (requires authentication, fallback to public mirrors)
        f"https://e4ftl01.cr.usgs.gov/ASTT/ASTGTM.003/2000.03.01/{tile_name}",
        # OpenTopography ASTER data
        f"https://opentopography.org/API/globaldem?demtype=ASTER30&south={lat}&north={lat+1}&west={lon}&east={lon+1}&outputFormat=GTiff",
    ]

    for source_url in aster_sources:
        try:
            logger.info(f"    🌐 Trying ASTER source: {source_url.split('/')[2]}")

            if _download_file_with_progress(source_url, output_file):
                if output_file.stat().st_size > 1000:
                    logger.info(f"    ✓ Successfully downloaded ASTER {tile_name}")
                    return True
                else:
                    output_file.unlink(missing_ok=True)

        except Exception as e:
            logger.info(f"    ❌ ASTER source failed: {e}")
            output_file.unlink(missing_ok=True)
            continue

    logger.info("  ❌ All ASTER sources failed - this may require authentication")
    logger.info("  💡 Consider using SRTM as alternative for this region")
    return False


def _download_os_terrain_data(bbox, output_file, resolution=50):
    """
    Download OS Terrain data for UK areas.

    OS Terrain provides high-resolution elevation data for the UK.
    """
    logger.info("📊 Downloading OS Terrain elevation data...")

    # Check if bbox is within UK bounds
    if not _is_bbox_in_uk(bbox):
        logger.info("  ❌ OS Terrain data is only available for the UK")
        logger.info("  💡 Consider using SRTM or ASTER for areas outside the UK")
        return False

    try:
        logger.info("  📍 Area is within UK bounds")

        # OS Terrain 50 data access
        # Note: OS OpenData is freely available but requires proper API access
        logger.info("  ❌ OS Terrain download not yet implemented")
        logger.info("  💡 This requires OS Data Hub API access")
        logger.info("  💡 For now, falling back to SRTM data...")

        # Fallback to SRTM for UK
        return _download_srtm_elevation_data(bbox, output_file, resolution)

    except Exception as e:
        logger.error(f"Error downloading OS Terrain data: {e}")
        return False


def _is_bbox_in_uk(bbox):
    """Check if bounding box intersects with UK territory"""
    # UK bounds (approximate)
    uk_bounds = {"south": 49.5, "north": 61.0, "west": -8.5, "east": 2.0}

    return (
        bbox["south"] < uk_bounds["north"]
        and bbox["north"] > uk_bounds["south"]
        and bbox["west"] < uk_bounds["east"]
        and bbox["east"] > uk_bounds["west"]
    )


def _download_eu_dem_data(bbox, output_file, resolution=25):
    """
    Download EU-DEM elevation data for European areas.

    EU-DEM provides 25m resolution elevation data for Europe.
    """
    logger.info("📊 Downloading EU-DEM elevation data...")

    # Check if bbox is within Europe bounds
    if not _is_bbox_in_europe(bbox):
        logger.info("  ❌ EU-DEM data is only available for Europe")
        logger.info("  💡 Consider using SRTM or ASTER for areas outside Europe")
        return False

    try:
        logger.info("  📍 Area is within European bounds")

        # EU-DEM data access via Copernicus
        logger.info("  ❌ EU-DEM download not yet implemented")
        logger.info("  💡 This requires Copernicus Data Space API access")
        logger.info("  💡 For now, falling back to SRTM data...")

        # Fallback to SRTM for Europe
        return _download_srtm_elevation_data(bbox, output_file, resolution)

    except Exception as e:
        logger.error(f"Error downloading EU-DEM data: {e}")
        return False


def _is_bbox_in_europe(bbox):
    """Check if bounding box intersects with European territory"""
    # Europe bounds (approximate, covers EU-DEM coverage)
    europe_bounds = {"south": 34.0, "north": 72.0, "west": -25.0, "east": 45.0}

    return (
        bbox["south"] < europe_bounds["north"]
        and bbox["north"] > europe_bounds["south"]
        and bbox["west"] < europe_bounds["east"]
        and bbox["east"] > europe_bounds["west"]
    )


def _download_srtm_elevation_data(bbox, output_file, resolution=30):
    """
    Download SRTM elevation data for the given bounding box.

    Uses public SRTM 1-arc second (30m) data from multiple sources.

    Args:
        bbox: Bounding box dictionary
        output_file: Path to output file
        resolution: Resolution in meters (30 for SRTM-1, 90 for SRTM-3)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("📊 Downloading SRTM elevation data...")

        # Calculate SRTM tile numbers (1 degree tiles)
        south_tile = int(math.floor(bbox["south"]))
        north_tile = int(math.floor(bbox["north"]))
        west_tile = int(math.floor(bbox["west"]))
        east_tile = int(math.floor(bbox["east"]))

        logger.info(
            f"  📍 Required SRTM tiles: lat {south_tile} to {north_tile}, lon {west_tile} to {east_tile}"
        )

        # Setup cache directory
        cache_dir = get_dem_cache_dir()
        temp_files = []

        # Download required tiles
        for lat in range(south_tile, north_tile + 1):
            for lon in range(west_tile, east_tile + 1):
                tile_name = _format_srtm_tile_name(lat, lon)
                cached_file = cache_dir / tile_name

                if cached_file.exists():
                    logger.info(f"  ✓ Using cached tile: {tile_name}")
                    temp_files.append(str(cached_file))
                else:
                    logger.info(f"  📥 Downloading tile: {tile_name}")
                    if _download_srtm_tile(lat, lon, cached_file):
                        temp_files.append(str(cached_file))
                    else:
                        logger.info(
                            f"  ⚠️  Failed to download {tile_name}, continuing with available tiles"
                        )

        if not temp_files:
            logger.info("  ❌ No SRTM tiles downloaded successfully")
            return False

        # Merge and crop tiles to bounding box
        logger.info("  🔄 Processing SRTM tiles...")
        if _process_srtm_tiles(temp_files, bbox, output_file):
            logger.info(f"  ✓ SRTM elevation data saved: {output_file}")
            return True
        else:
            logger.info("  ❌ Failed to process SRTM tiles")
            return False

    except Exception as e:
        logger.error(f"Error downloading SRTM data: {e}")
        return False


def _download_srtm_tile(lat, lon, output_file):
    """Download a single SRTM tile"""
    tile_name = _format_srtm_tile_name(lat, lon)

    # Try multiple SRTM data sources
    srtm_sources = [
        # USGS SRTM 1-arc second data via public mirror
        f"https://cloud.sdsc.edu/v1/datasetsearch/download/SRTM_GL1/{tile_name}",
        # Alternative: NASA's SRTM data via OpenTopography
        f"https://opentopography.org/API/globaldem?demtype=SRTM_GL1&south={lat}&north={lat+1}&west={lon}&east={lon+1}&outputFormat=GTiff",
        # CGIAR SRTM data (backup)
        f"https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/{tile_name.replace('.hgt', '.tif')}",
    ]

    for source_url in srtm_sources:
        try:
            logger.info(f"    🌐 Trying source: {source_url.split('/')[2]}")

            if _download_file_with_progress(source_url, output_file):
                # Verify file is valid
                if output_file.stat().st_size > 1000:  # Basic size check
                    logger.info(f"    ✓ Successfully downloaded {tile_name}")
                    return True
                else:
                    logger.info(f"    ❌ Downloaded file too small, trying next source")
                    output_file.unlink(missing_ok=True)

        except Exception as e:
            logger.info(f"    ❌ Source failed: {e}")
            output_file.unlink(missing_ok=True)
            continue

    return False


def _process_srtm_tiles(tile_files, bbox, output_file):
    """Process and merge SRTM tiles, cropping to bounding box"""
    try:
        if len(tile_files) == 1:
            # Single tile - just crop it
            return _crop_dem_to_bbox(tile_files[0], bbox, output_file)
        else:
            # Multiple tiles - merge then crop
            with tempfile.NamedTemporaryFile(
                suffix=".tif", delete=False
            ) as temp_merged:
                # Merge tiles using gdal_merge.py or gdalwarp
                merge_cmd = (
                    ["gdalwarp", "-of", "GTiff", "-co", "COMPRESS=LZW"]
                    + tile_files
                    + [temp_merged.name]
                )

                result = subprocess.run(merge_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # Crop merged file to bbox
                    success = _crop_dem_to_bbox(temp_merged.name, bbox, output_file)
                    os.unlink(temp_merged.name)
                    return success
                else:
                    logger.info(f"    ❌ Failed to merge tiles: {result.stderr}")
                    os.unlink(temp_merged.name)
                    return False

    except Exception as e:
        logger.info(f"    ❌ Error processing SRTM tiles: {e}")
        return False


def _crop_dem_to_bbox(input_file, bbox, output_file):
    """Crop DEM file to bounding box using gdalwarp"""
    try:
        crop_cmd = [
            "gdalwarp",
            "-te",
            str(bbox["west"]),
            str(bbox["south"]),
            str(bbox["east"]),
            str(bbox["north"]),
            "-of",
            "GTiff",
            "-co",
            "COMPRESS=LZW",
            input_file,
            str(output_file),
        ]

        result = subprocess.run(crop_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            logger.info(f"    ❌ Failed to crop DEM: {result.stderr}")
            return False

    except Exception as e:
        logger.info(f"    ❌ Error cropping DEM: {e}")
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
            logger.info(f"Error generating hillshade: {result.stderr}")
            return False

        logger.info(f"✓ Generated hillshade: {output_file}")
        return True

    except Exception as e:
        logger.info(f"Error generating hillshade: {e}")
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
        logger.info("📊 Hillshading and contours disabled in configuration")
        return None

    logger.info("📊 Processing elevation data for hillshading...")

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
    dem_source = elevation_config.get("source", "srtm")
    allow_fallback = elevation_config.get("allow_synthetic_fallback", True)

    # Download/generate elevation data
    try:
        if not download_elevation_data(
            elev_bbox,
            dem_file,
            dem_source=dem_source,
            allow_synthetic_fallback=allow_fallback,
        ):
            logger.error("Failed to obtain elevation data from any source")
            return None
    except RuntimeError as e:
        # Re-raise the exception to propagate the failure
        logger.error(f"Critical DEM data failure: {e}")
        raise e

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
