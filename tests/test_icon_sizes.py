"""Test icon sizes to ensure consistency"""

import xml.etree.ElementTree as ET
from pathlib import Path


def test_question_mark_icon_size():
    """Test that the question mark icon has the correct size (14px)"""
    icon_path = Path("icons/question-1445-svgrepo-com.svg")
    
    # Parse the SVG file
    tree = ET.parse(icon_path)
    root = tree.getroot()
    
    # Check width and height attributes
    width = root.get("width")
    height = root.get("height")
    
    assert width == "14px", f"Expected width to be 14px, but got {width}"
    assert height == "14px", f"Expected height to be 14px, but got {height}"


def test_symlinked_icons_point_to_question_mark():
    """Test that placeholder icons are symlinked to the question mark icon"""
    question_mark_path = Path("icons/question-1445-svgrepo-com.svg")
    
    # Icons that should be symlinked to the question mark
    symlinked_icons = [
        "icons/palette-14.svg",
        "icons/rock-14.svg",
        "icons/ruins-14.svg",
    ]
    
    for icon_name in symlinked_icons:
        icon_path = Path(icon_name)
        
        # Check if it's a symlink
        assert icon_path.is_symlink(), f"{icon_name} should be a symlink"
        
        # Check if it points to the question mark icon
        target = icon_path.resolve()
        expected = question_mark_path.resolve()
        
        assert target == expected, (
            f"{icon_name} should point to question-1445-svgrepo-com.svg, "
            f"but points to {target}"
        )


def test_icon_size_consistency():
    """Test that all -14 icons have consistent sizing"""
    icons_dir = Path("icons")
    
    # Find all -14.svg icons
    icon_14_files = list(icons_dir.glob("*-14.svg"))
    
    assert len(icon_14_files) > 0, "Should have at least one -14.svg icon"
    
    for icon_path in icon_14_files:
        # Skip symlinks, we only check actual files
        if icon_path.is_symlink():
            continue
            
        try:
            tree = ET.parse(icon_path)
            root = tree.getroot()
            
            # Get viewBox to understand the coordinate system
            viewBox = root.get("viewBox")
            
            # Most -14 icons should have viewBox="0 0 14 14" or similar
            # The question mark has a different viewBox but width/height should be 14px
            width = root.get("width")
            height = root.get("height")
            
            # If width and height are specified, they should be reasonable
            # (14px is correct, but some may use 100% with viewBox)
            if width and "px" in width:
                size = int(width.replace("px", ""))
                assert 10 <= size <= 20, (
                    f"{icon_path.name} has unusual pixel size: {width}. "
                    f"Expected around 14px for consistency."
                )
            
        except ET.ParseError:
            # Some files might not be valid XML (like the 404 error page)
            pass
