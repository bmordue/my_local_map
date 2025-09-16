"""Style generation utilities"""

from pathlib import Path
import string
import re


def build_mapnik_style(style_name, data_dir, area_config=None, hillshade_available=False, route_available=False):
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
    
    # Check if route data exists
    route_file = abs_data_dir / "tourist_routes.geojson"
    has_routes = route_file.exists() and route_available
    
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
    
    # Remove route-related sections if route data doesn't exist
    if not has_routes:
        print(f"  ⚠ No route data found, excluding route layers from style")
        # Remove route style definition
        template_content = re.sub(
            r'<!-- TOURIST ROUTES.*?</Style>',
            '',
            template_content,
            flags=re.DOTALL
        )
        # Remove route layer definition  
        template_content = re.sub(
            r'<!-- TOURIST ROUTES - planned routes -->.*?</Layer>',
            '',
            template_content,
            flags=re.DOTALL
        )
    else:
        print(f"  ✓ Route data found, including route layers in style")
    
    # Create template and substitute variables
    template = string.Template(template_content)
    
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

    if area_config and area_config.get('contours', {}).get('enabled', False):
        contours_config = area_config['contours']
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
    
    # Route planning configuration
    routes_config = {}
    routes_status = "off"
    route_file_path = ""
    walking_color = "#0066CC"
    walking_width = 2.0
    walking_opacity = 0.8
    walking_dash = "5,2"
    accessible_color = "#00AA44"
    accessible_width = 2.5
    accessible_opacity = 0.9
    accessible_dash = "10,5"
    cycling_color = "#CC6600"
    cycling_width = 1.8
    cycling_opacity = 0.8
    cycling_dash = "3,3"

    if (area_config and 
        area_config.get('route_planning', {}).get('enabled', False) and 
        has_routes):
        routes_config = area_config['route_planning']
        routes_status = "on"
        route_file_path = str(route_file)
        
        style_config = routes_config.get('style', {})
        
        # Walking route style
        walking_style = style_config.get('walking', {})
        walking_color = walking_style.get('color', '#0066CC')
        walking_width = walking_style.get('width', 2.0)
        walking_opacity = walking_style.get('opacity', 0.8)
        walking_dash = walking_style.get('dash_array', '5,2')
        
        # Accessible route style
        accessible_style = style_config.get('accessible', {})
        accessible_color = accessible_style.get('color', '#00AA44')
        accessible_width = accessible_style.get('width', 2.5)
        accessible_opacity = accessible_style.get('opacity', 0.9)
        accessible_dash = accessible_style.get('dash_array', '10,5')
        
        # Cycling route style
        cycling_style = style_config.get('cycling', {})
        cycling_color = cycling_style.get('color', '#CC6600')
        cycling_width = cycling_style.get('width', 1.8)
        cycling_opacity = cycling_style.get('opacity', 0.8)
        cycling_dash = cycling_style.get('dash_array', '3,3')
    
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
        ROUTES_STATUS=routes_status,
        ROUTE_FILE=route_file_path,
        WALKING_COLOR=walking_color,
        WALKING_WIDTH=walking_width,
        WALKING_OPACITY=walking_opacity,
        WALKING_DASH=walking_dash,
        ACCESSIBLE_COLOR=accessible_color,
        ACCESSIBLE_WIDTH=accessible_width,
        ACCESSIBLE_OPACITY=accessible_opacity,
        ACCESSIBLE_DASH=accessible_dash,
        CYCLING_COLOR=cycling_color,
        CYCLING_WIDTH=cycling_width,
        CYCLING_OPACITY=cycling_opacity,
        CYCLING_DASH=cycling_dash
    )
    
    output_file = f"styles/{style_name}_map_style.xml"
    with open(output_file, 'w') as f:
        f.write(style_xml)
    
    return output_file
