"""Style generation utilities"""

from pathlib import Path
import string


def build_mapnik_style(style_name, data_dir):
    """Build Mapnik XML from template and data directory"""
    template_file = Path(f"styles/{style_name}.xml")
    
    if not template_file.exists():
        raise FileNotFoundError(f"Style template not found: {template_file}")
    
    with open(template_file) as f:
        template = string.Template(f.read())
    
    # Convert data_dir to absolute path to avoid relative path issues
    abs_data_dir = Path(data_dir).resolve()
    
    # Substitute template variables
    style_xml = template.substitute(DATA_DIR=str(abs_data_dir))
    
    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, 'w') as f:
        f.write(style_xml)
    
    return output_file
