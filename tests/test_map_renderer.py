"""Tests for map renderer module"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.map_renderer import execute_map_rendering, create_mapnik_style, render_map


class TestMapRenderer:
    """Test map rendering functions"""

    @pytest.fixture
    def sample_area_config(self):
        """Sample area configuration for testing"""
        return {
            "center": {"lat": 57.3167, "lon": -2.8833},
            "coverage": {"width_km": 8, "height_km": 12},
            "scale": 25000,
            "name": "Lumsden, Aberdeenshire",
        }

    @pytest.fixture
    def sample_output_format(self):
        """Sample output format for testing"""
        return {
            "width_mm": 297,
            "height_mm": 420,
            "dpi": 300
        }

    @pytest.fixture
    def sample_bbox(self):
        """Sample bounding box for testing"""
        return {
            "south": 57.0,
            "north": 57.5,
            "west": -3.0,
            "east": -2.5,
        }

    @pytest.mark.unit
    def test_create_mapnik_style(self, sample_area_config):
        """Test mapnik style creation"""
        with patch("utils.map_renderer.build_mapnik_style", return_value="tourist_map_style.xml") as mock_build:
            
            style_file = create_mapnik_style("osm_data", sample_area_config, True)
            
            mock_build.assert_called_once_with("tourist", "osm_data", sample_area_config, True)
            assert style_file == "tourist_map_style.xml"

    @pytest.mark.unit
    def test_render_map_mapnik_not_available(self, sample_bbox):
        """Test render_map when mapnik is not available"""
        with patch("builtins.__import__", side_effect=ImportError):
            result = render_map("style.xml", sample_bbox, "output.png", 100, 100)
            assert result is False

    @pytest.mark.unit
    def test_render_map_success(self, sample_bbox):
        """Test successful map rendering"""
        # Mock mapnik module and its components
        mock_mapnik = MagicMock()
        mock_map = MagicMock()
        mock_mapnik.Map.return_value = mock_map
        
        # Mock the projection and transform objects
        mock_projection = MagicMock()
        mock_transform = MagicMock()
        mock_bbox_transformed = MagicMock()
        
        mock_mapnik.Projection.return_value = mock_projection
        mock_mapnik.ProjTransform.return_value = mock_transform
        mock_mapnik.Box2d.return_value = MagicMock()
        mock_transform.forward.return_value = mock_bbox_transformed
        
        with patch.dict('sys.modules', {'mapnik': mock_mapnik}), \
             patch("utils.map_renderer.MapLegend") as mock_legend_class, \
             patch("utils.map_renderer.add_legend_to_image", return_value=True), \
             patch("os.path.getsize", return_value=1024000):  # 1MB
            
            mock_legend = MagicMock()
            mock_legend.render_to_map.return_value = "legend_data"
            mock_legend_class.return_value = mock_legend
            
            result = render_map("style.xml", sample_bbox, "output.png", 100, 100)
            
            assert result is True
            mock_mapnik.load_map.assert_called_once_with(mock_map, "style.xml")
            mock_mapnik.render_to_file.assert_called_once_with(mock_map, "output.png", "png")

    @pytest.mark.unit
    def test_execute_map_rendering_success(self, sample_area_config, sample_output_format, sample_bbox):
        """Test successful map rendering workflow"""
        with patch("pathlib.Path.mkdir"), \
             patch("utils.map_renderer.create_mapnik_style", return_value="style.xml"), \
             patch("utils.map_renderer.render_map", return_value=True):
            
            result = execute_map_rendering(
                "lumsden", sample_area_config, sample_output_format, sample_bbox,
                "osm_data", True, 100, 100
            )
            
            assert result is True

    @pytest.mark.unit
    def test_execute_map_rendering_failure(self, sample_area_config, sample_output_format, sample_bbox):
        """Test failed map rendering workflow"""
        with patch("pathlib.Path.mkdir"), \
             patch("utils.map_renderer.create_mapnik_style", return_value="style.xml"), \
             patch("utils.map_renderer.render_map", return_value=False):
            
            result = execute_map_rendering(
                "lumsden", sample_area_config, sample_output_format, sample_bbox,
                "osm_data", True, 100, 100
            )
            
            assert result is False