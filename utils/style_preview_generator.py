#!/usr/bin/env python3
"""
Style Preview Generator for Lumsden Tourist Map
Creates a grid of map previews showing different styling options including hillshading variants
"""

import logging
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Add project root to Python path to handle imports when run from utils directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
# Define project root as a constant to be reused

from utils.config import (calculate_pixel_dimensions, load_area_config,
                          load_output_format)
from utils.data_processing import (calculate_bbox, convert_osm_to_shapefiles,
                                   process_elevation_and_contours)
from utils.elevation_processing import process_elevation_for_hillshading
from utils.style_builder import build_mapnik_style

logger = logging.getLogger(__name__)


def render_preview_map(
    style_name,
    data_dir,
    bbox,
    width_px,
    height_px,
    area_config=None,
    hillshade_available=False,
):
    """Render a small preview map using a specific style"""
    try:
        import mapnik
    except ImportError:
        logger.info(
            "Error: python-mapnik not available. Install with: pip install mapnik"
        )
        return None

    # Build the style with hillshading configuration
    style_file = build_mapnik_style(
        style_name, data_dir, area_config, hillshade_available
    )

    # Create map
    m = mapnik.Map(width_px, height_px)
    mapnik.load_map(m, style_file)

    # Set bounding box
    bbox_wgs84 = mapnik.Box2d(bbox["west"], bbox["south"], bbox["east"], bbox["north"])

    # Transform to Mercator
    proj_wgs84 = mapnik.Projection("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    proj_merc = mapnik.Projection(m.srs)
    transform = mapnik.ProjTransform(proj_wgs84, proj_merc)

    bbox_merc = transform.forward(bbox_wgs84)
    m.zoom_to_box(bbox_merc)

    # Render to memory
    im = mapnik.Image(width_px, height_px)
    mapnik.render(m, im)

    # Convert to PIL Image
    img_data = im.tostring("png")
    from io import BytesIO

    pil_image = Image.open(BytesIO(img_data))

    return pil_image


def create_style_grid(
    styles,
    data_dir,
    bbox,
    preview_size,
    area_config=None,
    hillshade_available=False,
    cols=2,
):
    """Create a grid of style previews"""
    logger.info(f"Creating style preview grid with {len(styles)} styles...")

    rows = math.ceil(len(styles) / cols)

    # Calculate grid dimensions
    title_height = 40
    padding = 20
    grid_width = cols * preview_size[0] + (cols - 1) * padding
    grid_height = rows * (preview_size[1] + title_height) + (rows - 1) * padding

    # Create the main grid image
    grid_img = Image.new("RGB", (grid_width, grid_height), color="white")

    # Try to load a font from several common locations
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",  # Alternate Linux
        "/Library/Fonts/Arial.ttf",  # macOS
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        "C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf",  # Windows alternate
    ]
    font = None
    title_font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, 16)
                title_font = ImageFont.truetype(path, 20)
                break
            except (OSError, IOError):
                continue
    if font is None or title_font is None:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    draw = ImageDraw.Draw(grid_img)

    for i, (
        style_name,
        style_title,
        style_area_config,
        style_hillshade_available,
    ) in enumerate(styles):
        row = i // cols
        col = i % cols

        logger.info(f"  Rendering {style_title} ({style_name})...")

        # Calculate position
        x = col * (preview_size[0] + padding)
        y = row * (preview_size[1] + title_height + padding)

        # Render the preview map
        preview_img = render_preview_map(
            style_name,
            data_dir,
            bbox,
            preview_size[0],
            preview_size[1],
            style_area_config,
            style_hillshade_available,
        )

        if preview_img:
            # Paste the preview into the grid
            grid_img.paste(preview_img, (x, y + title_height))

            # Add title
            title_bbox = draw.textbbox((0, 0), style_title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = x + (preview_size[0] - title_width) // 2
            draw.text((title_x, y + 5), style_title, fill="black", font=font)
        else:
            # Draw error placeholder
            draw.rectangle(
                [
                    x,
                    y + title_height,
                    x + preview_size[0],
                    y + title_height + preview_size[1],
                ],
                fill="lightgray",
                outline="red",
            )
            draw.text((x + 10, y + title_height + 10), "Error", fill="red", font=font)

    return grid_img


def main():
    logger.info("Style Preview Generator for Lumsden Tourist Map")
    logger.info("=" * 55)

    # Ensure we're working from the project root directory
    # Use the PROJECT_ROOT constant defined at the module level
    os.chdir(PROJECT_ROOT)

    # Load configuration
    area_config = load_area_config("lumsden")
    preview_format = load_output_format("preview")
    preview_width, preview_height = calculate_pixel_dimensions(preview_format)

    logger.info(
        f"Center: {area_config['center']['lat']}, {area_config['center']['lon']}"
    )
    logger.info(f"Preview size: {preview_width}×{preview_height} pixels")
    logger.info()

    # Calculate area
    bbox = calculate_bbox(
        area_config["center"]["lat"],
        area_config["center"]["lon"],
        area_config["coverage"]["width_km"],
        area_config["coverage"]["height_km"],
    )

    # Ensure data is available
    osm_file = Path(area_config.get("osm_file", "data/lumsden_area.osm"))

    if not osm_file.exists():
        logger.info(
            "OSM data file not found. Run map_generator.py first to download data."
        )
        return 1

    # Convert to shapefiles if needed
    data_dir = Path("data")
    osm_data_dir = data_dir / "osm_data"
    if not osm_data_dir.exists():
        logger.info("Converting OSM data to shapefiles...")
        osm_data_dir = convert_osm_to_shapefiles(str(osm_file))
    else:
        logger.info(f"Using existing shapefile data: {osm_data_dir}")
        osm_data_dir = str(osm_data_dir)

    # Ensure contour data is available for preview generation
    logger.info("Checking contour data availability...")
    contour_file = Path(osm_data_dir) / "contours.shp"
    if not contour_file.exists():
        logger.info("Generating contour data for previews...")
        contour_data = process_elevation_and_contours(
            bbox, osm_data_dir, contour_interval=10, enable_contours=True
        )
        if contour_data:
            logger.info("Contour data ready for preview generation")
        else:
            logger.info(
                "Could not generate contour data, previews will show without contours"
            )
    else:
        logger.info("Contour data already available")

    # Process elevation data for hillshading if enabled
    hillshade_available = False
    hillshade_file = process_elevation_for_hillshading(bbox, area_config, osm_data_dir)
    if hillshade_file:
        hillshade_available = True
        logger.info(f"Hillshading data available: {hillshade_file}")

    # Create area configs for hillshading variants
    area_config_no_hillshade = area_config.copy()
    if "hillshading" in area_config_no_hillshade:
        area_config_no_hillshade["hillshading"] = area_config_no_hillshade[
            "hillshading"
        ].copy()
        area_config_no_hillshade["hillshading"]["enabled"] = False

    # Define available styles including hillshading and contour line variants
    base_styles = [
        ("tourist", "Tourist (Default)"),
        ("tourist_no_contours", "Tourist - No Contours"),
        ("tourist_contours_prominent", "Tourist - Prominent Contours"),
        ("blue_theme", "Blue Theme"),
        ("warm_theme", "Warm Theme"),
        ("monochrome_theme", "Monochrome"),
        ("delicate_theme", "Delicate Purple"),
        ("high_contrast", "High Contrast"),
        ("minimalist", "Minimalist"),
    ]

    styles = []

    # Add standard versions (no hillshading)
    for style_name, style_title in base_styles:
        styles.append((style_name, style_title, area_config_no_hillshade, False))

    # Add hillshading versions if available
    if hillshade_available:
        for style_name, style_title in base_styles:
            hillshade_title = f"{style_title} + Hillshade"
            styles.append((style_name, hillshade_title, area_config, True))

    logger.info(f"Available styles: {len(styles)}")
    for style_name, style_title, _, hillshade_enabled in styles:
        hillshade_status = "with hillshading" if hillshade_enabled else "standard"
        logger.info(f"  - {style_title} ({hillshade_status})")
    logger.info()

    # Create the style grid
    grid_img = create_style_grid(
        styles, osm_data_dir, bbox, (preview_width, preview_height), cols=4
    )

    # Save the grid
    data_dir.mkdir(exist_ok=True)
    output_file = data_dir / "style_preview_grid.png"
    grid_img.save(str(output_file), "PNG")

    # Also save individual previews
    preview_dir = data_dir / "style_previews"
    preview_dir.mkdir(exist_ok=True)

    logger.info("\nSaving individual previews...")
    for style_name, style_title, style_area_config, style_hillshade_available in styles:
        preview_img = render_preview_map(
            style_name,
            osm_data_dir,
            bbox,
            preview_width,
            preview_height,
            style_area_config,
            style_hillshade_available,
        )
        if preview_img:
            # Create safe filename
            safe_title = (
                style_title.replace(" ", "_")
                .replace("+", "plus")
                .replace("(", "")
                .replace(")", "")
            )
            preview_file = preview_dir / f"{safe_title}_preview.png"
            preview_img.save(str(preview_file), "PNG")
            logger.info(f"  Saved {preview_file}")

    file_size_kb = os.path.getsize(output_file) / 1024
    logger.info(f"\nSUCCESS!")
    logger.info(f"Style grid: {output_file} ({file_size_kb:.1f} KB)")
    logger.info(f"Individual previews: {preview_dir}")

    if hillshade_available:
        standard_count = len(base_styles)
        hillshade_count = len(base_styles)
        logger.info(
            f"Grid shows {standard_count} standard styles + {hillshade_count} hillshading variants"
        )
        logger.info(
            f"Hillshading enhances topographical visualization with terrain relief"
        )
    else:
        logger.info(
            f"Grid shows {len(styles)} different style options at lower resolution"
        )
        logger.info(f"Enable hillshading in config/areas.json to see terrain variants")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
