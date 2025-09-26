"""Unit tests for configuration utilities"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from utils.config import (
    calculate_pixel_dimensions,
    load_area_config,
    load_output_format,
)


class TestConfigUtilities:
    """Test configuration loading and processing"""

    @pytest.fixture
    def sample_areas_config(self):
        """Sample areas configuration for testing"""
        return {
            "lumsden": {
                "center": {"lat": 57.3167, "lon": -2.8833},
                "coverage": {"width_km": 8, "height_km": 12},
                "scale": 25000,
                "name": "Lumsden, Aberdeenshire",
            },
            "test_area": {
                "center": {"lat": 55.0, "lon": -3.0},
                "coverage": {"width_km": 10, "height_km": 15},
                "scale": 50000,
                "name": "Test Area",
            },
        }

    @pytest.fixture
    def sample_output_formats(self):
        """Sample output formats configuration for testing"""
        return {
            "A3": {
                "width_mm": 297,
                "height_mm": 420,
                "dpi": 300,
                "description": "Standard A3 format",
            },
            "A4": {
                "width_mm": 210,
                "height_mm": 297,
                "dpi": 300,
                "description": "Standard A4 format",
            },
        }

    @pytest.mark.unit
    def test_load_area_config_success(self, sample_areas_config):
        """Test successful loading of area configuration"""
        mock_file_content = json.dumps(sample_areas_config)

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("pathlib.Path.open"):
                result = load_area_config("lumsden")

        assert result == sample_areas_config["lumsden"]
        assert result["center"]["lat"] == 57.3167
        assert result["center"]["lon"] == -2.8833
        assert result["coverage"]["width_km"] == 8
        assert result["coverage"]["height_km"] == 12
        assert result["scale"] == 25000

    @pytest.mark.unit
    def test_load_area_config_nonexistent_area(self, sample_areas_config):
        """Test loading non-existent area raises KeyError"""
        mock_file_content = json.dumps(sample_areas_config)

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("pathlib.Path.open"):
                with pytest.raises(KeyError):
                    load_area_config("nonexistent_area")

    @pytest.mark.unit
    def test_load_output_format_success(self, sample_output_formats):
        """Test successful loading of output format configuration"""
        mock_file_content = json.dumps(sample_output_formats)

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("pathlib.Path.open"):
                result = load_output_format("A3")

        assert result == sample_output_formats["A3"]
        assert result["width_mm"] == 297
        assert result["height_mm"] == 420
        assert result["dpi"] == 300

    @pytest.mark.unit
    def test_load_output_format_nonexistent_format(self, sample_output_formats):
        """Test loading non-existent format raises KeyError"""
        mock_file_content = json.dumps(sample_output_formats)

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("pathlib.Path.open"):
                with pytest.raises(KeyError):
                    load_output_format("B5")

    @pytest.mark.unit
    def test_calculate_pixel_dimensions_a3(self):
        """Test pixel dimension calculation for A3 format"""
        output_format = {"width_mm": 297, "height_mm": 420, "dpi": 300}

        width_px, height_px = calculate_pixel_dimensions(output_format)

        # Expected: 297mm / 25.4mm_per_inch * 300dpi = 3507px
        # Expected: 420mm / 25.4mm_per_inch * 300dpi = 4960px
        assert width_px == 3507
        assert height_px == 4960

    @pytest.mark.unit
    def test_calculate_pixel_dimensions_a4(self):
        """Test pixel dimension calculation for A4 format"""
        output_format = {"width_mm": 210, "height_mm": 297, "dpi": 300}

        width_px, height_px = calculate_pixel_dimensions(output_format)

        # Expected: 210mm / 25.4mm_per_inch * 300dpi = 2480px
        # Expected: 297mm / 25.4mm_per_inch * 300dpi = 3507px
        assert width_px == 2480
        assert height_px == 3507

    @pytest.mark.unit
    def test_calculate_pixel_dimensions_different_dpi(self):
        """Test pixel dimension calculation with different DPI"""
        output_format = {"width_mm": 100, "height_mm": 100, "dpi": 150}

        width_px, height_px = calculate_pixel_dimensions(output_format)

        # Expected: 100mm / 25.4mm_per_inch * 150dpi = 590px
        expected_pixels = int(100 / 25.4 * 150)
        assert width_px == expected_pixels
        assert height_px == expected_pixels

    @pytest.mark.unit
    def test_calculate_pixel_dimensions_precision(self):
        """Test that pixel dimensions are properly rounded to integers"""
        output_format = {"width_mm": 100.5, "height_mm": 200.7, "dpi": 72}

        width_px, height_px = calculate_pixel_dimensions(output_format)

        assert isinstance(width_px, int)
        assert isinstance(height_px, int)
        assert width_px > 0
        assert height_px > 0
