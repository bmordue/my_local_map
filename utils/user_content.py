#!/usr/bin/env python3
"""
User-Generated Content Integration for Lumsden Tourist Map
Implements Phase 3 functionality for community contributions
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils.data_processing import calculate_bbox
from utils.config import load_area_config


class UserContentManager:
    """Manages user-generated content for the map including reviews, photos, and POI updates"""
    
    def __init__(self, db_path: str = "enhanced_data/lumsden_tourist_user.db"):
        """Initialize user content manager with database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize user content database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User reviews and ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id INTEGER NOT NULL,
                poi_type TEXT NOT NULL,  -- 'attraction', 'accommodation', 'dining', 'activity'
                user_name TEXT,
                user_email TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                review_text TEXT,
                visit_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
                moderation_notes TEXT
            )
        ''')
        
        # User-submitted photos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id INTEGER NOT NULL,
                poi_type TEXT NOT NULL,
                user_name TEXT,
                user_email TEXT,
                photo_path TEXT NOT NULL,
                caption TEXT,
                taken_date TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                moderation_notes TEXT
            )
        ''')
        
        # User-contributed POI updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_poi_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id INTEGER,  -- NULL for new POIs
                poi_type TEXT NOT NULL,
                user_name TEXT,
                user_email TEXT,
                update_type TEXT NOT NULL,  -- 'new', 'update', 'correction'
                name TEXT,
                description TEXT,
                lat REAL,
                lon REAL,
                opening_hours TEXT,
                phone TEXT,
                website TEXT,
                amenities TEXT,
                additional_info TEXT,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                moderation_notes TEXT
            )
        ''')
        
        # Community tips and local knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id INTEGER,  -- Can be NULL for general area tips
                tip_category TEXT,  -- 'access', 'seasonal', 'local_knowledge', 'safety'
                user_name TEXT,
                tip_text TEXT NOT NULL,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                helpful_votes INTEGER DEFAULT 0,
                moderation_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def submit_review(self, poi_id: int, poi_type: str, user_name: str, 
                     user_email: str, rating: int, review_text: str, 
                     visit_date: Optional[str] = None) -> int:
        """Submit a user review for a POI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_reviews 
            (poi_id, poi_type, user_name, user_email, rating, review_text, visit_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (poi_id, poi_type, user_name, user_email, rating, review_text, visit_date))
        
        review_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return review_id
    
    def submit_photo(self, poi_id: int, poi_type: str, user_name: str,
                    user_email: str, photo_path: str, caption: str = "",
                    taken_date: Optional[str] = None) -> int:
        """Submit a user photo for a POI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_photos 
            (poi_id, poi_type, user_name, user_email, photo_path, caption, taken_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (poi_id, poi_type, user_name, user_email, photo_path, caption, taken_date))
        
        photo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return photo_id
    
    def submit_poi_update(self, poi_type: str, update_type: str, user_name: str,
                         user_email: str, poi_data: Dict[str, Any], 
                         poi_id: Optional[int] = None) -> int:
        """Submit a POI update or new POI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_poi_updates 
            (poi_id, poi_type, user_name, user_email, update_type, name, description,
             lat, lon, opening_hours, phone, website, amenities, additional_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            poi_id, poi_type, user_name, user_email, update_type,
            poi_data.get('name'), poi_data.get('description'),
            poi_data.get('lat'), poi_data.get('lon'),
            poi_data.get('opening_hours'), poi_data.get('phone'),
            poi_data.get('website'), poi_data.get('amenities'),
            poi_data.get('additional_info')
        ))
        
        update_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return update_id
    
    def submit_tip(self, tip_category: str, user_name: str, tip_text: str,
                  poi_id: Optional[int] = None) -> int:
        """Submit a local tip or knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_tips 
            (poi_id, tip_category, user_name, tip_text)
            VALUES (?, ?, ?, ?)
        ''', (poi_id, tip_category, user_name, tip_text))
        
        tip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return tip_id
    
    def get_reviews_for_poi(self, poi_id: int, poi_type: str, status: str = 'approved') -> List[Dict]:
        """Get approved reviews for a specific POI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_name, rating, review_text, visit_date, created_at
            FROM user_reviews 
            WHERE poi_id = ? AND poi_type = ? AND status = ?
            ORDER BY created_at DESC
        ''', (poi_id, poi_type, status))
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                'user_name': row[0],
                'rating': row[1],
                'review_text': row[2],
                'visit_date': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return reviews
    
    def get_average_rating(self, poi_id: int, poi_type: str) -> Optional[float]:
        """Get average user rating for a POI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(rating) FROM user_reviews 
            WHERE poi_id = ? AND poi_type = ? AND status = 'approved'
        ''', (poi_id, poi_type))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] is not None else None
    
    def moderate_content(self, table_name: str, content_id: int, status: str, 
                        moderation_notes: str = "") -> bool:
        """Moderate user-generated content"""
        valid_tables = ['user_reviews', 'user_photos', 'user_poi_updates', 'user_tips']
        valid_statuses = ['pending', 'approved', 'rejected']
        
        if table_name not in valid_tables or status not in valid_statuses:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            UPDATE {table_name} 
            SET status = ?, moderation_notes = ? 
            WHERE id = ?
        ''', (status, moderation_notes, content_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_pending_content(self, table_name: str) -> List[Dict]:
        """Get all pending content for moderation"""
        valid_tables = ['user_reviews', 'user_photos', 'user_poi_updates', 'user_tips']
        
        if table_name not in valid_tables:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT * FROM {table_name} WHERE status = "pending"')
        
        columns = [description[0] for description in cursor.description]
        pending_content = []
        
        for row in cursor.fetchall():
            pending_content.append(dict(zip(columns, row)))
        
        conn.close()
        return pending_content
    
    def export_user_content_to_geojson(self, area_name: str = "lumsden") -> Dict[str, Any]:
        """Export user-contributed content to GeoJSON format for map integration"""
        area_config = load_area_config(area_name)
        bbox = calculate_bbox(
            area_config['center']['lat'], 
            area_config['center']['lon'],
            area_config['coverage']['width_km'], 
            area_config['coverage']['height_km']
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get approved POI updates that have coordinates
        cursor.execute('''
            SELECT name, description, lat, lon, poi_type, opening_hours, 
                   phone, website, amenities, submitted_at, user_name
            FROM user_poi_updates 
            WHERE status = 'approved' AND lat IS NOT NULL AND lon IS NOT NULL
            AND lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
        ''', (bbox['south'], bbox['north'], bbox['west'], bbox['east']))
        
        features = []
        for row in cursor.fetchall():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row[3], row[2]]  # [lon, lat]
                },
                "properties": {
                    "name": row[0],
                    "description": row[1],
                    "poi_type": row[4],
                    "opening_hours": row[5],
                    "phone": row[6],
                    "website": row[7],
                    "amenities": row[8],
                    "submitted_at": row[9],
                    "contributor": row[10],
                    "data_source": "user_generated"
                }
            }
            features.append(feature)
        
        conn.close()
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get statistics about user-generated content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count reviews by status
        cursor.execute('SELECT status, COUNT(*) FROM user_reviews GROUP BY status')
        stats['reviews'] = dict(cursor.fetchall())
        
        # Count photos by status
        cursor.execute('SELECT status, COUNT(*) FROM user_photos GROUP BY status')
        stats['photos'] = dict(cursor.fetchall())
        
        # Count POI updates by status
        cursor.execute('SELECT status, COUNT(*) FROM user_poi_updates GROUP BY status')
        stats['poi_updates'] = dict(cursor.fetchall())
        
        # Count tips by status
        cursor.execute('SELECT status, COUNT(*) FROM user_tips GROUP BY status')
        stats['tips'] = dict(cursor.fetchall())
        
        # Get most active contributors
        cursor.execute('''
            SELECT user_name, COUNT(*) as contributions
            FROM (
                SELECT user_name FROM user_reviews WHERE status = 'approved'
                UNION ALL
                SELECT user_name FROM user_photos WHERE status = 'approved'
                UNION ALL
                SELECT user_name FROM user_poi_updates WHERE status = 'approved'
                UNION ALL
                SELECT user_name FROM user_tips WHERE status = 'approved'
            ) GROUP BY user_name
            ORDER BY contributions DESC
            LIMIT 5
        ''')
        stats['top_contributors'] = [{'name': row[0], 'contributions': row[1]} 
                                   for row in cursor.fetchall()]
        
        conn.close()
        return stats