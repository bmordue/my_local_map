#!/usr/bin/env python3
"""
Web-based Interactive Map Server for Lumsden Tourist Map
Serves interactive map using Leaflet.js with existing map data and styling
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory
from utils.config import load_area_config, load_output_format
from utils.data_processing import convert_osm_to_shapefiles, calculate_bbox
from utils.create_enhanced_data import create_enhanced_tourist_database

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')

# Configuration
AREA_NAME = 'lumsden'
DATA_DIR = 'data'
WEB_DIR = 'web'

@app.route('/')
def index():
    """Serve the main interactive map page"""
    area_config = load_area_config(AREA_NAME)
    bbox = calculate_bbox(
        area_config['center']['lat'],
        area_config['center']['lon'],
        area_config['coverage']['width_km'],
        area_config['coverage']['height_km']
    )
    
    return render_template('index.html', 
                         center_lat=area_config['center']['lat'],
                         center_lon=area_config['center']['lon'],
                         bbox=bbox,
                         area_name=area_config['name'])

@app.route('/api/config')
def get_config():
    """API endpoint to get map configuration"""
    area_config = load_area_config(AREA_NAME)
    bbox = calculate_bbox(
        area_config['center']['lat'],
        area_config['center']['lon'],
        area_config['coverage']['width_km'],
        area_config['coverage']['height_km']
    )
    
    return jsonify({
        'center': area_config['center'],
        'bbox': bbox,
        'name': area_config['name'],
        'scale': area_config['scale']
    })

@app.route('/api/data/<layer>')
def get_layer_data(layer):
    """Serve GeoJSON data for map layers"""
    enhanced_data_dir = Path('enhanced_data')
    
    # Map layer names to files
    layer_files = {
        'attractions': 'tourist_attractions.geojson',
        'accommodation': 'accommodation.geojson',
        'dining': 'dining.geojson',
        'activities': 'activities.geojson',
        'trails': 'walking_trails.geojson'
    }
    
    if layer in layer_files:
        file_path = enhanced_data_dir / layer_files[layer]
        if file_path.exists():
            with open(file_path, 'r') as f:
                return jsonify(json.load(f))
    
    return jsonify({'type': 'FeatureCollection', 'features': []})

@app.route('/map_image')
def get_map_image():
    """Serve the generated static map image as a tile overlay"""
    map_file = Path(DATA_DIR) / 'lumsden_tourist_map_A3.png'
    if map_file.exists():
        return send_from_directory(DATA_DIR, 'lumsden_tourist_map_A3.png')
    return "Map not found", 404

@app.route('/initialize')
def initialize_data():
    """Initialize and prepare data for web mapping"""
    try:
        # Ensure enhanced data exists
        enhanced_data_dir = Path('enhanced_data')
        if not enhanced_data_dir.exists():
            print("Creating enhanced tourist data...")
            create_enhanced_tourist_database()
        
        return jsonify({'status': 'success', 'message': 'Data initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def create_web_directories():
    """Create necessary web directories if they don't exist"""
    web_dirs = ['web', 'web/static', 'web/templates', 'web/static/css', 'web/static/js']
    for dir_path in web_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    print("🌐 Starting Lumsden Interactive Map Server...")
    create_web_directories()
    
    # Initialize data if needed
    enhanced_data_dir = Path('enhanced_data')
    if not enhanced_data_dir.exists():
        print("📊 Creating enhanced tourist data...")
        try:
            create_enhanced_tourist_database()
        except Exception as e:
            print(f"⚠️  Warning: Could not create enhanced data: {e}")
    
    print(f"🚀 Server starting at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)