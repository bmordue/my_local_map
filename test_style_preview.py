#!/usr/bin/env python3
"""
Test script for style preview functionality
"""

import os
import sys
from pathlib import Path

def test_style_templates():
    """Test that all style templates exist and are valid XML"""
    styles_dir = Path("styles")
    
    expected_styles = [
        "tourist.xml",
        "blue_theme.xml", 
        "warm_theme.xml",
        "monochrome_theme.xml",
        "delicate_theme.xml",
        "high_contrast.xml",
        "minimalist.xml"
    ]
    
    print("Testing style templates...")
    
    for style_file in expected_styles:
        style_path = styles_dir / style_file
        if not style_path.exists():
            print(f"❌ Missing style template: {style_file}")
            return False
        
        # Basic XML validation
        try:
            with open(style_path) as f:
                content = f.read()
                if not content.startswith('<?xml'):
                    print(f"❌ Invalid XML format: {style_file}")
                    return False
                if '$DATA_DIR' not in content:
                    print(f"❌ Missing $DATA_DIR placeholder: {style_file}")
                    return False
                    
            print(f"✓ {style_file}")
        except Exception as e:
            print(f"❌ Error reading {style_file}: {e}")
            return False
    
    return True

def test_config_files():
    """Test that configuration files are valid"""
    print("\nTesting configuration files...")
    
    config_dir = Path("config")
    
    # Test areas.json
    areas_file = config_dir / "areas.json"
    if not areas_file.exists():
        print("❌ Missing config/areas.json")
        return False
    
    try:
        import json
        with open(areas_file) as f:
            areas = json.load(f)
            if 'lumsden' not in areas:
                print("❌ Missing lumsden configuration in areas.json")
                return False
        print("✓ config/areas.json")
    except Exception as e:
        print(f"❌ Error in areas.json: {e}")
        return False
    
    # Test output_formats.json
    formats_file = config_dir / "output_formats.json"
    if not formats_file.exists():
        print("❌ Missing config/output_formats.json")
        return False
    
    try:
        with open(formats_file) as f:
            formats = json.load(f)
            if 'preview' not in formats:
                print("❌ Missing preview format in output_formats.json")
                return False
        print("✓ config/output_formats.json")
    except Exception as e:
        print(f"❌ Error in output_formats.json: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")
    
    try:
        import mapnik
        print(f"✓ mapnik {mapnik.mapnik_version()}")
    except ImportError:
        print("❌ mapnik not available")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL (Pillow)")
    except ImportError:
        print("❌ PIL (Pillow) not available")
        return False
    
    try:
        import subprocess
        result = subprocess.run(["ogr2ogr", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split(',')[0]
            print(f"✓ {version}")
        else:
            print("❌ ogr2ogr not working")
            return False
    except Exception:
        print("❌ ogr2ogr not available")
        return False
    
    return True

def test_data_files():
    """Test that required data files exist"""
    print("\nTesting data files...")
    
    osm_file = Path("lumsden_area.osm")
    
    if not osm_file.exists():
        print("❌ Missing lumsden_area.osm")
        return False
    
    file_size = osm_file.stat().st_size
    if file_size < 1000:  # Should be at least 1KB
        print(f"❌ OSM file too small: {file_size} bytes")
        return False
    
    print(f"✓ data/lumsden_area.osm ({file_size} bytes)")
    
    # Check if shapefiles exist
    osm_data_dir = data_dir / "osm_data"
    if osm_data_dir.exists():
        shapefiles = list(osm_data_dir.glob("*.shp"))
        print(f"✓ {len(shapefiles)} shapefiles available")
    else:
        print("ℹ️  Shapefiles not yet generated (will be created on first run)")
    
    return True

def main():
    print("🧪 Style Preview System Test Suite")
    print("=" * 40)
    
    tests = [
        test_dependencies,
        test_config_files, 
        test_style_templates,
        test_data_files
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Style preview system ready.")
        print("\nRun: python3 style_preview_generator.py")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())