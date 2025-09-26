"""
Tests for contour line generation functionality
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from utils.data_processing import (
    download_elevation_data,
    generate_contour_lines,
    process_elevation_and_contours,
)


@pytest.mark.unit
class TestContourGeneration:
    """Test contour line generation functionality"""

    def test_download_elevation_data_success(self):
        """Test successful elevation data generation"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Mock GDAL command execution
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

                # Mock file existence after creation
                with patch("pathlib.Path.exists", return_value=True):
                    result = download_elevation_data(bbox, str(output_file))

                assert result == str(output_file)
                mock_run.assert_called_once()

    def test_download_elevation_data_failure(self):
        """Test elevation data generation failure"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_elevation.tif"

            # Mock GDAL command failure
            with patch("subprocess.run") as mock_run:
                from subprocess import CalledProcessError

                mock_run.side_effect = CalledProcessError(1, "gdal_translate")

                result = download_elevation_data(bbox, str(output_file))

                assert result is None

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

    def test_generate_contour_lines_missing_elevation(self):
        """Test contour generation with missing elevation file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            elevation_file = Path(temp_dir) / "missing_elevation.tif"
            output_dir = Path(temp_dir) / "contours"

            result = generate_contour_lines(str(elevation_file), str(output_dir))

            assert result is None

    def test_generate_contour_lines_gdal_failure(self):
        """Test contour generation with GDAL failure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            elevation_file = Path(temp_dir) / "elevation.tif"
            output_dir = Path(temp_dir) / "contours"

            # Create a fake elevation file
            elevation_file.touch()

            with patch("subprocess.run") as mock_run:
                from subprocess import CalledProcessError

                mock_run.side_effect = CalledProcessError(1, "gdal_contour")

                result = generate_contour_lines(str(elevation_file), str(output_dir))

                assert result is None

    def test_process_elevation_and_contours_disabled(self):
        """Test contour processing when disabled"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_and_contours(
                bbox, temp_dir, enable_contours=False
            )

            assert result is None

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

    def test_process_elevation_and_contours_elevation_failure(self):
        """Test contour processing when elevation data fails"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "utils.data_processing.download_elevation_data"
            ) as mock_download:
                # Mock elevation failure
                mock_download.return_value = None

                result = process_elevation_and_contours(
                    bbox, temp_dir, enable_contours=True
                )

                assert result is None

    def test_process_elevation_and_contours_contour_failure(self):
        """Test contour processing when contour generation fails"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "utils.data_processing.download_elevation_data"
            ) as mock_download:
                with patch(
                    "utils.data_processing.generate_contour_lines"
                ) as mock_generate:
                    # Mock successful elevation but failed contours
                    elevation_file = f"{temp_dir}/elevation_data.tif"
                    mock_download.return_value = elevation_file
                    mock_generate.return_value = None

                    result = process_elevation_and_contours(
                        bbox, temp_dir, enable_contours=True
                    )

                    assert result is None


@pytest.mark.unit
class TestContourConfiguration:
    """Test contour configuration handling"""

    def test_contour_interval_parameter(self):
        """Test contour interval parameter handling"""
        bbox = {"north": 57.37, "south": 57.26, "east": -2.82, "west": -2.95}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "utils.data_processing.download_elevation_data"
            ) as mock_download:
                with patch(
                    "utils.data_processing.generate_contour_lines"
                ) as mock_generate:
                    elevation_file = f"{temp_dir}/elevation_data.tif"
                    contour_file = f"{temp_dir}/contours.shp"

                    mock_download.return_value = elevation_file
                    mock_generate.return_value = contour_file

                    # Test different intervals
                    for interval in [5, 10, 25, 50]:
                        result = process_elevation_and_contours(
                            bbox,
                            temp_dir,
                            contour_interval=interval,
                            enable_contours=True,
                        )

                        assert result["interval"] == interval
                        mock_generate.assert_called_with(
                            elevation_file, temp_dir, interval
                        )
