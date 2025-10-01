"""
Map Rendering Workflow Module

Handles the high-level map rendering workflow:
- Style creation
- Map rendering coordination
- Output file management
"""

import logging
import os
from pathlib import Path

from .legend import MapLegend, add_legend_to_image
from .style_builder import build_mapnik_style

logger = logging.getLogger(__name__)


def create_mapnik_style(data_dir, area_config, hillshade_available=False):
    """Create a tourist-focused Mapnik XML style using template"""
    style_file = build_mapnik_style(
        "tourist", data_dir, area_config, hillshade_available
    )
    logger.info(f"🎨 Created tourist-focused map style: {style_file}")
    return style_file


def render_map(style_file, bbox, output_file, width_px, height_px):
    """Render the map using Mapnik"""
    try:
        import mapnik
    except ImportError:
        logger.error("python-mapnik not available. Install with: pip install mapnik")
        return False

    logger.info("🖼️  Rendering A3 tourist map...")

    # Create map
    m = mapnik.Map(width_px, height_px)
    mapnik.load_map(m, style_file)

    # Set bounding box
    # The bounding box from the script is in WGS84 (lat/lon)
    bbox_wgs84 = mapnik.Box2d(bbox["west"], bbox["south"], bbox["east"], bbox["north"])

    # The map projection is Mercator, so we need to transform the bbox
    proj_wgs84 = mapnik.Projection("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    proj_merc = mapnik.Projection(m.srs)
    transform = mapnik.ProjTransform(proj_wgs84, proj_merc)

    bbox_merc = transform.forward(bbox_wgs84)
    m.zoom_to_box(bbox_merc)

    # Render base map
    mapnik.render_to_file(m, output_file, "png")

    # Create and add legend
    logger.info("🗺️  Adding map legend...")
    legend = MapLegend()
    legend_data = legend.render_to_map(m)

    # Add legend overlay to the image
    if add_legend_to_image(output_file, legend_data):
        logger.info("✓ Legend added successfully")
    else:
        logger.info("Legend could not be added (continuing without legend)")

    file_size_mb = os.path.getsize(output_file) / 1024 / 1024
    logger.info(f"✓ Map rendered successfully: {output_file} ({file_size_mb:.1f} MB)")
    return True


def execute_map_rendering(
    area_name,
    area_config,
    output_format,
    bbox,
    osm_data_dir,
    hillshade_available,
    width_px,
    height_px,
):
    """
    Execute the complete map rendering workflow.

    Args:
        area_name: Name of the geographic area
        area_config: Area configuration dictionary
        output_format: Output format configuration
        bbox: Bounding box for the area
        osm_data_dir: Directory containing OSM shapefiles
        hillshade_available: Whether hillshading is available
        width_px, height_px: Output dimensions in pixels

    Returns:
        bool: Success flag
    """
    # Ensure data directory exists for output
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Create map style
    logger.info("\n🎨 Creating tourist map style...")
    style_file = create_mapnik_style(osm_data_dir, area_config, hillshade_available)

    # Render map
    logger.info(f"\n🖼️  Rendering A3 map ({width_px}×{height_px} pixels)...")
    output_file = data_dir / f"{area_name}_tourist_map_A3.png"

    if render_map(style_file, bbox, str(output_file), width_px, height_px):
        logger.info("\n🎉 SUCCESS!")
        logger.info(f"📄 Tourist map: {output_file}")
        logger.info(
            f"📐 Print size: A3 ({output_format['width_mm']}×{output_format['height_mm']}mm at {output_format['dpi']} DPI)"
        )
        logger.info(f"🎯 Perfect for planning day trips around {area_config['name']}!")
        return True
    else:
        logger.error("\nMap rendering failed")
        return False
