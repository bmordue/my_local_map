#!/usr/bin/env python3
"""
Test OSM data integration with proper coordinates
"""

import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from utils.data_processing import (calculate_bbox, convert_osm_to_shapefiles,
                                   download_osm_data,
                                   validate_osm_data_quality)


class TestOSMIntegration:
    """Test OSM data integration and coordinate handling"""

    def test_osm_data_validation(self):
        """Test OSM data validation function"""
        osm_file = "lumsden_area.osm"
        assert Path(osm_file).exists(), f"OSM test file {osm_file} not found"

        # Test validation function
        is_valid = validate_osm_data_quality(osm_file)
        assert is_valid, "OSM data validation should pass for test data"

    def test_coordinate_completeness(self):
        """Test that all nodes have proper coordinates"""
        osm_file = "lumsden_area.osm"
        tree = ET.parse(osm_file)
        root = tree.getroot()

        nodes = root.findall("node")
        assert len(nodes) > 0, "Should have some nodes"

        nodes_with_coords = 0
        for node in nodes:
            if "lat" in node.attrib and "lon" in node.attrib:
                # Validate coordinate values are reasonable for Scotland (Aberdeenshire area)
                lat = float(node.attrib["lat"])
                lon = float(node.attrib["lon"])
                assert 56.0 < lat < 59.0, f"Latitude {lat} should be in Scotland range"
                assert -4.3 < lon < -1.0, f"Longitude {lon} should be in Scotland range"
                nodes_with_coords += 1

        # All nodes should have coordinates
        assert nodes_with_coords == len(nodes), "All nodes should have coordinates"

    def test_shapefile_conversion_with_features(self):
        """Test that OSM to shapefile conversion extracts features properly"""
        if Path("data/osm_data").exists():
            import shutil

            shutil.rmtree("data/osm_data")

        # Convert OSM to shapefiles
        data_dir = convert_osm_to_shapefiles("lumsden_area.osm")
        assert data_dir is not None, "Conversion should succeed"

        # Check that shapefiles were created
        data_path = Path(data_dir)
        assert data_path.exists(), "Data directory should exist"

        # Check individual shapefiles
        shapefiles = ["points", "lines", "multilinestrings", "multipolygons"]
        for shpname in shapefiles:
            shp_file = data_path / f"{shpname}.shp"
            assert shp_file.exists(), f"Shapefile {shpname}.shp should exist"

            # Check feature count using ogrinfo
            try:
                result = subprocess.run(
                    ["ogrinfo", "-so", str(shp_file), shpname],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                feature_count = None
                for line in result.stdout.split("\n"):
                    if "Feature Count:" in line:
                        feature_count = int(line.split(":")[1].strip())
                        break

                # For our test data, we should have features in points and lines at least
                if shpname in ["points", "lines"]:
                    assert (
                        feature_count is not None and feature_count > 0
                    ), f"{shpname} should have features: got {feature_count}"

            except subprocess.CalledProcessError as e:
                pytest.fail(f"Failed to check {shpname} features: {e}")

    def test_bbox_calculation(self):
        """Test bounding box calculation for coordinates"""
        # Test with Lumsden coordinates
        center_lat, center_lon = 57.3167, -2.8833
        width_km, height_km = 8, 12

        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)

        # Check bbox structure
        required_keys = ["south", "north", "west", "east"]
        for key in required_keys:
            assert key in bbox, f"bbox should contain {key}"

        # Check coordinate order and reasonableness
        assert bbox["south"] < bbox["north"], "South should be less than north"
        assert bbox["west"] < bbox["east"], "West should be less than east"

        # Check coordinates are around Lumsden area
        assert (
            57.2 < bbox["south"] < bbox["north"] < 57.4
        ), "Latitude should be in Lumsden range"
        assert (
            -3.0 < bbox["west"] < bbox["east"] < -2.7
        ), "Longitude should be in Lumsden range"

    def test_overpass_query_structure(self):
        """Test that the Overpass API query is properly structured"""
        import unittest.mock

        from utils.data_processing import download_osm_data

        # Mock the requests.post to capture the query
        with unittest.mock.patch("utils.data_processing.requests.post") as mock_post:
            # Set up mock to avoid actual network call
            mock_response = unittest.mock.Mock()
            mock_response.status_code = 200
            mock_response.content = b"<osm></osm>"
            mock_post.return_value = mock_response

            bbox = calculate_bbox(57.3167, -2.8833, 8, 12)

            with tempfile.NamedTemporaryFile() as tmp:
                download_osm_data(bbox, tmp.name)

                # Check that requests.post was called
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args

                # Check the query structure
                query = kwargs["data"]
                assert "out:xml" in query, "Query should specify XML output"
                assert "timeout:300" in query, "Query should have timeout"
                assert "maxsize:" in query, "Query should have maxsize limit"
                assert "node(" in query, "Query should include nodes"
                assert "way(" in query, "Query should include ways"
                assert "relation(" in query, "Query should include relations"
                assert "out meta" in query, "Query should request metadata"

                # Check coordinate format in query
                bbox_str = (
                    f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
                )
                assert bbox_str in query, "Query should contain proper bbox coordinates"


if __name__ == "__main__":
    pytest.main([__file__])
