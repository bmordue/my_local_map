# Real-time Information Integration Documentation

## Overview

The Lumsden Tourist Map Generator now includes real-time information integration as part of Phase 2 development. This feature adds live weather conditions and local events to enhance the tourist experience with up-to-date information.

## Features Implemented

### ✅ Weather Information
- **Current Conditions**: Temperature, weather condition, humidity, wind speed and direction
- **Service Integration**: Configurable weather service (currently using mock data for demo)
- **Visual Display**: Weather icon and information overlay on map
- **Legend Integration**: Current weather shown in map legend

### ✅ Events Information  
- **Local Events**: Community events, cultural activities, sports events
- **Event Details**: Title, description, location, dates, organizer, admission
- **Filtering**: By proximity (configurable radius) and date range (upcoming events)
- **Visual Display**: Category-specific icons on map with event labels

### ✅ Data Management
- **Caching System**: 1-hour data cache to reduce API calls
- **Fallback Mode**: Graceful degradation when real-time services unavailable
- **GeoJSON Export**: Real-time data exported for mapping integration
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Configuration

Real-time features are configured in `config/areas.json`:

```json
{
  "lumsden": {
    "realtime": {
      "enabled": true,
      "weather": {
        "enabled": true,
        "display": "legend",
        "api_key": null
      },
      "events": {
        "enabled": true,
        "display": "overlay",
        "radius_km": 15,
        "max_events": 5
      },
      "cache_duration_hours": 1,
      "fallback_mode": true
    }
  }
}
```

### Configuration Options

- **enabled**: Master switch for real-time features
- **weather.enabled**: Enable weather information display
- **weather.display**: Where to show weather ("legend" or "overlay")
- **weather.api_key**: API key for weather service (optional)
- **events.enabled**: Enable events information display
- **events.display**: Where to show events ("overlay" or "legend")  
- **events.radius_km**: Search radius for local events
- **events.max_events**: Maximum number of events to display
- **cache_duration_hours**: How long to cache real-time data
- **fallback_mode**: Continue with static data if real-time fails

## Technical Architecture

### Data Sources
1. **Weather Service** (`WeatherService` class)
   - Mock data service for demonstration
   - Extensible for real API integration (OpenWeatherMap, Met Office)
   - Realistic Scottish weather patterns

2. **Events Service** (`EventsService` class)
   - Mock local events data
   - Extensible for real API integration (VisitScotland, local authorities)
   - Date filtering and proximity-based selection

### Integration Points
1. **Main Generator** (`map_generator.py`)
   - Real-time data fetching integrated into generation pipeline
   - Passes data to style builder and legend system

2. **Style System** (`style_builder.py`)
   - Dynamic inclusion of real-time layers in Mapnik XML
   - Conditional rendering based on data availability

3. **Legend System** (`legend.py`)
   - Enhanced to display weather and events summary
   - Dynamic legend sizing based on content

### File Structure
```
utils/
├── realtime_data.py      # Core real-time data services
├── style_builder.py      # Extended for real-time overlays  
├── legend.py            # Enhanced for real-time display
└── config.py            # Configuration loading

data/
├── osm_data/
│   ├── realtime_weather.geojson   # Weather overlay data
│   └── realtime_events.geojson    # Events overlay data
└── realtime_cache/
    └── realtime_data.json         # Cached real-time data

styles/
├── tourist.xml          # Enhanced template with real-time layers
└── tourist_map_style.xml # Generated style with real-time data
```

## Generated Overlays

### Weather GeoJSON
```json
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": [-2.8833, 57.3167]
    },
    "properties": {
      "type": "weather",
      "temperature": 15,
      "condition": "Clear",
      "description": "clear sky",
      "display_text": "Clear 15°C"
    }
  }]
}
```

### Events GeoJSON
```json
{
  "type": "FeatureCollection", 
  "features": [{
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": [-2.8825, 57.3175]
    },
    "properties": {
      "type": "event",
      "title": "Lumsden Village Fête",
      "category": "community",
      "date_start": "2025-09-21T14:00:00",
      "location_name": "Lumsden Village Green",
      "admission": "Free"
    }
  }]
}
```

## Usage Examples

### Basic Usage
```bash
# Generate map with real-time information
python3 map_generator.py

# Real-time features enabled by default when configured
```

### Configuration Examples
```python
# Disable real-time features
config["realtime"]["enabled"] = False

# Weather only (no events)
config["realtime"]["events"]["enabled"] = False

# Increase event search radius
config["realtime"]["events"]["radius_km"] = 25
```

## Production Considerations

### API Integration
For production deployment, replace mock services with real APIs:

```python
# Weather Service - OpenWeatherMap example
def _get_openweather_data(self, lat, lon):
    url = f"{self.openweather_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
    response = requests.get(url)
    return response.json()

# Events Service - VisitScotland API example  
def get_visitscotland_events(self, lat, lon, radius_km):
    url = f"https://api.visitscotland.com/events?lat={lat}&lon={lon}&radius={radius_km}"
    response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
    return response.json()
```

### Performance Optimization
- **Caching**: Implemented with configurable duration
- **Async Processing**: Consider async requests for multiple APIs
- **Rate Limiting**: Implement rate limiting for API calls
- **Error Recovery**: Graceful fallback to cached or static data

### Monitoring and Logging
- Real-time data fetch success/failure rates
- API response times and reliability
- Cache hit rates and effectiveness
- User engagement with real-time features

## Testing and Validation

The implementation includes comprehensive validation:

### Validation Script
```bash
# Run built-in validation
python3 validate_realtime.py

# Expected output:
# ✅ VALIDATION RESULTS: 6 passed, 0 failed
# 🎉 All real-time information features are working correctly!
```

### Manual Verification
1. **Weather Display**: Check legend shows current weather
2. **Events Overlay**: Verify event icons appear on map
3. **Data Freshness**: Confirm timestamps are current
4. **Fallback Behavior**: Test with disabled APIs
5. **Configuration**: Test various config combinations

## Future Enhancements

### Phase 3 Roadmap
- **Traffic Information**: Road conditions and closures
- **Live Transportation**: Bus schedules and delays
- **Seasonal Information**: Trail conditions, opening hours
- **Social Integration**: User-generated content and reviews
- **Push Notifications**: Event reminders and weather alerts

### API Integrations Planned
- **Met Office DataPoint**: UK weather data
- **VisitScotland Open API**: Official tourism events
- **Traffic Scotland**: Road condition updates
- **Traveline Scotland**: Public transport data
- **Aberdeen City/Aberdeenshire Council**: Local authority events

## Error Handling

The system includes comprehensive error handling:

### Network Issues
- Graceful fallback to cached data
- Clear user messaging about data availability
- Continuation with static map generation

### Data Quality
- Validation of API responses
- Filtering of invalid or expired data
- Default values for missing information

### Configuration Errors
- Validation of configuration settings
- Helpful error messages for misconfigurations
- Safe defaults for missing config values

## Support and Troubleshooting

### Common Issues
1. **No real-time data**: Check network connectivity and API keys
2. **Outdated information**: Clear cache directory to force refresh
3. **Missing overlays**: Verify configuration settings are correct
4. **Performance issues**: Adjust cache duration and API timeouts

### Debug Information
Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This documentation provides comprehensive coverage of the real-time information integration feature, supporting both current usage and future development.