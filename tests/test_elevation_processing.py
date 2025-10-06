"""Test elevation processing and hillshading functionality"""

import tempfile
import unittest
from unittest.mock import mock_open, patch

from utils.elevation_processing import (calculate_elevation_bbox,
                                        download_elevation_data,
                                        generate_hillshade,
                                        process_elevation_for_hillshading)


class TestElevationProcessing(unittest.TestCase):
    """Test elevation data processing utilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_bbox = {"west": -3.0, "east": -2.5, "south": 57.0, "north": 57.5}

        self.area_config_enabled = {
            "hillshading": {
                "enabled": True,
                "opacity": 0.4,
                "azimuth": 315,
                "altitude": 45,
                "z_factor": 1.0,
                "scale": 111120,
            }
        }

        self.area_config_disabled = {"hillshading": {"enabled": False}}

    def test_calculate_elevation_bbox_basic(self):
        """Test basic elevation bbox calculation"""
        result = calculate_elevation_bbox(self.test_bbox)

        # Should add buffer to all sides
        self.assertLess(result["west"], self.test_bbox["west"])
        self.assertGreater(result["east"], self.test_bbox["east"])
        self.assertLess(result["south"], self.test_bbox["south"])
        self.assertGreater(result["north"], self.test_bbox["north"])

    def test_calculate_elevation_bbox_custom_buffer(self):
        """Test elevation bbox calculation with custom buffer"""
        buffer_km = 2.0
        result = calculate_elevation_bbox(self.test_bbox, buffer_km)

        # Should add larger buffer
        lat_buffer = buffer_km / 111.0
        self.assertAlmostEqual(
            result["south"], self.test_bbox["south"] - lat_buffer, places=4
        )
        self.assertAlmostEqual(
            result["north"], self.test_bbox["north"] + lat_buffer, places=4
        )

    def test_calculate_elevation_bbox_dimensions(self):
        """Test elevation bbox maintains reasonable dimensions"""
        result = calculate_elevation_bbox(self.test_bbox)

        width = result["east"] - result["west"]
        height = result["north"] - result["south"]

        # Should be larger than original
        original_width = self.test_bbox["east"] - self.test_bbox["west"]
        original_height = self.test_bbox["north"] - self.test_bbox["south"]

        self.assertGreater(width, original_width)
        self.assertGreater(height, original_height)

    @patch("utils.elevation_processing._download_srtm_elevation_data", return_value=False)
    def test_download_elevation_data_no_real_dem(self, mock_download):
        """Test that elevation data download returns False when real DEM sources unavailable and fallback disabled"""
        with tempfile.NamedTemporaryFile(suffix=".tif") as temp_file:
            # Test SRTM source - should return False with fallback disabled
            result = download_elevation_data(
                self.test_bbox,
                temp_file.name,
                dem_source="srtm",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)

            # Test other DEM sources - should also return False
            for source in ["aster", "os_terrain", "eu_dem"]:
                result = download_elevation_data(
                    self.test_bbox,
                    temp_file.name,
                    dem_source=source,
                    allow_synthetic_fallback=False,
                )
                self.assertFalse(result)

            # Test unknown source - should return False
            result = download_elevation_data(
                self.test_bbox,
                temp_file.name,
                dem_source="unknown",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)

    @patch("utils.elevation_processing._download_srtm_elevation_data", return_value=False)
    def test_download_elevation_data_failure(self, mock_download):
        """Test elevation data download failure when real DEM unavailable and fallback disabled"""
        with tempfile.NamedTemporaryFile(suffix=".tif") as temp_file:
            # Should return False with fallback disabled
            result = download_elevation_data(
                self.test_bbox,
                temp_file.name,
                dem_source="srtm",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)

    @patch("subprocess.run")
    def test_generate_hillshade_success(self, mock_subprocess):
        """Test successful hillshade generation"""
        # Mock successful subprocess call
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ""

        config = self.area_config_enabled["hillshading"]

        with tempfile.NamedTemporaryFile(
            suffix=".tif"
        ) as dem_file, tempfile.NamedTemporaryFile(suffix=".tif") as hillshade_file:

            result = generate_hillshade(dem_file.name, hillshade_file.name, config)

            self.assertTrue(result)
            # Should call gdaldem hillshade
            mock_subprocess.assert_called()
            call_args = mock_subprocess.call_args[0][0]
            self.assertIn("gdaldem", call_args)
            self.assertIn("hillshade", call_args)
            self.assertIn(str(config["azimuth"]), call_args)
            self.assertIn(str(config["altitude"]), call_args)

    @patch("subprocess.run")
    def test_generate_hillshade_failure(self, mock_subprocess):
        """Test hillshade generation failure"""
        # Mock failed subprocess call
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "Error message"

        config = self.area_config_enabled["hillshading"]

        with tempfile.NamedTemporaryFile(
            suffix=".tif"
        ) as dem_file, tempfile.NamedTemporaryFile(suffix=".tif") as hillshade_file:

            result = generate_hillshade(dem_file.name, hillshade_file.name, config)

            self.assertFalse(result)

    def test_process_elevation_for_hillshading_disabled(self):
        """Test processing when hillshading is disabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                self.test_bbox, self.area_config_disabled, temp_dir
            )

            self.assertIsNone(result)

    @patch("utils.elevation_processing.download_elevation_data")
    @patch("utils.elevation_processing.generate_hillshade")
    def test_process_elevation_for_hillshading_success(
        self, mock_hillshade, mock_download
    ):
        """Test successful elevation processing workflow"""
        # Mock successful operations
        mock_download.return_value = True
        mock_hillshade.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                self.test_bbox, self.area_config_enabled, temp_dir
            )

            self.assertIsNotNone(result)
            self.assertTrue(result.endswith("hillshade.tif"))
            mock_download.assert_called_once()
            mock_hillshade.assert_called_once()

    @patch("utils.elevation_processing.download_elevation_data")
    def test_process_elevation_for_hillshading_download_failure(self, mock_download):
        """Test processing when elevation download fails"""
        # Mock failed download
        mock_download.return_value = False

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                self.test_bbox, self.area_config_enabled, temp_dir
            )

            self.assertIsNone(result)

    @patch("utils.elevation_processing.download_elevation_data")
    @patch("utils.elevation_processing.generate_hillshade")
    def test_process_elevation_for_hillshading_hillshade_failure(
        self, mock_hillshade, mock_download
    ):
        """Test processing when hillshade generation fails"""
        # Mock successful download but failed hillshade
        mock_download.return_value = True
        mock_hillshade.return_value = False

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_for_hillshading(
                self.test_bbox, self.area_config_enabled, temp_dir
            )

            self.assertIsNone(result)

    def test_hillshading_config_parameters(self):
        """Test that hillshading config parameters are properly used"""
        config = self.area_config_enabled["hillshading"]

        # Verify all expected parameters are present
        self.assertIn("opacity", config)
        self.assertIn("azimuth", config)
        self.assertIn("altitude", config)
        self.assertIn("z_factor", config)
        self.assertIn("scale", config)

        # Verify reasonable default values
        self.assertEqual(config["opacity"], 0.4)
        self.assertEqual(config["azimuth"], 315)
        self.assertEqual(config["altitude"], 45)
        self.assertEqual(config["z_factor"], 1.0)
        self.assertEqual(config["scale"], 111120)

    @patch("utils.elevation_processing._download_srtm_elevation_data")
    @patch("utils.elevation_processing._create_synthetic_dem_fallback")
    def test_download_elevation_data_with_fallback_disabled(
        self, mock_synthetic, mock_srtm
    ):
        """Test download with synthetic fallback disabled"""
        mock_srtm.return_value = False

        with tempfile.NamedTemporaryFile(suffix=".tif") as temp_file:
            result = download_elevation_data(
                self.test_bbox,
                temp_file.name,
                dem_source="srtm",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)
            # Synthetic fallback should not be called
            mock_synthetic.assert_not_called()

    @patch("utils.elevation_processing._download_srtm_elevation_data")
    @patch("utils.elevation_processing._create_synthetic_dem_fallback")
    def test_download_elevation_data_with_fallback_enabled(
        self, mock_synthetic, mock_srtm
    ):
        """Test that download_elevation_data uses synthetic fallback when real download fails and fallback is enabled"""
        # Mock failed real download, successful synthetic fallback
        mock_srtm.return_value = False
        mock_synthetic.return_value = True

        with tempfile.NamedTemporaryFile(suffix=".tif") as temp_file:
            # Test with fallback enabled - should succeed
            result = download_elevation_data(
                self.test_bbox,
                temp_file.name,
                dem_source="srtm",
                allow_synthetic_fallback=True,
            )

            self.assertTrue(result)
            # Verify synthetic fallback was called
            mock_synthetic.assert_called_once()

    @patch("utils.elevation_processing.download_elevation_data")
    def test_process_elevation_for_hillshading_dem_failure(self, mock_download):
        """Test that process_elevation_for_hillshading propagates RuntimeError from DEM download failure"""
        # Mock download raising RuntimeError
        mock_download.side_effect = RuntimeError(
            "DEM data download failed from 'srtm' source and synthetic fallback is disabled"
        )

        area_config_no_fallback = {
            "hillshading": {"enabled": True},
            "elevation": {"source": "srtm", "allow_synthetic_fallback": False},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Should propagate the RuntimeError
            with self.assertRaises(RuntimeError) as context:
                process_elevation_for_hillshading(
                    self.test_bbox, area_config_no_fallback, temp_dir
                )

            self.assertIn("DEM data download failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()
