"""
Tests for Ordnance Survey data processing functionality
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from utils.os_data_processing import OSDataProcessor, integrate_os_data_with_map


class TestOSDataProcessor:
    """Test Ordnance Survey data processing utilities"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = OSDataProcessor(data_dir=self.temp_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.unit
    def test_os_processor_initialization(self):
        """Test OS data processor initialization"""
        processor = OSDataProcessor()
        assert processor.data_dir.name == "os_data"
        assert "roads" in processor.os_products
        assert "boundaries" in processor.os_products
        assert "rights_of_way" in processor.os_products

    @pytest.mark.unit
    def test_create_mock_roads_csv(self):
        """Test mock roads CSV data generation"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        roads_data = self.processor._create_mock_roads_csv(bbox)

        assert len(roads_data) > 0
        assert isinstance(roads_data, list)
        assert all("class" in road for road in roads_data)
        assert any(road["class"] == "A Road" for road in roads_data)

    @pytest.mark.unit
    def test_create_mock_boundaries_csv(self):
        """Test mock boundaries CSV data generation"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        boundaries_data = self.processor._create_mock_boundaries_csv(bbox)

        assert len(boundaries_data) > 0
        assert isinstance(boundaries_data, list)
        assert all("type" in boundary for boundary in boundaries_data)
        assert any(boundary["type"] == "Administrative" for boundary in boundaries_data)

    @pytest.mark.unit
    def test_create_mock_rights_of_way_csv(self):
        """Test mock rights of way CSV data generation"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        row_data = self.processor._create_mock_rights_of_way_csv(bbox)

        assert len(row_data) > 0
        assert isinstance(row_data, list)
        assert all("type" in item for item in row_data)
        assert any(item["type"] == "Footpath" for item in row_data)

    @pytest.mark.unit
    def test_download_os_data_unknown_product(self):
        """Test handling of unknown OS product"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        result = self.processor.download_os_data("unknown_product", bbox, "test_output")

        assert result is False

    @pytest.mark.unit
    def test_download_os_data_success(self):
        """Test successful OS data download (mock)"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        output_file = Path(self.temp_dir) / "test_output"

        result = self.processor.download_os_data("roads", bbox, str(output_file))

        assert result is True
        # Check CSV file was created
        csv_file = output_file.parent / f"{output_file.stem}.csv"
        assert csv_file.exists()

    @pytest.mark.unit
    def test_convert_os_to_shapefiles_unknown_product(self):
        """Test conversion with unknown product key"""
        result = self.processor.convert_os_to_shapefiles(
            "dummy_file", "unknown_product"
        )
        assert result is None

    @pytest.mark.unit
    def test_convert_os_to_shapefiles_nonexistent_file(self):
        """Test conversion with non-existent input file"""
        result = self.processor.convert_os_to_shapefiles("nonexistent_file", "roads")
        assert result is None

    @pytest.mark.unit
    def test_process_os_data_for_area_empty_layers(self):
        """Test processing with empty layer list"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        result = self.processor.process_os_data_for_area(bbox, enabled_layers=[])

        assert isinstance(result, dict)
        assert len(result) == 0

    @pytest.mark.unit
    def test_process_os_data_for_area_unknown_layer(self):
        """Test processing with unknown layer"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        result = self.processor.process_os_data_for_area(
            bbox, enabled_layers=["unknown_layer"]
        )

        assert isinstance(result, dict)
        assert len(result) == 0


class TestOSDataIntegration:
    """Test OS data integration with mapping pipeline"""

    @pytest.mark.unit
    def test_integrate_os_data_disabled(self):
        """Test OS data integration when disabled"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        os_config = {"enabled": False}

        result = integrate_os_data_with_map(bbox, os_config)

        assert isinstance(result, dict)
        assert len(result) == 0

    @pytest.mark.unit
    def test_integrate_os_data_no_config(self):
        """Test OS data integration with no config"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}

        result = integrate_os_data_with_map(bbox, None)

        assert isinstance(result, dict)
        assert len(result) == 0

    @pytest.mark.unit
    @patch("utils.os_data_processing.OSDataProcessor")
    def test_integrate_os_data_enabled(self, mock_processor_class):
        """Test OS data integration when enabled"""
        bbox = {"north": 57.4, "south": 57.3, "east": -2.8, "west": -2.9}
        os_config = {"enabled": True, "layers": ["roads", "boundaries"]}

        # Mock the processor
        mock_processor = Mock()
        mock_processor.process_os_data_for_area.return_value = {
            "roads": "/path/to/roads"
        }
        mock_processor_class.return_value = mock_processor

        result = integrate_os_data_with_map(bbox, os_config)

        # Verify processor was called correctly
        mock_processor_class.assert_called_once()
        mock_processor.process_os_data_for_area.assert_called_once_with(
            bbox, ["roads", "boundaries"]
        )

        assert isinstance(result, dict)
        assert "roads" in result


class TestOSDataConfiguration:
    """Test OS data configuration handling"""

    @pytest.mark.unit
    def test_os_products_structure(self):
        """Test that OS products are properly structured"""
        processor = OSDataProcessor()

        for product_key, product_info in processor.os_products.items():
            assert "name" in product_info
            assert "url" in product_info
            assert "description" in product_info
            assert isinstance(product_info["name"], str)
            assert isinstance(product_info["url"], str)
            assert isinstance(product_info["description"], str)

    @pytest.mark.unit
    def test_os_data_dir_creation(self):
        """Test OS data directory creation"""
        temp_dir = tempfile.mkdtemp()
        try:
            data_dir = Path(temp_dir) / "test_os_data"
            processor = OSDataProcessor(data_dir=str(data_dir))

            assert data_dir.exists()
            assert data_dir.is_dir()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
