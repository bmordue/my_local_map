#!/usr/bin/env python3
"""
Style Preview Generator for Lumsden Tourist Map
Creates a grid of map previews showing different styling options
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from utils.config import load_area_config, load_output_format, calculate_pixel_dimensions
from utils.style_builder import build_mapnik_style
from utils.data_processing import calculate_bbox, convert_osm_to_shapefiles

def render_preview_map(style_name, data_dir, bbox, width_px, height_px):
    """Render a small preview map using a specific style"""
    try:
        import mapnik
    except ImportError:
        print("Error: python-mapnik not available. Install with: pip install mapnik")
        return None
    
    # Build the style
    style_file = build_mapnik_style(style_name, data_dir)
    
    # Create map
    m = mapnik.Map(width_px, height_px)
    mapnik.load_map(m, style_file)
    
    # Set bounding box
    bbox_wgs84 = mapnik.Box2d(bbox['west'], bbox['south'], bbox['east'], bbox['north'])
    
    # Transform to Mercator
    proj_wgs84 = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    proj_merc = mapnik.Projection(m.srs)
    transform = mapnik.ProjTransform(proj_wgs84, proj_merc)
    
    bbox_merc = transform.forward(bbox_wgs84)
    m.zoom_to_box(bbox_merc)
    
    # Render to memory
    im = mapnik.Image(width_px, height_px)
    mapnik.render(m, im)
    
    # Convert to PIL Image
    img_data = im.tostring('png')
    from io import BytesIO
    pil_image = Image.open(BytesIO(img_data))
    
    return pil_image

def create_style_grid(styles, data_dir, bbox, preview_size, cols=2):
    """Create a grid of style previews"""
    print(f"Creating style preview grid with {len(styles)} styles...")
    
    rows = math.ceil(len(styles) / cols)
    
    # Calculate grid dimensions
    title_height = 40
    padding = 20
    grid_width = cols * preview_size[0] + (cols - 1) * padding
    grid_height = rows * (preview_size[1] + title_height) + (rows - 1) * padding
    
    # Create the main grid image
    grid_img = Image.new('RGB', (grid_width, grid_height), color='white')
    
    # Try to load a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except (OSError, IOError):
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(grid_img)
    
    for i, (style_name, style_title) in enumerate(styles):
        row = i // cols
        col = i % cols
        
        print(f"  Rendering {style_title} ({style_name})...")
        
        # Calculate position
        x = col * (preview_size[0] + padding)
        y = row * (preview_size[1] + title_height + padding)
        
        # Render the preview map
        preview_img = render_preview_map(style_name, data_dir, bbox, preview_size[0], preview_size[1])
        
        if preview_img:
            # Paste the preview into the grid
            grid_img.paste(preview_img, (x, y + title_height))
            
            # Add title
            title_bbox = draw.textbbox((0, 0), style_title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = x + (preview_size[0] - title_width) // 2
            draw.text((title_x, y + 5), style_title, fill='black', font=font)
        else:
            # Draw error placeholder
            draw.rectangle([x, y + title_height, x + preview_size[0], y + title_height + preview_size[1]], 
                         fill='lightgray', outline='red')
            draw.text((x + 10, y + title_height + 10), "Error", fill='red', font=font)
    
    return grid_img

def main():
    print("🎨 Style Preview Generator for Lumsden Tourist Map")
    print("=" * 55)
    
    # Load configuration
    area_config = load_area_config("lumsden")
    preview_format = load_output_format("preview")
    preview_width, preview_height = calculate_pixel_dimensions(preview_format)
    
    print(f"📍 Center: {area_config['center']['lat']}, {area_config['center']['lon']}")
    print(f"📏 Preview size: {preview_width}×{preview_height} pixels")
    print()
    
    # Calculate area
    bbox = calculate_bbox(
        area_config["center"]["lat"], 
        area_config["center"]["lon"], 
        area_config["coverage"]["width_km"], 
        area_config["coverage"]["height_km"]
    )
    
    # Ensure data is available
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    osm_file = data_dir / "lumsden_area.osm"
    
    if not osm_file.exists():
        print("❌ OSM data file not found. Run map_generator.py first to download data.")
        return 1
    
    # Convert to shapefiles if needed
    osm_data_dir = data_dir / "osm_data"
    if not osm_data_dir.exists():
        print("🔄 Converting OSM data to shapefiles...")
        osm_data_dir = convert_osm_to_shapefiles(str(osm_file))
    else:
        print(f"📁 Using existing shapefile data: {osm_data_dir}")
        osm_data_dir = str(osm_data_dir)
    
    # Define available styles
    styles = [
        ("tourist", "Tourist (Default)"),
        ("blue_theme", "Blue Theme"),
        ("warm_theme", "Warm Theme"), 
        ("monochrome_theme", "Monochrome"),
        ("delicate_theme", "Delicate Purple")
    ]
    
    print(f"🎨 Available styles: {len(styles)}")
    for style_name, style_title in styles:
        print(f"  • {style_title}")
    print()
    
    # Create the style grid
    grid_img = create_style_grid(styles, osm_data_dir, bbox, (preview_width, preview_height), cols=3)
    
    # Save the grid
    output_file = data_dir / "style_preview_grid.png"
    grid_img.save(str(output_file), 'PNG')
    
    # Also save individual previews
    preview_dir = data_dir / "style_previews"
    preview_dir.mkdir(exist_ok=True)
    
    print("\n📁 Saving individual previews...")
    for style_name, style_title in styles:
        preview_img = render_preview_map(style_name, osm_data_dir, bbox, preview_width, preview_height)
        if preview_img:
            preview_file = preview_dir / f"{style_name}_preview.png"
            preview_img.save(str(preview_file), 'PNG')
            print(f"  ✓ Saved {preview_file}")
    
    file_size_kb = os.path.getsize(output_file) / 1024
    print(f"\n🎉 SUCCESS!")
    print(f"📄 Style grid: {output_file} ({file_size_kb:.1f} KB)")
    print(f"📁 Individual previews: {preview_dir}")
    print(f"🎯 Grid shows {len(styles)} different style options at lower resolution")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())