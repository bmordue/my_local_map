#!/usr/bin/env python3
"""
Test script for legend functionality
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.legend import MapLegend, add_legend_to_image


def test_legend_creation():
    """Test that legend can be created with expected items"""
    print("Testing legend creation...")

    legend = MapLegend()

    # Check that legend has items
    if len(legend.items) == 0:
        print("❌ Legend has no items")
        return False

    print(f"✓ Legend created with {len(legend.items)} items")

    # Check categories
    categories = legend.get_legend_summary()
    print(f"✓ Legend categories: {categories['categories']}")

    # Check some expected items
    labels = [item.label for item in legend.items]
    expected_items = [
        "Forest / Woodland",
        "Primary Roads",
        "Points of Interest",
        "Buildings",
    ]

    for expected in expected_items:
        if expected not in labels:
            print(f"❌ Missing expected legend item: {expected}")
            return False
        print(f"✓ Found expected item: {expected}")

    return True


def test_legend_image_processing():
    """Test that legend can be added to an image"""
    print("\nTesting legend image processing...")

    # Check if we have PIL
    try:
        from PIL import Image, ImageDraw

        print("✓ PIL available for image processing")
    except ImportError:
        print("❌ PIL not available")
        return False

    # Create a simple test image
    test_image_path = "/tmp/test_map.png"
    img = Image.new("RGB", (400, 300), color="lightblue")
    img.save(test_image_path)
    print("✓ Test image created")

    # Create legend and add to image
    legend = MapLegend()

    # Mock map object for legend positioning
    class MockMap:
        def __init__(self):
            self.width = 400
            self.height = 300

    mock_map = MockMap()
    legend_data = legend.render_to_map(mock_map)

    # Add legend to image
    output_path = "/tmp/test_map_with_legend.png"
    if add_legend_to_image(test_image_path, legend_data, output_path):
        print("✓ Legend successfully added to test image")

        # Verify output exists and is larger (due to legend)
        if os.path.exists(output_path):
            original_size = os.path.getsize(test_image_path)
            legend_size = os.path.getsize(output_path)
            if legend_size > original_size:
                print(
                    f"✓ Output image larger than original ({legend_size} vs {original_size} bytes)"
                )
                return True
            else:
                print(f"❌ Output image not larger than original")
                return False
        else:
            print("❌ Output image not created")
            return False
    else:
        print("❌ Failed to add legend to image")
        return False


def main():
    """Run all legend tests"""
    print("🧪 Testing Legend Functionality")
    print("=" * 50)

    all_tests_passed = True

    # Test legend creation
    if not test_legend_creation():
        all_tests_passed = False

    # Test image processing
    if not test_legend_image_processing():
        all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All legend tests passed!")
        return 0
    else:
        print("❌ Some legend tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
