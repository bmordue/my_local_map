"""Integration tests for the main map generator application"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import sys


class TestMapGeneratorIntegration:
    """Integration tests for the complete map generation process"""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies for integration testing"""
        return {
            'area_config': {
                "center": {"lat": 57.3167, "lon": -2.8833},
                "coverage": {"width_km": 8, "height_km": 12},
                "scale": 25000,
                "name": "Lumsden, Aberdeenshire"
            },
            'output_format': {
                "width_mm": 297,
                "height_mm": 420,
                "dpi": 300,
                "description": "Standard A3 format"
            }
        }

    @pytest.mark.integration
    def test_main_with_mocked_dependencies(self, mock_dependencies):
        """Test main function with all dependencies mocked"""
        
        # Import here to avoid import-time side effects
        import map_generator
        
        with patch('map_generator.load_area_config') as mock_load_area, \
             patch('map_generator.load_output_format') as mock_load_output, \
             patch('map_generator.calculate_pixel_dimensions') as mock_calc_pixels, \
             patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('map_generator.download_osm_data') as mock_download, \
             patch('map_generator.convert_osm_to_shapefiles') as mock_convert, \
             patch('map_generator.create_mapnik_style') as mock_create_style, \
             patch('map_generator.render_map') as mock_render:
            
            # Setup mocks
            mock_load_area.return_value = mock_dependencies['area_config']
            mock_load_output.return_value = mock_dependencies['output_format']
            mock_calc_pixels.return_value = (3507, 4960)
            mock_exists.return_value = True  # OSM file exists
            mock_convert.return_value = "/mock/osm_data"
            mock_create_style.return_value = "mock_style.xml"
            mock_render.return_value = True
            
            # Run main function
            result = map_generator.main()
            
            # Verify success
            assert result == 0


class TestRenderMapUnit:
    """Unit tests for the render_map function"""

    @pytest.mark.unit
    def test_render_map_import_error_handling(self):
        """Test render_map when mapnik import fails"""
        import map_generator
        
        # Mock the mapnik import to fail
        with patch.dict('sys.modules', {'mapnik': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mapnik'")):
                result = map_generator.render_map("test.xml", {}, "test.png", 100, 100)
        with patch('builtins.__import__', side_effect=ImportError("No module named 'mapnik'")):
            result = map_generator.render_map("test.xml", {}, "test.png", 100, 100)
            assert result is False

    @pytest.mark.unit 
    def test_render_map_with_mock_mapnik(self):
        """Test successful rendering with mocked mapnik"""
        import map_generator
        
        # Create a mock mapnik module
        mock_mapnik = MagicMock()
        mock_map_instance = MagicMock()
        mock_mapnik.Map.return_value = mock_map_instance
        mock_mapnik.Box2d.return_value = MagicMock()
        mock_mapnik.Projection.return_value = MagicMock()
        mock_mapnik.ProjTransform.return_value = MagicMock()
        
        with patch.dict('sys.modules', {'mapnik': mock_mapnik}):
            with patch('os.path.getsize', return_value=1024*1024):
                style_file = "test.xml"
                bbox = {'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}
                output_file = "test.png"
                
                result = map_generator.render_map(style_file, bbox, output_file, 1000, 1000)
                
                assert result is True
                mock_mapnik.Map.assert_called_once_with(1000, 1000)


class TestCreateMapnikStyleUnit:
    """Unit tests for create_mapnik_style function"""

    @pytest.mark.unit
    def test_create_mapnik_style_calls_build_function(self):
        """Test that create_mapnik_style calls the build function correctly"""
        import map_generator
        
        area_config = {"hillshading": {"enabled": True}}
        
        with patch('map_generator.build_mapnik_style') as mock_build:
            mock_build.return_value = "tourist_map_style.xml"
            
            result = map_generator.create_mapnik_style("/test/data", area_config, True)
            
            assert result == "tourist_map_style.xml"
            mock_build.assert_called_once_with("tourist", "/test/data", area_config, True)


class TestConfigurationHandling:
    """Test configuration loading in main function"""

    @pytest.mark.unit
    def test_configuration_loading_sequence(self):
        """Test that configuration is loaded in the correct sequence"""
        import map_generator
        
        with patch('map_generator.load_area_config') as mock_load_area, \
             patch('map_generator.load_output_format') as mock_load_output, \
             patch('map_generator.calculate_pixel_dimensions') as mock_calc_pixels, \
             patch('map_generator.calculate_bbox') as mock_calc_bbox, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('map_generator.convert_osm_to_shapefiles', return_value="/data"), \
             patch('map_generator.create_mapnik_style', return_value="style.xml"), \
             patch('map_generator.render_map', return_value=True):
            
            # Setup return values
            area_config = {"center": {"lat": 57.3167, "lon": -2.8833}, 
                          "coverage": {"width_km": 8, "height_km": 12},
                          "scale": 25000}
            output_format = {"width_mm": 297, "height_mm": 420, "dpi": 300}
            
            mock_load_area.return_value = area_config
            mock_load_output.return_value = output_format
            mock_calc_pixels.return_value = (3507, 4960)
            mock_calc_bbox.return_value = {'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}
            
            # Run main
            result = map_generator.main()
            
            # Verify function calls
            mock_load_area.assert_called_once_with("lumsden")
            mock_load_output.assert_called_once_with("A3")
            mock_calc_pixels.assert_called_once_with(output_format)
            mock_calc_bbox.assert_called_once_with(57.3167, -2.8833, 8, 12)
            
            assert result == 0


class TestFileHandling:
    """Test file handling in the application"""

    @pytest.mark.unit
    def test_osm_file_exists_path(self):
        """Test behavior when OSM file exists"""
        import map_generator
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('map_generator.load_area_config', return_value={"center": {"lat": 57.3167, "lon": -2.8833}, "coverage": {"width_km": 8, "height_km": 12}, "scale": 25000}), \
             patch('map_generator.load_output_format', return_value={"width_mm": 297, "height_mm": 420, "dpi": 300}), \
             patch('map_generator.calculate_pixel_dimensions', return_value=(3507, 4960)), \
             patch('map_generator.calculate_bbox', return_value={'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}), \
             patch('map_generator.download_osm_data') as mock_download, \
             patch('map_generator.convert_osm_to_shapefiles', return_value="/data"), \
             patch('map_generator.create_mapnik_style', return_value="style.xml"), \
             patch('map_generator.render_map', return_value=True):
            
            # Set file to exist
            mock_exists.return_value = True
            
            result = map_generator.main()
            
            # Download should not be called when file exists
            mock_download.assert_not_called()
            assert result == 0

    @pytest.mark.unit 
    def test_osm_file_download_needed(self):
        """Test behavior when OSM file needs to be downloaded"""
        import map_generator
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('map_generator.load_area_config', return_value={"center": {"lat": 57.3167, "lon": -2.8833}, "coverage": {"width_km": 8, "height_km": 12}, "scale": 25000}), \
             patch('map_generator.load_output_format', return_value={"width_mm": 297, "height_mm": 420, "dpi": 300}), \
             patch('map_generator.calculate_pixel_dimensions', return_value=(3507, 4960)), \
             patch('map_generator.calculate_bbox', return_value={'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}), \
             patch('map_generator.download_osm_data') as mock_download, \
             patch('map_generator.convert_osm_to_shapefiles', return_value="/data"), \
             patch('map_generator.create_mapnik_style', return_value="style.xml"), \
             patch('map_generator.render_map', return_value=True):
            
            # Set file to not exist
            mock_exists.return_value = False
            mock_download.return_value = True  # Successful download
            
            result = map_generator.main()
            
            # Download should be called when file doesn't exist
            mock_download.assert_called_once()
            assert result == 0


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.unit
    def test_download_failure_handling(self):
        """Test handling when OSM download fails"""
        import map_generator
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.mkdir'), \
             patch('map_generator.load_area_config', return_value={"center": {"lat": 57.3167, "lon": -2.8833}, "coverage": {"width_km": 8, "height_km": 12}, "scale": 25000}), \
             patch('map_generator.load_output_format', return_value={"width_mm": 297, "height_mm": 420, "dpi": 300}), \
             patch('map_generator.calculate_pixel_dimensions', return_value=(3507, 4960)), \
             patch('map_generator.calculate_bbox', return_value={'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}), \
             patch('map_generator.download_osm_data', return_value=False) as mock_download, \
             patch('map_generator.convert_osm_to_shapefiles') as mock_convert:
            
            result = map_generator.main()
            
            # Should return failure code
            assert result == 1
            # Download should be attempted
            mock_download.assert_called_once()
            # Conversion should not be called after download failure
            mock_convert.assert_not_called()

    @pytest.mark.unit
    def test_render_failure_handling(self):
        """Test handling when map rendering fails"""
        import map_generator
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.mkdir'), \
             patch('map_generator.load_area_config', return_value={"center": {"lat": 57.3167, "lon": -2.8833}, "coverage": {"width_km": 8, "height_km": 12}, "scale": 25000}), \
             patch('map_generator.load_output_format', return_value={"width_mm": 297, "height_mm": 420, "dpi": 300}), \
             patch('map_generator.calculate_pixel_dimensions', return_value=(3507, 4960)), \
             patch('map_generator.calculate_bbox', return_value={'south': 57.0, 'north': 57.5, 'west': -3.0, 'east': -2.5}), \
             patch('map_generator.convert_osm_to_shapefiles', return_value="/data"), \
             patch('map_generator.create_mapnik_style', return_value="style.xml"), \
             patch('map_generator.render_map', return_value=False) as mock_render:
            
            result = map_generator.main()
            
            # Should return failure code
            assert result == 1
            # Render should be attempted
            mock_render.assert_called_once()