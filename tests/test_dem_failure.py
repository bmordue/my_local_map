#!/usr/bin/env python3
"""
Test script to demonstrate DEM failure behavior with synthetic fallback disabled.

This script tests the scenario where:
1. Real DEM data cannot be downloaded (simulated by network issues)
2. Synthetic fallback is disabled in configuration
3. Script should fail immediately with clear error message
"""

import logging
import os
import sys
import tempfile
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.config import load_area_config
from utils.data_processing import calculate_bbox
from utils.elevation_processing import process_elevation_for_hillshading
from utils.logging_config import setup_logging


def test_dem_failure_behavior():
    """Test DEM failure behavior with different configurations"""
    print("🧪 Testing DEM failure behavior...")
    
    # Set up logging
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)
    
    # Create test bbox
    bbox = {
        "west": -3.0,
        "east": -2.5,
        "south": 57.0,
        "north": 57.5
    }
    
    print("\n1️⃣ Testing with synthetic fallback ENABLED (should succeed)...")
    try:
        area_config_with_fallback = {
            "hillshading": {"enabled": True},
            "elevation": {
                "source": "srtm",
                "allow_synthetic_fallback": True
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                bbox, area_config_with_fallback, temp_dir
            )
            if result:
                print("   ✅ SUCCESS: Generated hillshade with synthetic DEM fallback")
            else:
                print("   ⚠️  WARNING: No hillshade generated (hillshading may be disabled)")
                
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
    
    print("\n2️⃣ Testing with synthetic fallback DISABLED (should fail)...")
    try:
        area_config_no_fallback = {
            "hillshading": {"enabled": True},
            "elevation": {
                "source": "srtm",
                "allow_synthetic_fallback": False
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                bbox, area_config_no_fallback, temp_dir
            )
            print("   ❌ UNEXPECTED: Should have failed but didn't")
            
    except RuntimeError as e:
        print(f"   ✅ EXPECTED FAILURE: {e}")
        print("   ✅ Script correctly failed when DEM data unavailable and fallback disabled")
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR TYPE: {e}")
    
    print("\n3️⃣ Testing real area configuration (Balmoral Castle - fallback disabled)...")
    try:
        # Load Balmoral Castle config (configured with fallback disabled)
        area_config = load_area_config("balmoral_castle")
        bbox = calculate_bbox(
            area_config["center"]["lat"],
            area_config["center"]["lon"],
            area_config["coverage"]["width_km"],
            area_config["coverage"]["height_km"]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(bbox, area_config, temp_dir)
            print("   ❌ UNEXPECTED: Balmoral Castle should have failed")
            
    except RuntimeError as e:
        print(f"   ✅ EXPECTED FAILURE: {e}")
        print("   ✅ Balmoral Castle correctly fails with synthetic fallback disabled")
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        
    print("\n4️⃣ Testing area with fallback enabled (Lumsden - should succeed)...")
    try:
        # Load Lumsden config (configured with fallback enabled)
        area_config = load_area_config("lumsden")
        bbox = calculate_bbox(
            area_config["center"]["lat"],
            area_config["center"]["lon"],
            area_config["coverage"]["width_km"],
            area_config["coverage"]["height_km"]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(bbox, area_config, temp_dir)
            if result:
                print("   ✅ SUCCESS: Lumsden generated hillshade successfully")
            else:
                print("   ⚠️  WARNING: No hillshade generated")
                
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        
    print("\n🎯 Test Summary:")
    print("   - Areas with 'allow_synthetic_fallback: true' should succeed")
    print("   - Areas with 'allow_synthetic_fallback: false' should fail immediately")
    print("   - Balmoral Castle is configured to fail (for demonstration)")
    print("   - Lumsden is configured to succeed with synthetic fallback")


if __name__ == "__main__":
    test_dem_failure_behavior()
