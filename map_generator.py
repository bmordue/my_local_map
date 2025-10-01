#!/usr/bin/env python3
"""
Lightweight A3 Tourist Map Generator for Aberdeenshire
Uses configuration-driven approach for maximum flexibility
"""

import argparse
import logging
import os
from pathlib import Path

from utils.config import (
    calculate_pixel_dimensions,
    load_area_config,
    load_output_format,
)
from utils.data_processing import calculate_bbox
from utils.logging_config import setup_logging, get_logger

# from utils.download_icons import download_icons # not needed - icons are already present

# Configuration will be loaded dynamically

logger = get_logger(__name__)


def main(area_name="lumsden", verbose=False):
    """
    Main map generation function - orchestrates the complete workflow.
    
    Args:
        area_name: Name of the geographic area to generate map for
        verbose: Enable verbose/debug logging output
        
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Set up logging based on verbose flag
    setup_logging(verbose=verbose)
    
    logger.info("🗺️  My Local Map Generator - Multi-Area Support")
    logger.info("=" * 50)
    logger.info(f"📍 Area: {area_name.title()}")

    # Load and validate configuration
    try:
        area_config = load_area_config(area_name)
    except KeyError:
        logger.error(f"Area '{area_name}' not found in configuration.")
        logger.info("Available areas:")
        from utils.config import list_areas

        for area in list_areas():
            logger.info(f"  - {area}")
        return 1

    output_format = load_output_format("A3")
    width_px, height_px = calculate_pixel_dimensions(output_format)

    # Display area information
    bbox = calculate_bbox(
        area_config["center"]["lat"],
        area_config["center"]["lon"],
        area_config["coverage"]["width_km"],
        area_config["coverage"]["height_km"],
    )
    logger.info(f"📍 Area: {area_config['name']} ({area_config['center']['lat']}, {area_config['center']['lon']})")
    logger.info(f"📏 Coverage: {area_config['coverage']['width_km']}×{area_config['coverage']['height_km']}km")
    logger.info(f"🎯 Scale: 1:{area_config['scale']:,}")
    logger.info("")

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Execute data processing pipeline
    from utils.data_pipeline import process_data_pipeline
    osm_data_dir, hillshade_available, pipeline_success = process_data_pipeline(
        area_name, area_config, bbox, data_dir
    )
    
    if not pipeline_success:
        return 1

    # Run quality validation if enabled
    from utils.quality_validation import run_enhanced_data_validation
    run_enhanced_data_validation(bbox)

    # Execute map rendering workflow
    from utils.map_renderer import execute_map_rendering
    rendering_success = execute_map_rendering(
        area_name, area_config, output_format, bbox, 
        osm_data_dir, hillshade_available, width_px, height_px
    )

    return 0 if rendering_success else 1


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate a tourist map for a specified area in Aberdeenshire"
    )
    parser.add_argument(
        "area",
        nargs="?",
        default="lumsden",
        help="The area to generate a map for (default: lumsden)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose/debug logging output"
    )

    # Parse arguments
    args = parser.parse_args()

    # Run main with the specified area and verbose flag
    import sys

    sys.exit(main(args.area, verbose=args.verbose))
