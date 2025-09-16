# Route Planning Demo Configuration

This document demonstrates how to configure different route planning options.

## Basic Configuration

To enable route planning, add the following to `config/areas.json`:

```json
{
  "lumsden": {
    "route_planning": {
      "enabled": true,
      "route_types": ["walking", "accessible"],
      "max_walking_distance": 5.0,
      "max_accessible_distance": 3.0,
      "max_cycling_distance": 10.0
    }
  }
}
```

## Route Types Available

1. **Walking Routes** (`"walking"`)
   - Standard walking pace (4 km/h)
   - Suitable for general tourists
   - Default maximum distance: 5 km

2. **Accessible Routes** (`"accessible"`)
   - Wheelchair-friendly paths
   - Slower walking pace (3 km/h)
   - Includes accessibility features
   - Default maximum distance: 3 km

3. **Cycling Routes** (`"cycling"`)
   - Cycling pace (15 km/h)
   - Longer distance routes
   - Default maximum distance: 10 km

## Style Customization

The route appearance can be customized in the configuration:

```json
{
  "route_planning": {
    "style": {
      "walking": {
        "color": "#0066CC",
        "width": 2.0,
        "opacity": 0.8,
        "dash_array": "5,2"
      },
      "accessible": {
        "color": "#00AA44",
        "width": 2.5,
        "opacity": 0.9,
        "dash_array": "10,5"
      },
      "cycling": {
        "color": "#CC6600",
        "width": 1.8,
        "opacity": 0.8,
        "dash_array": "3,3"
      }
    }
  }
}
```

## Disabling Route Planning

To disable route planning, set `"enabled": false` or omit the `route_planning` section entirely.

## Generated Output

When enabled, route planning creates:

1. **GeoJSON File**: `data/osm_data/tourist_routes.geojson`
   - Contains route coordinates and metadata
   - Can be used with other mapping software
   
2. **Map Overlay**: Routes appear on the generated map
   - Different colors/styles for each route type
   - Proper layering with other map elements

## Route Features

Each generated route includes:
- **Distance**: Total route length in kilometers
- **Estimated Time**: Based on route type and walking/cycling speed
- **Accessibility Features**: For accessible routes only
- **Description**: Human-readable route summary
- **Coordinates**: Full path coordinates for mapping

## Example Output

```json
{
  "name": "Lumsden Walking Route",
  "route_type": "walking",
  "distance_km": 1.92,
  "estimated_time_hours": 0.48,
  "accessibility_features": [],
  "description": "A circular walking route around Lumsden village"
}
```

This route planning system enhances the tourist map by providing practical route suggestions for visitors to the area.