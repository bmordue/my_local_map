"""Tests for route planning functionality"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import math

from utils.route_planning import (
    RoutePoint, Route, RoutePlanner, 
    process_route_planning, export_routes_to_geojson
)


class TestRoutePoint:
    """Test RoutePoint class functionality"""
    
    def test_route_point_creation(self):
        """Test creating a route point"""
        point = RoutePoint(57.3167, -2.8833, "Lumsden Center", "start")
        
        assert point.lat == 57.3167
        assert point.lon == -2.8833
        assert point.name == "Lumsden Center"
        assert point.poi_type == "start"
    
    def test_route_point_distance_calculation(self):
        """Test distance calculation between points"""
        point1 = RoutePoint(57.3167, -2.8833)
        point2 = RoutePoint(57.3200, -2.8800)
        
        distance = point1.distance_to(point2)
        
        # Should be approximately 0.5 km (rough calculation)
        assert 0.3 < distance < 0.7
        
    def test_route_point_to_dict(self):
        """Test converting route point to dictionary"""
        point = RoutePoint(57.3167, -2.8833, "Test Point", "attraction")
        result = point.to_dict()
        
        expected = {
            'lat': 57.3167,
            'lon': -2.8833,
            'name': "Test Point",
            'poi_type': "attraction"
        }
        assert result == expected


class TestRoute:
    """Test Route class functionality"""
    
    def test_route_creation(self):
        """Test creating a route"""
        route = Route("Test Route", "walking")
        
        assert route.name == "Test Route"
        assert route.route_type == "walking"
        assert len(route.points) == 0
        assert route.total_distance == 0.0
        assert route.estimated_time == 0.0
    
    def test_route_add_points(self):
        """Test adding points to a route"""
        route = Route("Test Route", "walking")
        
        point1 = RoutePoint(57.3167, -2.8833, "Start")
        point2 = RoutePoint(57.3200, -2.8800, "End")
        
        route.add_point(point1)
        assert len(route.points) == 1
        assert route.total_distance == 0.0  # Single point has no distance
        
        route.add_point(point2)
        assert len(route.points) == 2
        assert route.total_distance > 0.0  # Two points should have distance
        assert route.estimated_time > 0.0  # Should have estimated time
    
    def test_route_time_estimation_by_type(self):
        """Test different time estimations for different route types"""
        point1 = RoutePoint(57.3167, -2.8833)
        point2 = RoutePoint(57.3200, -2.8800)
        
        # Test walking route
        walking_route = Route("Walking", "walking")
        walking_route.add_point(point1)
        walking_route.add_point(point2)
        walking_time = walking_route.estimated_time
        
        # Test accessible route
        accessible_route = Route("Accessible", "accessible")
        accessible_route.add_point(point1)
        accessible_route.add_point(point2)
        accessible_time = accessible_route.estimated_time
        
        # Test cycling route
        cycling_route = Route("Cycling", "cycling")
        cycling_route.add_point(point1)
        cycling_route.add_point(point2)
        cycling_time = cycling_route.estimated_time
        
        # Accessible should be slower than walking, cycling should be fastest
        assert accessible_time > walking_time
        assert cycling_time < walking_time
    
    def test_route_to_dict(self):
        """Test converting route to dictionary"""
        route = Route("Test Route", "walking")
        point1 = RoutePoint(57.3167, -2.8833, "Start", "start")
        route.add_point(point1)
        route.accessibility_features = ["Paved paths"]
        route.description = "Test description"
        
        result = route.to_dict()
        
        assert result['name'] == "Test Route"
        assert result['route_type'] == "walking"
        assert len(result['points']) == 1
        assert result['accessibility_features'] == ["Paved paths"]
        assert result['description'] == "Test description"


class TestRoutePlanner:
    """Test RoutePlanner class functionality"""
    
    def setup_method(self):
        """Set up test data for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.area_config = {
            'center': {'lat': 57.3167, 'lon': -2.8833},
            'route_planning': {
                'enabled': True,
                'route_types': ['walking'],
                'max_walking_distance': 5.0
            }
        }
        self.planner = RoutePlanner(str(self.temp_dir), self.area_config)
    
    def test_route_planner_creation(self):
        """Test creating a route planner"""
        assert self.planner.center_lat == 57.3167
        assert self.planner.center_lon == -2.8833
        assert self.planner.osm_data_dir == self.temp_dir
    
    @patch('subprocess.run')
    def test_extract_poi_points_no_shapefile(self, mock_run):
        """Test POI extraction when shapefile doesn't exist"""
        points = self.planner.extract_poi_points()
        
        assert len(points) == 0
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_extract_poi_points_with_shapefile(self, mock_run):
        """Test POI extraction with existing shapefile"""
        # Create mock shapefile
        points_shapefile = self.temp_dir / "points.shp"
        points_shapefile.touch()
        
        # Mock ogrinfo output
        mock_run.return_value.stdout = "POINT (-2.8833 57.3167)\nPOINT (-2.8800 57.3200)\n"
        
        points = self.planner.extract_poi_points()
        
        assert len(points) == 2
        assert points[0].lat == 57.3167
        assert points[0].lon == -2.8833
        mock_run.assert_called_once()
    
    def test_create_sample_lumsden_route(self):
        """Test creating sample Lumsden route"""
        route = self.planner._create_sample_lumsden_route("Test Route", "walking")
        
        assert route.name == "Test Route"
        assert route.route_type == "walking"
        assert len(route.points) == 6  # Start + 4 stops + return
        assert route.total_distance > 0.0
        assert route.estimated_time > 0.0
        assert "circular walking route" in route.description
    
    def test_create_accessibility_route(self):
        """Test creating accessibility route"""
        route_config = {'name': 'Accessible Route', 'max_distance_km': 5.0}
        route = self.planner.create_accessibility_route(route_config)
        
        assert route.route_type == 'accessible'
        assert len(route.accessibility_features) > 0
        assert "Wheelchair accessible paths" in route.accessibility_features
    
    def test_create_tourist_route_no_pois(self):
        """Test creating tourist route when no POIs found"""
        route_config = {'name': 'Tourist Route', 'type': 'walking'}
        route = self.planner.create_tourist_route(route_config)
        
        assert route is not None
        assert route.name == 'Tourist Route'
        assert route.route_type == 'walking'
        assert len(route.points) > 0  # Should create sample route


class TestRouteProcessing:
    """Test main route processing functions"""
    
    def setup_method(self):
        """Set up test data for each test"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def test_process_route_planning_disabled(self):
        """Test route planning when disabled"""
        area_config = {'route_planning': {'enabled': False}}
        
        result = process_route_planning(area_config, str(self.temp_dir))
        
        assert result == {}
    
    def test_process_route_planning_no_config(self):
        """Test route planning when no config provided"""
        area_config = {}
        
        result = process_route_planning(area_config, str(self.temp_dir))
        
        assert result == {}
    
    def test_process_route_planning_enabled(self):
        """Test route planning when enabled"""
        area_config = {
            'center': {'lat': 57.3167, 'lon': -2.8833},
            'route_planning': {
                'enabled': True,
                'route_types': ['walking', 'accessible'],
                'max_walking_distance': 5.0,
                'max_accessible_distance': 3.0
            }
        }
        
        result = process_route_planning(area_config, str(self.temp_dir))
        
        assert 'routes' in result
        assert 'total_routes' in result
        assert result['total_routes'] > 0
        assert len(result['routes']) == 2  # walking + accessible
        
        # Check that GeoJSON file was created
        geojson_file = Path(result['geojson_file'])
        assert geojson_file.exists()
        
        # Verify GeoJSON content
        with open(geojson_file) as f:
            geojson_data = json.load(f)
        assert geojson_data['type'] == 'FeatureCollection'
        assert len(geojson_data['features']) == 2


class TestGeoJSONExport:
    """Test GeoJSON export functionality"""
    
    def test_export_routes_to_geojson(self):
        """Test exporting routes to GeoJSON format"""
        route = Route("Test Route", "walking")
        route.add_point(RoutePoint(57.3167, -2.8833, "Start"))
        route.add_point(RoutePoint(57.3200, -2.8800, "End"))
        route.description = "Test route description"
        
        geojson = export_routes_to_geojson([route])
        
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == 1
        
        feature = geojson['features'][0]
        assert feature['type'] == 'Feature'
        assert feature['geometry']['type'] == 'LineString'
        assert len(feature['geometry']['coordinates']) == 2
        
        props = feature['properties']
        assert props['name'] == "Test Route"
        assert props['route_type'] == "walking"
        assert props['distance_km'] > 0
        assert props['estimated_time_hours'] > 0
        assert props['description'] == "Test route description"
    
    def test_export_empty_routes(self):
        """Test exporting empty route list"""
        geojson = export_routes_to_geojson([])
        
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == 0
    
    def test_export_route_with_single_point(self):
        """Test exporting route with only one point (should be skipped)"""
        route = Route("Single Point Route", "walking")
        route.add_point(RoutePoint(57.3167, -2.8833, "Lonely Point"))
        
        geojson = export_routes_to_geojson([route])
        
        assert geojson['type'] == 'FeatureCollection'
        assert len(geojson['features']) == 0  # Single point routes are skipped


class TestIntegration:
    """Integration tests for route planning"""
    
    def test_route_planning_workflow(self):
        """Test complete route planning workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            area_config = {
                'center': {'lat': 57.3167, 'lon': -2.8833},
                'route_planning': {
                    'enabled': True,
                    'route_types': ['walking'],
                    'max_walking_distance': 3.0
                }
            }
            
            # Process route planning
            result = process_route_planning(area_config, temp_dir)
            
            # Verify results
            assert result['total_routes'] == 1
            assert len(result['routes']) == 1
            
            route_data = result['routes'][0]
            assert route_data['name'] == 'Lumsden Walking Route'
            assert route_data['route_type'] == 'walking'
            assert route_data['total_distance'] > 0
            
            # Verify GeoJSON file exists and is valid
            geojson_path = Path(result['geojson_file'])
            assert geojson_path.exists()
            
            with open(geojson_path) as f:
                geojson_data = json.load(f)
            
            assert geojson_data['type'] == 'FeatureCollection'
            assert len(geojson_data['features']) == 1
            
            feature = geojson_data['features'][0]
            assert feature['geometry']['type'] == 'LineString'
            assert len(feature['geometry']['coordinates']) > 2  # Multi-point route