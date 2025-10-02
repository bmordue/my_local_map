"""Style generation utilities"""

import logging
import re
import string
from pathlib import Path

logger = logging.getLogger(__name__)


def build_mapnik_style(
    style_name, data_dir, area_config=None, hillshade_available=False
):
    """Build Mapnik XML from template and data directory"""
    template_file = Path(f"styles/{style_name}.xml")

    if not template_file.exists():
        raise FileNotFoundError(f"Style template not found: {template_file}")

    with open(template_file) as f:
        template_content = f.read()

    # Check if contour data exists
    abs_data_dir = Path(data_dir).resolve()
    contour_file = abs_data_dir / "contours.shp"
    has_contours = contour_file.exists()

    # Remove contour-related sections if contour data doesn't exist
    if not has_contours:
        logger.info(f"  ⚠ No contour data found, excluding contour layers from style")
        # Remove contour style definition
        template_content = re.sub(
            r"<!-- CONTOUR LINES.*?</Style>", "", template_content, flags=re.DOTALL
        )
        # Remove contour layer definition
        template_content = re.sub(
            r"<!-- CONTOUR LINES - elevation contours -->.*?</Layer>",
            "",
            template_content,
            flags=re.DOTALL,
        )
    else:
        logger.info(f"  ✓ Contour data found, including contour layers in style")

    # Create template and substitute variables
    template = string.Template(template_content)

    # Substitute template variables
    abs_icons_dir = Path("icons").resolve()

    # Hillshading configuration
    hillshade_config = {}
    hillshade_file = ""
    hillshade_status = "off"
    hillshade_opacity = 0.4

    if (
        area_config
        and area_config.get("hillshading", {}).get("enabled", False)
        and hillshade_available
    ):
        hillshade_config = area_config["hillshading"]
        hillshade_file = str(abs_data_dir / "hillshade.tif")
        hillshade_status = "on"
        hillshade_opacity = hillshade_config.get("opacity", 0.4)

    # Contour lines configuration
    contours_config = {}
    contours_status = "off"
    contour_interval = 10
    contour_major_interval = 50
    contour_minor_color = "#8B4513"
    contour_minor_width = 0.5
    contour_minor_opacity = 0.6
    contour_major_color = "#654321"
    contour_major_width = 1.2
    contour_major_opacity = 0.8

    if area_config and area_config.get("contours", {}).get("enabled", False):
        contours_config = area_config["contours"]
        contours_status = "on"
        contour_interval = contours_config.get("interval", 10)
        contour_major_interval = contours_config.get("major_interval", 50)

        minor_style = contours_config.get("style", {}).get("minor", {})
        major_style = contours_config.get("style", {}).get("major", {})

        contour_minor_color = minor_style.get("color", "#8B4513")
        contour_minor_width = minor_style.get("width", 0.5)
        contour_minor_opacity = minor_style.get("opacity", 0.6)
        contour_major_color = major_style.get("color", "#654321")
        contour_major_width = major_style.get("width", 1.2)
        contour_major_opacity = major_style.get("opacity", 0.8)

    style_xml = template.substitute(
        DATA_DIR=str(abs_data_dir),
        ICONS_DIR=str(abs_icons_dir),
        HILLSHADE_FILE=hillshade_file,
        HILLSHADE_STATUS=hillshade_status,
        HILLSHADE_OPACITY=hillshade_opacity,
        CONTOURS_STATUS=contours_status,
        CONTOUR_INTERVAL=contour_interval,
        CONTOUR_MAJOR_INTERVAL=contour_major_interval,
        CONTOUR_MINOR_COLOR=contour_minor_color,
        CONTOUR_MINOR_WIDTH=contour_minor_width,
        CONTOUR_MINOR_OPACITY=contour_minor_opacity,
        CONTOUR_MAJOR_COLOR=contour_major_color,
        CONTOUR_MAJOR_WIDTH=contour_major_width,
        CONTOUR_MAJOR_OPACITY=contour_major_opacity,
    )

    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, "w") as f:
        f.write(style_xml)

    return output_file
