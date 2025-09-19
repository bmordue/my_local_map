# My Local Map - Brownfield Product Requirements Document

Version: 1.0
Date: 2025-09-18
Author: Product Management

## 1. Executive Summary

### 1.1 Project Overview
"My Local Map" is an existing map generation system that creates high-quality, printable tourist maps for the Lumsden area of Aberdeenshire, Scotland. The system combines OpenStreetMap data with enhanced local tourism information to produce detailed A3 maps suitable for printing and distribution.

### 1.2 Enhancement Goals
This brownfield project aims to enhance the existing system with several key improvements:
- Expand coverage to additional areas in Aberdeenshire and beyond
- Integrate higher quality data sources including Ordnance Survey data
- Improve user experience with web and mobile interfaces
- Add advanced features like route planning and real-time information
- Maintain the system's core strength of producing high-quality printable maps

### 1.3 Success Metrics
- Increase map coverage area by 500%
- Improve map update frequency to monthly
- Achieve 99.5% system uptime
- Reduce map generation time by 30%
- Expand user base to 1000 monthly active users

## 2. Current System Overview

### 2.1 System Description
The current system generates printable A3 tourist maps (297×420mm at 300 DPI) for the Lumsden area using:
- OpenStreetMap data acquired via Overpass API
- Enhanced local tourism data stored in SQLite
- Synthetic elevation data for hillshading and contour generation
- Mapnik for map rendering
- GDAL/OGR for geospatial data processing

### 2.2 Key Features
- High-quality printable A3 maps
- Hillshading and contour line visualization
- Enhanced tourism data including attractions, accommodations, and activities
- SVG icon system for points of interest
- Template-based styling with Mapnik XML
- Reproducible development environment with Nix

### 2.3 Technology Stack
- Python 3.12
- Mapnik rendering engine
- GDAL/OGR geospatial tools
- SQLite database
- NumPy for elevation processing
- requests for HTTP operations
- Pillow for image processing

### 2.4 Current Limitations
- Limited to single geographic area (Lumsden)
- Synthetic elevation data only (no real DEM sources)
- Command-line only interface
- No web or mobile access
- No real-time information integration
- No route planning capabilities

## 3. Stakeholder Analysis

### 3.1 Primary Users
1. **Local Tourists** - Visitors to the area seeking information about attractions, accommodations, and activities
2. **Local Businesses** - Tourism-related businesses that benefit from increased visitor traffic
3. **Community Organizations** - Groups promoting local tourism and outdoor activities
4. **Print Distribution Points** - Hotels, visitor centers, and shops that display and distribute maps

### 3.2 Secondary Users
1. **System Administrators** - Individuals responsible for maintaining and updating the map system
2. **Content Curators** - Personnel managing the enhanced tourism database
3. **Developers** - Technical staff maintaining and extending the system

### 3.3 Business Stakeholders
1. **Local Government** - Municipalities interested in promoting tourism
2. **Tourism Boards** - Regional organizations promoting visitor activities
3. **Funding Organizations** - Entities providing financial support for tourism initiatives

## 4. Functional Requirements

### 4.1 Current Capabilities
- Generate printable A3 tourist maps with 300 DPI resolution
- Include hillshading and contour lines for topographic information
- Display 25+ categories of points of interest
- Support SVG icons for visual representation of amenities
- Process OpenStreetMap data via Overpass API queries
- Convert OSM data to shapefiles for Mapnik rendering
- Provide template-based Mapnik XML styling system
- Generate map legends with categorized items
- Offer reproducible development environment with Nix

### 4.2 Enhanced Capabilities (Planned)
- Multi-area coverage (extend beyond Lumsden to entire Aberdeenshire)
- Integration with Ordnance Survey data sources
- Real-time information feeds (weather, trail conditions, event schedules)
- Web interface for map browsing and printing
- Mobile app for on-device map access
- Route planning and navigation features
- User feedback and rating system
- Social sharing capabilities
- Custom map creation tools

## 5. Non-Functional Requirements

### 5.1 Performance
- Map generation time: Under 5 minutes for A3 maps
- Web interface response time: Under 2 seconds for standard requests
- Mobile app startup time: Under 3 seconds
- Map rendering performance: 60 FPS for pan/zoom operations

### 5.2 Scalability
- Support up to 1000 concurrent web users
- Handle 100 concurrent map generation requests
- Store and process data for 50+ geographic areas
- Scale to 10GB+ of geospatial data

### 5.3 Reliability
- System uptime: 99.5% availability
- Data backup and recovery procedures
- Automated error detection and reporting
- Graceful degradation during service outages

### 5.4 Security
- Secure API access with authentication
- Protection against malicious map generation requests
- Regular security audits and updates
- Data privacy compliance for user information

### 5.5 Usability
- Intuitive web interface with clear navigation
- Mobile-responsive design for all device sizes
- Accessible design compliant with WCAG 2.1 AA standards
- Comprehensive user documentation and help system

### 5.6 Maintainability
- Modular architecture for easy feature updates
- Comprehensive test suite with 80%+ code coverage
- Clear documentation for all system components
- Automated deployment and update procedures

## 6. User Stories

### 6.1 Map User Stories
1. As a tourist, I want to view a map of the Lumsden area so that I can plan my visit.
2. As a tourist, I want to find nearby restaurants on the map so that I can choose where to eat.
3. As a tourist, I want to see walking trails on the map so that I can plan outdoor activities.
4. As a tourist, I want to print a map at home so that I can take it with me during my visit.
5. As a tourist, I want to view the map on my mobile phone so that I can navigate while out.
6. As a tourist, I want to find accommodation options on the map so that I can book a place to stay.
7. As a tourist, I want to see topographic information on the map so that I can understand the terrain.

### 6.2 Enhanced System User Stories
1. As a tourist, I want to view maps of multiple areas in Aberdeenshire so that I can explore the region.
2. As a tourist, I want to plan a walking route between points of interest so that I can efficiently visit attractions.
3. As a tourist, I want to see real-time weather information on the map so that I can plan accordingly.
4. As a tourist, I want to share interesting locations with friends so that I can recommend places to visit.
5. As a business owner, I want to add my business to the map so that I can attract more customers.
6. As a system administrator, I want to update map data monthly so that the information remains current.
7. As a content curator, I want to manage tourism information in a database so that I can easily update details.

## 7. Technical Requirements

### 7.1 Architecture Requirements
- Maintain existing modular architecture with clear separation of concerns
- Implement microservices for new web/mobile features
- Ensure backward compatibility with existing map generation system
- Design for horizontal scaling of web services
- Implement robust data caching for improved performance

### 7.2 Technology Requirements
- Continue using Python 3.12 for core map generation
- Adopt Django/Flask for web interface development
- Use React Native for mobile app development
- Integrate with Ordnance Survey API for premium data
- Implement PostgreSQL for enhanced data storage
- Use Redis for caching and session management
- Deploy with Docker containers for consistent environments
- Use Nginx as reverse proxy and load balancer

### 7.3 Data Model Requirements
- Extend current SQLite schema for enhanced tourism data
- Implement user account system for web/mobile access
- Design route planning data structures
- Create real-time information integration framework
- Develop feedback and rating data models
- Design custom map creation storage schemas

### 7.4 Integration Requirements
- Integrate with Ordnance Survey data APIs
- Connect to weather services for real-time information
- Implement social media sharing APIs
- Provide export options for GPX/KML route files
- Enable payment processing for premium features
- Integrate with Google Maps/Apple Maps for navigation

## 8. Implementation Roadmap

### 8.1 Phase 1: Core Enhancements (Months 1-4)
- Expand geographic coverage to 10+ areas in Aberdeenshire
- Integrate real DEM data sources (SRTM, OS Terrain 50)
- Implement web interface for map browsing
- Add basic route planning features
- Improve map generation performance

### 8.2 Phase 2: Advanced Features (Months 5-8)
- Develop mobile app for iOS and Android
- Integrate real-time information feeds
- Implement user accounts and personalization
- Add social sharing capabilities
- Enhance route planning with elevation profiles

### 8.3 Phase 3: Premium Features (Months 9-12)
- Implement custom map creation tools
- Add augmented reality features for mobile
- Integrate with booking systems for accommodations/activities
- Provide analytics dashboard for administrators
- Enable offline map downloads for mobile

## 9. Success Metrics

### 9.1 User Metrics
- 1000 monthly active users on web interface
- 500 monthly active users on mobile app
- 4.5+ average user rating
- 30% month-over-month user growth

### 9.2 System Metrics
- 99.5% system uptime
- Under 2 second average web response time
- Under 5 minute average map generation time
- 95% successful map generation rate

### 9.3 Business Metrics
- 25% increase in local tourism business inquiries
- 500 businesses listed in the system
- 1000 user-generated routes created monthly
- 10000 map downloads per month

## 10. Risks and Mitigation

### 10.1 Technical Risks
- **Risk**: Integration with Ordnance Survey APIs may be complex
  **Mitigation**: Start with limited data sets and gradually expand
- **Risk**: Mobile app development may exceed timeline
  **Mitigation**: Develop core features first, add enhancements incrementally
- **Risk**: Performance issues with increased data volume
  **Mitigation**: Implement robust caching and optimize data processing

### 10.2 Business Risks
- **Risk**: Limited adoption of new web/mobile features
  **Mitigation**: Conduct user research and implement feedback loops
- **Risk**: Competition from established map providers
  **Mitigation**: Focus on hyper-local content and community engagement
- **Risk**: Data licensing costs may exceed budget
  **Mitigation**: Start with free data sources and transition gradually

### 10.3 Operational Risks
- **Risk**: System administrator turnover may affect maintenance
  **Mitigation**: Document processes thoroughly and cross-train team members
- **Risk**: Data quality issues may affect map accuracy
  **Mitigation**: Implement data validation and verification procedures

## 11. Budget and Resource Requirements

### 11.1 Development Resources
- 2 Full-stack developers (12 months)
- 1 Mobile developer (8 months)
- 1 UX/UI designer (6 months)
- 1 DevOps engineer (4 months)
- 1 Project manager (12 months)

### 11.2 Technology Costs
- Ordnance Survey API licensing: £5,000/year
- Cloud hosting (AWS/Azure): £3,000/year
- Development tools and software licenses: £2,000/year
- Testing and QA services: £2,000

### 11.3 Operational Costs
- System administration: £2,000/year
- Data updates and maintenance: £1,000/year
- Marketing and promotion: £3,000

## 12. Appendices

### 12.1 File Structure
```
/home/ben/Projects/mine/my_local_map/
├── config/
│   ├── areas.json          # Geographic area configurations
│   └── output_formats.json # Output format specifications
├── data/                   # Generated data (git-ignored)
├── icons/                  # SVG icons for POIs
├── styles/                 # Mapnik XML style templates
├── utils/                  # Utility modules
├── web/                    # New web interface (planned)
├── mobile/                 # New mobile app (planned)
├── map_generator.py        # Main map generation script
└── requirements.txt        # Python dependencies
```

### 12.2 Feature Categories
The enhanced system will support the following point of interest categories:
1. Accommodations (Hotels, B&Bs, Campsites)
2. Dining (Restaurants, Cafes, Pubs)
3. Attractions (Museums, Historic Sites, Nature Spots)
4. Outdoor Activities (Walking Trails, Cycling Routes, Fishing)
5. Shopping (Local Shops, Markets, Souvenirs)
6. Services (ATMs, Pharmacies, Gas Stations)
7. Transportation (Bus Stops, Train Stations, Parking)
8. Emergency Services (Hospitals, Police, Fire)
9. Entertainment (Theatres, Cinemas, Sports Venues)
10. Education (Libraries, Schools, Colleges)

### 12.3 Data Sources
1. **Primary**: OpenStreetMap via Overpass API
2. **Enhanced**: Custom SQLite database with local tourism information
3. **Premium**: Ordnance Survey data (planned)
4. **Real-time**: Weather services, event calendars (planned)
5. **User-generated**: Reviews, ratings, route sharing (planned)