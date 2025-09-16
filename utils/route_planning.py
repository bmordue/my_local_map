"""
Route planning utilities for tourist map generation

Provides walking route optimization, accessibility options, 
and multi-modal transport integration capabilities.
"""

import math
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import subprocess
import tempfile
import os


class RoutePoint:
    """Represents a point in a route with coordinates and metadata"""
    
    def __init__(self, lat: float, lon: float, name: str = "", poi_type: str = ""):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.poi_type = poi_type
        
    def distance_to(self, other: 'RoutePoint') -> float:
        """Calculate distance to another point in kilometers"""
        R = 6371  # Earth radius in km
        
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(other.lat), math.radians(other.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'lat': self.lat,
            'lon': self.lon,
            'name': self.name,
            'poi_type': self.poi_type
        }


class Route:
    """Represents a complete route with metadata"""
    
    def __init__(self, name: str, route_type: str = "walking"):
        self.name = name
        self.route_type = route_type  # walking, cycling, accessible, multi-modal
        self.points: List[RoutePoint] = []
        self.total_distance = 0.0
        self.estimated_time = 0.0  # in hours
        self.accessibility_features: List[str] = []
        self.description = ""
        
    def add_point(self, point: RoutePoint):
        """Add a point to the route"""
        self.points.append(point)
        self._recalculate_metrics()
    
    def _recalculate_metrics(self):
        """Recalculate total distance and time"""
        if len(self.points) < 2:
            self.total_distance = 0.0
            self.estimated_time = 0.0
            return
            
        total_dist = 0.0
        for i in range(len(self.points) - 1):
            total_dist += self.points[i].distance_to(self.points[i + 1])
            
        self.total_distance = total_dist
        
        # Estimate time based on route type
        if self.route_type == "walking":
            self.estimated_time = total_dist / 4.0  # 4 km/h average walking speed
        elif self.route_type == "cycling":
            self.estimated_time = total_dist / 15.0  # 15 km/h average cycling speed
        elif self.route_type == "accessible":
            self.estimated_time = total_dist / 3.0  # Slower pace for accessibility
        else:
            self.estimated_time = total_dist / 4.0  # Default to walking speed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'route_type': self.route_type,
            'points': [p.to_dict() for p in self.points],
            'total_distance': self.total_distance,
            'estimated_time': self.estimated_time,
            'accessibility_features': self.accessibility_features,
            'description': self.description
        }


class RoutePlanner:
    """Main route planning engine"""
    
    def __init__(self, osm_data_dir: str, area_config: Dict[str, Any]):
        self.osm_data_dir = Path(osm_data_dir)
        self.area_config = area_config
        self.center_lat = area_config['center']['lat']
        self.center_lon = area_config['center']['lon']
        
    def extract_poi_points(self) -> List[RoutePoint]:
        """Extract points of interest from OSM data for route planning"""
        points = []
        points_shapefile = self.osm_data_dir / "points.shp"
        
        if not points_shapefile.exists():
            print("⚠ Points shapefile not found, cannot extract POIs")
            return points
            
        try:
            # Use ogrinfo to extract POI data
            result = subprocess.run([
                "ogrinfo", "-al", str(points_shapefile), "-geom=SUMMARY"
            ], capture_output=True, text=True, check=True)
            
            # Parse the output to extract POI information
            # This is a simplified version - in practice, you'd want more robust parsing
            lines = result.stdout.split('\n')
            current_poi = {}
            
            for line in lines:
                if 'POINT' in line and '(' in line:
                    # Extract coordinates from POINT (lon lat) format
                    coords_str = line.split('(')[1].split(')')[0]
                    lon, lat = map(float, coords_str.split())
                    
                    # Create a basic POI (this would be enhanced with real OSM tag parsing)
                    poi = RoutePoint(lat, lon, f"POI_{len(points)}", "attraction")
                    points.append(poi)
                    
        except subprocess.CalledProcessError as e:
            print(f"⚠ Error extracting POI points: {e}")
        except Exception as e:
            print(f"⚠ Error processing POI data: {e}")
            
        return points
    
    def create_tourist_route(self, route_config: Dict[str, Any]) -> Optional[Route]:
        """Create a tourist route connecting points of interest"""
        route_name = route_config.get('name', 'Tourist Route')
        route_type = route_config.get('type', 'walking')
        max_distance = route_config.get('max_distance_km', 5.0)
        
        # Extract POIs from the map data
        poi_points = self.extract_poi_points()
        
        if not poi_points:
            # Create a sample route if no POIs are found
            print("📍 Creating sample tourist route around Lumsden")
            return self._create_sample_lumsden_route(route_name, route_type)
        
        # Create route using nearest neighbor algorithm for simplicity
        route = Route(route_name, route_type)
        
        # Start from the center point
        start_point = RoutePoint(self.center_lat, self.center_lon, "Start", "start")
        route.add_point(start_point)
        
        # Find nearby POIs and create a circuit
        nearby_pois = [poi for poi in poi_points 
                      if start_point.distance_to(poi) <= max_distance]
        
        if nearby_pois:
            # Simple nearest neighbor routing
            current_point = start_point
            visited = set()
            
            while len(visited) < min(len(nearby_pois), 5):  # Limit to 5 POIs
                nearest_poi = None
                min_distance = float('inf')
                
                for poi in nearby_pois:
                    if id(poi) not in visited:
                        distance = current_point.distance_to(poi)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_poi = poi
                
                if nearest_poi:
                    route.add_point(nearest_poi)
                    visited.add(id(nearest_poi))
                    current_point = nearest_poi
                else:
                    break
            
            # Return to start to complete the circuit
            if len(route.points) > 1:
                route.add_point(start_point)
        
        route.description = f"Tourist circuit covering {len(route.points)-1} points of interest"
        return route
    
    def _create_sample_lumsden_route(self, route_name: str, route_type: str) -> Route:
        """Create a sample walking route around Lumsden"""
        route = Route(route_name, route_type)
        
        # Define some key points around Lumsden for a sample route
        route_points = [
            RoutePoint(57.3167, -2.8833, "Lumsden Village Center", "start"),
            RoutePoint(57.3200, -2.8800, "Village Hall", "building"),
            RoutePoint(57.3180, -2.8750, "Local Shop", "amenity"),
            RoutePoint(57.3150, -2.8780, "Church", "building"),
            RoutePoint(57.3130, -2.8820, "Scenic Viewpoint", "attraction"),
            RoutePoint(57.3167, -2.8833, "Lumsden Village Center", "end")
        ]
        
        for point in route_points:
            route.add_point(point)
        
        if route_type == "accessible":
            route.accessibility_features = [
                "Paved paths where possible",
                "Minimal elevation changes",
                "Rest points available"
            ]
        
        route.description = f"A circular {route_type} route around Lumsden village"
        return route
    
    def create_accessibility_route(self, route_config: Dict[str, Any]) -> Optional[Route]:
        """Create an accessibility-friendly route"""
        config = dict(route_config)
        config['type'] = 'accessible'
        config['max_distance_km'] = min(config.get('max_distance_km', 3.0), 3.0)
        
        route = self.create_tourist_route(config)
        if route:
            route.route_type = 'accessible'
            route.accessibility_features = [
                "Wheelchair accessible paths",
                "Minimal gradient",
                "Regular rest areas",
                "Well-maintained surfaces"
            ]
        return route


def process_route_planning(area_config: Dict[str, Any], osm_data_dir: str) -> Dict[str, Any]:
    """
    Main function to process route planning configuration and generate routes
    
    Args:
        area_config: Area configuration dictionary
        osm_data_dir: Directory containing OSM shapefiles
    
    Returns:
        Dictionary containing generated routes and metadata
    """
    route_config = area_config.get('route_planning', {})
    
    if not route_config.get('enabled', False):
        print("📍 Route planning disabled")
        return {}
    
    print("🗺️ Processing route planning...")
    
    planner = RoutePlanner(osm_data_dir, area_config)
    routes = []
    
    # Generate different types of routes based on configuration
    route_types = route_config.get('route_types', ['walking'])
    
    for route_type in route_types:
        if route_type == 'walking':
            route = planner.create_tourist_route({
                'name': 'Lumsden Walking Route',
                'type': 'walking',
                'max_distance_km': route_config.get('max_walking_distance', 5.0)
            })
        elif route_type == 'accessible':
            route = planner.create_accessibility_route({
                'name': 'Accessible Lumsden Route',
                'type': 'accessible',
                'max_distance_km': route_config.get('max_accessible_distance', 3.0)
            })
        elif route_type == 'cycling':
            route = planner.create_tourist_route({
                'name': 'Lumsden Cycling Route',
                'type': 'cycling',
                'max_distance_km': route_config.get('max_cycling_distance', 10.0)
            })
        else:
            continue
        
        if route:
            routes.append(route)
            print(f"✓ Generated {route.route_type} route: {route.name} "
                  f"({route.total_distance:.1f}km, {route.estimated_time:.1f}h)")
    
    # Save routes to GeoJSON for map integration
    if routes:
        routes_geojson = export_routes_to_geojson(routes)
        output_file = Path(osm_data_dir) / "tourist_routes.geojson"
        
        with open(output_file, 'w') as f:
            json.dump(routes_geojson, f, indent=2)
        
        print(f"✓ Routes exported to: {output_file}")
    
    return {
        'routes': [route.to_dict() for route in routes],
        'geojson_file': str(output_file) if routes else None,
        'total_routes': len(routes)
    }


def export_routes_to_geojson(routes: List[Route]) -> Dict[str, Any]:
    """Export routes to GeoJSON format for map visualization"""
    features = []
    
    for route in routes:
        if len(route.points) < 2:
            continue
            
        # Create LineString geometry from route points
        coordinates = [[point.lon, point.lat] for point in route.points]
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "name": route.name,
                "route_type": route.route_type,
                "distance_km": round(route.total_distance, 2),
                "estimated_time_hours": round(route.estimated_time, 2),
                "accessibility_features": route.accessibility_features,
                "description": route.description
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }