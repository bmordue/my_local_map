#!/usr/bin/env python3
"""
Tests for User-Generated Content Integration
Tests the Phase 3 user content functionality
"""

import unittest
import tempfile
import json
import sqlite3
from pathlib import Path
from utils.user_content import UserContentManager
from utils.moderation import ContentModerator


class TestUserContentManager(unittest.TestCase):
    """Test cases for UserContentManager"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_user_content.db"
        self.manager = UserContentManager(str(self.db_path))
    
    def test_database_initialization(self):
        """Test that database is properly initialized"""
        self.assertTrue(self.db_path.exists())
        
        # Check that all tables exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['user_reviews', 'user_photos', 'user_poi_updates', 'user_tips']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_submit_review(self):
        """Test review submission"""
        review_id = self.manager.submit_review(
            poi_id=1,
            poi_type='attraction',
            user_name='Test User',
            user_email='test@example.com',
            rating=5,
            review_text='Great place to visit!',
            visit_date='2024-01-01'
        )
        
        self.assertIsInstance(review_id, int)
        self.assertGreater(review_id, 0)
        
        # Verify review was stored
        reviews = self.manager.get_reviews_for_poi(1, 'attraction', 'pending')
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['user_name'], 'Test User')
        self.assertEqual(reviews[0]['rating'], 5)
    
    def test_submit_poi_update(self):
        """Test POI update submission"""
        poi_data = {
            'name': 'Test POI',
            'description': 'A test point of interest',
            'lat': 57.3167,
            'lon': -2.8833,
            'opening_hours': '9:00-17:00',
            'amenities': 'Parking, WiFi'
        }
        
        update_id = self.manager.submit_poi_update(
            poi_type='attraction',
            update_type='new',
            user_name='Test User',
            user_email='test@example.com',
            poi_data=poi_data
        )
        
        self.assertIsInstance(update_id, int)
        self.assertGreater(update_id, 0)
    
    def test_submit_tip(self):
        """Test tip submission"""
        tip_id = self.manager.submit_tip(
            tip_category='local_knowledge',
            user_name='Local Guide',
            tip_text='Best photos taken in the morning',
            poi_id=1
        )
        
        self.assertIsInstance(tip_id, int)
        self.assertGreater(tip_id, 0)
    
    def test_average_rating(self):
        """Test average rating calculation"""
        # Submit multiple reviews
        self.manager.submit_review(1, 'attraction', 'User 1', None, 4, 'Good')
        self.manager.submit_review(1, 'attraction', 'User 2', None, 5, 'Excellent')
        
        # Approve reviews
        self.manager.moderate_content('user_reviews', 1, 'approved')
        self.manager.moderate_content('user_reviews', 2, 'approved')
        
        avg_rating = self.manager.get_average_rating(1, 'attraction')
        self.assertEqual(avg_rating, 4.5)
    
    def test_export_to_geojson(self):
        """Test GeoJSON export functionality"""
        # Submit and approve a POI update
        poi_data = {
            'name': 'Test POI',
            'description': 'A test point of interest',
            'lat': 57.3167,
            'lon': -2.8833,
            'amenities': 'Parking'
        }
        
        update_id = self.manager.submit_poi_update(
            poi_type='attraction',
            update_type='new',
            user_name='Test User',
            user_email='test@example.com',
            poi_data=poi_data
        )
        
        # Approve the update
        self.manager.moderate_content('user_poi_updates', update_id, 'approved')
        
        # Export to GeoJSON
        geojson = self.manager.export_user_content_to_geojson()
        
        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertEqual(len(geojson['features']), 1)
        
        feature = geojson['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        self.assertEqual(feature['geometry']['type'], 'Point')
        self.assertEqual(feature['properties']['name'], 'Test POI')
        self.assertEqual(feature['properties']['data_source'], 'user_generated')
    
    def test_content_statistics(self):
        """Test content statistics"""
        # Submit some content
        self.manager.submit_review(1, 'attraction', 'User 1', None, 5, 'Great!')
        self.manager.submit_tip('local_knowledge', 'Local', 'Useful tip')
        
        stats = self.manager.get_content_statistics()
        
        self.assertIn('reviews', stats)
        self.assertIn('tips', stats)
        self.assertEqual(stats['reviews']['pending'], 1)
        self.assertEqual(stats['tips']['pending'], 1)


class TestContentModerator(unittest.TestCase):
    """Test cases for ContentModerator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_moderation.db"
        self.moderator = ContentModerator()
        self.moderator.manager = UserContentManager(str(self.db_path))
    
    def test_moderation(self):
        """Test content moderation"""
        # Submit a review
        review_id = self.moderator.manager.submit_review(
            poi_id=1,
            poi_type='attraction',
            user_name='Test User',
            user_email='test@example.com',
            rating=5,
            review_text='Excellent attraction!',
        )
        
        # Test approval
        success = self.moderator.manager.moderate_content('user_reviews', review_id, 'approved', 'Looks good')
        self.assertTrue(success)
        
        # Verify status change
        reviews = self.moderator.manager.get_reviews_for_poi(1, 'attraction', 'approved')
        self.assertEqual(len(reviews), 1)
    
    def test_auto_moderation(self):
        """Test automated moderation"""
        # Submit safe content
        self.moderator.manager.submit_review(1, 'attraction', 'User', None, 4, 'Nice place to visit')
        self.moderator.manager.submit_tip('local_knowledge', 'Local', 'Good tip for visitors')
        
        # Submit unsafe content
        self.moderator.manager.submit_review(2, 'attraction', 'Spammer', None, 1, 'spam spam spam')
        
        # Run auto-moderation
        moderated_count = self.moderator.auto_moderate_content()
        
        self.assertGreater(moderated_count, 0)
        
        # Check that safe content was approved
        stats = self.moderator.manager.get_content_statistics()
        self.assertGreater(stats.get('reviews', {}).get('approved', 0), 0)


class TestUserContentIntegration(unittest.TestCase):
    """Integration tests for user content system"""
    
    def test_full_workflow(self):
        """Test complete user content workflow"""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "integration_test.db"
        
        # 1. Initialize system
        manager = UserContentManager(str(db_path))
        moderator = ContentModerator()
        moderator.manager = manager
        
        # 2. Submit various content types
        review_id = manager.submit_review(1, 'attraction', 'Tourist', 'tourist@example.com', 5, 'Amazing castle!')
        
        poi_data = {
            'name': 'Hidden Gem',
            'description': 'Local secret spot',
            'lat': 57.3200,
            'lon': -2.8800,
            'amenities': 'Free parking'
        }
        poi_id = manager.submit_poi_update('attraction', 'new', 'Local', 'local@example.com', poi_data)
        
        tip_id = manager.submit_tip('photography', 'Photographer', 'Best light at sunrise')
        
        # 3. Moderate content
        manager.moderate_content('user_reviews', review_id, 'approved')
        manager.moderate_content('user_poi_updates', poi_id, 'approved') 
        manager.moderate_content('user_tips', tip_id, 'approved')
        
        # 4. Export for map integration
        geojson = manager.export_user_content_to_geojson()
        
        # 5. Verify integration readiness
        self.assertEqual(len(geojson['features']), 1)  # Only POI with coordinates
        self.assertEqual(geojson['features'][0]['properties']['name'], 'Hidden Gem')
        
        # 6. Check statistics
        stats = manager.get_content_statistics()
        self.assertEqual(stats['reviews']['approved'], 1)
        self.assertEqual(stats['poi_updates']['approved'], 1)
        self.assertEqual(stats['tips']['approved'], 1)


def run_tests():
    """Run all user content tests"""
    print("🧪 Running User-Generated Content Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestUserContentManager))
    test_suite.addTest(unittest.makeSuite(TestContentModerator))
    test_suite.addTest(unittest.makeSuite(TestUserContentIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)