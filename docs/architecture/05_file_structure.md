# File Structure

```
/home/ben/Projects/mine/my_local_map/
├── config/
│   ├── areas.json          # Geographic area configurations
│   └── output_formats.json # Output format specifications
├── data/                   # Generated data (git-ignored)
├── icons/                  # SVG icons for POIs
├── styles/                 # Mapnik XML style templates
├── utils/                  # Utility modules
│   ├── config.py           # Configuration management
│   ├── data_processing.py  # OSM data conversion and processing
│   ├── elevation_processing.py  # Elevation data and hillshading
│   ├── style_builder.py    # Mapnik style generation
│   ├── legend.py           # Legend generation
│   └── create_enhanced_data.py  # Tourism database creation
├── lumsden_area.osm        # Source OSM data
├── map_generator.py        # Main map generation script
├── requirements.txt        # Python dependencies
├── shell.nix               # Nix development environment
└── README.md               # Project documentation