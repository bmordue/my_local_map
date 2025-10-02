#!/usr/bin/env python3
"""Test script for elevation data processing - updated for real DEM sources only"""

import os
import sys
from pathlib import Path

# Add the utils directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from elevation_processing import (calculate_elevation_bbox,
                                  download_elevation_data)


def main():
    # Define a test bounding box for Lumsden area
    test_bbox = {"south": 57.25, "north": 57.35, "west": -2.95, "east": -2.85}

    # Calculate buffered bbox for elevation data
    elev_bbox = calculate_elevation_bbox(test_bbox)

    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Test that synthetic elevation data is no longer available
    print("Testing that synthetic elevation data generation has been removed...")
    synthetic_file = output_dir / "synthetic_elevation.tif"
    result = download_elevation_data(
        elev_bbox, str(synthetic_file), dem_source="synthetic"
    )
    if not result:
        print("✓ Successfully confirmed synthetic elevation data generation removed")
    else:
        print(
            "✗ Synthetic elevation data generation still available (should be removed)"
        )

    # Test SRTM elevation data (should fail gracefully without real implementation)
    print("\nTesting SRTM elevation data (should fail gracefully)...")
    srtm_file = output_dir / "srtm_elevation.tif"
    result = download_elevation_data(elev_bbox, str(srtm_file), dem_source="srtm")
    if not result:
        print("✓ SRTM elevation data correctly fails without real DEM implementation")
    else:
        print("✗ SRTM elevation data unexpectedly succeeded")


if __name__ == "__main__":
    main()
