"""Test real DEM data source implementations"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from utils.elevation_processing import (_download_file_with_progress,
                                        _format_aster_tile_name,
                                        _format_srtm_tile_name,
                                        _is_bbox_in_europe, _is_bbox_in_uk,
                                        download_elevation_data,
                                        get_dem_cache_dir)


class TestDEMSources(unittest.TestCase):
    """Test DEM data source implementations"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_bbox_uk = {
            "north": 57.37,
            "south": 57.26,
            "east": -2.82,
            "west": -2.95,
        }

        self.test_bbox_europe = {"north": 48.9, "south": 48.8, "east": 2.4, "west": 2.3}

        self.test_bbox_global = {
            "north": 35.7,
            "south": 35.6,
            "east": 139.8,
            "west": 139.7,
        }

    def test_get_dem_cache_dir(self):
        """Test DEM cache directory creation"""
        cache_dir = get_dem_cache_dir()
        self.assertTrue(cache_dir.exists())
        self.assertTrue(cache_dir.is_dir())
        self.assertIn(".my_local_map", str(cache_dir))

    def test_format_srtm_tile_name(self):
        """Test SRTM tile name formatting"""
        # Test positive coordinates
        self.assertEqual(_format_srtm_tile_name(57.3, -2.8), "N57W002.hgt")

        # Test negative coordinates
        self.assertEqual(_format_srtm_tile_name(-10.5, 15.2), "S10E015.hgt")

        # Test edge cases
        self.assertEqual(_format_srtm_tile_name(0.0, 0.0), "N00E000.hgt")
        self.assertEqual(_format_srtm_tile_name(-0.1, -0.1), "S00W000.hgt")

    def test_format_aster_tile_name(self):
        """Test ASTER tile name formatting"""
        self.assertEqual(_format_aster_tile_name(57.3, -2.8), "N57W002")
        self.assertEqual(_format_aster_tile_name(-10.5, 15.2), "S10E015")

    def test_is_bbox_in_uk(self):
        """Test UK bounding box detection"""
        self.assertTrue(_is_bbox_in_uk(self.test_bbox_uk))
        self.assertFalse(_is_bbox_in_uk(self.test_bbox_global))

        # Test edge cases
        self.assertTrue(
            _is_bbox_in_uk({"north": 50.0, "south": 49.0, "east": -1.0, "west": -2.0})
        )

    def test_is_bbox_in_europe(self):
        """Test Europe bounding box detection"""
        self.assertTrue(_is_bbox_in_europe(self.test_bbox_europe))
        self.assertTrue(_is_bbox_in_europe(self.test_bbox_uk))  # UK is in Europe
        self.assertFalse(_is_bbox_in_europe(self.test_bbox_global))

    def test_download_elevation_data_all_sources(self):
        """Test all DEM source options"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Test all supported sources - should fail gracefully in sandboxed environment
            for source in ["srtm", "aster", "os_terrain", "eu_dem"]:
                result = download_elevation_data(
                    self.test_bbox_uk,
                    output_file,
                    dem_source=source,
                    allow_synthetic_fallback=False,
                )
                # In sandboxed environment, all should return False
                self.assertFalse(
                    result, f"Source {source} should fail without network access"
                )

    def test_download_elevation_data_unknown_source(self):
        """Test unknown DEM source handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            result = download_elevation_data(
                self.test_bbox_uk,
                output_file,
                dem_source="unknown_source",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)

    @patch("requests.get")
    def test_download_file_with_progress_success(self, mock_get):
        """Test successful file download with progress"""
        # Mock successful download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content.return_value = [b"test_data" * 100]
        mock_get.return_value = mock_response

        with tempfile.NamedTemporaryFile() as temp_file:
            result = _download_file_with_progress(
                "https://example.com/test.tif", temp_file.name
            )
            self.assertTrue(result)

    @patch("requests.get")
    def test_download_file_with_progress_failure(self, mock_get):
        """Test failed file download handling"""
        # Mock failed download
        mock_get.side_effect = Exception("Network error")

        with tempfile.NamedTemporaryFile() as temp_file:
            result = _download_file_with_progress(
                "https://example.com/test.tif", temp_file.name
            )
            self.assertFalse(result)

    def test_os_terrain_uk_only(self):
        """Test OS Terrain is only used for UK areas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # UK area should try OS Terrain (then fallback to SRTM)
            result = download_elevation_data(
                self.test_bbox_uk,
                output_file,
                dem_source="os_terrain",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)  # Should fail in sandboxed environment

            # Non-UK area should reject OS Terrain immediately
            result = download_elevation_data(
                self.test_bbox_global,
                output_file,
                dem_source="os_terrain",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)

    def test_eu_dem_europe_only(self):
        """Test EU-DEM is only used for European areas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # European area should try EU-DEM (then fallback to SRTM)
            result = download_elevation_data(
                self.test_bbox_europe,
                output_file,
                dem_source="eu_dem",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)  # Should fail in sandboxed environment

            # Non-European area should reject EU-DEM immediately
            result = download_elevation_data(
                self.test_bbox_global,
                output_file,
                dem_source="eu_dem",
                allow_synthetic_fallback=False,
            )
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
