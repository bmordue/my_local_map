"""Test elevation processing and hillshading functionality"""

import unittest
from unittest.mock import patch, mock_open
import tempfile

from utils.elevation_processing import (
    calculate_elevation_bbox,
    download_elevation_data,
    generate_hillshade,
    process_elevation_data,
    generate_synthetic_dem,
)


class TestDownloadElevationData(unittest.TestCase):
    """Test the download_elevation_data function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_bbox = {
            'west': -3.0,
            'east': -2.5,
            'south': 57.0,
            'north': 57.5
        }

    @patch('elevation.clip')
    @patch('utils.elevation_processing.generate_synthetic_dem')
    def test_download_real_dem_success(self, mock_generate_synthetic, mock_clip):
        """Test successful download of real DEM data"""
        with tempfile.NamedTemporaryFile(suffix='.tif') as temp_file:
            result = download_elevation_data(self.test_bbox, temp_file.name, dem_source="real")
            self.assertTrue(result)
            mock_clip.assert_called_once()
            mock_generate_synthetic.assert_not_called()

    @patch('elevation.clip')
    @patch('utils.elevation_processing.generate_synthetic_dem')
    def test_download_real_dem_failure_fallback(self, mock_generate_synthetic, mock_clip):
        """Test fallback to synthetic DEM when real download fails"""
        mock_clip.side_effect = Exception("Download failed")
        mock_generate_synthetic.return_value = True
        with tempfile.NamedTemporaryFile(suffix='.tif') as temp_file:
            result = download_elevation_data(self.test_bbox, temp_file.name, dem_source="real")
            self.assertTrue(result)
            mock_clip.assert_called_once()
            mock_generate_synthetic.assert_called_once()

    @patch('utils.elevation_processing.generate_synthetic_dem')
    def test_download_synthetic_dem(self, mock_generate_synthetic):
        """Test generation of synthetic DEM"""
        mock_generate_synthetic.return_value = True
        with tempfile.NamedTemporaryFile(suffix='.tif') as temp_file:
            result = download_elevation_data(self.test_bbox, temp_file.name, dem_source="synthetic")
            self.assertTrue(result)
            mock_generate_synthetic.assert_called_once()


class TestProcessElevationData(unittest.TestCase):
    """Test elevation data processing utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_bbox = {
            'west': -3.0,
            'east': -2.5,
            'south': 57.0,
            'north': 57.5
        }
        
        self.area_config_enabled = {
            'hillshading': {
                'enabled': True,
                'opacity': 0.4,
                'azimuth': 315,
                'altitude': 45,
                'z_factor': 1.0,
                'scale': 111120,
                'dem_source': 'real'
            },
            'contours': {
                'enabled': True,
                'interval': 10
            }
        }
        
        self.area_config_disabled = {
            'hillshading': {
                'enabled': False
            },
            'contours': {
                'enabled': False
            }
        }
    
    def test_calculate_elevation_bbox_basic(self):
        """Test basic elevation bbox calculation"""
        result = calculate_elevation_bbox(self.test_bbox)
        
        # Should add buffer to all sides
        self.assertLess(result['west'], self.test_bbox['west'])
        self.assertGreater(result['east'], self.test_bbox['east'])
        self.assertLess(result['south'], self.test_bbox['south'])
        self.assertGreater(result['north'], self.test_bbox['north'])
    
    def test_calculate_elevation_bbox_custom_buffer(self):
        """Test elevation bbox calculation with custom buffer"""
        buffer_km = 2.0
        result = calculate_elevation_bbox(self.test_bbox, buffer_km)
        
        # Should add larger buffer
        lat_buffer = buffer_km / 111.0
        self.assertAlmostEqual(
            result['south'], 
            self.test_bbox['south'] - lat_buffer,
            places=4
        )
        self.assertAlmostEqual(
            result['north'], 
            self.test_bbox['north'] + lat_buffer,
            places=4
        )
    
    def test_calculate_elevation_bbox_dimensions(self):
        """Test elevation bbox maintains reasonable dimensions"""
        result = calculate_elevation_bbox(self.test_bbox)
        
        width = result['east'] - result['west']
        height = result['north'] - result['south']
        
        # Should be larger than original
        original_width = self.test_bbox['east'] - self.test_bbox['west']
        original_height = self.test_bbox['north'] - self.test_bbox['south']
        
        self.assertGreater(width, original_width)
        self.assertGreater(height, original_height)
    
    @patch('subprocess.run')
    def test_generate_hillshade_success(self, mock_subprocess):
        """Test successful hillshade generation"""
        # Mock successful subprocess call
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ""
        
        config = self.area_config_enabled['hillshading']
        
        with tempfile.NamedTemporaryFile(suffix='.tif') as dem_file, \
             tempfile.NamedTemporaryFile(suffix='.tif') as hillshade_file:
            
            result = generate_hillshade(dem_file.name, hillshade_file.name, config)
            
            self.assertTrue(result)
            # Should call gdaldem hillshade
            mock_subprocess.assert_called()
            call_args = mock_subprocess.call_args[0][0]
            self.assertIn('gdaldem', call_args)
            self.assertIn('hillshade', call_args)
            self.assertIn(str(config['azimuth']), call_args)
            self.assertIn(str(config['altitude']), call_args)
    
    @patch('subprocess.run')
    def test_generate_hillshade_failure(self, mock_subprocess):
        """Test hillshade generation failure"""
        # Mock failed subprocess call
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "Error message"
        
        config = self.area_config_enabled['hillshading']
        
        with tempfile.NamedTemporaryFile(suffix='.tif') as dem_file, \
             tempfile.NamedTemporaryFile(suffix='.tif') as hillshade_file:
            
            result = generate_hillshade(dem_file.name, hillshade_file.name, config)
            
            self.assertFalse(result)
    
    def test_process_elevation_data_disabled(self):
        """Test processing when hillshading and contours are disabled"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_data(
                self.test_bbox, 
                self.area_config_disabled, 
                temp_dir
            )
            
            self.assertEqual(result, {})
    
    @patch('utils.elevation_processing.download_elevation_data')
    @patch('utils.elevation_processing.generate_hillshade')
    @patch('utils.elevation_processing.generate_contours')
    def test_process_elevation_data_success(self, mock_contours, mock_hillshade, mock_download):
        """Test successful elevation processing workflow"""
        # Mock successful operations
        mock_download.return_value = True
        mock_hillshade.return_value = True
        mock_contours.return_value = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_data(
                self.test_bbox, 
                self.area_config_enabled, 
                temp_dir
            )
            
            self.assertIn("hillshade_file", result)
            self.assertIn("contours_file", result)
            self.assertTrue(result["hillshade_file"].endswith('hillshade.tif'))
            self.assertTrue(result["contours_file"].endswith('contours.shp'))
            mock_download.assert_called_once()
            mock_hillshade.assert_called_once()
            mock_contours.assert_called_once()
    
    @patch('utils.elevation_processing.download_elevation_data')
    def test_process_elevation_data_download_failure(self, mock_download):
        """Test processing when elevation download fails"""
        # Mock failed download
        mock_download.return_value = False
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = process_elevation_data(
                self.test_bbox, 
                self.area_config_enabled, 
                temp_dir
            )
            
            self.assertEqual(result, {})

    def test_hillshading_config_parameters(self):
        """Test that hillshading config parameters are properly used"""
        config = self.area_config_enabled['hillshading']
        
        # Verify all expected parameters are present
        self.assertIn('opacity', config)
        self.assertIn('azimuth', config)
        self.assertIn('altitude', config)
        self.assertIn('z_factor', config)
        self.assertIn('scale', config)
        self.assertIn('dem_source', config)
        
        # Verify reasonable default values
        self.assertEqual(config['opacity'], 0.4)
        self.assertEqual(config['azimuth'], 315)
        self.assertEqual(config['altitude'], 45)
        self.assertEqual(config['z_factor'], 1.0)
        self.assertEqual(config['scale'], 111120)
        self.assertEqual(config['dem_source'], 'real')


if __name__ == '__main__':
    unittest.main()