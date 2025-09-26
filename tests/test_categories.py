#!/usr/bin/env python3
"""Test script for new content categories"""

import os
import sys
from pathlib import Path

# Add the utils directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from style_builder import build_mapnik_style


def main():
    # Create a test configuration with some of our new features
    test_config = {
        "hillshading": {"enabled": False},
        "contours": {"enabled": False},
        "elevation": {"source": "synthetic"},
    }

    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    # Test building the style with our new categories
    print("Testing style generation with new content categories...")
    try:
        style_file = build_mapnik_style("tourist", "data", test_config)
        print(f"✓ Successfully generated style with new categories: {style_file}")

        # Check if the style file contains our new styles
        with open(style_file, "r") as f:
            content = f.read()

        # Check for our new style names
        new_styles = ["recreation", "emergency"]
        found_styles = []

        for style in new_styles:
            if f'<Style name="{style}"' in content:
                found_styles.append(style)
                print(f"✓ Found new style: {style}")
            else:
                print(f"✗ Missing new style: {style}")

        if len(found_styles) == len(new_styles):
            print("✓ All new styles are present in the generated style file")
        else:
            print("⚠ Some new styles are missing from the generated style file")

    except Exception as e:
        print(f"✗ Error generating style: {e}")


if __name__ == "__main__":
    main()
