"""Legend generation utilities for tourist maps"""

from pathlib import Path


class LegendItem:
    """Represents a single item in the map legend"""
    
    def __init__(self, label, symbol_type, **kwargs):
        self.label = label
        self.symbol_type = symbol_type  # 'line', 'polygon', 'point'
        self.properties = kwargs


class MapLegend:
    """Generates and renders map legends"""
    
    def __init__(self):
        self.items = []
        self._load_tourist_legend_items()
    
    def _load_tourist_legend_items(self):
        """Load legend items based on tourist.xml style"""
        
        # Land use categories
        self.items.extend([
            LegendItem("Forest / Woodland", "polygon", 
                      fill="#d4e6b7", fill_opacity=0.8),
            LegendItem("Farmland / Grassland", "polygon", 
                      fill="#e8f5d4", fill_opacity=0.6),
            LegendItem("Parks / Gardens", "polygon", 
                      fill="#c8facc", fill_opacity=0.8),
        ])
        
        # Water features
        self.items.extend([
            LegendItem("Water Bodies", "polygon", 
                      fill="#7dd3c0", fill_opacity=0.8),
            LegendItem("Rivers", "line", 
                      stroke="#7dd3c0", stroke_width=3, stroke_opacity=0.9),
            LegendItem("Streams", "line", 
                      stroke="#7dd3c0", stroke_width=1.5, stroke_opacity=0.8),
            LegendItem("Canals", "line", 
                      stroke="#5dade2", stroke_width=2, stroke_opacity=0.8),
        ])
        
        # Roads
        self.items.extend([
            LegendItem("Motorways", "line", 
                      stroke="#e74c3c", stroke_width=4, stroke_opacity=0.9),
            LegendItem("Primary Roads", "line", 
                      stroke="#f39c12", stroke_width=3, stroke_opacity=0.9),
            LegendItem("Secondary Roads", "line", 
                      stroke="#f1c40f", stroke_width=2.5, stroke_opacity=0.8),
            LegendItem("Minor Roads", "line", 
                      stroke="#34495e", stroke_width=1.5, stroke_opacity=0.7),
            LegendItem("Residential Roads", "line", 
                      stroke="#ecf0f1", stroke_width=1.5, stroke_opacity=0.8),
        ])
        
        # Paths
        self.items.extend([
            LegendItem("Footpaths", "line", 
                      stroke="#8e44ad", stroke_width=1.5, stroke_opacity=0.8, 
                      stroke_dasharray="3,2"),
            LegendItem("Cycle Paths", "line", 
                      stroke="#27ae60", stroke_width=2, stroke_opacity=0.9, 
                      stroke_dasharray="4,2"),
        ])
        
        # Buildings and POIs
        self.items.extend([
            LegendItem("Buildings", "polygon", 
                      fill="#bdc3c7", fill_opacity=0.6, 
                      stroke="#7f8c8d", stroke_width=0.5),
            # Points of Interest with new icons
            LegendItem("Food & Drink", "icon", icon_path="icons/restaurant-15.svg"),
            LegendItem("Accommodation", "icon", icon_path="icons/lodging-15.svg"),
            LegendItem("Attractions", "icon", icon_path="icons/attraction-15.svg"),
            LegendItem("Shopping", "icon", icon_path="icons/shop-15.svg"),
            LegendItem("Transportation", "icon", icon_path="icons/car-15.svg"),
            LegendItem("Public Services", "icon", icon_path="icons/toilet-15.svg"),
            LegendItem("Healthcare", "icon", icon_path="icons/hospital-15.svg"),
            LegendItem("Religious Sites", "icon", icon_path="icons/religious-christian-15.svg"),
        ])
    
    def render_to_map(self, map_obj, legend_width=200, legend_height=None):
        """Render legend directly onto the map object"""
        
        # Calculate legend height based on number of items
        if legend_height is None:
            item_height = 18  # pixels per legend item
            padding = 20
            title_height = 25
            legend_height = len(self.items) * item_height + padding * 2 + title_height
        
        # Position legend in bottom-right corner with margin
        map_width = map_obj.width
        map_height = map_obj.height
        margin = 20
        
        legend_x = map_width - legend_width - margin
        legend_y = map_height - legend_height - margin
        
        # Return the legend data for external rendering
        return {
            'position': (legend_x, legend_y),
            'size': (legend_width, legend_height),
            'items': self.items,
            'title': 'Map Legend'
        }
    
    def get_legend_summary(self):
        """Get a summary of legend items for reference"""
        return {
            'total_items': len(self.items),
            'categories': {
                'Land Use': len([i for i in self.items if 'Forest' in i.label or 'Farmland' in i.label or 'Parks' in i.label]),
                'Water Features': len([i for i in self.items if 'Water' in i.label or 'River' in i.label or 'Stream' in i.label or 'Canal' in i.label]),
                'Transportation': len([i for i in self.items if 'Road' in i.label or 'Motorway' in i.label or 'path' in i.label]),
                'Buildings & POIs': len([i for i in self.items if 'Building' in i.label or 'Points of Interest' in i.label]),
            }
        }


def add_legend_to_image(image_path, legend_data, output_path=None):
    """Add legend overlay to an existing map image using PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Warning: PIL not available, skipping legend overlay")
        return False
    
    if output_path is None:
        output_path = image_path
    
    # Load the map image
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        
        # Extract legend info
        legend_x, legend_y = legend_data['position']
        legend_width, legend_height = legend_data['size']
        items = legend_data['items']
        title = legend_data['title']
        
        # Draw legend background
        background_coords = [
            (legend_x, legend_y),
            (legend_x + legend_width, legend_y + legend_height)
        ]
        draw.rectangle(background_coords, fill=(255, 255, 255, 230), outline=(51, 51, 51), width=2)
        
        # Try to load font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf", 14)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVu-Sans.ttf", 11)
        except (OSError, IOError):
            # Fall back to default font
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Draw title
        title_y = legend_y + 10
        draw.text((legend_x + 10, title_y), title, fill=(44, 62, 80), font=title_font)
        
        # Draw legend items
        item_y = title_y + 25
        item_height = 16
        symbol_size = 12
        
        for item in items:
            symbol_x = legend_x + 10
            symbol_y = item_y + (item_height - symbol_size) // 2
            text_x = symbol_x + symbol_size + 8
            
            # Draw symbol based on type
            if item.symbol_type == "polygon":
                # Draw filled rectangle
                fill_color = _hex_to_rgb(item.properties.get('fill', '#bdc3c7'))
                symbol_coords = [
                    (symbol_x, symbol_y),
                    (symbol_x + symbol_size, symbol_y + symbol_size)
                ]
                draw.rectangle(symbol_coords, fill=fill_color, outline=(127, 140, 141))
                
            elif item.symbol_type == "line":
                # Draw line
                stroke_color = _hex_to_rgb(item.properties.get('stroke', '#34495e'))
                stroke_width = max(1, int(item.properties.get('stroke_width', 1)))
                
                if 'stroke_dasharray' in item.properties:
                    # For dashed lines, draw multiple short segments
                    for i in range(0, symbol_size, 4):
                        if i + 2 <= symbol_size:
                            line_coords = [
                                (symbol_x + i, symbol_y + symbol_size // 2),
                                (symbol_x + i + 2, symbol_y + symbol_size // 2)
                            ]
                            draw.line(line_coords, fill=stroke_color, width=stroke_width)
                else:
                    # Solid line
                    line_coords = [
                        (symbol_x, symbol_y + symbol_size // 2),
                        (symbol_x + symbol_size, symbol_y + symbol_size // 2)
                    ]
                    draw.line(line_coords, fill=stroke_color, width=stroke_width)
                    
            elif item.symbol_type == "point":
                # Draw circle
                fill_color = _hex_to_rgb(item.properties.get('fill', '#e74c3c'))
                radius = item.properties.get('width', 6) // 2
                center_x = symbol_x + symbol_size // 2
                center_y = symbol_y + symbol_size // 2
                circle_coords = [
                    (center_x - radius, center_y - radius),
                    (center_x + radius, center_y + radius)
                ]
                draw.ellipse(circle_coords, fill=fill_color)
            
            elif item.symbol_type == "icon":
                # Draw a placeholder for the icon
                icon_path = item.properties.get('icon_path')
                if icon_path and Path(icon_path).exists():
                    try:
                        from io import BytesIO
                        import cairosvg
                        from PIL import Image
                        # Convert SVG to PNG in-memory
                        with open(icon_path, 'rb') as svg_file:
                            svg_data = svg_file.read()
                        png_bytes = cairosvg.svg2png(bytestring=svg_data, output_width=symbol_size, output_height=symbol_size)
                        png_io = BytesIO(png_bytes)
                        icon_img = Image.open(png_io).convert('RGBA')
                        # Paste PNG onto legend
                        img.paste(icon_img, (symbol_x, symbol_y), icon_img)
                    except Exception as e:
                        # Fallback: draw a placeholder rectangle if conversion fails
                        fill_color = (142, 68, 173) # Purple
                        symbol_coords = [
                            (symbol_x, symbol_y),
                            (symbol_x + symbol_size, symbol_y + symbol_size)
                        ]
                        draw.rectangle(symbol_coords, fill=fill_color)
                else:
                    # Draw a fallback if icon is missing
                    draw.text((symbol_x, symbol_y), "?", fill=(44, 62, 80), font=text_font)

            # Draw label text
            draw.text((text_x, symbol_y), item.label, fill=(44, 62, 80), font=text_font)
            
            item_y += item_height
        
        # Save the image with legend
        img.save(output_path, 'PNG')
        return True


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return (189, 195, 199)  # Default gray color