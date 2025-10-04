#!/usr/bin/env python3
"""
Diagnostic script to test DEM download functionality
"""

import logging
from pathlib import Path
from utils.elevation_processing import download_elevation_data

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Test bbox for Lumsden area
bbox = {
    "north": 57.37,
    "south": 57.26,
    "east": -2.82,
    "west": -2.95
}

output_file = Path("test_elevation.tif")

logger.info("Starting DEM download diagnostic test")
logger.info(f"Bbox: {bbox}")
logger.info(f"Output: {output_file}")

try:
    success = download_elevation_data(
        bbox,
        output_file,
        dem_source="srtm",
        allow_synthetic_fallback=True
    )
    
    if success:
        logger.info(f"SUCCESS: DEM downloaded to {output_file}")
        logger.info(f"File size: {output_file.stat().st_size} bytes")
    else:
        logger.error("FAILED: DEM download returned False")
        
except Exception as e:
    logger.error(f"EXCEPTION: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
