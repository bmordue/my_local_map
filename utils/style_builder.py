"""Style generation utilities"""

import re
import string
from pathlib import Path


def build_mapnik_style(
    style_name, data_dir, area_config=None, hillshade_available=False, os_data_dirs=None
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
        print(f"  ⚠ No contour data found, excluding contour layers from style")
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
        print(f"  ✓ Contour data found, including contour layers in style")

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
        contour_interval = contours_config.get('interval', 10)
        contour_major_interval = contours_config.get('major_interval', 50)
        
        minor_style = contours_config.get('style', {}).get('minor', {})
        major_style = contours_config.get('style', {}).get('major', {})
        
        contour_minor_color = minor_style.get('color', '#8B4513')
        contour_minor_width = minor_style.get('width', 0.5)
        contour_minor_opacity = minor_style.get('opacity', 0.6)
        contour_major_color = major_style.get('color', '#654321')
        contour_major_width = major_style.get('width', 1.2)
        contour_major_opacity = major_style.get('opacity', 0.8)
    
    # Ordnance Survey data configuration
    os_roads_dir = ""
    os_boundaries_dir = ""
    os_rights_of_way_dir = ""
    os_status = "off"
    os_roads_primary_color = "#CC6600"
    os_roads_primary_width = 2.0
    os_roads_secondary_color = "#FF9933"
    os_roads_secondary_width = 1.5
    os_boundaries_admin_color = "#8B4513"
    os_boundaries_admin_width = 1.2
    os_rights_of_way_footpath_color = "#228B22"
    os_rights_of_way_footpath_width = 1.0
    
    if os_data_dirs and area_config and area_config.get('ordnance_survey', {}).get('enabled', False):
        # Only enable OS layers if we actually have valid data
        valid_os_dirs = {k: v for k, v in os_data_dirs.items() if v is not None}
        
        if valid_os_dirs:
            os_status = "on"
            os_config = area_config['ordnance_survey']
            style_config = os_config.get('style', {})
            
            # Set OS data directories (use absolute paths)
            if 'roads' in valid_os_dirs:
                os_roads_dir = str(Path(valid_os_dirs['roads']).resolve())
            if 'boundaries' in valid_os_dirs:
                os_boundaries_dir = str(Path(valid_os_dirs['boundaries']).resolve())
            if 'rights_of_way' in valid_os_dirs:
                os_rights_of_way_dir = str(Path(valid_os_dirs['rights_of_way']).resolve())
        
            # Configure roads styling
            roads_style = style_config.get('roads', {})
            os_roads_primary_color = roads_style.get('primary_color', '#CC6600')
            os_roads_primary_width = roads_style.get('primary_width', 2.0)
            os_roads_secondary_color = roads_style.get('secondary_color', '#FF9933')
            os_roads_secondary_width = roads_style.get('secondary_width', 1.5)
            
            # Configure boundaries styling
            boundaries_style = style_config.get('boundaries', {})
            os_boundaries_admin_color = boundaries_style.get('admin_color', '#8B4513')
            os_boundaries_admin_width = boundaries_style.get('admin_width', 1.2)
            
            # Configure rights of way styling
            row_style = style_config.get('rights_of_way', {})
            os_rights_of_way_footpath_color = row_style.get('footpath_color', '#228B22')
            os_rights_of_way_footpath_width = row_style.get('footpath_width', 1.0)
    
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
        OS_STATUS=os_status,
        OS_ROADS_DIR=os_roads_dir,
        OS_BOUNDARIES_DIR=os_boundaries_dir,
        OS_RIGHTS_OF_WAY_DIR=os_rights_of_way_dir,
        OS_ROADS_PRIMARY_COLOR=os_roads_primary_color,
        OS_ROADS_PRIMARY_WIDTH=os_roads_primary_width,
        OS_ROADS_SECONDARY_COLOR=os_roads_secondary_color,
        OS_ROADS_SECONDARY_WIDTH=os_roads_secondary_width,
        OS_BOUNDARIES_ADMIN_COLOR=os_boundaries_admin_color,
        OS_BOUNDARIES_ADMIN_WIDTH=os_boundaries_admin_width,
        OS_RIGHTS_OF_WAY_FOOTPATH_COLOR=os_rights_of_way_footpath_color,
        OS_RIGHTS_OF_WAY_FOOTPATH_WIDTH=os_rights_of_way_footpath_width
    )

    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, "w") as f:
        f.write(style_xml)

    return output_file
