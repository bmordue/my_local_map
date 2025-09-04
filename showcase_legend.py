#!/usr/bin/env python3
"""
Showcase the implemented legend functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.legend import MapLegend

def main():
    print("🗺️ Lumsden Tourist Map - Legend Implementation Showcase")
    print("=" * 60)
    
    # Create legend instance
    legend = MapLegend()
    
    # Show summary
    summary = legend.get_legend_summary()
    print(f"📊 Legend Summary:")
    print(f"   Total Items: {summary['total_items']}")
    print(f"   Categories: {len(summary['categories'])}")
    print()
    
    # Show all categories and items
    categories = {
        "Land Use": [],
        "Water Features": [],
        "Transportation": [],
        "Buildings & POIs": []
    }
    
    for item in legend.items:
        if any(keyword in item.label for keyword in ["Forest", "Farmland", "Parks"]):
            categories["Land Use"].append(item)
        elif any(keyword in item.label for keyword in ["Water", "River", "Stream", "Canal"]):
            categories["Water Features"].append(item)
        elif any(keyword in item.label for keyword in ["Road", "Motorway", "path"]):
            categories["Transportation"].append(item)
        else:
            categories["Buildings & POIs"].append(item)
    
    for category, items in categories.items():
        if items:
            print(f"📂 {category}:")
            for item in items:
                symbol_type = {"polygon": "⬜", "line": "━━", "point": "●"}[item.symbol_type]
                print(f"   {symbol_type} {item.label}")
            print()
    
    print("✅ Legend Implementation Features:")
    print("   • Smart positioning (bottom-right corner)")
    print("   • Color-accurate symbols")
    print("   • Categorized organization") 
    print("   • PIL-based image overlay")
    print("   • Non-intrusive transparent background")
    print("   • Comprehensive symbol coverage")
    print()
    print("🎯 Successfully addresses issue #25: 'Add a legend to the map'")

if __name__ == "__main__":
    main()