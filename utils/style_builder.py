"""Style generation utilities"""

from pathlib import Path
import string
import re


def build_mapnik_style(style_name, data_dir):
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
            r'<!-- CONTOUR LINES.*?</Style>',
            '',
            template_content,
            flags=re.DOTALL
        )
        # Remove contour layer definition  
        template_content = re.sub(
            r'<!-- CONTOUR LINES - elevation contours -->.*?</Layer>',
            '',
            template_content,
            flags=re.DOTALL
        )
    else:
        print(f"  ✓ Contour data found, including contour layers in style")
    
    # Create template and substitute variables
    template = string.Template(template_content)
    
    # Convert data_dir to absolute path to avoid relative path issues
    abs_data_dir = Path(data_dir).resolve()
    abs_data_dir = Path(data_dir).resolve()
    
    # Substitute template variables
    abs_icons_dir = Path("icons").resolve()
    style_xml = template.substitute(DATA_DIR=str(abs_data_dir), ICONS_DIR=str(abs_icons_dir))
    
    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, 'w') as f:
        f.write(style_xml)
    
    return output_file
