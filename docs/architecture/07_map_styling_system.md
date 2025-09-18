# Map Styling System

The styling system uses Mapnik XML templates with variable substitution:

### Style Categories
1. **Land Use**: Forests, farmland, parks, nature reserves
2. **Water Features**: Rivers, streams, lakes, canals
3. **Transportation**: Roads (classified by type), paths, trails
4. **Buildings**: General building footprints
5. **Points of Interest**: Icons for various amenities
6. **Place Labels**: Hierarchical text for settlements
7. **Contour Lines**: Elevation representation
8. **Hillshading**: Topographic relief visualization

### Icon System
The system uses SVG icons for point features:
- Restaurants, accommodations, attractions
- Shops, services, transportation
- Natural features, emergency services

### Layer Ordering
1. Hillshade (background)
2. Contour lines
3. Land use and water features
4. Buildings
5. Roads (major to minor)
6. Paths and trails
7. Points of interest
8. Text labels (topmost)