# Style Preview System

This system generates preview images showing various styling options for the Lumsden Tourist Map, allowing users to compare different visual approaches and choose their preferred style.

## Features

### Style Variations

The system includes 7 different style themes that demonstrate various parameterizable options:

1. **Tourist (Default)** - The original balanced style for tourist use
2. **Blue Theme** - Cool color palette with blue accents
3. **Warm Theme** - Warm colors with oranges and yellows  
4. **Monochrome** - Grayscale with thick, bold lines
5. **Delicate Purple** - Soft purple theme with thin, elegant lines
6. **High Contrast** - Bright, vivid colors with maximum visibility
7. **Minimalist** - Subtle colors with very thin, minimal lines

### Parameterizable Options Demonstrated

- **Color Schemes**: Cool blues, warm oranges, monochrome grays, soft purples, high contrast colors
- **Line Widths**: From minimalist (0.1-1.5px) to bold (8-10px) 
- **Background Colors**: Light themed backgrounds ranging from pure white to tinted
- **Opacity Levels**: Various transparency settings from 0.3 to 1.0
- **Point Marker Sizes**: From tiny (2px) to large (16px)
- **Dash Patterns**: Different stroke patterns for paths and secondary roads
- **Building Styles**: Different fills, outlines, and opacity combinations

## Usage

### Generate Style Previews

```bash
python3 style_preview_generator.py
```

This creates:
- `data/style_preview_grid.png` - Grid layout showing all styles
- `data/style_previews/` - Individual preview images for each style

### Output Specifications

- **Preview Resolution**: 590×832 pixels (lower than A3 for smaller file sizes)
- **Grid Layout**: 3 columns, automatically calculated rows
- **File Sizes**: 
  - Grid image: ~54KB
  - Individual previews: 5-9KB each
- **Format**: PNG with RGB color space

### Configuration

Preview size is configured in `config/output_formats.json`:

```json
"preview": {
  "width_mm": 100,
  "height_mm": 141, 
  "dpi": 150,
  "description": "Small preview format for style comparison"
}
```

## Adding New Styles

1. Create a new XML template in `styles/` directory
2. Follow the existing template structure with `$DATA_DIR` placeholder
3. Add the style to the list in `style_preview_generator.py`
4. Run the generator to include it in previews

### Template Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<Map srs="+proj=merc..." background-color="#your_bg_color">
  
  <!-- Style definitions -->
  <Style name="landuse">
    <Rule>
      <Filter>[landuse] = 'forest'</Filter>
      <PolygonSymbolizer fill="#color" fill-opacity="0.8"/>
    </Rule>
  </Style>
  
  <!-- Layer definitions -->
  <Layer name="landuse" srs="+proj=longlat...">
    <StyleName>landuse</StyleName>
    <Datasource>
      <Parameter name="file">$DATA_DIR/multipolygons.shp</Parameter>
    </Datasource>
  </Layer>
  
</Map>
```

## Technical Implementation

### Dependencies

- **Mapnik**: Map rendering engine
- **PIL (Pillow)**: Image processing for grid creation
- **GDAL**: Geospatial data processing

### Architecture

1. **Style Templates**: XML files with parameterizable styling
2. **Style Builder**: Processes templates and substitutes data paths
3. **Preview Renderer**: Creates low-resolution map images
4. **Grid Generator**: Combines individual previews into comparison grid

### Performance

- Preview generation: ~1-2 seconds per style
- Total time: ~15 seconds for all 7 styles
- Memory efficient: Renders one style at a time
- File size optimized: Lower DPI reduces output size

## Integration

The style preview system integrates with the existing map generation infrastructure:

- Uses same configuration system (`utils/config.py`)
- Leverages existing style builder (`utils/style_builder.py`)
- Shares data processing utilities (`utils/data_processing.py`)
- Compatible with existing OSM data pipeline

## Benefits

### For Users
- **Visual Comparison**: Easy side-by-side style comparison
- **Quick Preview**: Fast rendering at lower resolution
- **Style Selection**: Clear demonstration of available options
- **Parameter Understanding**: Shows impact of different styling choices

### For Developers
- **Style Testing**: Quick validation of new style designs
- **Parameter Experimentation**: Easy testing of color schemes and line weights
- **Documentation**: Visual documentation of available styles
- **Quality Assurance**: Batch verification of style rendering

## Output Examples

The system demonstrates clear differentiation between styles:

- **Line Weight Contrast**: Minimalist (0.1-1.5px) vs High Contrast (8-10px)
- **Color Variety**: Blue theme blues vs Warm theme oranges vs Monochrome grays
- **Opacity Range**: Minimalist (0.3-0.6) vs High Contrast (0.9-1.0)
- **Background Variation**: Pure white to tinted backgrounds
- **Marker Scaling**: Tiny minimalist dots vs large high-contrast circles

This provides users with a comprehensive view of available styling options while keeping file sizes manageable for web distribution and quick comparison.