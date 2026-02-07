#!/usr/bin/env python3
"""
Update layout icon colors for MangoBar.

Usage:
    python scripts/update_icon_color.py <color>
    
Examples:
    python scripts/update_icon_color.py "#9d7cd8"  # Tokyo Night purple
    python scripts/update_icon_color.py "#7aa2f7"  # Tokyo Night blue
    python scripts/update_icon_color.py "#f7768e"  # Tokyo Night red
"""

import os
import sys
import re


def update_svg_color(svg_path, new_color):
    """Update the stroke color in an SVG file."""
    with open(svg_path, 'r') as f:
        content = f.read()
    
    # Replace any hex color in stroke attribute
    updated = re.sub(r'stroke="#[0-9a-fA-F]{6}"', f'stroke="{new_color}"', content)
    
    with open(svg_path, 'w') as f:
        f.write(updated)


def update_all_icons(color):
    """Update all layout icons with the specified color."""
    # Get the base directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    layouts_dir = os.path.join(base_dir, "assets", "layouts")
    
    if not os.path.exists(layouts_dir):
        print(f"Error: Layouts directory not found at {layouts_dir}")
        return False
    
    # Get all SVG files (excluding preview.html)
    svg_files = [f for f in os.listdir(layouts_dir) if f.endswith('.svg')]
    
    if not svg_files:
        print(f"Error: No SVG files found in {layouts_dir}")
        return False
    
    print(f"Updating {len(svg_files)} icon(s) to color: {color}")
    
    for svg_file in svg_files:
        svg_path = os.path.join(layouts_dir, svg_file)
        update_svg_color(svg_path, color)
        print(f"  ✓ {svg_file}")
    
    # Also update preview.html if it exists
    preview_path = os.path.join(layouts_dir, "preview.html")
    if os.path.exists(preview_path):
        with open(preview_path, 'r') as f:
            content = f.read()
        updated = re.sub(r'stroke="#[0-9a-fA-F]{6}"', f'stroke="{color}"', content)
        with open(preview_path, 'w') as f:
            f.write(updated)
        print(f"  ✓ preview.html")
    
    print(f"\n✅ Successfully updated all icons to {color}")
    print("   Restart MangoBar to see the changes.")
    return True


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        print("\nCommon Tokyo Night colors:")
        print("  Purple:  #9d7cd8")
        print("  Magenta: #bb9af7")
        print("  Blue:    #7aa2f7")
        print("  Cyan:    #7dcfff")
        print("  Green:   #9ece6a")
        print("  Red:     #f7768e")
        print("  Orange:  #ff9e64")
        print("  Yellow:  #e0af68")
        sys.exit(1)
    
    color = sys.argv[1]
    
    # Validate color format
    if not re.match(r'^#[0-9a-fA-F]{6}$', color):
        print(f"Error: Invalid color format '{color}'")
        print("Color must be in hex format: #RRGGBB (e.g., #9d7cd8)")
        sys.exit(1)
    
    if update_all_icons(color):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
