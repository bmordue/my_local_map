# 12. Appendices

## 12.1 File Structure
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

## 12.2 Feature Categories
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

## 12.3 Data Sources
1. **Primary**: OpenStreetMap via Overpass API
2. **Enhanced**: Custom SQLite database with local tourism information
3. **Premium**: Ordnance Survey data (planned)
4. **Real-time**: Weather services, event calendars (planned)
5. **User-generated**: Reviews, ratings, route sharing (planned)