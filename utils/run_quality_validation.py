#!/usr/bin/env python3
"""
Data Quality Validation Runner for Lumsden Tourist Map Generator

This script loads enhanced data and runs comprehensive quality validation checks
as specified in Phase 2 roadmap requirements.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add the root directory to path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.config import load_area_config
from utils.data_processing import calculate_bbox
from utils.quality_validation import validate_data_quality

logger = logging.getLogger(__name__)


def load_enhanced_data(data_dir: str = "enhanced_data") -> dict:
    """
    Load enhanced data from GeoJSON files

    Args:
        data_dir: Directory containing enhanced data files

    Returns:
        Dictionary with data sources loaded from files
    """
    data_sources = {}
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.warning(f" Enhanced data directory not found: {data_dir}")
        logger.info("   Generating sample data for validation testing...")
        return generate_sample_data()

    # Load GeoJSON files
    geojson_files = {
        "tourist_attractions": "tourist_attractions.geojson",
        "accommodation": "accommodation.geojson",
        "dining": "dining.geojson",
        "activities": "activities.geojson",
        "walking_trails": "walking_trails.geojson",
    }

    for source_name, filename in geojson_files.items():
        file_path = data_path / filename
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    geojson_data = json.load(f)

                # Extract features from GeoJSON
                features = geojson_data.get("features", [])
                data_list = []

                for feature in features:
                    item = feature.get("properties", {}).copy()

                    # Add geometry coordinates to properties
                    geom = feature.get("geometry", {})
                    if geom.get("type") == "Point":
                        coords = geom.get("coordinates", [])
                        if len(coords) >= 2:
                            item["lon"] = coords[0]
                            item["lat"] = coords[1]

                    data_list.append(item)

                data_sources[source_name] = data_list
                logger.info(f"✓ Loaded {len(data_list)} items from {filename}")

            except Exception as e:
                logger.warning(f" Error loading {filename}: {e}")
        else:
            logger.warning(f" File not found: {filename}")

    if not data_sources:
        logger.warning(" No enhanced data found, using sample data for validation")
        return generate_sample_data()

    return data_sources


def generate_sample_data() -> dict:
    """
    Generate sample data for validation testing

    Returns:
        Dictionary with sample data sources
    """
    return {
        "attractions": [
            {
                "name": "Lumsden Castle Ruins",
                "lat": 57.3167,
                "lon": -2.8833,
                "type": "historic_site",
                "description": "Medieval castle ruins with panoramic views",
                "opening_hours": {
                    "monday": "09:00-17:00",
                    "tuesday": "09:00-17:00",
                    "wednesday": "09:00-17:00",
                    "thursday": "09:00-17:00",
                    "friday": "09:00-17:00",
                    "saturday": "10:00-16:00",
                    "sunday": "10:00-16:00",
                },
                "seasonal_info": "Open April to October",
            },
            {
                "name": "Lumsden Church",
                "lat": 57.3165,
                "lon": -2.8840,
                "type": "religious_site",
                "description": "Historic parish church",
            },
        ],
        "accommodation": [
            {
                "name": "Lumsden Inn",
                "lat": 57.3170,
                "lon": -2.8830,
                "type": "inn",
                "contact": "+44 1464 861234",
                "amenities": ["wifi", "parking", "restaurant"],
            },
            {
                "name": "Aberdeenshire B&B",
                "lat": 57.3160,
                "lon": -2.8825,
                "type": "bed_breakfast",
                "contact": "+44 1464 861456",
            },
        ],
        "dining": [
            {
                "name": "Village Cafe",
                "lat": 57.3168,
                "lon": -2.8835,
                "cuisine_type": "british",
                "contact": "+44 1464 861789",
                "opening_hours": {
                    "monday": "closed",
                    "tuesday": "08:00-16:00",
                    "wednesday": "08:00-16:00",
                    "thursday": "08:00-16:00",
                    "friday": "08:00-16:00",
                    "saturday": "09:00-17:00",
                    "sunday": "09:00-15:00",
                },
            }
        ],
        "activities": [
            {
                "name": "Hill Walking Tour",
                "lat": 57.3200,
                "lon": -2.8800,
                "description": "Guided walking tour of local hills",
                "duration": "3 hours",
                "seasonal_info": "Available May to September",
            }
        ],
    }


def main():
    """Main function to run quality validation"""
    logger.info("🔍 Data Quality Validation for Lumsden Tourist Map")
    logger.info("=" * 60)

    try:
        # Load area configuration
        area_config = load_area_config("lumsden")
        logger.info(f"📍 Validation area: {area_config['name']}")

        # Calculate bounding box for coordinate validation
        bbox = calculate_bbox(
            area_config["center"]["lat"],
            area_config["center"]["lon"],
            area_config["coverage"]["width_km"],
            area_config["coverage"]["height_km"],
        )

        logger.info(
            f"🗺️  Map bounds: {bbox['south']:.4f}°S to {bbox['north']:.4f}°N, "
            f"{bbox['west']:.4f}°W to {bbox['east']:.4f}°E"
        )
        logger.info()

        # Load data sources
        logger.info("📂 Loading data sources...")
        data_sources = load_enhanced_data()

        total_items = sum(len(data) for data in data_sources.values())
        logger.info(f"📊 Total items to validate: {total_items}")
        logger.info()

        # Run quality validation
        validation_report = validate_data_quality(
            data_sources, bbox, output_dir="validation_reports"
        )

        # Generate summary
        logger.info("\n" + "=" * 60)
        logger.info("📋 VALIDATION SUMMARY")
        logger.info("=" * 60)

        total_checks = len(validation_report.results)
        passed_checks = sum(1 for r in validation_report.results if r.passed)
        failed_checks = total_checks - passed_checks

        logger.info(f"Total validation checks: {total_checks}")
        logger.info(f"Passed checks: {passed_checks}")
        logger.info(f"Failed checks: {failed_checks}")

        total_errors = sum(len(r.errors) for r in validation_report.results)
        total_warnings = sum(len(r.warnings) for r in validation_report.results)

        logger.info(f"Total errors: {total_errors}")
        logger.info(f"Total warnings: {total_warnings}")

        # Overall status
        overall_status = "✅ PASSED" if failed_checks == 0 else "❌ FAILED"
        logger.info(f"\nOverall Quality Status: {overall_status}")

        # Show recommendations
        report_dict = validation_report.generate_report()
        if report_dict["recommendations"]:
            logger.info("\n🔧 RECOMMENDATIONS:")
            for i, rec in enumerate(report_dict["recommendations"], 1):
                logger.info(f"{i}. {rec}")

        logger.info("\n" + "=" * 60)
        logger.info(
            "📄 Detailed report saved to: validation_reports/quality_validation_report.json"
        )

        # Return appropriate exit code
        return 0 if failed_checks == 0 else 1

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
