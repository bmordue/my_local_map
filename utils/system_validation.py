#!/usr/bin/env python3
"""
Simple validation script to check that the map generator can be imported and has basic functionality
"""

import os
import sys

# Add the root directory to path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        import map_generator

        print("✓ Main map_generator module imported successfully")

        from utils import config, data_processing, style_builder

        print("✓ All utility modules imported successfully")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_configuration_loading():
    """Test that configuration files can be loaded"""
    try:
        from utils.config import (
            calculate_pixel_dimensions,
            load_area_config,
            load_output_format,
        )

        area_config = load_area_config("lumsden")
        print(f"✓ Area config loaded: {area_config['name']}")

        output_format = load_output_format("A3")
        print(f"✓ Output format loaded: {output_format['description']}")

        width_px, height_px = calculate_pixel_dimensions(output_format)
        print(f"✓ Pixel dimensions calculated: {width_px}x{height_px}")

        return True
    except Exception as e:
        print(f"✗ Configuration loading error: {e}")
        return False


def test_data_processing():
    """Test basic data processing functions"""
    try:
        from utils.data_processing import calculate_bbox

        bbox = calculate_bbox(57.3167, -2.8833, 8, 12)
        print(f"✓ Bounding box calculated: {bbox}")

        return True
    except Exception as e:
        print(f"✗ Data processing error: {e}")
        return False


def test_quality_validation():
    """Test quality validation system functionality"""
    try:
        from utils.quality_validation import (
            AttributeValidator,
            CoordinateValidator,
            CrossReferenceValidator,
            TemporalValidator,
            ValidationResult,
            validate_data_quality,
        )

        # Test basic validation functionality
        bbox = {"south": 57.26, "north": 57.37, "west": -2.95, "east": -2.82}
        coord_validator = CoordinateValidator(bbox)

        # Test with sample data
        sample_data = [{"lat": 57.32, "lon": -2.88, "name": "Test Location"}]
        result = coord_validator.validate_coordinates(sample_data)

        print(
            f"✓ Quality validation system functional: {result.stats.get('valid_coordinates', 0)} valid coordinates"
        )

        return True
    except Exception as e:
        print(f"✗ Quality validation error: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🧪 Running Map Generator Validation Tests")
    print("=" * 50)

    all_passed = True

    tests = [
        ("Module imports", test_imports),
        ("Configuration loading", test_configuration_loading),
        ("Data processing", test_data_processing),
        ("Quality validation system", test_quality_validation),
    ]

    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("❌ Some validation tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
