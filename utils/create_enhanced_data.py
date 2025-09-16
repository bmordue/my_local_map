#!/usr/bin/env python3
"""
Enhanced Map Data Integration - Demonstrating Additional Data Sources
"""

import json
import csv
from pathlib import Path
import sqlite3

def create_enhanced_tourist_database():
    """Create a comprehensive tourist database for the Lumsden area"""
    
    # Create enhanced database
    db_path = Path("enhanced_data/lumsden_tourist.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create comprehensive tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tourist_attractions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            subtype TEXT,
            description TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            opening_hours TEXT,
            website TEXT,
            phone TEXT,
            admission_fee TEXT,
            accessibility TEXT,
            parking BOOLEAN,
            seasonal BOOLEAN,
            rating REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accommodation (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            star_rating INTEGER,
            description TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            capacity INTEGER,
            price_range TEXT,
            website TEXT,
            phone TEXT,
            amenities TEXT,
            pet_friendly BOOLEAN,
            wifi BOOLEAN,
            parking BOOLEAN
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dining (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            cuisine TEXT,
            description TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            price_range TEXT,
            opening_hours TEXT,
            website TEXT,
            phone TEXT,
            outdoor_seating BOOLEAN,
            takeaway BOOLEAN,
            wheelchair_accessible BOOLEAN,
            local_produce BOOLEAN
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            activity_type TEXT,
            description TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            duration TEXT,
            difficulty TEXT,
            booking_required BOOLEAN,
            seasonal BOOLEAN,
            equipment_provided BOOLEAN,
            cost TEXT,
            min_age INTEGER,
            max_group_size INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS walking_trails (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            start_lat REAL NOT NULL,
            start_lon REAL NOT NULL,
            end_lat REAL,
            end_lon REAL,
            distance_km REAL,
            duration_hours REAL,
            difficulty TEXT,
            surface_type TEXT,
            circular BOOLEAN,
            waymarked BOOLEAN,
            facilities TEXT,
            highlights TEXT
        )
    ''')
    
    # Insert comprehensive sample data
    
    # Tourist Attractions
    attractions = [
        ("Corgarff Castle", "historic", "castle", "16th-century tower house with star-shaped curtain wall", 57.335, -2.865, "Apr-Sep: 9:30-17:30", "www.historicenvironment.scot", "+44 1975 651460", "Adult £5, Child £3", "Partial wheelchair access", True, False, 4.2),
        ("Lumsden Heritage Trail", "tourism", "trail", "Self-guided heritage walk through village", 57.3167, -2.8833, "Always open", None, None, "Free", "Fully accessible", True, False, 4.0),
        ("Bellabeg Forest Walks", "natural", "forest", "Network of woodland paths with wildlife viewing", 57.340, -2.850, "Always open", None, None, "Free", "Some accessible paths", True, False, 4.3),
        ("River Don Fishing", "leisure", "fishing", "Excellent salmon and trout fishing", 57.320, -2.870, "Season: Feb-Oct", "www.riverdon-angling.co.uk", "+44 1975 651234", "Day permit £25", "Riverbank access varies", True, True, 4.1),
        ("Lumsden Viewpoint", "tourism", "viewpoint", "Panoramic views of Don Valley", 57.330, -2.875, "Always open", None, None, "Free", "Accessible by car", True, False, 4.5),
    ]
    
    cursor.executemany('''
        INSERT INTO tourist_attractions 
        (name, type, subtype, description, lat, lon, opening_hours, website, phone, admission_fee, accessibility, parking, seasonal, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', attractions)
    
    # Accommodation
    accommodation = [
        ("The Corgarff Arms", "hotel", 3, "Traditional Highland inn with modern amenities", 57.315, -2.885, 12, "££", "www.corgarffarms.com", "+44 1975 651234", "Restaurant, Bar, Wifi", True, True, True),
        ("Lumsden Farm B&B", "bed_and_breakfast", None, "Working farm offering comfortable rooms", 57.312, -2.879, 6, "£", "www.lumsdenfarm.co.uk", "+44 1975 651567", "Breakfast, Farm tours", True, True, True),
        ("Highland Holiday Cottage", "holiday_cottage", None, "Self-catering cottage for families", 57.308, -2.888, 8, "££", "www.highland-cottage.com", "+44 1975 651890", "Kitchen, Garden, Parking", True, True, True),
        ("Camping Barn", "hostel", None, "Basic accommodation for walkers", 57.325, -2.872, 16, "£", None, "+44 1975 651445", "Shared facilities, Drying room", False, False, True),
    ]
    
    cursor.executemany('''
        INSERT INTO accommodation 
        (name, type, star_rating, description, lat, lon, capacity, price_range, website, phone, amenities, pet_friendly, wifi, parking)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', accommodation)
    
    # Dining
    dining = [
        ("The Village Tearoom", "cafe", "British", "Homemade cakes and light lunches", 57.316, -2.884, "££", "9:00-17:00 (Closed Mon)", "www.villagetearoom.co.uk", "+44 1975 651333", True, True, True, True),
        ("Lumsden Fish & Chips", "restaurant", "Fish & Chips", "Fresh local fish, takeaway available", 57.318, -2.882, "£", "17:00-21:00 (Closed Sun)", None, "+44 1975 651777", False, True, True, False),
        ("The Highland Restaurant", "restaurant", "Scottish", "Fine dining with local produce", 57.315, -2.885, "£££", "18:00-22:00 (Closed Mon-Tue)", "www.highland-restaurant.com", "+44 1975 651234", True, False, True, True),
        ("Mobile Coffee Van", "cafe", "Coffee", "Morning coffee and pastries", 57.317, -2.883, "£", "7:00-11:00 (Weekdays)", None, "+44 7700 123456", False, True, True, True),
    ]
    
    cursor.executemany('''
        INSERT INTO dining 
        (name, type, cuisine, description, lat, lon, price_range, opening_hours, website, phone, outdoor_seating, takeaway, wheelchair_accessible, local_produce)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', dining)
    
    # Activities
    activities = [
        ("Guided Castle Tour", "tourism", "guided_tour", "Expert-led tour of Corgarff Castle", 57.335, -2.865, "1.5 hours", "Easy", True, True, True, "£8", 5, 20),
        ("Forest Bushcraft", "outdoor", "bushcraft", "Learn traditional woodland skills", 57.340, -2.850, "Half day", "Moderate", True, True, True, "£45", 8, 12),
        ("River Don Kayaking", "water", "kayaking", "Gentle paddling downstream", 57.320, -2.870, "3 hours", "Easy", True, True, True, "£35", 12, 8),
        ("Highland Photography", "tourism", "photography", "Capture stunning Highland scenery", 57.330, -2.875, "4 hours", "Easy", True, False, True, "£25", 10, 10),
        ("Farm Experience", "agritourism", "farm_visit", "Meet animals and learn about farming", 57.312, -2.879, "2 hours", "Easy", True, False, False, "£12", 3, 15),
    ]
    
    cursor.executemany('''
        INSERT INTO activities 
        (name, type, activity_type, description, lat, lon, duration, difficulty, booking_required, seasonal, equipment_provided, cost, min_age, max_group_size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', activities)
    
    # Walking Trails
    trails = [
        ("Lumsden Village Loop", "Easy circular walk around village", 57.3167, -2.8833, 57.3167, -2.8833, 2.5, 1.0, "Easy", "Pavement/grass", True, True, "Benches, Village shop", "Church, Heritage signs"),
        ("Corgarff Castle Walk", "Historic walk to castle and back", 57.3167, -2.8833, 57.335, -2.865, 4.2, 1.5, "Moderate", "Path/track", False, True, "Castle visitor center", "Castle, River views"),
        ("Bellabeg Forest Trail", "Woodland circuit with wildlife", 57.340, -2.850, 57.340, -2.850, 3.8, 2.0, "Easy", "Forest path", True, True, "Car park, Information board", "Wildlife, Ancient trees"),
        ("River Don Riverside", "Following the river downstream", 57.320, -2.870, 57.305, -2.895, 6.5, 2.5, "Moderate", "Riverside path", False, True, "Bridge access", "River pools, Fishing spots"),
        ("Highland Viewpoint Trek", "Climb for panoramic views", 57.3167, -2.8833, 57.330, -2.875, 3.2, 1.8, "Moderate", "Hill path", False, True, "Viewpoint bench", "Valley views, Highland scenery"),
    ]
    
    cursor.executemany('''
        INSERT INTO walking_trails 
        (name, description, start_lat, start_lon, end_lat, end_lon, distance_km, duration_hours, difficulty, surface_type, circular, waymarked, facilities, highlights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', trails)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Created comprehensive tourist database: {db_path}")
    print(f"  - {len(attractions)} tourist attractions")
    print(f"  - {len(accommodation)} accommodation options")
    print(f"  - {len(dining)} dining venues") 
    print(f"  - {len(activities)} activities")
    print(f"  - {len(trails)} walking trails")
    
    return db_path

def export_database_to_geojson(db_path):
    """Export database to GeoJSON for use in mapping"""
    
    conn = sqlite3.connect(db_path)
    
    # Export each table to GeoJSON
    tables = ['tourist_attractions', 'accommodation', 'dining', 'activities']
    
    for table in tables:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create GeoJSON
        features = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            lat = row_dict.pop('lat')
            lon = row_dict.pop('lon')
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": row_dict
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        output_file = Path(f"enhanced_data/{table}.geojson")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"✓ Exported {table}: {len(features)} features")
    
    # Export trails separately (they have start/end points)
    cursor.execute("SELECT * FROM walking_trails")
    trails = cursor.fetchall()
    cursor.execute("PRAGMA table_info(walking_trails)")
    trail_columns = [col[1] for col in cursor.fetchall()]
    
    trail_features = []
    for trail in trails:
        trail_dict = dict(zip(trail_columns, trail))
        start_lat = trail_dict.pop('start_lat')
        start_lon = trail_dict.pop('start_lon')
        end_lat = trail_dict.pop('end_lat', None)
        end_lon = trail_dict.pop('end_lon', None)
        
        # Create line geometry if we have end points
        if end_lat and end_lon and (start_lat != end_lat or start_lon != end_lon):
            geometry = {
                "type": "LineString",
                "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
            }
        else:
            geometry = {
                "type": "Point", 
                "coordinates": [start_lon, start_lat]
            }
        
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": trail_dict
        }
        trail_features.append(feature)
    
    trails_geojson = {
        "type": "FeatureCollection",
        "features": trail_features
    }
    
    with open("enhanced_data/walking_trails.geojson", 'w') as f:
        json.dump(trails_geojson, f, indent=2)
    
    print(f"✓ Exported walking_trails: {len(trail_features)} features")
    
    conn.close()

if __name__ == "__main__":
    print("Creating Enhanced Tourist Data Integration")
    print("=" * 50)
    
    db_path = create_enhanced_tourist_database()
    export_database_to_geojson(db_path)
    
    print("\n🎉 Enhanced tourist data created!")
    print("📊 Database: data/enhanced_data/lumsden_tourist.db")
    print("🗺️  GeoJSON files: data/enhanced_data/*.geojson")
    print("📋 Ready for integration with mapping systems")
