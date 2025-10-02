# My local map

Render a local map suitable for printing.

## Features

### Map Content Categories (25+ types)
- **Natural Features**: Forests, heath, moors, wetlands, grasslands, scree
- **Land Use**: Residential, commercial, industrial, agricultural areas
- **Transportation**: Roads (all categories), railways, cycling paths, walking trails
- **Points of Interest**: 50+ amenity types including restaurants, hotels, attractions, services
- **Buildings**: Categorized by type (churches, schools, hospitals, public buildings)
- **Place Labels**: Towns, villages, farms with hierarchical text sizing
- **Water Features**: Rivers, streams, springs, water bodies
- **Elevation Data**: Contour lines showing terrain features and elevation changes
- Accommodation: Hotels, B&Bs, hostels, camping with amenities
- Dining: Restaurants, cafes, pubs with cuisine types and features
- Attractions: Historic sites, viewpoints, museums with ratings
- Activities: Guided tours, outdoor activities, sports with booking info
- Walking Trails: Detailed trail information with difficulty and facilities
- **Topographic Features**: Elevation contours for outdoor activity planning

## Quick Start

### Prerequisites
- Python 3.12+
- GDAL/OGR tools
- Mapnik rendering library

### Nix shell

This project provides a shell.nix to install dependencies and set up a development environment.

```bash
nix-shell
```

### Manual installation
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install gdal-bin python3-mapnik

# Install Python dependencies
pip3 install -r requirements.txt

# Run enhanced map generator
python3 map_generator.py
```

#### Option 2: Nix Development Environment (Recommended)
If you have Nix installed, you can use the provided development environment:

```bash
# Clone repository
git clone https://github.com/bmordue/my_local_map.git
cd my_local_map

# Enter Nix development shell (using flake)
nix develop

# Or use traditional shell.nix
nix-shell

# Run enhanced map generator
python map_generator.py

# Run tests
pytest tests/
```

**Benefits of Nix approach:**
- 🚀 Reproducible development environment
- 📦 All dependencies managed declaratively
- ⚡ Fast setup on any system with Nix
- 🧪 Integrated testing and linting tools
- 🔧 Same environment used in CI/CD

### Output
- Enhanced Map: `lumsden_enhanced_tourist_map_A3.png` (3507×4960 pixels, A3 300DPI)
- Style File: `tourist_map_style.xml` (Comprehensive Mapnik styling)
- Enhanced Data: `enhanced_data/` directory with tourist database and GeoJSON files

## Data Sources Integration

### Primary Sources
1. OpenStreetMap: Base geographic data via Overpass API
2. Tourist Database: Comprehensive local tourism information
3. Sample Data: Demonstration datasets for the Lumsden area

### Enhanced Data Categories
```
enhanced_data/
├── lumsden_tourist.db          # SQLite database with full tourist info
├── tourist_attractions.geojson # 5 attractions with ratings & details
├── accommodation.geojson       # 4 accommodation options with amenities
├── dining.geojson             # 4 dining venues with cuisine types
├── activities.geojson         # 5 activities with booking requirements
└── walking_trails.geojson     # 5 trails with distances & waymarking
```

## Map Style

### Categories
```xml
<!-- 25+ comprehensive style categories -->
- Enhanced Land Use (9 categories)
- Water Features (4 types)  
- Transportation (8 road/path types)
- Buildings (5 specialized types)
- Points of Interest (15+ categories)
- Place Labels (3 hierarchy levels)
```

## Project roadmap

### Phase 1: Foundation
- [x] Fix OSM data extraction (Overpass query with complete nodes)
- [x] Create comprehensive map styling (25+ feature categories)
- [x] Build tourist information database
- [x] Generate sample enhanced data
- [x] Export data to mapping formats (GeoJSON)

### Phase 2: Content Expansion 
- [ ] Integrate live OSM data with proper coordinates
- [ ] Add elevation data and contour lines
- [ ] Include Ordnance Survey data layers
- [ ] Add real-time information (weather, events)
- [x] Implement quality validation systems

### Phase 3: Advanced Features 
- [ ] Web-based interactive map
- [ ] Mobile-friendly version
- [ ] Multi-language support
- [ ] User-generated content integration
- [ ] Route planning capabilities

## Technical Implementation

### Architecture
```
External APIs → Data Validation → SQLite Database → GeoJSON Export → Mapnik Rendering → PNG Output
```

### Key Components
- `map_generator.py`: Main map generation script with enhanced styling
- `create_enhanced_data.py`: Tourist database creation and export

### Rendering Pipeline
1. Data Collection: OSM download + enhanced tourist data
2. Processing: Convert to shapefiles and validate
3. Styling: Apply comprehensive Mapnik style rules
4. Rendering: Generate high-resolution A3 PNG output

## Content Statistics

### Current Implementation
- Base Map Features: 4 OSM layer types (points, lines, multilinestrings, multipolygons)
- Enhanced Styling: 25+ style categories with 100+ individual rules
- Tourist Database: 23 venues/attractions with detailed information
- Sample Data: 15 POIs + 5 land use categories
- Map Coverage: 8×12km area around Lumsden (96 square kilometers)

## Map Output Specifications

- Format: PNG image
- Resolution: 3507×4960 pixels (A3 at 300 DPI)
- Print Size: 297×420mm (standard A3)
- Color Space: RGBA with transparency support
- File Size: ~79KB (efficient for web and print)

## Documentation

- [MAP_ENHANCEMENT_PLAN.md](MAP_ENHANCEMENT_PLAN.md): Comprehensive plan for adding content
- [DATA_SOURCES_INTEGRATION.md](DATA_SOURCES_INTEGRATION.md): Guide for external data integration
- [QUALITY_VALIDATION.md](docs/QUALITY_VALIDATION.md): Quality validation system documentation
- [TESTING.md](docs/TESTING.md): Testing infrastructure and guidelines
- Style XML: Detailed Mapnik styling with extensive comments

## Quality Validation System

The project includes a comprehensive quality validation system that ensures data accuracy and completeness:

- **Coordinate Validation**: Ensures all points fall within map bounds and use valid coordinate formats
- **Attribute Completeness**: Verifies required fields are populated with configurable rules per data type
- **Temporal Validation**: Validates opening hours and seasonal information in multiple formats  
- **Cross-Reference Validation**: Compares multiple sources for consistency and detects conflicts

Run quality validation:
```bash
# System validation (checks imports, configuration, basic functionality)
python3 utils/system_validation.py

# Data quality validation (comprehensive data checking)
python3 utils/run_quality_validation.py

# Integrated with map generation
ENABLE_QUALITY_VALIDATION=1 python3 map_generator.py
```
