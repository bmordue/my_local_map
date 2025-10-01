"""Geographic and data processing utilities"""

import logging
import math
import os
import subprocess
import tempfile
from pathlib import Path

import requests
import xml

logger = logging.getLogger(__name__)


def calculate_bbox(center_lat, center_lon, width_km, height_km):
    """Calculate bounding box around center point"""
    lat_deg_per_km = 1 / 111.32
    lon_deg_per_km = 1 / (111.32 * abs(math.cos(math.radians(center_lat))))

    half_height_deg = (height_km / 2) * lat_deg_per_km
    half_width_deg = (width_km / 2) * lon_deg_per_km

    return {
        "south": center_lat - half_height_deg,
        "north": center_lat + half_height_deg,
        "west": center_lon - half_width_deg,
        "east": center_lon + half_width_deg,
    }


def download_osm_data(bbox, output_file):
    """Download OSM data using Overpass API with proper coordinate extraction"""
    # Enhanced Overpass query to ensure complete node coordinates for all ways and relations
    overpass_query = f"""
    [out:xml][timeout:300][maxsize:1073741824];
    (
      // Get all nodes in the bounding box
      node({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
      // Get all ways in the bounding box
      way({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
      // Get all relations in the bounding box
      relation({bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']});
    );
    // Recurse down to get all child elements (essential for proper coordinates)
    (._;>;);
    // Output with complete metadata and coordinates
    out meta;
    """

    overpass_url = "http://overpass-api.de/api/interpreter"

    logger.info("Downloading OSM data from Overpass API...")
    logger.info(
        f"  Query area: {bbox['south']:.4f},{bbox['west']:.4f} to {bbox['north']:.4f},{bbox['east']:.4f}"
    )

    try:
        response = requests.post(overpass_url, data=overpass_query, timeout=600)

        if response.status_code == 200:
            # Validate that we got actual OSM data, not an error message
            content = response.content
            if (
                b"<osm" in content and len(content) > 500
            ):  # Reduced threshold for testing
                with open(output_file, "wb") as f:
                    f.write(content)

                # Validate the downloaded data
                file_size_kb = len(content) / 1024
                logger.info(f"✓ OSM data saved: {output_file} ({file_size_kb:.1f} KB)")

                # Basic content validation
                if b"node" in content and b"way" in content:
                    logger.info("✓ Data validation: Contains nodes and ways")
                else:
                    logger.warning("Data validation: Limited data - may be sparse area")

                return True
            else:
                logger.error(f"Invalid OSM data received (size: {len(content)} bytes)")
                return False
        else:
            logger.error(f"Failed to download OSM data: HTTP {response.status_code}")
            if response.content:
                error_msg = response.content.decode("utf-8", errors="ignore")[:200]
                logger.info(f"   Error details: {error_msg}")
            return False

    except requests.exceptions.Timeout:
        logger.error("Request timed out - Overpass API may be busy")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Connection failed - check network connectivity")
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading OSM data: {e}")
        return False


def validate_osm_data_quality(osm_file):
    """Validate and analyze the quality of downloaded OSM data"""
    try:
        import xml.etree.ElementTree as ET

        logger.info(f"📊 Analyzing OSM data quality: {osm_file}")

        # Parse the OSM file to count elements
        tree = ET.parse(osm_file)
        root = tree.getroot()

        node_count = len(root.findall("node"))
        way_count = len(root.findall("way"))
        relation_count = len(root.findall("relation"))

        logger.info(f"   Nodes: {node_count}")
        logger.info(f"   Ways: {way_count}")
        logger.info(f"   Relations: {relation_count}")

        # Check for coordinate completeness in nodes
        nodes_with_coords = 0
        for node in root.findall("node"):
            if "lat" in node.attrib and "lon" in node.attrib:
                nodes_with_coords += 1

        coord_completeness = (
            (nodes_with_coords / node_count * 100) if node_count > 0 else 0
        )
        logger.info(
            f"   Coordinate completeness: {coord_completeness:.1f}% ({nodes_with_coords}/{node_count})"
        )

        # Check for tagged features (POIs, roads, etc.)
        tagged_features = 0
        feature_types = {}

        for element in root.findall(".//tag"):
            key = element.get("k", "")
            value = element.get("v", "")
            if key and value:
                tagged_features += 1
                if key not in feature_types:
                    feature_types[key] = set()
                feature_types[key].add(value)

        logger.info(f"   Tagged features: {tagged_features}")
        logger.info(f"   Feature types: {len(feature_types)} categories")

        # Show most common feature types
        if feature_types:
            common_types = sorted(
                feature_types.items(), key=lambda x: len(x[1]), reverse=True
            )[:5]
            logger.info("   Top feature categories:")
            for key, values in common_types:
                logger.info(f"     {key}: {len(values)} different values")

        # Quality assessment
        quality_score = 0
        if node_count > 100:
            quality_score += 25
        elif node_count > 10:
            quality_score += 10

        if way_count > 10:
            quality_score += 25
        elif way_count > 1:
            quality_score += 10

        if coord_completeness > 95:
            quality_score += 25
        elif coord_completeness > 80:
            quality_score += 15

        if tagged_features > 50:
            quality_score += 25
        elif tagged_features > 10:
            quality_score += 15

        logger.info(f"   Quality score: {quality_score}/100")

        if quality_score >= 75:
            logger.info("   ✓ Excellent data quality")
        elif quality_score >= 50:
            logger.info("   ✓ Good data quality")
        elif quality_score >= 25:
            logger.info("   ⚠ Fair data quality - may have limited features")
        else:
            logger.info("   ⚠ Poor data quality - very limited data")

        return quality_score >= 25

    except (xml.etree.ElementTree.ParseError, FileNotFoundError) as e:
        logger.info(f"   ❌ Error analyzing OSM data: {e}")
        return False


def convert_osm_to_shapefiles(osm_file):
    """Convert OSM data to shapefiles using ogr2ogr - no database needed!"""
    logger.info("Converting OSM data to shapefiles (no database required)...")

    output_dir = Path("data/osm_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check ogr2ogr version
    try:
        result = subprocess.run(
            ["ogr2ogr", "--version"], capture_output=True, text=True, check=True
        )
        logger.info(f"  Using GDAL/OGR version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.info(
            f"  Error: Could not find or run 'ogr2ogr'. Is GDAL installed and in your PATH?"
        )
        return None

    # First, let's see what layers are available in the OSM file
    logger.info("  Inspecting OSM file for available layers...")
    try:
        result = subprocess.run(
            ["ogrinfo", osm_file], capture_output=True, text=True, check=True
        )
        logger.info("  Available layers:")
        for line in result.stdout.split("\n"):
            if "Layer name:" in line:
                logger.info(f"    {line.strip()}")
    except subprocess.CalledProcessError as e:
        logger.info(f"  Warning: Could not inspect OSM file: {e}")

    # OSM layers to extract (these are the standard OSM layer names)
    layers = {
        "points": "points of interest, towns, etc.",
        "lines": "roads, paths, boundaries",
        "multilinestrings": "complex routes",
        "multipolygons": "land use, water bodies, buildings",
    }

    created_files = []

    for layer_name, description in layers.items():
        logger.info(f"  Extracting {layer_name} ({description})...")
        output_file = output_dir / f"{layer_name}.shp"

        cmd = [
            "ogr2ogr",
            "-f",
            "ESRI Shapefile",
            "-overwrite",
            "--debug",
            "on",
            str(output_file),
            osm_file,
            layer_name,
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if output_file.exists():
                logger.info(f"    ✓ Created {output_file}")
                created_files.append(layer_name)
            else:
                logger.info(f"    ⚠ Command succeeded but file not found: {output_file}")
                if result.stdout:
                    logger.info(f"      ogr2ogr stdout:\n{result.stdout}")
                if result.stderr:
                    logger.info(f"      ogr2ogr stderr:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.info(f"    ⚠ Error creating {layer_name}:")
            logger.info(f"      Command: {' '.join(cmd)}")
            logger.info(f"      Stderr: {e.stderr.strip()}")
            logger.info(f"      Stdout: {e.stdout.strip()}")

    logger.info(f"  Successfully created {len(created_files)} shapefiles: {created_files}")

    # Verify files exist and show their info
    for layer in created_files:
        shp_file = output_dir / f"{layer}.shp"
        if shp_file.exists():
            try:
                result = subprocess.run(
                    ["ogrinfo", "-so", str(shp_file), layer],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                # Count features
                feature_count = "unknown"
                for line in result.stdout.split("\n"):
                    if "Feature Count:" in line:
                        feature_count = line.split(":")[1].strip()
                        break
                logger.info(f"    {layer}: {feature_count} features")
            except:
                logger.info(f"    {layer}: file exists but couldn't get info")

    return str(output_dir)


# Synthetic elevation data generation removed per issue requirements
# Real DEM data sources should be used instead
def download_elevation_data(bbox, output_file="elevation_data.tif"):
    """
    Download elevation data for the given bounding box using real DEM sources.
    Synthetic elevation data generation has been removed.
    
    Args:
        bbox: Bounding box dictionary with north, south, east, west
        output_file: Path to output elevation file
        
    Returns:
        None - Real DEM data download not implemented
    """
    logger.error("Real DEM data download not implemented")
    logger.error("Synthetic elevation data generation removed per requirements")
    logger.error("Please implement real DEM sources (SRTM, ASTER, OS Terrain, EU-DEM)")
    return None


def generate_contour_lines(elevation_file, output_dir, interval=10):
    """
    Generate contour lines from elevation data using GDAL

    Args:
        elevation_file: Path to elevation raster (GeoTIFF)
        output_dir: Directory to save contour shapefiles
        interval: Contour interval in meters

    Returns:
        Path to contour shapefile or None if failed
    """
    logger.info(f"📏 Generating contour lines (interval: {interval}m)...")

    if not Path(elevation_file).exists():
        logger.warning(f"Elevation file not found: {elevation_file}")
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    contour_file = output_dir / "contours.shp"

    try:
        # Use gdal_contour to generate contour lines
        cmd = [
            "gdal_contour",
            "-a",
            "elevation",  # Attribute name for elevation values
            "-i",
            str(interval),  # Contour interval
            "-f",
            "ESRI Shapefile",
            str(elevation_file),
            str(contour_file),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        if contour_file.exists():
            # Get feature count for reporting
            try:
                info_result = subprocess.run(
                    ["ogrinfo", "-so", str(contour_file)],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                feature_count = "unknown"
                for line in info_result.stdout.split("\n"):
                    if "Feature Count:" in line:
                        feature_count = line.split(":")[1].strip()
                        break

                logger.info(f"✓ Generated contour lines: {contour_file}")
                logger.info(f"  Features: {feature_count} contour lines")
                logger.info(f"  Interval: {interval}m")

                return str(contour_file)
            except subprocess.CalledProcessError:
                logger.info(f"✓ Generated contour lines: {contour_file}")
                return str(contour_file)
        else:
            logger.warning("Contour generation completed but no output file found")
            return None

    except subprocess.CalledProcessError as e:
        logger.warning(f"Error generating contour lines:")
        logger.info(f"  Command: {' '.join(cmd)}")
        error_msg = e.stderr.strip() if e.stderr else "No error details available"
        logger.info(f"  Error: {error_msg}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error in contour generation: {e}")
        return None


def process_elevation_and_contours(
    bbox, data_dir, contour_interval=10, enable_contours=True
):
    """
    Main function to handle elevation data and contour generation

    Args:
        bbox: Bounding box dictionary with north, south, east, west
        data_dir: Directory for output files
        contour_interval: Elevation interval for contour lines in meters
        enable_contours: Whether to generate contours

    Returns:
        Dictionary with paths to generated files or None if disabled/failed
    """
    if not enable_contours:
        logger.info("📏 Contour generation disabled")
        return None

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    elevation_file = data_dir / "elevation_data.tif"

    # Download/generate elevation data
    if not elevation_file.exists():
        result = download_elevation_data(bbox, str(elevation_file))
        if not result:
            logger.warning("Could not obtain elevation data, skipping contours")
            return None
    else:
        logger.info(f"📁 Using existing elevation data: {elevation_file}")

    # Generate contour lines
    contour_file = generate_contour_lines(
        str(elevation_file), str(data_dir), contour_interval
    )

    if contour_file:
        return {
            "elevation_file": str(elevation_file),
            "contour_file": contour_file,
            "interval": contour_interval,
        }
    else:
        return None

