"""Style generation utilities"""

from pathlib import Path
import string


def build_mapnik_style(style_name, data_dir, area_config=None, hillshade_available=False):
    """Build Mapnik XML from template and data directory"""
    template_file = Path(f"styles/{style_name}.xml")
    
    if not template_file.exists():
        raise FileNotFoundError(f"Style template not found: {template_file}")
    
    with open(template_file) as f:
        template = string.Template(f.read())
    
    # Convert data_dir to absolute path to avoid relative path issues
    abs_data_dir = Path(data_dir).resolve()
    
    # Substitute template variables
    abs_icons_dir = Path("icons").resolve()
    
    # Hillshading configuration
    hillshade_config = {}
    hillshade_file = ""
    hillshade_status = "off"
    hillshade_opacity = 0.4
    
    if (area_config and 
        area_config.get('hillshading', {}).get('enabled', False) and 
        hillshade_available):
        hillshade_config = area_config['hillshading']
        hillshade_file = str(abs_data_dir / "hillshade.tif")
        hillshade_status = "on"
        hillshade_opacity = hillshade_config.get('opacity', 0.4)
    
    style_xml = template.substitute(
        DATA_DIR=str(abs_data_dir), 
        ICONS_DIR=str(abs_icons_dir),
        HILLSHADE_FILE=hillshade_file,
        HILLSHADE_STATUS=hillshade_status,
        HILLSHADE_OPACITY=hillshade_opacity
    )
    
    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, 'w') as f:
        f.write(style_xml)
    
    return output_file
