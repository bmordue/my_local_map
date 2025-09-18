"""Unit tests for data processing utilities"""

import math
from unittest.mock import MagicMock, mock_open, patch

import pytest

from utils.data_processing import (
    calculate_bbox,
    convert_osm_to_shapefiles,
    download_osm_data,
)


class TestDataProcessing:
    """Test geographic and data processing utilities"""

    @pytest.mark.unit
    def test_calculate_bbox_basic(self):
        """Test basic bounding box calculation"""
        center_lat = 57.3167
        center_lon = -2.8833
        width_km = 8
        height_km = 12
        
        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)
        
        # Verify bbox structure
        assert isinstance(bbox, dict)
        assert 'south' in bbox
        assert 'north' in bbox
        assert 'west' in bbox
        assert 'east' in bbox
        
        # Verify center is actually in the middle
        center_lat_calc = (bbox['south'] + bbox['north']) / 2
        center_lon_calc = (bbox['west'] + bbox['east']) / 2
        
        assert abs(center_lat_calc - center_lat) < 0.001
        assert abs(center_lon_calc - center_lon) < 0.001

    @pytest.mark.unit
    def test_calculate_bbox_coordinates_valid(self):
        """Test that calculated bbox coordinates are valid"""
        center_lat = 57.3167
        center_lon = -2.8833
        width_km = 8
        height_km = 12
        
        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)
        
        # North should be greater than South
        assert bbox['north'] > bbox['south']
        
        # East should be greater than West (for this longitude)
        assert bbox['east'] > bbox['west']
        
        # Latitude should be valid (-90 to 90)
        assert -90 <= bbox['south'] <= 90
        assert -90 <= bbox['north'] <= 90
        
        # Longitude should be valid (-180 to 180)
        assert -180 <= bbox['west'] <= 180
        assert -180 <= bbox['east'] <= 180

    @pytest.mark.unit
    def test_calculate_bbox_dimensions(self):
        """Test that bbox dimensions approximately match input"""
        center_lat = 57.3167
        center_lon = -2.8833
        width_km = 8
        height_km = 12
        
        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)
        
        # Calculate actual dimensions using the same logic as the function
        lat_deg_per_km = 1 / 111.32
        lon_deg_per_km = 1 / (111.32 * abs(math.cos(math.radians(center_lat))))
        
        expected_height_deg = height_km * lat_deg_per_km
        expected_width_deg = width_km * lon_deg_per_km
        
        actual_height_deg = bbox['north'] - bbox['south']
        actual_width_deg = bbox['east'] - bbox['west']
        
        assert abs(actual_height_deg - expected_height_deg) < 0.001
        assert abs(actual_width_deg - expected_width_deg) < 0.001

    @pytest.mark.unit
    def test_calculate_bbox_equator(self):
        """Test bbox calculation at equator (edge case)"""
        center_lat = 0.0  # Equator
        center_lon = 0.0
        width_km = 10
        height_km = 10
        
        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)
        
        # At equator, longitude conversion is simplest
        assert bbox['north'] > bbox['south']
        assert bbox['east'] > bbox['west']
        assert abs((bbox['north'] + bbox['south']) / 2) < 0.001  # Should be near 0

    @pytest.mark.unit
    def test_calculate_bbox_poles(self):
        """Test bbox calculation near poles"""
        center_lat = 85.0  # Near north pole
        center_lon = 0.0
        width_km = 5
        height_km = 5
        
        bbox = calculate_bbox(center_lat, center_lon, width_km, height_km)
        
        # Should still produce valid coordinates
        assert bbox['north'] > bbox['south']
        assert bbox['north'] <= 90  # Don't exceed north pole
        assert bbox['south'] >= -90

    @pytest.mark.unit
    @patch('requests.post')
    def test_download_osm_data_success(self, mock_post):
        """Test successful OSM data download"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<osm>test data</osm>'
        mock_post.return_value = mock_response
        
        bbox = {'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}
        output_file = '/tmp/test.osm'
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = download_osm_data(bbox, output_file)
        
        assert result is True
        mock_post.assert_called_once()
        mock_file.assert_called_once_with(output_file, 'wb')

    @pytest.mark.unit
    @patch('requests.post')
    def test_download_osm_data_failure(self, mock_post):
        """Test OSM data download failure"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        bbox = {'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}
        output_file = '/tmp/test.osm'
        
        result = download_osm_data(bbox, output_file)
        
        assert result is False
        mock_post.assert_called_once()

    @pytest.mark.unit
    @patch('requests.post')
    def test_download_osm_data_query_format(self, mock_post):
        """Test that OSM query is properly formatted"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<osm>test data</osm>'
        mock_post.return_value = mock_response
        
        bbox = {'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}
        output_file = '/tmp/test.osm'
        
        with patch('builtins.open', mock_open()):
            download_osm_data(bbox, output_file)
        
        # Verify the query contains the bbox coordinates
        call_args = mock_post.call_args
        query = call_args[1]['data']  # Get the data parameter
        
        assert '57.0' in query  # south
        assert '57.5' in query  # north
        assert '-3.0' in query  # west
        assert '-2.5' in query  # east

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_convert_osm_to_shapefiles_success(self, mock_exists, mock_mkdir, mock_run):
        """Test successful OSM to shapefile conversion"""
        # Mock successful ogr2ogr commands
        mock_run.return_value = MagicMock(
            stdout="Success",
            stderr="",
            returncode=0
        )
        mock_exists.return_value = True
        
        osm_file = '/tmp/test.osm'
        
        result = convert_osm_to_shapefiles(osm_file)
        
        assert result is not None
        assert 'osm_data' in result
        mock_mkdir.assert_called()

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_convert_osm_to_shapefiles_ogr2ogr_not_found(self, mock_run):
        """Test handling when ogr2ogr is not available"""
        # Mock ogr2ogr not found
        mock_run.side_effect = FileNotFoundError("ogr2ogr not found")
        
        osm_file = '/tmp/test.osm'
        
        result = convert_osm_to_shapefiles(osm_file)
        
        assert result is None

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_convert_osm_to_shapefiles_layers(self, mock_mkdir, mock_run):
        """Test that all expected layers are processed"""
        # Mock successful ogr2ogr commands
        mock_run.return_value = MagicMock(
            stdout="Layer info",
            stderr="",
            returncode=0
        )
        
        osm_file = '/tmp/test.osm'
        
        with patch('pathlib.Path.exists', return_value=True):
            result = convert_osm_to_shapefiles(osm_file)
        
        # Verify ogr2ogr was called for each expected layer
        expected_layers = ['points', 'lines', 'multilinestrings', 'multipolygons']
        
        # Should be called for version check, info, and then for each layer
        assert mock_run.call_count >= len(expected_layers)
        
        # Check that each layer was processed
        call_args_list = [call[0][0] for call in mock_run.call_args_list]
        
        for layer in expected_layers:
            # Check if any call includes this layer name
            layer_processed = any(layer in ' '.join(args) for args in call_args_list if isinstance(args, list))
            assert layer_processed, f"Layer {layer} was not processed"