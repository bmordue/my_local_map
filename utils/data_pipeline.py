"""
Data Pipeline Management Module

Handles the sequential data processing steps needed for map generation:
- OSM data validation and downloading
- Shapefile conversion
- Elevation, hillshading, and contour processing (driven by area config)
"""

import logging
import os
from pathlib import Path

from .data_processing import (convert_osm_to_shapefiles, download_osm_data,
                              validate_osm_data_quality)
from .elevation_processing import process_elevation_for_hillshading

logger = logging.getLogger(__name__)


def prepare_osm_data(area_name, area_config, bbox, data_dir):
    """
    Prepare OSM data for map generation.

    Args:
        area_name: Name of the geographic area
        area_config: Area configuration dictionary
        bbox: Bounding box for the area
        data_dir: Path object for data directory

    Returns:
        tuple: (osm_file_path, success_flag)
    """
    # Determine OSM file path (configurable, default to data/lumsden_area.osm)
    osm_file_path = area_config.get("osm_file", f"data/{area_name}_area.osm")
    osm_file = Path(osm_file_path)

    if not osm_file.exists():
        logger.info(f"OSM file not found at {osm_file}. Downloading...")
        if not download_osm_data(bbox, str(osm_file)):
            logger.error("Failed to download OSM data")
            return None, False

        # Validate the downloaded data quality
        if not validate_osm_data_quality(str(osm_file)):
            logger.warning("Downloaded OSM data has low quality")
            logger.warning("Map may have limited features, but continuing...")
    else:
        logger.info(f"📁 Using existing OSM data: {osm_file}")
        # Also validate existing data
        validate_osm_data_quality(str(osm_file))

    return str(osm_file), True


def process_data_pipeline(area_name, area_config, bbox, data_dir):
    """
    Execute the complete data processing pipeline.

    Args:
        area_name: Name of the geographic area
        area_config: Area configuration dictionary
        bbox: Bounding box for the area
        data_dir: Path object for data directory

    Returns:
        tuple: (osm_data_dir, hillshade_available, success_flag)
    """
    # Prepare OSM data
    osm_file, osm_success = prepare_osm_data(area_name, area_config, bbox, data_dir)
    if not osm_success:
        return None, False, False

    # Convert to shapefiles (no database!)
    logger.info("\n🔄 Converting OSM data to shapefiles...")
    osm_data_dir = convert_osm_to_shapefiles(osm_file)

    # Process elevation data for hillshading and contours if enabled.
    # process_elevation_for_hillshading downloads DEM data once and
    # generates both hillshade and contour outputs based on the
    # area_config "hillshading" and "contours" sections.
    if osm_data_dir:
        logger.info("\n🏔️  Processing elevation data (hillshading & contours)...")
        try:
            hillshade_file = process_elevation_for_hillshading(
                bbox, area_config, osm_data_dir
            )
        except RuntimeError as e:
            logger.error(f"❌ Critical elevation data failure: {e}")
            logger.error("❌ Cannot proceed without required DEM data")
            return None, False, False
    else:
        logger.warning("Skipping elevation processing due to missing OSM data directory")
        hillshade_file = None
    hillshade_available = hillshade_file is not None

    return osm_data_dir, hillshade_available, True
