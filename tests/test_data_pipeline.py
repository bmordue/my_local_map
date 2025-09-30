"""Tests for data pipeline module"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.data_pipeline import prepare_osm_data, process_data_pipeline


class TestDataPipeline:
    """Test data pipeline functions"""

    @pytest.fixture
    def sample_area_config(self):
        """Sample area configuration for testing"""
        return {
            "center": {"lat": 57.3167, "lon": -2.8833},
            "coverage": {"width_km": 8, "height_km": 12},
            "scale": 25000,
            "name": "Lumsden, Aberdeenshire",
            "osm_file": "data/lumsden_area.osm",
            "contours": {"enabled": True, "interval": 10},
            "hillshading": {"enabled": True, "opacity": 0.4}
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
    def test_prepare_osm_data_existing_file(self, sample_area_config, sample_bbox):
        """Test OSM data preparation when file exists"""
        with patch("pathlib.Path.exists", return_value=True), \
             patch("utils.data_pipeline.validate_osm_data_quality", return_value=True):
            
            osm_file, success = prepare_osm_data("lumsden", sample_area_config, sample_bbox, Path("data"))
            
            assert success is True
            assert osm_file == "data/lumsden_area.osm"

    @pytest.mark.unit
    def test_prepare_osm_data_download_success(self, sample_area_config, sample_bbox):
        """Test OSM data preparation with successful download"""
        with patch("pathlib.Path.exists", return_value=False), \
             patch("utils.data_pipeline.download_osm_data", return_value=True), \
             patch("utils.data_pipeline.validate_osm_data_quality", return_value=True):
            
            osm_file, success = prepare_osm_data("lumsden", sample_area_config, sample_bbox, Path("data"))
            
            assert success is True
            assert osm_file == "data/lumsden_area.osm"

    @pytest.mark.unit
    def test_prepare_osm_data_download_failure(self, sample_area_config, sample_bbox):
        """Test OSM data preparation with failed download"""
        with patch("pathlib.Path.exists", return_value=False), \
             patch("utils.data_pipeline.download_osm_data", return_value=False):
            
            osm_file, success = prepare_osm_data("lumsden", sample_area_config, sample_bbox, Path("data"))
            
            assert success is False
            assert osm_file is None

    @pytest.mark.unit
    def test_process_data_pipeline_success(self, sample_area_config, sample_bbox):
        """Test successful data pipeline processing"""
        with patch("utils.data_pipeline.prepare_osm_data", return_value=("data/lumsden_area.osm", True)), \
             patch("utils.data_pipeline.convert_osm_to_shapefiles", return_value="osm_data"), \
             patch("utils.data_pipeline.process_elevation_and_contours", return_value={"interval": 10}), \
             patch("utils.data_pipeline.process_elevation_for_hillshading", return_value="hillshade.tif"):
            
            osm_data_dir, hillshade_available, success = process_data_pipeline(
                "lumsden", sample_area_config, sample_bbox, Path("data")
            )
            
            assert success is True
            assert osm_data_dir == "osm_data"
            assert hillshade_available is True

    @pytest.mark.unit
    def test_process_data_pipeline_osm_failure(self, sample_area_config, sample_bbox):
        """Test data pipeline with OSM preparation failure"""
        with patch("utils.data_pipeline.prepare_osm_data", return_value=(None, False)):
            
            osm_data_dir, hillshade_available, success = process_data_pipeline(
                "lumsden", sample_area_config, sample_bbox, Path("data")
            )
            
            assert success is False
            assert osm_data_dir is None
            assert hillshade_available is False

    @pytest.mark.unit
    def test_process_data_pipeline_no_hillshading(self, sample_area_config, sample_bbox):
        """Test data pipeline when hillshading is not available"""
        with patch("utils.data_pipeline.prepare_osm_data", return_value=("data/lumsden_area.osm", True)), \
             patch("utils.data_pipeline.convert_osm_to_shapefiles", return_value="osm_data"), \
             patch("utils.data_pipeline.process_elevation_and_contours", return_value={"interval": 10}), \
             patch("utils.data_pipeline.process_elevation_for_hillshading", return_value=None):
            
            osm_data_dir, hillshade_available, success = process_data_pipeline(
                "lumsden", sample_area_config, sample_bbox, Path("data")
            )
            
            assert success is True
            assert osm_data_dir == "osm_data"
            assert hillshade_available is False