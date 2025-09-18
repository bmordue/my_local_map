"""
Ordnance Survey Data Processing Module
Handles integration of OS Open Data layers including roads, boundaries, and terrain
"""

import os
import requests
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class OSDataProcessor:
    """Handles downloading and processing of Ordnance Survey Open Data"""
    
    def __init__(self, data_dir: str = "data/os_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # OS Open Data product URLs (these are demonstration URLs - actual URLs would need updating)
        self.os_products = {
            'roads': {
                'name': 'OS Open Roads',
                'url': 'https://api.os.uk/downloads/v1/products/OpenRoads/downloads?area=GB&format=ESRI+Shapefile',
                'layer_name': 'RoadLink',
                'description': 'Detailed road network data'
            },
            'boundaries': {
                'name': 'OS Boundary-Line',
                'url': 'https://api.os.uk/downloads/v1/products/BoundaryLine/downloads?area=GB&format=ESRI+Shapefile', 
                'layer_name': 'boundary_line',
                'description': 'Administrative and electoral boundaries'
            },
            'terrain': {
                'name': 'OS Terrain 50',
                'url': 'https://api.os.uk/downloads/v1/products/Terrain50/downloads?area=GB&format=ASCII+Grid',
                'layer_name': 'terrain50',
                'description': 'Digital terrain model at 50m resolution'
            },
            'rights_of_way': {
                'name': 'OS Open Greenspace',
                'url': 'https://api.os.uk/downloads/v1/products/OpenGreenspace/downloads?area=GB&format=ESRI+Shapefile',
                'layer_name': 'GreenspaceSite',
                'description': 'Public rights of way and green spaces'
            }
        }

    def download_os_data(self, product_key: str, bbox: Dict[str, float], output_file: str) -> bool:
        """
        Download OS Open Data for a specific product and bounding box
        
        Args:
            product_key: Key identifying the OS product (roads, boundaries, etc.)
            bbox: Bounding box dict with keys: north, south, east, west
            output_file: Path to save the downloaded data
            
        Returns:
            bool: True if download successful, False otherwise
        """
        if product_key not in self.os_products:
            print(f"❌ Unknown OS product: {product_key}")
            return False
            
        product = self.os_products[product_key]
        print(f"📡 Downloading {product['name']}...")
        
        try:
            # Note: In a real implementation, this would need proper API credentials
            # and the correct API endpoint with bbox filtering
            # For now, we'll create a demonstration/mock implementation
            
            # Since we can't actually download OS data in this environment,
            # we'll create a mock shapefile structure to demonstrate the integration
            return self._create_mock_os_data(product_key, bbox, output_file)
            
        except Exception as e:
            print(f"❌ Failed to download {product['name']}: {e}")
            return False

    def _create_mock_os_data(self, product_key: str, bbox: Dict[str, float], output_file: str) -> bool:
        """
        Create mock OS data for demonstration purposes
        In a real implementation, this would be replaced with actual OS API calls
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        product = self.os_products[product_key]
        
        # Create actual mock shapefile data for demonstration
        # For now, create a simple CSV file that can be used to generate shapefiles
        base_name = output_path.stem
        output_dir = output_path.parent
        
        # Create mock CSV data that represents the OS data structure
        csv_file = output_dir / f"{base_name}.csv"
        
        # Generate appropriate mock data based on product type
        if product_key == 'roads':
            mock_data = self._create_mock_roads_csv(bbox)
        elif product_key == 'boundaries':
            mock_data = self._create_mock_boundaries_csv(bbox)
        elif product_key == 'rights_of_way':
            mock_data = self._create_mock_rights_of_way_csv(bbox)
        else:
            mock_data = []
        
        # Write CSV data
        if mock_data:
            with open(csv_file, 'w', newline='') as f:
                header = list(mock_data[0].keys())
                f.write(','.join(header) + '\n')
                for row in mock_data:
                    values = [str(row.get(col, '')) for col in header]
                    f.write(','.join(values) + '\n')
        
        # Also create the referenced output file so the conversion doesn't fail
        with open(output_path, 'w') as f:
            f.write(f"# Mock {product['name']} Data File\n")
            f.write(f"# In a real implementation, this would be downloaded from OS API\n")
            f.write(f"# CSV data available at: {csv_file}\n")
            f.write(f"# Bounding box: {bbox}\n")
        
        print(f"  ✓ Created mock {product['name']}: {csv_file}")
        return True

    def _create_mock_roads_csv(self, bbox: Dict[str, float]) -> List[Dict[str, str]]:
        """Generate mock CSV roads data for the bounding box"""
        # Create sample roads data crossing the bounding box
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lon = (bbox['east'] + bbox['west']) / 2
        
        return [
            {
                'id': '1', 'class': 'A Road', 'name': 'A944', 
                'start_lat': str(bbox['south']), 'start_lon': str(center_lon),
                'end_lat': str(bbox['north']), 'end_lon': str(center_lon)
            },
            {
                'id': '2', 'class': 'B Road', 'name': 'B9119',
                'start_lat': str(center_lat), 'start_lon': str(bbox['west']),
                'end_lat': str(center_lat), 'end_lon': str(bbox['east'])
            },
            {
                'id': '3', 'class': 'Unclassified', 'name': 'Local Road',
                'start_lat': str(center_lat + 0.005), 'start_lon': str(center_lon - 0.01),
                'end_lat': str(center_lat - 0.005), 'end_lon': str(center_lon + 0.01)
            }
        ]

    def _create_mock_boundaries_csv(self, bbox: Dict[str, float]) -> List[Dict[str, str]]:
        """Generate mock CSV boundary data for the bounding box"""
        return [
            {
                'id': '1', 'type': 'Administrative', 'name': 'Aberdeenshire',
                'start_lat': str(bbox['south']), 'start_lon': str(bbox['west']),
                'end_lat': str(bbox['north']), 'end_lon': str(bbox['east'])
            },
            {
                'id': '2', 'type': 'Parish', 'name': 'Lumsden Parish',
                'start_lat': str(bbox['south'] + 0.01), 'start_lon': str(bbox['west'] + 0.01),
                'end_lat': str(bbox['north'] - 0.01), 'end_lon': str(bbox['east'] - 0.01)
            }
        ]

    def _create_mock_rights_of_way_csv(self, bbox: Dict[str, float]) -> List[Dict[str, str]]:
        """Generate mock CSV rights of way data for the bounding box"""
        center_lat = (bbox['north'] + bbox['south']) / 2
        center_lon = (bbox['east'] + bbox['west']) / 2
        
        return [
            {
                'id': '1', 'type': 'Footpath', 'name': 'Lumsden Loop',
                'start_lat': str(center_lat), 'start_lon': str(center_lon - 0.005),
                'end_lat': str(center_lat + 0.01), 'end_lon': str(center_lon + 0.005)
            },
            {
                'id': '2', 'type': 'Bridleway', 'name': 'Hill Track',
                'start_lat': str(center_lat + 0.005), 'start_lon': str(center_lon),
                'end_lat': str(center_lat + 0.015), 'end_lon': str(center_lon + 0.01)
            }
        ]

    def convert_os_to_shapefiles(self, os_data_file: str, product_key: str) -> Optional[str]:
        """
        Convert downloaded OS data to shapefiles for use with Mapnik
        
        Args:
            os_data_file: Path to downloaded OS data file
            product_key: Type of OS data being processed
            
        Returns:
            str: Path to output directory if successful, None otherwise
        """
        if product_key not in self.os_products:
            print(f"❌ Unknown OS product key: {product_key}")
            return None
            
        product = self.os_products[product_key]
        print(f"🔄 Converting {product['name']} to shapefiles...")
        
        output_dir = self.data_dir / product_key
        output_dir.mkdir(exist_ok=True)
        
        # For mock implementation with CSV data, create simple shapefiles
        if Path(os_data_file).exists():
            csv_file = Path(os_data_file).parent / f"{Path(os_data_file).stem}.csv"
            if csv_file.exists():
                # Create a mock shapefile using the CSV data
                return self._create_mock_shapefile(csv_file, output_dir, product_key)
            else:
                print(f"  ✓ Mock {product['name']} ready for integration (no conversion needed)")
                return str(output_dir)
        
        # In a real implementation, this would use ogr2ogr to convert OS formats
        try:
            if product_key == 'terrain' and os_data_file.endswith('.asc'):
                # Convert ASCII Grid to GeoTIFF
                output_file = output_dir / "terrain.tif"
                cmd = [
                    "gdal_translate",
                    "-of", "GTiff",
                    os_data_file,
                    str(output_file)
                ]
            else:
                # Convert shapefile-based data
                output_file = output_dir / f"{product_key}.shp"
                cmd = [
                    "ogr2ogr",
                    "-f", "ESRI Shapefile",
                    str(output_file),
                    os_data_file,
                    product.get('layer_name', product_key)
                ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✓ Converted {product['name']}: {output_file}")
            return str(output_dir)
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to convert {product['name']}: {e}")
            return None
        except FileNotFoundError:
            print(f"  ❌ GDAL tools not found. Install gdal-bin package.")
            return None

    def _create_mock_shapefile(self, csv_file: Path, output_dir: Path, product_key: str) -> str:
        """
        Create a mock shapefile from CSV data for demonstration purposes
        """
        try:
            shapefile = output_dir / f"{product_key}.shp"
            
            # Create a simple valid empty shapefile using ogr2ogr
            # First create a temporary SQL command to generate empty geometries
            temp_sql = f"SELECT '{product_key}' as name, 'demo' as type"
            
            cmd = [
                "ogr2ogr",
                "-f", "ESRI Shapefile",
                "-overwrite",
                "-nln", product_key,
                str(shapefile),
                "/dev/null",
                "-dialect", "sqlite",
                "-sql", temp_sql,
                "-a_srs", "EPSG:4326"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check if the shapefile was created and is valid
            if shapefile.exists() and shapefile.stat().st_size > 0:
                print(f"  ✓ Created valid empty shapefile: {shapefile}")
                return str(output_dir)
            
        except Exception as e:
            print(f"  ⚠️ Could not create shapefile from CSV: {e}")
        
        # Fallback: disable OS layer for this product
        print(f"  ⚠️ OS {product_key} layer will be disabled due to shapefile creation issues")
        return None

    def process_os_data_for_area(self, bbox: Dict[str, float], enabled_layers: List[str] = None) -> Dict[str, str]:
        """
        Process all enabled OS data layers for a given area
        
        Args:
            bbox: Bounding box for the area of interest
            enabled_layers: List of OS layers to process (default: all)
            
        Returns:
            Dict mapping layer names to their output directories
        """
        if enabled_layers is None:
            enabled_layers = list(self.os_products.keys())
        
        print("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Processing Ordnance Survey data layers...")
        
        processed_layers = {}
        
        for layer_key in enabled_layers:
            if layer_key not in self.os_products:
                print(f"  ⚠️  Skipping unknown layer: {layer_key}")
                continue
                
            product = self.os_products[layer_key]
            print(f"  📊 Processing {product['name']}...")
            
            # Download the data
            download_file = self.data_dir / f"{layer_key}_raw_data"
            if self.download_os_data(layer_key, bbox, str(download_file)):
                # Convert to shapefiles
                output_dir = self.convert_os_to_shapefiles(str(download_file), layer_key)
                if output_dir:
                    processed_layers[layer_key] = output_dir
                    print(f"  ✅ {product['name']} ready for mapping")
                else:
                    print(f"  ⚠️ {product['name']} processing failed - layer will be disabled")
            else:
                print(f"  ❌ Failed to download {product['name']}")
        
        if processed_layers:
            print(f"🎯 Successfully processed {len(processed_layers)} OS data layers")
        else:
            print("⚠️  No OS data layers were successfully processed")
        
        return processed_layers


def integrate_os_data_with_map(bbox: Dict[str, float], os_config: Dict = None) -> Dict[str, str]:
    """
    Main function to integrate OS data into the mapping pipeline
    
    Args:
        bbox: Bounding box for the area to map
        os_config: Configuration dict specifying which OS layers to include
        
    Returns:
        Dict mapping OS layer names to their data directories
    """
    if not os_config or not os_config.get('enabled', False):
        return {}
    
    processor = OSDataProcessor()
    
    enabled_layers = os_config.get('layers', ['roads', 'boundaries'])
    
    return processor.process_os_data_for_area(bbox, enabled_layers)