"""Real-time data integration for weather and events"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherService:
    """Weather data service using Met Office API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://datapoint.metoffice.gov.uk/public/data"
        # Fallback to OpenWeatherMap if Met Office API not available
        self.openweather_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get current weather data for given coordinates"""
        try:
            # Try OpenWeatherMap first (free tier available)
            return self._get_openweather_data(lat, lon)
        except Exception as e:
            logger.warning(f"Weather data unavailable: {e}")
            return self._get_mock_weather_data(lat, lon)
    
    def _get_openweather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get weather data from OpenWeatherMap (requires API key in production)"""
        # For demo purposes, return mock data since we don't have API keys in sandbox
        return self._get_mock_weather_data(lat, lon)
    
    def _get_mock_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Generate realistic mock weather data for Aberdeenshire"""
        import random
        
        # Typical Scottish weather conditions
        conditions = [
            {"main": "Partly Cloudy", "description": "partly cloudy", "temp": 12},
            {"main": "Overcast", "description": "overcast clouds", "temp": 10},  
            {"main": "Light Rain", "description": "light rain", "temp": 9},
            {"main": "Clear", "description": "clear sky", "temp": 15},
            {"main": "Cloudy", "description": "few clouds", "temp": 11}
        ]
        
        condition = random.choice(conditions)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "current": {
                "temperature": condition["temp"],
                "condition": condition["main"],
                "description": condition["description"],
                "humidity": random.randint(60, 85),
                "wind_speed": random.randint(5, 20),
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "visibility": random.randint(8, 15),
                "timestamp": datetime.now().isoformat()
            },
            "forecast": self._generate_mock_forecast()
        }
    
    def _generate_mock_forecast(self) -> List[Dict[str, Any]]:
        """Generate 3-day weather forecast"""
        forecast = []
        base_temps = [11, 13, 9]  # Typical Scottish temperatures
        conditions = ["Partly Cloudy", "Light Rain", "Overcast"]
        
        for i in range(3):
            date = datetime.now() + timedelta(days=i+1)
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "temperature_max": base_temps[i] + 3,
                "temperature_min": base_temps[i] - 2,
                "condition": conditions[i],
                "description": f"{conditions[i].lower()}"
            })
        
        return forecast


class EventsService:
    """Events data service for local tourism events"""
    
    def __init__(self):
        self.visitscotland_url = "https://www.visitscotland.com/api"  # Hypothetical
        self.aberdeenshire_url = "https://www.aberdeenshire.gov.uk/api"  # Hypothetical
        
    def get_local_events(self, lat: float, lon: float, radius_km: float = 10) -> List[Dict[str, Any]]:
        """Get local events within specified radius"""
        try:
            # For demo purposes, return mock data since APIs may not be available
            return self._get_mock_events_data(lat, lon, radius_km)
        except Exception as e:
            logger.warning(f"Events data unavailable: {e}")
            return []
    
    def _get_mock_events_data(self, lat: float, lon: float, radius_km: float) -> List[Dict[str, Any]]:
        """Generate realistic mock events data for the Lumsden area"""
        # Generate dynamic dates for upcoming events
        base_date = datetime.now()
        future_dates = [
            base_date + timedelta(days=5),  # 5 days from now
            base_date + timedelta(days=12), # 12 days from now  
            base_date + timedelta(days=20)  # 20 days from now
        ]
        
        events = [
            {
                "id": "evt_001",
                "title": "Lumsden Village Fête",
                "description": "Annual village fête with traditional games, local food, and craft stalls",
                "location": {
                    "name": "Lumsden Village Green",
                    "lat": 57.3175,
                    "lon": -2.8825,
                    "address": "Village Green, Lumsden, AB54 4JN"
                },
                "date_start": future_dates[0].strftime("%Y-%m-%dT14:00:00"),
                "date_end": future_dates[0].strftime("%Y-%m-%dT18:00:00"),
                "category": "community",
                "organizer": "Lumsden Community Council",
                "website": "https://lumsdenvillage.org/events",
                "admission": "Free",
                "accessibility": "Wheelchair accessible"
            },
            {
                "id": "evt_002", 
                "title": "Guided Historical Walk",
                "description": "Explore Lumsden's fascinating history with local historian",
                "location": {
                    "name": "Lumsden Parish Church",
                    "lat": 57.3170,
                    "lon": -2.8830,
                    "address": "Church Street, Lumsden"
                },
                "date_start": future_dates[1].strftime("%Y-%m-%dT10:00:00"),
                "date_end": future_dates[1].strftime("%Y-%m-%dT12:00:00"),
                "category": "cultural",
                "organizer": "Aberdeenshire Heritage Trust",
                "admission": "£5 adults, children free",
                "booking_required": True
            },
            {
                "id": "evt_003",
                "title": "Highland Games",
                "description": "Traditional Scottish Highland Games with caber tossing, hammer throw, and Highland dancing",
                "location": {
                    "name": "Rhynie Sports Field",
                    "lat": 57.3450,
                    "lon": -2.8900,
                    "address": "Rhynie, AB54 4LA"
                },
                "date_start": future_dates[2].strftime("%Y-%m-%dT11:00:00"),
                "date_end": future_dates[2].strftime("%Y-%m-%dT17:00:00"),
                "category": "sport",
                "organizer": "Rhynie Highland Games Association",
                "admission": "£8 adults, £3 children",
                "parking": "Available on site"
            }
        ]
        
        # Filter events by proximity and date (within next 30 days)
        now = datetime.now()
        filtered_events = []
        
        for event in events:
            event_date = datetime.fromisoformat(event["date_start"].replace("Z", "+00:00").replace("T", " ").split("+")[0])
            
            # Check if event is within next 30 days
            if now <= event_date <= now + timedelta(days=30):
                # Simple distance check (not precise but adequate for demo)
                event_lat = event["location"]["lat"]
                event_lon = event["location"]["lon"]
                
                # Rough distance calculation
                lat_diff = abs(lat - event_lat)
                lon_diff = abs(lon - event_lon)
                approx_distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough conversion
                
                if approx_distance_km <= radius_km:
                    # Add distance and status info
                    event["distance_km"] = round(approx_distance_km, 1)
                    event["status"] = "upcoming"
                    filtered_events.append(event)
        
        return filtered_events


class RealTimeDataManager:
    """Manager class for coordinating real-time data services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weather_service = WeatherService(config.get("weather_api_key"))
        self.events_service = EventsService()
        self.cache_dir = Path("data/realtime_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_realtime_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get all real-time data for map area"""
        data = {
            "weather": None,
            "events": [],
            "timestamp": datetime.now().isoformat(),
            "location": {"lat": lat, "lon": lon}
        }
        
        # Get weather data
        print("📡 Fetching weather information...")
        weather_data = self.weather_service.get_weather_data(lat, lon)
        if weather_data:
            data["weather"] = weather_data
            print(f"   ✓ Current weather: {weather_data['current']['condition']} ({weather_data['current']['temperature']}°C)")
        
        # Get events data
        print("📅 Fetching local events...")
        events_data = self.events_service.get_local_events(lat, lon, radius_km=15)
        if events_data:
            data["events"] = events_data
            print(f"   ✓ Found {len(events_data)} upcoming events")
            for event in events_data[:3]:  # Show first 3 events
                event_date = datetime.fromisoformat(event["date_start"].replace("T", " "))
                print(f"     • {event['title']} - {event_date.strftime('%B %d')}")
        
        # Cache the data
        self._cache_data(data)
        
        return data
    
    def _cache_data(self, data: Dict[str, Any]):
        """Cache real-time data with timestamp"""
        cache_file = self.cache_dir / "realtime_data.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Real-time data cached to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache data: {e}")
    
    def get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get cached data if recent (less than 1 hour old)"""
        cache_file = self.cache_dir / "realtime_data.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if cache is recent (within 1 hour)
            cache_time = datetime.fromisoformat(data.get("timestamp", ""))
            if datetime.now() - cache_time > timedelta(hours=1):
                return None
            
            return data
            
        except Exception as e:
            logger.warning(f"Failed to read cached data: {e}")
            return None


def create_realtime_geojson(realtime_data: Dict[str, Any], output_dir: Path) -> List[str]:
    """Create GeoJSON files for real-time data"""
    output_files = []
    
    # Create weather data GeoJSON
    if realtime_data.get("weather"):
        weather_geojson = create_weather_geojson(realtime_data["weather"])
        weather_file = output_dir / "realtime_weather.geojson"
        
        with open(weather_file, 'w') as f:
            json.dump(weather_geojson, f, indent=2)
        output_files.append(str(weather_file))
        print(f"   ✓ Created weather overlay: {weather_file}")
    
    # Create events data GeoJSON
    events_list = realtime_data.get("events", [])
    if events_list:
        events_geojson = create_events_geojson(events_list)
        events_file = output_dir / "realtime_events.geojson"
        
        with open(events_file, 'w') as f:
            json.dump(events_geojson, f, indent=2)
        output_files.append(str(events_file))
        print(f"   ✓ Created events overlay: {events_file}")
    else:
        print(f"   • No current events to display")
    
    return output_files


def create_weather_geojson(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create GeoJSON for weather information"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [weather_data["location"]["lon"], weather_data["location"]["lat"]]
                },
                "properties": {
                    "type": "weather",
                    "temperature": weather_data["current"]["temperature"],
                    "condition": weather_data["current"]["condition"],
                    "description": weather_data["current"]["description"],
                    "humidity": weather_data["current"]["humidity"],
                    "wind_speed": weather_data["current"]["wind_speed"],
                    "wind_direction": weather_data["current"]["wind_direction"],
                    "visibility": weather_data["current"]["visibility"],
                    "timestamp": weather_data["current"]["timestamp"],
                    "display_text": f"{weather_data['current']['condition']} {weather_data['current']['temperature']}°C"
                }
            }
        ]
    }


def create_events_geojson(events_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create GeoJSON for events information"""
    features = []
    
    for event in events_data:
        feature = {
            "type": "Feature", 
            "geometry": {
                "type": "Point",
                "coordinates": [event["location"]["lon"], event["location"]["lat"]]
            },
            "properties": {
                "type": "event",
                "title": event["title"],
                "description": event.get("description", ""),
                "category": event.get("category", "general"),
                "date_start": event["date_start"],
                "date_end": event["date_end"],
                "location_name": event["location"]["name"],
                "organizer": event.get("organizer", ""),
                "admission": event.get("admission", ""),
                "distance_km": event.get("distance_km", 0),
                "status": event.get("status", "unknown"),
                "booking_required": event.get("booking_required", False)
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }