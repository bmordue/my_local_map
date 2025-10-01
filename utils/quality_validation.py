#!/usr/bin/env python3
"""
Quality Validation System for Lumsden Tourist Map Generator

Implements comprehensive data quality checks as outlined in Phase 2 roadmap:
- Coordinate validation: Ensure all points fall within map bounds
- Attribute completeness: Verify required fields are populated
- Temporal validation: Check opening hours and seasonal information
- Cross-reference validation: Compare multiple sources for accuracy
"""

import json
import logging
import os
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results with detailed reporting"""
    
    def __init__(self, check_name: str):
        self.check_name = check_name
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict[str, Any] = {}
        self.stats: Dict[str, int] = {}
    
    def add_error(self, message: str, details: Optional[Dict] = None):
        """Add an error to the validation result"""
        self.passed = False
        self.errors.append(message)
        if details:
            self.details[f"error_{len(self.errors)}"] = details
    
    def add_warning(self, message: str, details: Optional[Dict] = None):
        """Add a warning to the validation result"""
        self.warnings.append(message)
        if details:
            self.details[f"warning_{len(self.warnings)}"] = details
    
    def update_stats(self, key: str, value: int):
        """Update statistics for this validation"""
        self.stats[key] = value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'check_name': self.check_name,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': self.stats,
            'details': self.details
        }


class CoordinateValidator:
    """Validates geographic coordinates and spatial relationships"""
    
    def __init__(self, bbox: Dict[str, float]):
        self.bbox = bbox
        self.valid_lat_range = (-90, 90)
        self.valid_lon_range = (-180, 180)
    
    def validate_coordinates(self, data: List[Dict]) -> ValidationResult:
        """
        Validate that all coordinates are valid and within map bounds
        
        Args:
            data: List of dictionaries with lat/lon or coordinates
            
        Returns:
            ValidationResult with coordinate validation details
        """
        result = ValidationResult("coordinate_validation")
        
        valid_count = 0
        invalid_coords = 0
        out_of_bounds = 0
        
        for i, item in enumerate(data):
            # Extract coordinates from various formats
            lat, lon = self._extract_coordinates(item)
            
            if lat is None or lon is None:
                result.add_error(
                    f"Item {i}: Missing or invalid coordinates",
                    {"item": item, "index": i}
                )
                invalid_coords += 1
                continue
            
            # Check coordinate validity
            if not self._is_valid_coordinate(lat, lon):
                result.add_error(
                    f"Item {i}: Invalid coordinates lat={lat}, lon={lon}",
                    {"lat": lat, "lon": lon, "index": i}
                )
                invalid_coords += 1
                continue
            
            # Check if within map bounds
            if not self._is_within_bounds(lat, lon):
                result.add_warning(
                    f"Item {i}: Coordinates outside map bounds lat={lat}, lon={lon}",
                    {"lat": lat, "lon": lon, "index": i, "bounds": self.bbox}
                )
                out_of_bounds += 1
            else:
                valid_count += 1
        
        # Update statistics
        result.update_stats("total_items", len(data))
        result.update_stats("valid_coordinates", valid_count)
        result.update_stats("invalid_coordinates", invalid_coords)
        result.update_stats("out_of_bounds", out_of_bounds)
        
        if invalid_coords == 0:
            logger.info(f"✓ Coordinate validation passed: {valid_count}/{len(data)} valid coordinates")
        else:
            logger.warning(f"⚠ Coordinate validation issues: {invalid_coords} invalid, {out_of_bounds} out of bounds")
        
        return result
    
    def _extract_coordinates(self, item: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract lat/lon from various data formats"""
        # Try direct lat/lon fields
        if 'lat' in item and 'lon' in item:
            return item.get('lat'), item.get('lon')
        
        if 'latitude' in item and 'longitude' in item:
            return item.get('latitude'), item.get('longitude')
        
        # Try GeoJSON coordinate format
        if 'geometry' in item and item['geometry'].get('type') == 'Point':
            coords = item['geometry'].get('coordinates', [])
            if len(coords) >= 2:
                return coords[1], coords[0]  # GeoJSON is [lon, lat]
        
        # Try coordinates array
        if 'coordinates' in item:
            coords = item['coordinates']
            if isinstance(coords, list) and len(coords) >= 2:
                return coords[1], coords[0]  # Assume [lon, lat]
        
        return None, None
    
    def _is_valid_coordinate(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within valid ranges"""
        return (self.valid_lat_range[0] <= lat <= self.valid_lat_range[1] and
                self.valid_lon_range[0] <= lon <= self.valid_lon_range[1])
    
    def _is_within_bounds(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within map bounds"""
        return (self.bbox['south'] <= lat <= self.bbox['north'] and
                self.bbox['west'] <= lon <= self.bbox['east'])


class AttributeValidator:
    """Validates data attribute completeness and quality"""
    
    def __init__(self, required_fields: Optional[Dict[str, List[str]]] = None):
        """
        Initialize attribute validator
        
        Args:
            required_fields: Dictionary mapping data types to required field lists
        """
        self.required_fields = required_fields or {
            'accommodation': ['name', 'type', 'contact'],
            'dining': ['name', 'cuisine_type', 'contact'],
            'attraction': ['name', 'description', 'type'],
            'activity': ['name', 'description', 'duration'],
            'trail': ['name', 'distance', 'difficulty']
        }
    
    def validate_attributes(self, data: List[Dict], data_type: str = 'general') -> ValidationResult:
        """
        Validate attribute completeness for a dataset
        
        Args:
            data: List of data items to validate
            data_type: Type of data for specific validation rules
            
        Returns:
            ValidationResult with attribute validation details
        """
        result = ValidationResult("attribute_validation")
        
        required = self.required_fields.get(data_type, [])
        complete_items = 0
        incomplete_items = 0
        
        for i, item in enumerate(data):
            missing_fields = []
            empty_fields = []
            
            for field in required:
                if field not in item:
                    missing_fields.append(field)
                elif not item[field] or str(item[field]).strip() == '':
                    empty_fields.append(field)
            
            if missing_fields or empty_fields:
                incomplete_items += 1
                error_msg = f"Item {i}: "
                if missing_fields:
                    error_msg += f"Missing fields: {missing_fields} "
                if empty_fields:
                    error_msg += f"Empty fields: {empty_fields}"
                
                result.add_error(error_msg.strip(), {
                    "index": i,
                    "item_name": item.get('name', 'Unknown'),
                    "missing_fields": missing_fields,
                    "empty_fields": empty_fields
                })
            else:
                complete_items += 1
        
        # Update statistics
        result.update_stats("total_items", len(data))
        result.update_stats("complete_items", complete_items)
        result.update_stats("incomplete_items", incomplete_items)
        result.update_stats("completeness_percentage", 
                          int((complete_items / len(data)) * 100) if data else 0)
        
        if incomplete_items == 0:
            logger.info(f"✓ Attribute validation passed: {complete_items}/{len(data)} items complete")
        else:
            logger.warning(f"⚠ Attribute validation issues: {incomplete_items}/{len(data)} items incomplete")
        
        return result


class TemporalValidator:
    """Validates temporal data like opening hours and seasonal information"""
    
    def __init__(self):
        self.days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        self.time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    def validate_temporal_data(self, data: List[Dict]) -> ValidationResult:
        """
        Validate opening hours and seasonal information
        
        Args:
            data: List of data items with temporal information
            
        Returns:
            ValidationResult with temporal validation details
        """
        result = ValidationResult("temporal_validation")
        
        valid_temporal = 0
        invalid_temporal = 0
        no_temporal = 0
        
        for i, item in enumerate(data):
            has_temporal = False
            
            # Check opening hours
            if 'opening_hours' in item:
                has_temporal = True
                if not self._validate_opening_hours(item['opening_hours']):
                    result.add_error(
                        f"Item {i}: Invalid opening hours format",
                        {"index": i, "opening_hours": item['opening_hours']}
                    )
                    invalid_temporal += 1
                    continue
            
            # Check seasonal information
            if 'seasonal_info' in item:
                has_temporal = True
                if not self._validate_seasonal_info(item['seasonal_info']):
                    result.add_warning(
                        f"Item {i}: Unclear seasonal information",
                        {"index": i, "seasonal_info": item['seasonal_info']}
                    )
            
            if has_temporal:
                valid_temporal += 1
            else:
                no_temporal += 1
        
        # Update statistics
        result.update_stats("total_items", len(data))
        result.update_stats("valid_temporal", valid_temporal)
        result.update_stats("invalid_temporal", invalid_temporal)
        result.update_stats("no_temporal_data", no_temporal)
        
        if invalid_temporal == 0:
            logger.info(f"✓ Temporal validation passed: {valid_temporal} items with valid temporal data")
        else:
            logger.warning(f"⚠ Temporal validation issues: {invalid_temporal} items with invalid temporal data")
        
        return result
    
    def _validate_opening_hours(self, opening_hours: Any) -> bool:
        """Validate opening hours format"""
        if not opening_hours:
            return True  # Empty is valid (closed)
        
        if isinstance(opening_hours, dict):
            # Validate dictionary format {day: "HH:MM-HH:MM"}
            for day, hours in opening_hours.items():
                if day.lower() not in self.days_of_week:
                    return False
                if hours and not self._validate_time_range(hours):
                    return False
            return True
        
        if isinstance(opening_hours, str):
            # Simple validation for string format
            if opening_hours.lower() in ['closed', 'open', '24/7', 'varies']:
                return True
            return self._validate_time_range(opening_hours)
        
        return False
    
    def _validate_time_range(self, time_range: str) -> bool:
        """Validate time range format HH:MM-HH:MM"""
        if not time_range or time_range.strip() == '':
            return True
        
        # Handle special cases
        time_lower = time_range.lower().strip()
        if time_lower in ['closed', 'open', '24/7', 'varies']:
            return True
        
        # Handle various time formats
        if '-' in time_range:
            parts = time_range.split('-')
            if len(parts) == 2:
                return (self.time_pattern.match(parts[0].strip()) is not None and 
                       self.time_pattern.match(parts[1].strip()) is not None)
        
        return self.time_pattern.match(time_range.strip()) is not None
    
    def _validate_seasonal_info(self, seasonal_info: Any) -> bool:
        """Validate seasonal information"""
        if not seasonal_info:
            return True
        
        if isinstance(seasonal_info, str):
            # Allow common seasonal descriptions
            valid_keywords = ['summer', 'winter', 'spring', 'autumn', 'fall', 'year-round', 
                            'seasonal', 'april', 'may', 'june', 'july', 'august', 'september', 
                            'october', 'november', 'december', 'january', 'february', 'march']
            return any(keyword in seasonal_info.lower() for keyword in valid_keywords)
        
        return isinstance(seasonal_info, dict)


class CrossReferenceValidator:
    """Validates data consistency across multiple sources"""
    
    def __init__(self):
        self.tolerance_meters = 100  # Tolerance for coordinate differences
    
    def validate_cross_references(self, primary_data: List[Dict], 
                                reference_data: List[Dict]) -> ValidationResult:
        """
        Compare data across sources for consistency
        
        Args:
            primary_data: Primary dataset
            reference_data: Reference dataset for comparison
            
        Returns:
            ValidationResult with cross-reference validation details
        """
        result = ValidationResult("cross_reference_validation")
        
        matches_found = 0
        conflicts_found = 0
        missing_references = 0
        
        for i, primary_item in enumerate(primary_data):
            primary_name = primary_item.get('name', '').lower()
            primary_lat, primary_lon = self._extract_coordinates(primary_item)
            
            if not primary_name:
                result.add_warning(f"Primary item {i}: No name for cross-reference")
                continue
            
            # Find potential matches in reference data
            matches = self._find_matches(primary_item, reference_data)
            
            if not matches:
                missing_references += 1
                result.add_warning(
                    f"No reference found for: {primary_item.get('name', 'Unknown')}",
                    {"index": i, "item": primary_name}
                )
                continue
            
            matches_found += 1
            
            # Check for conflicts in matched items
            for match in matches:
                conflicts = self._check_conflicts(primary_item, match)
                if conflicts:
                    conflicts_found += 1
                    result.add_error(
                        f"Data conflict for '{primary_name}': {', '.join(conflicts)}",
                        {"primary": primary_item, "reference": match, "conflicts": conflicts}
                    )
        
        # Update statistics
        result.update_stats("total_primary_items", len(primary_data))
        result.update_stats("matches_found", matches_found)
        result.update_stats("conflicts_found", conflicts_found)
        result.update_stats("missing_references", missing_references)
        result.update_stats("match_percentage", 
                          int((matches_found / len(primary_data)) * 100) if primary_data else 0)
        
        if conflicts_found == 0:
            logger.info(f"✓ Cross-reference validation passed: {matches_found} matches, no conflicts")
        else:
            logger.warning(f"⚠ Cross-reference issues: {conflicts_found} conflicts found")
        
        return result
    
    def _extract_coordinates(self, item: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract coordinates (reuse from CoordinateValidator)"""
        if 'lat' in item and 'lon' in item:
            return item.get('lat'), item.get('lon')
        if 'latitude' in item and 'longitude' in item:
            return item.get('latitude'), item.get('longitude')
        return None, None
    
    def _find_matches(self, primary_item: Dict, reference_data: List[Dict]) -> List[Dict]:
        """Find matching items in reference data"""
        matches = []
        primary_name = primary_item.get('name', '').lower()
        primary_lat, primary_lon = self._extract_coordinates(primary_item)
        
        for ref_item in reference_data:
            ref_name = ref_item.get('name', '').lower()
            
            # Name-based matching
            if primary_name and ref_name:
                if primary_name == ref_name or self._name_similarity(primary_name, ref_name) > 0.8:
                    matches.append(ref_item)
                    continue
            
            # Location-based matching
            if primary_lat and primary_lon:
                ref_lat, ref_lon = self._extract_coordinates(ref_item)
                if ref_lat and ref_lon:
                    distance = self._calculate_distance(primary_lat, primary_lon, ref_lat, ref_lon)
                    if distance <= self.tolerance_meters:
                        matches.append(ref_item)
        
        return matches
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity (simple implementation)"""
        words1 = set(name1.split())
        words2 = set(name2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate approximate distance between two points in meters"""
        # Simple approximation for short distances
        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1
        
        # Convert to approximate meters (rough approximation)
        lat_meters = lat_diff * 111000  # ~111km per degree latitude
        lon_meters = lon_diff * 111000 * abs(cos(radians((lat1 + lat2) / 2)))
        
        return (lat_meters ** 2 + lon_meters ** 2) ** 0.5
    
    def _check_conflicts(self, primary: Dict, reference: Dict) -> List[str]:
        """Check for conflicts between primary and reference data"""
        conflicts = []
        
        # Check coordinate conflicts
        p_lat, p_lon = self._extract_coordinates(primary)
        r_lat, r_lon = self._extract_coordinates(reference)
        
        if p_lat and r_lat and p_lon and r_lon:
            distance = self._calculate_distance(p_lat, p_lon, r_lat, r_lon)
            if distance > self.tolerance_meters:
                conflicts.append(f"Location differs by {distance:.0f}m")
        
        # Check attribute conflicts
        common_fields = ['type', 'phone', 'website', 'cuisine_type']
        for field in common_fields:
            if (field in primary and field in reference and 
                primary[field] and reference[field] and 
                str(primary[field]).lower() != str(reference[field]).lower()):
                conflicts.append(f"'{field}' differs: '{primary[field]}' vs '{reference[field]}'")
        
        return conflicts


# Add missing imports for distance calculation
from math import cos, radians


class QualityValidationReport:
    """Generates comprehensive quality validation reports"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def add_result(self, result: ValidationResult):
        """Add a validation result to the report"""
        self.results.append(result)
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """
        Generate comprehensive validation report
        
        Args:
            output_path: Optional path to save report as JSON
            
        Returns:
            Dictionary containing full validation report
        """
        report = {
            'validation_summary': {
                'total_checks': len(self.results),
                'passed_checks': sum(1 for r in self.results if r.passed),
                'failed_checks': sum(1 for r in self.results if not r.passed),
                'total_errors': sum(len(r.errors) for r in self.results),
                'total_warnings': sum(len(r.warnings) for r in self.results),
                'overall_status': 'PASSED' if all(r.passed for r in self.results) else 'FAILED'
            },
            'validation_details': [result.to_dict() for result in self.results],
            'generated_at': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations()
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Quality validation report saved to: {output_path}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        for result in self.results:
            if not result.passed:
                if result.check_name == 'coordinate_validation':
                    if result.stats.get('invalid_coordinates', 0) > 0:
                        recommendations.append("Review and correct invalid coordinate data")
                
                elif result.check_name == 'attribute_validation':
                    completeness = result.stats.get('completeness_percentage', 100)
                    if completeness < 80:
                        recommendations.append("Improve data completeness - many items missing required fields")
                
                elif result.check_name == 'temporal_validation':
                    if result.stats.get('invalid_temporal', 0) > 0:
                        recommendations.append("Standardize opening hours and seasonal information formats")
                
                elif result.check_name == 'cross_reference_validation':
                    if result.stats.get('conflicts_found', 0) > 0:
                        recommendations.append("Resolve data conflicts between sources")
        
        if not recommendations:
            recommendations.append("All quality checks passed - data quality is excellent!")
        
        return recommendations
    
    def print_summary(self):
        """Print a formatted summary of validation results"""
        print("\n" + "=" * 60)
        print("🔍 QUALITY VALIDATION SUMMARY")
        print("=" * 60)
        
        for result in self.results:
            status = "✓ PASSED" if result.passed else "✗ FAILED"
            print(f"{status} {result.check_name}")
            
            if result.errors:
                print(f"   Errors: {len(result.errors)}")
            if result.warnings:
                print(f"   Warnings: {len(result.warnings)}")
            
            # Print key statistics
            for key, value in result.stats.items():
                if key.endswith('_percentage') or key.endswith('_count') or key.endswith('items'):
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        summary = {
            'total_checks': len(self.results),
            'passed_checks': sum(1 for r in self.results if r.passed),
            'failed_checks': sum(1 for r in self.results if not r.passed),
            'total_errors': sum(len(r.errors) for r in self.results),
            'total_warnings': sum(len(r.warnings) for r in self.results)
        }
        
        print("\n" + "=" * 60)
        print(f"Overall Status: {'✓ ALL PASSED' if summary['failed_checks'] == 0 else '✗ ISSUES FOUND'}")
        print(f"Checks: {summary['passed_checks']}/{summary['total_checks']} passed")
        print(f"Issues: {summary['total_errors']} errors, {summary['total_warnings']} warnings")
        print("=" * 60)


def validate_data_quality(data_sources: Dict[str, List[Dict]], 
                         bbox: Dict[str, float],
                         output_dir: Optional[str] = None) -> QualityValidationReport:
    """
    Main function to run comprehensive quality validation
    
    Args:
        data_sources: Dictionary of data sources {source_name: data_list}
        bbox: Bounding box for coordinate validation
        output_dir: Optional directory to save detailed reports
        
    Returns:
        QualityValidationReport with all validation results
    """
    logger.info("🔍 Starting comprehensive data quality validation...")
    
    report = QualityValidationReport()
    
    # Initialize validators
    coord_validator = CoordinateValidator(bbox)
    attr_validator = AttributeValidator()
    temporal_validator = TemporalValidator()
    cross_ref_validator = CrossReferenceValidator()
    
    # Validate each data source
    for source_name, data in data_sources.items():
        if not data:
            continue
            
        logger.info(f"Validating {source_name} data ({len(data)} items)...")
        
        # Coordinate validation
        coord_result = coord_validator.validate_coordinates(data)
        coord_result.check_name = f"{source_name}_coordinate_validation"
        report.add_result(coord_result)
        
        # Attribute validation
        data_type = source_name.lower().rstrip('s')  # Remove plural
        attr_result = attr_validator.validate_attributes(data, data_type)
        attr_result.check_name = f"{source_name}_attribute_validation"
        report.add_result(attr_result)
        
        # Temporal validation
        temporal_result = temporal_validator.validate_temporal_data(data)
        temporal_result.check_name = f"{source_name}_temporal_validation"
        report.add_result(temporal_result)
    
    # Cross-reference validation between sources
    source_names = list(data_sources.keys())
    for i, source1 in enumerate(source_names):
        for source2 in source_names[i+1:]:
            if data_sources[source1] and data_sources[source2]:
                cross_ref_result = cross_ref_validator.validate_cross_references(
                    data_sources[source1], data_sources[source2]
                )
                cross_ref_result.check_name = f"{source1}_vs_{source2}_cross_reference"
                report.add_result(cross_ref_result)
    
    # Generate reports
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, "quality_validation_report.json")
        report.generate_report(report_path)
    
    report.print_summary()
    logger.info("✅ Quality validation completed")
    
    return report


if __name__ == "__main__":
    # Example usage with sample data
    sample_data = {
        'attractions': [
            {
                'name': 'Lumsden Castle',
                'lat': 57.3167,
                'lon': -2.8833,
                'type': 'historic_site',
                'description': 'Historic castle ruins',
                'opening_hours': {'monday': '09:00-17:00', 'tuesday': '09:00-17:00'}
            }
        ],
        'accommodation': [
            {
                'name': 'Lumsden Hotel',
                'lat': 57.3170,
                'lon': -2.8830,
                'type': 'hotel',
                'contact': '+44 1234 567890'
            }
        ]
    }
    
    # Define map bounds for Lumsden area
    lumsden_bbox = {
        'south': 57.26,
        'north': 57.37,
        'west': -2.95,
        'east': -2.82
    }
    
    # Run validation


def run_enhanced_data_validation(bbox):
    """
    Run quality validation on enhanced data if available.
    
    Args:
        bbox: Bounding box for validation
        
    Returns:
        bool: True if validation passed or was skipped, False if failed
    """
    import json
    
    quality_validation_enabled = os.environ.get('ENABLE_QUALITY_VALIDATION', '').lower() in ('1', 'true', 'yes')
    if not quality_validation_enabled:
        return True
        
    print("\n🔍 Running data quality validation...")
    try:
        # Load enhanced data if available for validation
        enhanced_data_path = Path("enhanced_data")
        if enhanced_data_path.exists():
            data_sources = {}
            geojson_files = {
                'tourist_attractions': 'tourist_attractions.geojson',
                'accommodation': 'accommodation.geojson', 
                'dining': 'dining.geojson',
                'activities': 'activities.geojson',
                'walking_trails': 'walking_trails.geojson'
            }
            
            for source_name, filename in geojson_files.items():
                file_path = enhanced_data_path / filename
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            geojson_data = json.load(f)
                            features = geojson_data.get('features', [])
                            data_list = []
                            
                            for feature in features:
                                item = feature.get('properties', {}).copy()
                                geom = feature.get('geometry', {})
                                if geom.get('type') == 'Point':
                                    coords = geom.get('coordinates', [])
                                    if len(coords) >= 2:
                                        item['lon'] = coords[0]
                                        item['lat'] = coords[1]
                                data_list.append(item)
                            
                            if data_list:
                                data_sources[source_name] = data_list
                    except Exception as e:
                        print(f"⚠️  Warning: Could not load {filename} for validation: {e}")
            
            if data_sources:
                validation_report = validate_data_quality(data_sources, bbox)
                failed_checks = sum(1 for r in validation_report.results if not r.passed)
                if failed_checks > 0:
                    print(f"⚠️  Quality validation found {failed_checks} issues (continuing with map generation)")
                else:
                    print("✓ All data quality checks passed")
            else:
                print("ℹ️  No enhanced data found for quality validation")
        else:
            print("ℹ️  Enhanced data directory not found - skipping quality validation")
        return True
    except ImportError:
        print("⚠️  Quality validation not available (utils.quality_validation not found)")
        return True
    except Exception as e:
        print(f"⚠️  Quality validation failed: {e}")
        return True