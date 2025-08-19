"""Unit tests for style builder utilities"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from utils.style_builder import build_mapnik_style


class TestStyleBuilder:
    """Test style generation utilities"""

    @pytest.fixture
    def sample_template(self):
        """Sample Mapnik XML template for testing"""
        return """<?xml version="1.0" encoding="utf-8"?>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over">
  
  <Layer name="test_layer">
    <Datasource>
      <Parameter name="file">${DATA_DIR}/test.shp</Parameter>
      <Parameter name="type">shape</Parameter>
    </Datasource>
  </Layer>
  
</Map>"""

    @pytest.fixture
    def expected_output(self):
        """Expected output after template substitution"""
        return """<?xml version="1.0" encoding="utf-8"?>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over">
  
  <Layer name="test_layer">
    <Datasource>
      <Parameter name="file">/path/to/data/test.shp</Parameter>
      <Parameter name="type">shape</Parameter>
    </Datasource>
  </Layer>
  
</Map>"""

    @pytest.mark.unit
    def test_build_mapnik_style_success(self, sample_template, expected_output):
        """Test successful Mapnik style building"""
        style_name = "tourist"
        data_dir = "/path/to/data"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=sample_template)) as mock_file:
                result = build_mapnik_style(style_name, data_dir)
        
        # Verify return value
        assert result == "styles/tourist_map_style.xml"
        
        # Verify file operations - check that write was called
        mock_file().write.assert_called()
        
        # Get the write call arguments and verify substitution occurred
        write_calls = mock_file().write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        assert "/path/to/data" in written_content
        assert "${DATA_DIR}" not in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_template_not_found(self):
        """Test handling when style template is not found"""
        style_name = "nonexistent"
        data_dir = "/path/to/data"
        
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                build_mapnik_style(style_name, data_dir)
        
        assert "Style template not found" in str(exc_info.value)
        assert "nonexistent.xml" in str(exc_info.value)

    @pytest.mark.unit
    def test_build_mapnik_style_template_path(self, sample_template):
        """Test that template path is constructed correctly"""
        style_name = "custom_style"
        data_dir = "/custom/data/path"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=sample_template)):
                build_mapnik_style(style_name, data_dir)
        
        # Test passes if no exception is raised and function completes

    @pytest.mark.unit
    def test_build_mapnik_style_output_filename(self, sample_template):
        """Test that output filename is generated correctly"""
        test_cases = [
            ("tourist", "styles/tourist_map_style.xml"),
            ("basic", "styles/basic_map_style.xml"),
            ("detailed", "styles/detailed_map_style.xml"),
        ]
        
        for style_name, expected_filename in test_cases:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=sample_template)):
                    result = build_mapnik_style(style_name, "/test/data")
            
            assert result == expected_filename

    @pytest.mark.unit
    def test_build_mapnik_style_data_dir_substitution(self, sample_template):
        """Test that DATA_DIR is properly substituted in template"""
        test_cases = [
            "/simple/path",
            "/complex/path/with/many/levels",
            "/path with spaces",
            "relative/path",
        ]
        
        for data_dir in test_cases:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=sample_template)) as mock_file:
                    build_mapnik_style("test", data_dir)
            
            # Get the written content
            write_calls = mock_file().write.call_args_list
            written_content = ''.join([call[0][0] for call in write_calls])
            
            # Verify substitution occurred
            assert data_dir in written_content
            assert "${DATA_DIR}" not in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_multiple_substitutions(self):
        """Test template with multiple DATA_DIR references"""
        template_with_multiple = """<?xml version="1.0" encoding="utf-8"?>
<Map>
  <Layer name="points">
    <Datasource>
      <Parameter name="file">${DATA_DIR}/points.shp</Parameter>
    </Datasource>
  </Layer>
  <Layer name="lines">
    <Datasource>
      <Parameter name="file">${DATA_DIR}/lines.shp</Parameter>
    </Datasource>
  </Layer>
  <Layer name="polygons">
    <Datasource>
      <Parameter name="file">${DATA_DIR}/multipolygons.shp</Parameter>
    </Datasource>
  </Layer>
</Map>"""
        
        data_dir = "/test/data"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=template_with_multiple)) as mock_file:
                build_mapnik_style("multi", data_dir)
        
        # Get the written content
        write_calls = mock_file().write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        
        # Verify all substitutions occurred
        assert written_content.count("/test/data") == 3
        assert "${DATA_DIR}" not in written_content
        assert "/test/data/points.shp" in written_content
        assert "/test/data/lines.shp" in written_content
        assert "/test/data/multipolygons.shp" in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_empty_template(self):
        """Test handling of empty template file"""
        empty_template = ""
        data_dir = "/test/data"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=empty_template)) as mock_file:
                result = build_mapnik_style("empty", data_dir)
        
        assert result == "styles/empty_map_style.xml"
        
        # Verify empty content was written
        write_calls = mock_file().write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        assert written_content == ""

    @pytest.mark.unit
    def test_build_mapnik_style_no_substitutions_needed(self):
        """Test template that doesn't need any substitutions"""
        template_no_subs = """<?xml version="1.0" encoding="utf-8"?>
<Map>
  <Layer name="static">
    <Datasource>
      <Parameter name="type">csv</Parameter>
      <Parameter name="inline">x,y,name
1,1,point1
2,2,point2</Parameter>
    </Datasource>
  </Layer>
</Map>"""
        
        data_dir = "/test/data"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=template_no_subs)) as mock_file:
                result = build_mapnik_style("static", data_dir)
        
        assert result == "styles/static_map_style.xml"
        
        # Content should remain unchanged
        write_calls = mock_file().write.call_args_list
        written_content = ''.join([call[0][0] for call in write_calls])
        assert written_content == template_no_subs