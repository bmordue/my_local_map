# Phase 1 Implementation: High-Priority Improvements

This document details the technical implementation plan for the high-priority items identified in our feature implementation plan.

## 1. Missing Icon Set

### Problem
Several icons referenced in the tourist.xml style file are missing:
- castle-14.svg
- ruins-14.svg
- rock-14.svg
- attraction-15.svg (referenced in legend but not in style)

### Solution
1. Create missing SVG icons that match the existing icon style
2. Update legend to include all icons
3. Verify all icon references in style files

### Implementation Steps

#### 1.1 Create Missing Icons
Create the following SVG icons in the `icons/` directory:
- castle-14.svg
- ruins-14.svg
- rock-14.svg
- attraction-15.svg

#### 1.2 Icon Design Specifications
- Size: 14px or 15px as appropriate
- Color: Black (#000000) for consistency
- Style: Simple, recognizable symbols
- Format: Valid SVG XML

#### 1.3 Update Style Files
Verify all icon references in `styles/tourist.xml`:
- Check that all referenced icons exist
- Ensure paths are correct
- Update any incorrect references

#### 1.4 Update Legend
Modify `utils/legend.py` to include all icons in the legend:
- Add missing items to `_load_tourist_legend_items()`
- Ensure icons display correctly in legend

### Files to Modify
1. icons/castle-14.svg (new)
2. icons/ruins-14.svg (new)
3. icons/rock-14.svg (new)
4. icons/attraction-15.svg (new)
5. styles/tourist.xml (verify)
6. utils/legend.py (update)

## 2. Enhanced Legend

### Problem
The current legend implementation is basic and doesn't show all map features.

### Solution
1. Expand legend to include all map features
2. Improve visual design
3. Add categorization of features

### Implementation Steps

#### 2.1 Legend Categories
Organize legend items into logical categories:
- Land Use
- Water Features
- Transportation
- Paths & Trails
- Buildings
- Points of Interest
- Topographic Features

#### 2.2 Add Missing Legend Items
Add legend entries for:
- All POI types (currently incomplete)
- Contour lines (when enabled)
- Hillshading (when enabled)
- Nature reserves
- Parks and gardens

#### 2.3 Improve Visual Design
- Add category headers
- Use consistent spacing
- Improve text readability
- Add background for better contrast

#### 2.4 Implementation
Modify `utils/legend.py`:
- Update `_load_tourist_legend_items()` method
- Enhance `render_to_map()` method for better layout
- Improve `add_legend_to_image()` for better rendering

### Files to Modify
1. utils/legend.py

## 3. Multiple Output Formats

### Problem
Currently only supports A3 format, but users need different sizes for different purposes.

### Solution
1. Add new output formats to configuration
2. Update map generator to support multiple formats
3. Add CLI option for format selection

### Implementation Steps

#### 3.1 Add New Output Formats
Add the following formats to `config/output_formats.json`:
```json
{
  "A4": {
    "width_mm": 210,
    "height_mm": 297,
    "dpi": 300,
    "description": "Standard A4 format"
  },
  "letter": {
    "width_mm": 216,
    "height_mm": 279,
    "dpi": 300,
    "description": "US Letter format"
  },
  "mobile": {
    "width_mm": 75,
    "height_mm": 133,
    "dpi": 150,
    "description": "Mobile screen format"
  }
}
```

#### 3.2 Update Configuration Management
Modify `utils/config.py`:
- Update `load_output_format()` to handle new formats
- Add validation for format parameters

#### 3.3 Update Map Generator
Modify `map_generator.py`:
- Add format parameter to command line arguments
- Update `main()` to accept format parameter
- Modify output file naming to include format

#### 3.4 Update Documentation
Update README.md to document new formats

### Files to Modify
1. config/output_formats.json
2. utils/config.py
3. map_generator.py
4. README.md

## Implementation Order

1. **Missing Icon Set**
   - Create SVG icons
   - Update legend
   - Verify style files

2. **Enhanced Legend**
   - Expand legend items
   - Improve visual design
   - Test rendering

3. **Multiple Output Formats**
   - Add formats to configuration
   - Update config management
   - Update map generator
   - Update documentation

## Testing Plan

### For Missing Icon Set
1. Verify all new icons render correctly
2. Check that all style references work
3. Confirm legend displays all icons

### For Enhanced Legend
1. Verify all map features appear in legend
2. Check visual design improvements
3. Test legend on different map sizes

### For Multiple Output Formats
1. Test each new format generates correctly
2. Verify file sizes are appropriate
3. Check CLI parameter handling
4. Confirm documentation is accurate

## Dependencies
- Existing GDAL/OGR and Mapnik installation
- Python PIL/Pillow for legend rendering
- CairoSVG for SVG processing

## Expected Outcomes
After implementing these high-priority improvements:
1. All map symbols will have corresponding icons
2. Legend will provide complete information about map features
3. Users can generate maps in multiple formats for different use cases
4. Overall map quality and usability will be significantly improved