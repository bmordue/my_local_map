"""Configuration management utilities"""

import json
from pathlib import Path


def load_area_config(area_name="lumsden"):
    """Load geographic area configuration"""
    config_file = Path("config/areas.json")
    with open(config_file) as f:
        areas = json.load(f)
    return areas[area_name]


def load_output_format(format_name="A3"):
    """Load output format specifications"""
    config_file = Path("config/output_formats.json")
    with open(config_file) as f:
        formats = json.load(f)
    return formats[format_name]


def calculate_pixel_dimensions(output_format):
    """Calculate pixel dimensions from output format
    
    Supports both millimeter-based formats (with width_mm/height_mm) 
    and pixel-based formats (with width_px/height_px)
    """
    if "width_px" in output_format and "height_px" in output_format:
        # Direct pixel specification for mobile/screen formats
        width_px = int(output_format["width_px"])
        height_px = int(output_format["height_px"])
    else:
        # Traditional millimeter-based calculation for print formats
        width_px = int(output_format["width_mm"] / 25.4 * output_format["dpi"])
        height_px = int(output_format["height_mm"] / 25.4 * output_format["dpi"])
    return width_px, height_px