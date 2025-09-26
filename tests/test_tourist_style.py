"""Tests for tourist.xml style validation and pattern matching improvements."""

import os
import re
import xml.etree.ElementTree as ET

import pytest


class TestTouristStyleXML:
    """Test suite for validating tourist.xml style file."""

    @pytest.fixture
    def tourist_xml_path(self):
        """Get path to tourist.xml file."""
        return os.path.join(os.path.dirname(__file__), "..", "styles", "tourist.xml")

    @pytest.fixture
    def tourist_xml_tree(self, tourist_xml_path):
        """Parse tourist.xml file."""
        assert os.path.exists(
            tourist_xml_path
        ), f"tourist.xml not found at {tourist_xml_path}"
        return ET.parse(tourist_xml_path)

    def test_tourist_xml_is_valid_xml(self, tourist_xml_tree):
        """Test that tourist.xml is valid XML."""
        root = tourist_xml_tree.getroot()
        assert root.tag == "Map"
        assert root is not None

    def test_tourist_xml_has_poi_style(self, tourist_xml_tree):
        """Test that tourist.xml contains the poi style section."""
        root = tourist_xml_tree.getroot()
        poi_styles = [
            style for style in root.findall("Style") if style.get("name") == "poi"
        ]
        assert len(poi_styles) == 1, "Expected exactly one poi style"

    def test_filter_patterns_use_regex_grouping(self, tourist_xml_tree):
        """Test that filter patterns use efficient regex grouping instead of multiple .match() calls."""
        root = tourist_xml_tree.getroot()

        # Find all Filter elements that contain .match() calls
        filter_elements = []
        for style in root.findall("Style"):
            for rule in style.findall("Rule"):
                for filter_elem in rule.findall("Filter"):
                    if filter_elem.text and ".match(" in filter_elem.text:
                        filter_elements.append(filter_elem.text.strip())

        assert len(filter_elements) > 0, "Should have at least some .match() filters"

        # Check for inefficient patterns with multiple .match() calls joined by 'or'
        inefficient_patterns = []
        for filter_text in filter_elements:
            # Count occurrences of .match( in the same filter
            match_count = filter_text.count(".match(")
            or_count = filter_text.count(" or ")

            # If there are multiple .match() calls with 'or' connectors, it could be optimized
            if match_count > 1 and or_count >= (match_count - 1):
                # This might be an inefficient pattern - check if it's a simple case that could use grouping
                if self._could_use_regex_grouping(filter_text):
                    inefficient_patterns.append(filter_text)

        # After improvements, there should be no inefficient patterns
        assert len(inefficient_patterns) == 0, (
            f"Found {len(inefficient_patterns)} filter patterns that could use regex grouping:\n"
            + "\n".join(f"- {pattern}" for pattern in inefficient_patterns)
        )

    def _could_use_regex_grouping(self, filter_text):
        """Check if a filter could benefit from regex grouping."""
        # Look for patterns like: [tag].match('.*prefix.*value1.*') or [tag].match('.*prefix.*value2.*')
        # These could be combined into: [tag].match('.*prefix.*(value1|value2).*')

        # Find all .match() calls with their patterns
        match_pattern = r"\[([^\]]+)\]\.match\('([^']+)'\)"
        matches = re.findall(match_pattern, filter_text)

        if len(matches) < 2:
            return False

        # Check if all matches use the same tag/attribute
        tags = [match[0] for match in matches]
        if len(set(tags)) > 1:
            return False  # Different tags, can't group

        # Check if the patterns have a common prefix/suffix structure
        patterns = [match[1] for match in matches]

        # Simple heuristic: if patterns start and end the same way, they might be groupable
        # For example: '.*amenity.*restaurant.*' and '.*amenity.*cafe.*'
        if len(patterns) >= 2:
            # Look for common prefixes that end with .* and common suffixes that start with .*
            first_pattern = patterns[0]
            common_prefix = ""
            common_suffix = ""

            # Find common prefix ending with .*
            for pattern in patterns[1:]:
                prefix = os.path.commonprefix([first_pattern, pattern])
                if prefix.endswith(".*"):
                    common_prefix = prefix
                    break

            # Find common suffix starting with .*
            for pattern in patterns[1:]:
                # Reverse strings to find common suffix
                suffix = os.path.commonprefix([first_pattern[::-1], pattern[::-1]])[
                    ::-1
                ]
                if suffix.startswith(".*"):
                    common_suffix = suffix
                    break

            # If we have both common prefix and suffix, this could probably be grouped
            if common_prefix and common_suffix:
                return True

        return False

    def test_specific_poi_categories_exist(self, tourist_xml_tree):
        """Test that expected POI categories are present in the style."""
        root = tourist_xml_tree.getroot()

        # Get all Filter elements from the poi style
        poi_style = None
        for style in root.findall("Style"):
            if style.get("name") == "poi":
                poi_style = style
                break

        assert poi_style is not None, "POI style not found"

        filter_texts = []
        for rule in poi_style.findall("Rule"):
            for filter_elem in rule.findall("Filter"):
                if filter_elem.text:
                    filter_texts.append(filter_elem.text.strip())

        # Check for expected categories
        expected_keywords = [
            "restaurant",
            "cafe",
            "pub",  # Food & Drink
            "hotel",
            "guest_house",
            "hostel",
            "chalet",
            "camp_site",  # Accommodation
            "bank",
            "post_office",  # Services
            "hospital",
            "pharmacy",
            "clinic",  # Healthcare
            "museum",
            "attraction",
            "viewpoint",  # Attractions
        ]

        filter_text_combined = " ".join(filter_texts)
        missing_keywords = []
        for keyword in expected_keywords:
            if keyword not in filter_text_combined:
                missing_keywords.append(keyword)

        assert (
            len(missing_keywords) == 0
        ), f"Missing expected POI keywords: {missing_keywords}"
