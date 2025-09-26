#!/usr/bin/env python3
"""
Tests for quality validation system
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from utils.quality_validation import (
    AttributeValidator,
    CoordinateValidator,
    CrossReferenceValidator,
    QualityValidationReport,
    TemporalValidator,
    ValidationResult,
    validate_data_quality,
)


class TestValidationResult:
    """Test ValidationResult container"""

    @pytest.mark.unit
    def test_validation_result_initialization(self):
        """Test ValidationResult initialization"""
        result = ValidationResult("test_check")
        assert result.check_name == "test_check"
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []
        assert result.details == {}
        assert result.stats == {}

    @pytest.mark.unit
    def test_add_error(self):
        """Test adding errors to validation result"""
        result = ValidationResult("test_check")
        result.add_error("Test error", {"detail": "value"})

        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
        assert "error_1" in result.details

    @pytest.mark.unit
    def test_add_warning(self):
        """Test adding warnings to validation result"""
        result = ValidationResult("test_check")
        result.add_warning("Test warning", {"detail": "value"})

        assert result.passed is True  # Warnings don't fail the check
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"
        assert "warning_1" in result.details

    @pytest.mark.unit
    def test_to_dict(self):
        """Test converting validation result to dictionary"""
        result = ValidationResult("test_check")
        result.add_error("Error")
        result.update_stats("count", 5)

        result_dict = result.to_dict()

        assert result_dict["check_name"] == "test_check"
        assert result_dict["passed"] is False
        assert len(result_dict["errors"]) == 1
        assert result_dict["stats"]["count"] == 5


class TestCoordinateValidator:
    """Test coordinate validation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.bbox = {"south": 57.26, "north": 57.37, "west": -2.95, "east": -2.82}
        self.validator = CoordinateValidator(self.bbox)

    @pytest.mark.unit
    def test_valid_coordinates_within_bounds(self):
        """Test validation of valid coordinates within bounds"""
        data = [
            {"lat": 57.32, "lon": -2.88, "name": "Test Point 1"},
            {"lat": 57.30, "lon": -2.85, "name": "Test Point 2"},
        ]

        result = self.validator.validate_coordinates(data)

        assert result.passed is True
        assert len(result.errors) == 0
        assert result.stats["valid_coordinates"] == 2
        assert result.stats["invalid_coordinates"] == 0

    @pytest.mark.unit
    def test_coordinates_out_of_bounds(self):
        """Test coordinates outside map bounds generate warnings"""
        data = [
            {"lat": 57.50, "lon": -2.88, "name": "Out of bounds"},  # North of bounds
            {"lat": 57.32, "lon": -2.88, "name": "Within bounds"},
        ]

        result = self.validator.validate_coordinates(data)

        assert result.passed is True  # Out of bounds is warning, not error
        assert len(result.warnings) == 1
        assert result.stats["out_of_bounds"] == 1
        assert result.stats["valid_coordinates"] == 1

    @pytest.mark.unit
    def test_invalid_coordinates(self):
        """Test invalid coordinate values"""
        data = [
            {"lat": 200, "lon": -2.88, "name": "Invalid lat"},  # Invalid latitude
            {"lat": 57.32, "lon": -300, "name": "Invalid lon"},  # Invalid longitude
            {"lat": None, "lon": -2.88, "name": "Missing lat"},  # Missing coordinate
        ]

        result = self.validator.validate_coordinates(data)

        assert result.passed is False
        assert len(result.errors) == 3
        assert result.stats["invalid_coordinates"] == 3

    @pytest.mark.unit
    def test_geojson_coordinate_extraction(self):
        """Test coordinate extraction from GeoJSON format"""
        data = [
            {
                "name": "GeoJSON Point",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-2.88, 57.32],  # GeoJSON format [lon, lat]
                },
            }
        ]

        result = self.validator.validate_coordinates(data)

        assert result.passed is True
        assert result.stats["valid_coordinates"] == 1

    @pytest.mark.unit
    def test_missing_coordinates(self):
        """Test handling of items without coordinates"""
        data = [{"name": "No coordinates"}, {"description": "Also no coordinates"}]

        result = self.validator.validate_coordinates(data)

        assert result.passed is False
        assert len(result.errors) == 2
        assert result.stats["invalid_coordinates"] == 2


class TestAttributeValidator:
    """Test attribute validation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = AttributeValidator()

    @pytest.mark.unit
    def test_complete_attributes(self):
        """Test validation with complete attributes"""
        data = [
            {
                "name": "Complete Accommodation",
                "type": "hotel",
                "contact": "+44 1234 567890",
            }
        ]

        result = self.validator.validate_attributes(data, "accommodation")

        assert result.passed is True
        assert result.stats["complete_items"] == 1
        assert result.stats["completeness_percentage"] == 100

    @pytest.mark.unit
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        data = [
            {
                "name": "Incomplete Item",
                # Missing 'type' and 'contact' for accommodation
            }
        ]

        result = self.validator.validate_attributes(data, "accommodation")

        assert result.passed is False
        assert len(result.errors) == 1
        assert result.stats["incomplete_items"] == 1
        assert result.stats["completeness_percentage"] == 0

    @pytest.mark.unit
    def test_empty_required_fields(self):
        """Test validation with empty required fields"""
        data = [
            {
                "name": "Empty Fields",
                "type": "",  # Empty string
                "contact": "   ",  # Whitespace only
            }
        ]

        result = self.validator.validate_attributes(data, "accommodation")

        assert result.passed is False
        assert len(result.errors) == 1
        assert "Empty fields: ['type', 'contact']" in result.errors[0]

    @pytest.mark.unit
    def test_custom_required_fields(self):
        """Test validation with custom required fields"""
        custom_validator = AttributeValidator({"custom": ["field1", "field2"]})

        data = [
            {"field1": "value1", "field2": "value2"},
            {"field1": "value1"},  # Missing field2
        ]

        result = custom_validator.validate_attributes(data, "custom")

        assert result.passed is False
        assert result.stats["complete_items"] == 1
        assert result.stats["incomplete_items"] == 1

    @pytest.mark.unit
    def test_unknown_data_type(self):
        """Test validation with unknown data type uses default rules"""
        data = [{"name": "Test"}]

        result = self.validator.validate_attributes(data, "unknown_type")

        # Should pass because no required fields defined for unknown type
        assert result.passed is True


class TestTemporalValidator:
    """Test temporal validation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = TemporalValidator()

    @pytest.mark.unit
    def test_valid_opening_hours_dict(self):
        """Test validation of opening hours in dictionary format"""
        data = [
            {
                "name": "Test Venue",
                "opening_hours": {
                    "monday": "09:00-17:00",
                    "tuesday": "09:00-17:00",
                    "wednesday": "closed",
                },
            }
        ]

        result = self.validator.validate_temporal_data(data)

        assert result.passed is True
        assert result.stats["valid_temporal"] == 1
        assert result.stats["invalid_temporal"] == 0

    @pytest.mark.unit
    def test_valid_opening_hours_string(self):
        """Test validation of opening hours in string format"""
        data = [
            {"name": "Always Open", "opening_hours": "24/7"},
            {"name": "Closed", "opening_hours": "closed"},
            {"name": "Time Range", "opening_hours": "09:00-17:00"},
        ]

        result = self.validator.validate_temporal_data(data)

        assert result.passed is True
        assert result.stats["valid_temporal"] == 3

    @pytest.mark.unit
    def test_invalid_opening_hours(self):
        """Test validation of invalid opening hours format"""
        data = [
            {
                "name": "Invalid Hours",
                "opening_hours": {
                    "invalid_day": "09:00-17:00",  # Invalid day name
                    "monday": "25:00-17:00",  # Invalid time
                },
            }
        ]

        result = self.validator.validate_temporal_data(data)

        assert result.passed is False
        assert len(result.errors) == 1
        assert result.stats["invalid_temporal"] == 1

    @pytest.mark.unit
    def test_seasonal_info_validation(self):
        """Test validation of seasonal information"""
        data = [
            {"name": "Summer Only", "seasonal_info": "Open April to October"},
            {"name": "Year Round", "seasonal_info": "Open year-round"},
            {"name": "Invalid Season", "seasonal_info": "xyz123"},
        ]

        result = self.validator.validate_temporal_data(data)

        # Should pass with warnings for unclear seasonal info
        assert result.passed is True
        assert len(result.warnings) >= 1  # Invalid season should generate warning

    @pytest.mark.unit
    def test_no_temporal_data(self):
        """Test handling of items without temporal information"""
        data = [{"name": "No temporal data"}]

        result = self.validator.validate_temporal_data(data)

        assert result.passed is True
        assert result.stats["no_temporal_data"] == 1


class TestCrossReferenceValidator:
    """Test cross-reference validation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = CrossReferenceValidator()

    @pytest.mark.unit
    def test_exact_name_match(self):
        """Test cross-reference validation with exact name matches"""
        primary_data = [{"name": "Test Location", "lat": 57.32, "lon": -2.88}]
        reference_data = [
            {"name": "Test Location", "lat": 57.32, "lon": -2.88, "type": "restaurant"}
        ]

        result = self.validator.validate_cross_references(primary_data, reference_data)

        assert result.passed is True
        assert result.stats["matches_found"] == 1
        assert result.stats["conflicts_found"] == 0

    @pytest.mark.unit
    def test_location_based_match(self):
        """Test cross-reference validation with location-based matching"""
        primary_data = [{"name": "Primary Location", "lat": 57.32, "lon": -2.88}]
        reference_data = [
            {"name": "Reference Location", "lat": 57.3201, "lon": -2.8801}  # Very close
        ]

        result = self.validator.validate_cross_references(primary_data, reference_data)

        assert result.stats["matches_found"] == 1

    @pytest.mark.unit
    def test_data_conflicts(self):
        """Test detection of data conflicts between sources"""
        primary_data = [
            {"name": "Test Restaurant", "type": "italian", "lat": 57.32, "lon": -2.88}
        ]
        reference_data = [
            {
                "name": "Test Restaurant",
                "type": "french",
                "lat": 57.32,
                "lon": -2.88,
            }  # Conflict in type
        ]

        result = self.validator.validate_cross_references(primary_data, reference_data)

        assert result.passed is False
        assert result.stats["conflicts_found"] == 1
        assert len(result.errors) == 1

    @pytest.mark.unit
    def test_missing_references(self):
        """Test handling of items with no cross-references"""
        primary_data = [{"name": "Unique Location", "lat": 57.32, "lon": -2.88}]
        reference_data = [{"name": "Different Location", "lat": 57.35, "lon": -2.85}]

        result = self.validator.validate_cross_references(primary_data, reference_data)

        assert result.passed is True  # Missing references are warnings, not errors
        assert result.stats["missing_references"] == 1
        assert len(result.warnings) == 1

    @pytest.mark.unit
    def test_coordinate_conflict_detection(self):
        """Test detection of coordinate conflicts"""
        primary_data = [{"name": "Test Location", "lat": 57.32, "lon": -2.88}]
        reference_data = [
            {"name": "Test Location", "lat": 57.35, "lon": -2.85}  # Different location
        ]

        result = self.validator.validate_cross_references(primary_data, reference_data)

        assert result.passed is False
        assert result.stats["conflicts_found"] == 1
        assert "Location differs by" in result.errors[0]


class TestQualityValidationReport:
    """Test quality validation reporting functionality"""

    @pytest.mark.unit
    def test_report_generation(self):
        """Test generation of quality validation report"""
        report = QualityValidationReport()

        # Add some test results
        result1 = ValidationResult("test_check_1")
        result1.add_error("Test error")
        result1.update_stats("count", 5)

        result2 = ValidationResult("test_check_2")
        result2.update_stats("count", 3)

        report.add_result(result1)
        report.add_result(result2)

        # Generate report
        report_dict = report.generate_report()

        assert report_dict["validation_summary"]["total_checks"] == 2
        assert report_dict["validation_summary"]["passed_checks"] == 1
        assert report_dict["validation_summary"]["failed_checks"] == 1
        assert report_dict["validation_summary"]["total_errors"] == 1
        assert report_dict["validation_summary"]["overall_status"] == "FAILED"

        assert len(report_dict["validation_details"]) == 2
        assert "generated_at" in report_dict
        assert "recommendations" in report_dict

    @pytest.mark.unit
    def test_report_file_output(self):
        """Test saving report to file"""
        report = QualityValidationReport()
        result = ValidationResult("test_check")
        report.add_result(result)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            report_dict = report.generate_report(temp_path)

            # Verify file was created and contains valid JSON
            assert os.path.exists(temp_path)
            with open(temp_path, "r") as f:
                saved_report = json.load(f)

            assert saved_report["validation_summary"]["total_checks"] == 1
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_recommendations_generation(self):
        """Test generation of recommendations"""
        report = QualityValidationReport()

        # Add failing coordinate validation
        coord_result = ValidationResult("coordinate_validation")
        coord_result.add_error("Invalid coordinates")
        coord_result.update_stats("invalid_coordinates", 5)

        # Add failing attribute validation
        attr_result = ValidationResult("attribute_validation")
        attr_result.add_error("Missing fields")
        attr_result.update_stats("completeness_percentage", 60)

        report.add_result(coord_result)
        report.add_result(attr_result)

        report_dict = report.generate_report()
        recommendations = report_dict["recommendations"]

        assert len(recommendations) >= 2
        assert any("coordinate" in rec.lower() for rec in recommendations)
        assert any("completeness" in rec.lower() for rec in recommendations)


class TestQualityValidationIntegration:
    """Test integration of quality validation system"""

    @pytest.mark.integration
    def test_validate_data_quality_complete_workflow(self):
        """Test complete quality validation workflow"""
        data_sources = {
            "attractions": [
                {
                    "name": "Test Attraction",
                    "lat": 57.32,
                    "lon": -2.88,
                    "type": "historic_site",
                    "description": "Test description",
                    "opening_hours": {"monday": "09:00-17:00"},
                }
            ],
            "accommodation": [
                {
                    "name": "Test Hotel",
                    "lat": 57.31,
                    "lon": -2.87,
                    "type": "hotel",
                    "contact": "+44 1234 567890",
                }
            ],
        }

        bbox = {"south": 57.26, "north": 57.37, "west": -2.95, "east": -2.82}

        # Run validation
        report = validate_data_quality(data_sources, bbox)

        # Verify report structure
        assert len(report.results) > 0

        # Should have coordinate, attribute, and temporal validation for each source
        check_names = [result.check_name for result in report.results]
        assert any("coordinate_validation" in name for name in check_names)
        assert any("attribute_validation" in name for name in check_names)
        assert any("temporal_validation" in name for name in check_names)

    @pytest.mark.integration
    def test_validate_with_output_directory(self):
        """Test validation with output directory specified"""
        data_sources = {"test_data": [{"name": "Test", "lat": 57.32, "lon": -2.88}]}

        bbox = {"south": 57.0, "north": 57.5, "west": -3.0, "east": -2.5}

        with tempfile.TemporaryDirectory() as temp_dir:
            report = validate_data_quality(data_sources, bbox, temp_dir)

            # Verify report file was created
            report_file = os.path.join(temp_dir, "quality_validation_report.json")
            assert os.path.exists(report_file)

            # Verify file contains valid JSON
            with open(report_file, "r") as f:
                saved_report = json.load(f)
            assert "validation_summary" in saved_report

    @pytest.mark.integration
    def test_empty_data_sources(self):
        """Test validation with empty data sources"""
        data_sources = {}
        bbox = {"south": 57.0, "north": 57.5, "west": -3.0, "east": -2.5}

        report = validate_data_quality(data_sources, bbox)

        # Should complete without errors even with no data
        assert len(report.results) == 0

    @pytest.mark.integration
    def test_validation_with_problematic_data(self):
        """Test validation with various data quality issues"""
        data_sources = {
            "problematic_data": [
                # Missing coordinates
                {"name": "No Location"},
                # Invalid coordinates
                {"name": "Bad Location", "lat": 200, "lon": -300},
                # Missing required fields
                {"name": "Incomplete", "lat": 57.32, "lon": -2.88},
                # Invalid temporal data
                {
                    "name": "Bad Hours",
                    "lat": 57.32,
                    "lon": -2.88,
                    "opening_hours": {"invalid_day": "25:00-30:00"},
                },
            ]
        }

        bbox = {"south": 57.0, "north": 57.5, "west": -3.0, "east": -2.5}

        report = validate_data_quality(data_sources, bbox)

        # Should detect multiple issues
        total_errors = sum(len(result.errors) for result in report.results)
        total_warnings = sum(len(result.warnings) for result in report.results)

        assert total_errors > 0 or total_warnings > 0


if __name__ == "__main__":
    pytest.main([__file__])
