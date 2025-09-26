#!/usr/bin/env python3
"""
Demonstration script showing OSM data integration capabilities
"""

import subprocess
import tempfile
from pathlib import Path

from utils.data_processing import (
    calculate_bbox,
    convert_osm_to_shapefiles,
    download_osm_data,
    validate_osm_data_quality,
)


def demonstrate_live_osm_integration():
    """Demonstrate live OSM data integration (when network available)"""
    print("🔍 OSM Live Data Integration Demonstration")
    print("=" * 50)

    # Calculate bbox for Lumsden area
    bbox = calculate_bbox(57.3167, -2.8833, 8, 12)
    print(f"Target area: {bbox}")

    # Test live download (will fail in sandboxed environment but shows capability)
    print("\n📡 Testing live OSM data download...")
    with tempfile.NamedTemporaryFile(suffix=".osm", delete=False) as tmp:
        success = download_osm_data(bbox, tmp.name)
        if success:
            print(f"✅ Live download successful: {tmp.name}")
            validate_osm_data_quality(tmp.name)
        else:
            print("❌ Live download failed - using offline mode")
            print("   In production: would use cached OSM data")

    # Show offline capability with existing data
    print("\n💾 Testing offline OSM data processing...")
    osm_file = "lumsden_area.osm"
    if Path(osm_file).exists():
        print(f"✅ Using offline OSM data: {osm_file}")

        # Validate data quality
        print("\n📊 Data Quality Analysis:")
        is_valid = validate_osm_data_quality(osm_file)

        if is_valid:
            print("\n🔄 Converting to shapefiles...")
            data_dir = convert_osm_to_shapefiles(osm_file)
            if data_dir:
                print(f"✅ Conversion successful: {data_dir}")

                # Show what features were extracted
                for layer in ["points", "lines", "multipolygons"]:
                    shp_file = Path(data_dir) / f"{layer}.shp"
                    if shp_file.exists():
                        try:
                            result = subprocess.run(
                                ["ogrinfo", "-so", str(shp_file), layer],
                                capture_output=True,
                                text=True,
                                check=True,
                            )

                            for line in result.stdout.split("\n"):
                                if "Feature Count:" in line or "Extent:" in line:
                                    print(f"   {layer}: {line.strip()}")
                        except:
                            pass

    print("\n✨ Integration Summary:")
    print("  ✓ Enhanced Overpass API query with proper coordinate extraction")
    print("  ✓ Data quality validation with completeness checking")
    print("  ✓ Robust error handling for network failures")
    print("  ✓ Offline mode with pre-downloaded data")
    print("  ✓ Complete coordinate preservation in shapefile conversion")
    print("  ✓ Feature counting and validation")


if __name__ == "__main__":
    demonstrate_live_osm_integration()
