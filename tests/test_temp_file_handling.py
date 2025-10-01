"""
Tests for improved temporary file handling in elevation data processing
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from utils.data_processing import (download_elevation_data,
                                   generate_contour_lines,
                                   process_elevation_and_contours)


@pytest.mark.unit
class TestTempFileHandling:
    """Test that temporary files are handled properly and cleaned up"""

    def test_download_elevation_data_no_tempfile_required(self):
        """Test that download_elevation_data no longer uses tempfiles since synthetic generation removed"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Since synthetic data generation is removed, this should return None immediately
            # without creating any temporary files
            with patch("tempfile.NamedTemporaryFile") as mock_temp:
                result = download_elevation_data(bbox, str(output_file))

                # Should return None because real DEM sources not implemented
                assert result is None

                # Should not create any temporary files
                mock_temp.assert_not_called()

    def test_no_temp_files_left_in_current_directory(self):
        """Test that no temporary files are left in the current working directory"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Get current directory files before the operation
            cwd = Path.cwd()
            files_before = set(cwd.glob("*.xyz"))

            # Mock subprocess.run to avoid actual GDAL execution
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

                with patch("pathlib.Path.exists", return_value=True):
                    result = download_elevation_data(bbox, str(output_file))

            # Get current directory files after the operation
            files_after = set(cwd.glob("*.xyz"))

            # Verify no new .xyz files were created in current directory
            assert (
                files_after == files_before
            ), "Temporary .xyz files left in current directory"

    def test_temp_file_cleanup_on_exception(self):
        """Test that temporary files are cleaned up even when exceptions occur"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Get current directory files before the operation
            cwd = Path.cwd()
            files_before = set(cwd.glob("*.xyz"))

            # Mock subprocess.run to raise an exception
            with patch("subprocess.run") as mock_run:
                from subprocess import CalledProcessError

                mock_run.side_effect = CalledProcessError(1, "gdal_translate")

                result = download_elevation_data(bbox, str(output_file))

                # Should return None due to exception
                assert result is None

            # Get current directory files after the operation
            files_after = set(cwd.glob("*.xyz"))

            # Verify no new .xyz files were created in current directory even with exception
            assert (
                files_after == files_before
            ), "Temporary .xyz files left after exception"

    def test_multiple_concurrent_instances_no_conflicts(self):
        """Test that multiple instances handle absence of synthetic data correctly"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_files = [
                Path(temp_dir) / f"test_elevation_{i}.tif" for i in range(3)
            ]

            # Since synthetic data generation is removed, all instances should return None
            # without creating any temporary files or conflicts
            with patch("tempfile.NamedTemporaryFile") as mock_temp:
                # Run multiple instances
                results = []
                for output_file in output_files:
                    result = download_elevation_data(bbox, str(output_file))
                    results.append(result)

                # All should return None (real DEM sources not implemented)
                assert all(result is None for result in results)

                # Should not create any temporary files
                mock_temp.assert_not_called()


@pytest.mark.unit
class TestContourGeneration:
    """Test contour line generation functionality"""

    def test_generate_contour_lines_success(self):
        """Test successful contour line generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            elevation_file = Path(temp_dir) / "elevation.tif"
            output_dir = Path(temp_dir) / "contours"

            # Create a fake elevation file
            elevation_file.touch()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

                # Mock contour file creation
                expected_contour_file = output_dir / "contours.shp"
                with patch("pathlib.Path.exists") as mock_exists:

                    def side_effect(path=None):
                        if path is None:
                            path = expected_contour_file
                        return str(path).endswith("elevation.tif") or str(
                            path
                        ).endswith("contours.shp")

                    mock_exists.side_effect = side_effect

                    result = generate_contour_lines(
                        str(elevation_file), str(output_dir), interval=10
                    )

                assert result == str(expected_contour_file)
                # Should be called twice: once for gdal_contour, once for ogrinfo
                assert mock_run.call_count == 2

    def test_process_elevation_and_contours_success(self):
        """Test successful complete contour processing"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "utils.data_processing.download_elevation_data"
            ) as mock_download:
                with patch(
                    "utils.data_processing.generate_contour_lines"
                ) as mock_generate:
                    # Mock successful operations
                    elevation_file = f"{temp_dir}/elevation_data.tif"
                    contour_file = f"{temp_dir}/contours.shp"

                    mock_download.return_value = elevation_file
                    mock_generate.return_value = contour_file

                    result = process_elevation_and_contours(
                        bbox, temp_dir, contour_interval=20, enable_contours=True
                    )

                    assert result is not None
                    assert result["elevation_file"] == elevation_file
                    assert result["contour_file"] == contour_file
                    assert result["interval"] == 20

                    mock_download.assert_called_once()
                    mock_generate.assert_called_once_with(elevation_file, temp_dir, 20)

    def test_process_elevation_and_contours_disabled(self):
        """Test contour processing when disabled"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_and_contours(
                bbox, temp_dir, enable_contours=False
            )

            assert result is None
