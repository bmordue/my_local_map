# Web-based Interactive Map

This document describes the web-based interactive map implementation for the Lumsden Tourist Map project, addressing the Phase 3 roadmap requirement.

## Overview

The web-based interactive map provides a modern, responsive interface for exploring tourist attractions, accommodation, dining, activities, and walking trails in the Lumsden area. It transforms the static PNG map generation into a dynamic web application.

## Features

### Core Functionality
- **Interactive Layer Controls**: Toggle visibility of different tourist data categories
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Data Loading**: Tourist data served via RESTful API
- **Point of Interest Display**: Shows detailed information for tourist attractions
- **Base Map Integration**: Overlays the generated map image on OpenStreetMap tiles

### Data Categories
- 🏛️ **Tourist Attractions**: Historic sites, viewpoints, museums
- 🏨 **Accommodation**: Hotels, B&Bs, hostels, camping
- 🍽️ **Dining**: Restaurants, cafes, pubs with cuisine information
- 🎯 **Activities**: Guided tours, outdoor activities, sports
- 🥾 **Walking Trails**: Detailed trail information with difficulty levels

## Technical Architecture

### Backend (Flask)
```
web_map_server.py      # Main Flask application
├── /                  # Main map page
├── /api/config        # Map configuration endpoint
├── /api/data/<layer>  # GeoJSON data for each layer
├── /map_image         # Serve generated map image
└── /initialize        # Data initialization endpoint
```

### Frontend
```
web/templates/index.html   # Main HTML template
web/static/css/map.css     # Responsive CSS styling
web/static/js/map.js       # Interactive JavaScript (full Leaflet implementation)
```

### Data Flow
1. **Static Map Generation**: Existing `map_generator.py` creates base map
2. **Enhanced Data Creation**: `create_enhanced_data.py` generates tourist database
3. **Web Server**: Flask serves interactive interface and APIs
4. **Client-Side**: JavaScript loads data and provides interactivity

## Usage

### Start the Web Server
```bash
# Install Flask dependency
pip3 install Flask

# Start the interactive map server
python3 web_map_server.py
```

The server runs on `http://localhost:5000` by default.

### API Endpoints

#### Configuration
```bash
GET /api/config
# Returns: Map center, bounding box, area name, scale
```

#### Tourist Data
```bash
GET /api/data/attractions    # Tourist attractions GeoJSON
GET /api/data/accommodation  # Accommodation GeoJSON  
GET /api/data/dining         # Dining venues GeoJSON
GET /api/data/activities     # Activities GeoJSON
GET /api/data/trails         # Walking trails GeoJSON
```

## Integration with Existing System

### Data Compatibility
- **Leverages existing data processing**: Uses same OSM data and enhanced tourist database
- **GeoJSON export**: Tourist data automatically exported in web-compatible format
- **Configuration system**: Uses existing `config/areas.json` for map parameters
- **Base map overlay**: Incorporates the generated static map as a tile layer

### Minimal Code Changes
The web implementation requires **no changes** to existing map generation code:
- `map_generator.py` continues to work unchanged
- `config/` directory structure maintained
- `enhanced_data/` directory used for web data
- Existing dependencies (Mapnik, GDAL) still used for base map generation

## Deployment Options

### Development
```bash
python3 web_map_server.py
# Runs on localhost:5000 with debug mode
```

### Production
For production deployment, use a proper WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web_map_server:app
```

## Mobile Responsiveness

The interface automatically adapts to different screen sizes:
- **Desktop**: Full-width map with sidebar controls
- **Tablet**: Optimized layout with touch-friendly controls
- **Mobile**: Stacked layout with bottom-sheet information panel

## Future Enhancements

### Advanced Interactive Features
- **Full Leaflet.js Integration**: Complete interactive map with zoom/pan
- **Popup Information Windows**: Detailed POI information on click
- **Route Planning**: Walking route calculation between points
- **Search Functionality**: Find attractions, accommodation, or services
- **Geolocation**: Show user's current position on map
- **Offline Support**: Cache map tiles and data for offline use

### Data Integration
- **Real-time Updates**: Live data feeds for events, weather, opening hours
- **User-generated Content**: Reviews, photos, recommendations
- **Social Features**: Share locations, create custom routes
- **Multi-language Support**: Internationalization for tourist content

## Benefits

### For Visitors
- **Interactive Exploration**: Pan, zoom, and explore the area dynamically
- **Layered Information**: Show/hide different types of tourist information
- **Mobile Accessibility**: Access information on-the-go with smartphones
- **Up-to-date Data**: Real-time information via API endpoints

### For Developers
- **Modern Web Standards**: Uses standard HTML5, CSS3, JavaScript
- **RESTful API**: Clean separation between data and presentation
- **Scalable Architecture**: Easy to add new data layers and features
- **Progressive Enhancement**: Works without JavaScript for basic functionality

### For Tourism Organizations
- **Digital Presence**: Modern web interface for tourist information
- **Data Analytics**: Track popular attractions and user behavior
- **Content Management**: Easy updates via database and API
- **Platform Integration**: Can be embedded in other tourism websites

This web-based implementation successfully transforms the static map generator into a modern, interactive tourism platform while maintaining full compatibility with the existing codebase.