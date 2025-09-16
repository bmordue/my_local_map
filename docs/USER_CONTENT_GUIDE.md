# User-Generated Content Integration Guide

This document provides comprehensive information about the Phase 3 user-generated content integration feature for the Lumsden Tourist Map.

## Overview

The user-generated content system allows community members to contribute reviews, local tips, photos, and POI updates to enhance the tourist map with local knowledge and real-time information.

## Key Features

### ✅ Implemented Features
- **User Reviews & Ratings**: Community feedback for attractions, accommodation, dining, and activities
- **Local Tips & Knowledge**: Insider information about access, seasonal conditions, safety, and photography
- **POI Updates**: Add new points of interest or correct existing information
- **Content Moderation**: Both manual and automated moderation systems
- **Community Statistics**: Track contributions and recognize top contributors
- **GeoJSON Integration**: Seamless integration with map rendering pipeline
- **Multiple Interfaces**: Command-line, interactive, and programmatic APIs

### 🔄 Framework Ready Features
- **Photo Submissions**: Database schema and processing pipeline implemented (needs file storage)
- **Multi-language Support**: Database structure supports internationalization
- **Advanced Analytics**: Foundation for analyzing contribution patterns

## Architecture

```
User Input → Content Validation → Database Storage → Moderation → Map Integration
     ↓              ↓                    ↓              ↓             ↓
  - Reviews     - Data types        - SQLite DB    - Manual     - GeoJSON Export
  - Tips        - Required fields   - User tables  - Automated  - Style Integration  
  - POI Info    - Coordinates       - Status       - Quality    - Map Rendering
  - Photos      - Text length       - Timestamps   - Control    - Legend Updates
```

## Database Schema

### User Reviews (`user_reviews`)
- POI association and type
- User information (name, email)
- Rating (1-5 scale)
- Review text and visit date
- Moderation status and notes

### User Photos (`user_photos`)
- POI association and type
- User information
- Photo path and caption
- Upload and taken timestamps
- Moderation workflow

### POI Updates (`user_poi_updates`)
- Update type (new, update, correction)
- Complete POI information
- Geographic coordinates
- Contact and timing information
- Submission tracking

### Local Tips (`user_tips`)
- Category-based organization
- Optional POI association
- Community voting system
- Knowledge categorization

## Usage Examples

### Command-Line Interface

```bash
# Generate sample content for demonstration
python3 user_content_cli.py generate-sample

# Submit a review
python3 user_content_cli.py submit-review \
  --poi-id 1 --poi-type attraction \
  --user-name "Sarah M." --rating 5 \
  --review-text "Absolutely stunning castle with incredible views!"

# Add a new POI
python3 user_content_cli.py submit-poi \
  --poi-type dining --update-type new \
  --user-name "Local Resident" \
  --name "Highland Café" \
  --description "Cozy local café with homemade cakes" \
  --lat 57.3180 --lon -2.8800

# Share local knowledge
python3 user_content_cli.py submit-tip \
  --category photography \
  --user-name "Local Photographer" \
  --tip-text "Best photos taken in morning light from the southeast hill"

# Moderate content
python3 user_content_cli.py moderate \
  --table user_reviews --content-id 1 \
  --status approved --notes "High quality review"

# Run automated moderation
python3 user_content_cli.py auto-moderate

# View community statistics
python3 user_content_cli.py stats

# Export for map integration
python3 user_content_cli.py export
```

### Interactive Interface

```bash
# Launch interactive submission interface
python3 user_content_cli.py interactive

# Launch interactive moderation interface
python3 user_content_cli.py moderate-interactive
```

### Programmatic API

```python
from utils.user_content import UserContentManager
from utils.moderation import ContentModerator

# Initialize systems
manager = UserContentManager()
moderator = ContentModerator()

# Submit content
review_id = manager.submit_review(
    poi_id=1, poi_type='attraction',
    user_name='Tourist', user_email='tourist@example.com',
    rating=5, review_text='Amazing place to visit!'
)

# Moderate content
success = manager.moderate_content('user_reviews', review_id, 'approved')

# Export for mapping
geojson = manager.export_user_content_to_geojson()

# Get statistics
stats = manager.get_content_statistics()
```

## Content Moderation

### Manual Moderation
- Review interface for pending submissions
- Status management (pending → approved/rejected)
- Moderation notes and feedback
- Bulk operations for efficiency

### Automated Moderation
- Content safety checks
- Length and quality validation
- Spam and inappropriate content detection
- Configurable strictness levels

### Quality Controls
- Rating validation (1-5 scale)
- Required field checking
- Geographic boundary validation
- Duplicate content detection

## Map Integration

### GeoJSON Export
User-contributed POIs are automatically exported to GeoJSON format and integrated into the map generation pipeline:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-2.88, 57.318]
      },
      "properties": {
        "name": "The Glenlivet Café",
        "description": "Cozy local café...",
        "poi_type": "dining",
        "contributor": "Local Resident",
        "data_source": "user_generated"
      }
    }
  ]
}
```

### Map Rendering
- User POIs are included in map rendering
- Special styling for user-contributed content
- Attribution to community contributors
- Integration with existing POI categories

## Community Features

### Top Contributors
- Recognition system for active community members
- Contribution counting across all content types
- Public acknowledgment in statistics

### Content Statistics
- Real-time tracking of submissions
- Moderation workflow metrics
- Community engagement analytics

## Quality Assurance

### Data Validation
- **Coordinate Validation**: Ensure points fall within map bounds
- **Required Fields**: Verify essential information is provided
- **Format Checking**: Validate phone numbers, URLs, dates
- **Content Review**: Check for appropriateness and accuracy

### Moderation Workflow
1. **Submission**: Users submit content through any interface
2. **Initial Validation**: Automatic checks for basic requirements
3. **Moderation Queue**: Content enters pending status
4. **Review Process**: Manual or automated moderation
5. **Decision**: Approve, reject, or request modifications
6. **Integration**: Approved content exported for map rendering

## Technical Implementation

### Database Management
- SQLite database for development and small-scale deployment
- Extensible to PostgreSQL/PostGIS for larger installations
- Full schema migration support
- Data backup and recovery procedures

### Security Considerations
- Input sanitization and validation
- SQL injection prevention
- Content screening for inappropriate material
- User attribution and contact validation

### Performance Optimization
- Indexed database queries
- Efficient GeoJSON generation
- Batch processing for large datasets
- Caching strategies for frequently accessed data

## Future Enhancements

### Phase 4 Considerations
- **Web Interface**: Browser-based content submission
- **Mobile App**: GPS-enabled contribution system
- **Real-time Sync**: Live updates between contributors
- **Advanced Analytics**: Contribution pattern analysis
- **API Integration**: External platform connections
- **Multilingual Support**: Content in multiple languages

### Community Growth
- **Contributor Onboarding**: Guided introduction process
- **Expertise Recognition**: Subject matter expert designation
- **Seasonal Campaigns**: Targeted content collection drives
- **Local Partnerships**: Integration with tourism boards and businesses

## Testing

Comprehensive test suite included:

```bash
# Run user content tests
PYTHONPATH=. python3 tests/test_user_content.py

# Test specific functionality
python3 -c "from tests.test_user_content import TestUserContentManager; 
           import unittest; unittest.main(argv=[''], module=TestUserContentManager, exit=False)"
```

## Troubleshooting

### Common Issues

**Database Permission Errors**
- Ensure write permissions to `enhanced_data/` directory
- Check SQLite database file permissions

**GeoJSON Export Issues**
- Verify approved content exists with coordinates
- Check area configuration boundaries

**Moderation Problems**
- Confirm content status transitions
- Validate moderation table names

**Integration Failures**
- Test individual components separately
- Check map generation pipeline integration

### Debugging

```bash
# Enable verbose logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from utils.user_content import UserContentManager
manager = UserContentManager()
stats = manager.get_content_statistics()
print(stats)
"
```

## Contributing

Community contributions to the user-generated content system are welcome:

1. **Content Submission**: Use the provided interfaces to add local knowledge
2. **Code Contributions**: Submit pull requests for system improvements
3. **Documentation**: Help improve this documentation
4. **Testing**: Report bugs and edge cases
5. **Feature Requests**: Suggest enhancements for community needs

---

The user-generated content integration represents a significant step toward creating a truly community-driven tourist resource for the Lumsden area, combining the reliability of OpenStreetMap data with the richness of local knowledge and real-time community input.