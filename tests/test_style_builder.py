"""Unit tests for style builder utilities"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

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
            with patch(
                "builtins.open", mock_open(read_data=sample_template)
            ) as mock_file:
                result = build_mapnik_style(style_name, data_dir)

        # Verify return value
        assert result == "styles/tourist_map_style.xml"

        # Verify file operations - check that write was called
        mock_file().write.assert_called()

        # Get the write call arguments and verify substitution occurred
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])
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
                with patch(
                    "builtins.open", mock_open(read_data=sample_template)
                ) as mock_file:
                    build_mapnik_style("test", data_dir)

            # Get the written content
            write_calls = mock_file().write.call_args_list
            written_content = "".join([call[0][0] for call in write_calls])

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
            with patch(
                "builtins.open", mock_open(read_data=template_with_multiple)
            ) as mock_file:
                build_mapnik_style("multi", data_dir)

        # Get the written content
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])

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
            with patch(
                "builtins.open", mock_open(read_data=empty_template)
            ) as mock_file:
                result = build_mapnik_style("empty", data_dir)

        assert result == "styles/empty_map_style.xml"

        # Verify empty content was written
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])
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
            with patch(
                "builtins.open", mock_open(read_data=template_no_subs)
            ) as mock_file:
                result = build_mapnik_style("static", data_dir)

        assert result == "styles/static_map_style.xml"

        # Content should remain unchanged
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])
        assert written_content == template_no_subs

    @pytest.mark.unit
    def test_build_mapnik_style_hillshading_enabled(self):
        """Test style building with hillshading enabled"""
        template_with_hillshade = """<?xml version="1.0" encoding="utf-8"?>
<Map>
  <Style name="hillshade">
    <Rule>
      <RasterSymbolizer opacity="$HILLSHADE_OPACITY"/>
    </Rule>
  </Style>
  <Layer name="hillshade" status="$HILLSHADE_STATUS">
    <Datasource>
      <Parameter name="file">$HILLSHADE_FILE</Parameter>
    </Datasource>
  </Layer>
  <Layer name="test">
    <Datasource>
      <Parameter name="file">$DATA_DIR/test.shp</Parameter>
    </Datasource>
  </Layer>
</Map>"""

        data_dir = "/test/data"
        area_config = {
            "hillshading": {
                "enabled": True,
                "opacity": 0.6,
                "azimuth": 270,
                "altitude": 30,
            }
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data=template_with_hillshade)
            ) as mock_file:
                result = build_mapnik_style(
                    "hillshade_test", data_dir, area_config, hillshade_available=True
                )

        assert result == "styles/hillshade_test_map_style.xml"

        # Verify hillshading parameters were substituted
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])

        assert 'opacity="0.6"' in written_content
        assert 'status="on"' in written_content
        assert "/test/data/hillshade.tif" in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_hillshading_disabled(self):
        """Test style building with hillshading disabled"""
        template_with_hillshade = """<?xml version="1.0" encoding="utf-8"?>
<Map>
  <Style name="hillshade">
    <Rule>
      <RasterSymbolizer opacity="$HILLSHADE_OPACITY"/>
    </Rule>
  </Style>
  <Layer name="hillshade" status="$HILLSHADE_STATUS">
    <Datasource>
      <Parameter name="file">$HILLSHADE_FILE</Parameter>
    </Datasource>
  </Layer>
</Map>"""

        data_dir = "/test/data"
        area_config = {"hillshading": {"enabled": False}}

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data=template_with_hillshade)
            ) as mock_file:
                result = build_mapnik_style(
                    "hillshade_disabled",
                    data_dir,
                    area_config,
                    hillshade_available=False,
                )

        assert result == "styles/hillshade_disabled_map_style.xml"

        # Verify hillshading is disabled
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])

        assert 'status="off"' in written_content
        assert (
            '<Parameter name="file"></Parameter>' in written_content
        )  # Empty file path

    @pytest.mark.unit
    def test_build_mapnik_style_no_area_config(self):
        """Test style building without area config (hillshading should be disabled)"""
        template_with_hillshade = """<?xml version="1.0" encoding="utf-8"?>
<Map>
  <Layer name="hillshade" status="$HILLSHADE_STATUS">
    <Datasource>
      <Parameter name="file">$HILLSHADE_FILE</Parameter>
    </Datasource>
  </Layer>
</Map>"""

        data_dir = "/test/data"

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data=template_with_hillshade)
            ) as mock_file:
                result = build_mapnik_style("no_config", data_dir)

        assert result == "styles/no_config_map_style.xml"

        # Verify hillshading is disabled by default
        write_calls = mock_file().write.call_args_list
        written_content = "".join([call[0][0] for call in write_calls])

        assert 'status="off"' in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_contours_enabled(self):
        """Test style building with contours enabled in configuration"""
        template_with_contours = """
        <Style name="contours">
          <Rule>
            <Filter>[elevation] % $CONTOUR_MAJOR_INTERVAL != 0</Filter>
            <LineSymbolizer stroke="$CONTOUR_MINOR_COLOR" stroke-width="$CONTOUR_MINOR_WIDTH"/>
          </Rule>
        </Style>
        <Layer name="contours" status="$CONTOURS_STATUS">
          <Datasource><Parameter name="file">$DATA_DIR/contours.shp</Parameter></Datasource>
        </Layer>
        """

        area_config = {
            "contours": {
                "enabled": True,
                "interval": 10,
                "major_interval": 25,
                "style": {
                    "minor": {"color": "#FF0000", "width": 0.8, "opacity": 0.7},
                    "major": {"color": "#AA0000", "width": 1.5, "opacity": 0.9},
                },
            }
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data=template_with_contours)
            ) as mock_file:
                with patch("pathlib.Path.resolve", return_value=Path("/test/data")):
                    result = build_mapnik_style("test", "/data", area_config)

                    # Get the written content
                    written_content = mock_file.return_value.write.call_args[0][0]

                    # Verify contour configuration was substituted correctly
                    assert 'status="on"' in written_content
                    assert "[elevation] % 25 != 0" in written_content
                    assert 'stroke="#FF0000"' in written_content
                    assert 'stroke-width="0.8"' in written_content

    @pytest.mark.unit
    def test_build_mapnik_style_contours_disabled(self):
        """Test style building with contours disabled in configuration"""
        template_with_contours = """
        <Layer name="contours" status="$CONTOURS_STATUS">
          <Datasource><Parameter name="file">$DATA_DIR/contours.shp</Parameter></Datasource>
        </Layer>
        """

        area_config = {"contours": {"enabled": False}}

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open", mock_open(read_data=template_with_contours)
            ) as mock_file:
                with patch("pathlib.Path.resolve", return_value=Path("/test/data")):
                    result = build_mapnik_style("test", "/data", area_config)

                    # Get the written content
                    written_content = mock_file.return_value.write.call_args[0][0]

                    # Verify contours are disabled
                    assert 'status="off"' in written_content
