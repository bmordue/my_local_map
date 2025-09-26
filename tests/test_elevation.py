#!/usr/bin/env python3
"""Test script for elevation data processing"""

import os
import sys
from pathlib import Path

# Add the utils directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from elevation_processing import calculate_elevation_bbox, download_elevation_data


def main():
    # Define a test bounding box for Lumsden area
    test_bbox = {"south": 57.25, "north": 57.35, "west": -2.95, "east": -2.85}

    # Calculate buffered bbox for elevation data
    elev_bbox = calculate_elevation_bbox(test_bbox)

    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Test synthetic elevation data
    print("Testing synthetic elevation data generation...")
    synthetic_file = output_dir / "synthetic_elevation.tif"
    if download_elevation_data(elev_bbox, str(synthetic_file), dem_source="synthetic"):
        print(f"✓ Successfully generated synthetic elevation data: {synthetic_file}")
    else:
        print("✗ Failed to generate synthetic elevation data")

    # Test SRTM elevation data (will fall back to synthetic)
    print("\nTesting SRTM elevation data generation...")
    srtm_file = output_dir / "srtm_elevation.tif"
    if download_elevation_data(elev_bbox, str(srtm_file), dem_source="srtm"):
        print(f"✓ Successfully generated SRTM-like elevation data: {srtm_file}")
    else:
        print("✗ Failed to generate SRTM-like elevation data")


if __name__ == "__main__":
    main()
