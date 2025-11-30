#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Visualizer - Generate visual diagram from SKILL layout code
Converts SKILL dbCreateParamInstByMasterName calls to visual representation
"""

import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Device type color mapping
# Color scheme:
# - Blue shades: Analog IO and power/ground
# - Green shades: Digital IO and capacitors
DEVICE_COLORS = {
    # Pad devices
    'PAD': '#FFD700',  # Gold
    'PAD60GU': '#FFD700',  # Gold
    
    # Analog IO devices (Blue shades)
    # PDB3AC (regular IO) and PVDD1AC/PVSS1AC (regular power/ground) have smaller color difference
    'PDB3AC': '#4A90E2',  # Medium blue - Analog bidirectional IO
    'PDB3AC_H_G': '#4A90E2',
    'PDB3AC_V_G': '#4A90E2',
    
    # Analog regular power/ground (Blue shades, close to PDB3AC)
    'PVDD1AC': '#5BA0F2',  # Slightly lighter blue - Analog regular power (VDD), close to PDB3AC
    'PVDD1AC_H_G': '#5BA0F2',
    'PVDD1AC_V_G': '#5BA0F2',
    'PVSS1AC': '#3A80D2',  # Slightly darker blue - Analog regular ground (VSS), close to PDB3AC
    'PVSS1AC_H_G': '#3A80D2',
    'PVSS1AC_V_G': '#3A80D2',
    
    # Analog voltage domain power/ground (Blue shades, more distinct from regular)
    # PVDD3AC/PVSS3AC and PVDD3A/PVSS3A have larger color difference
    'PVDD3AC': '#87CEEB',  # Light blue - Analog voltage domain power (VDD), more distinct
    'PVDD3AC_H_G': '#87CEEB',
    'PVDD3AC_V_G': '#87CEEB',
    'PVSS3AC': '#4682B4',  # Dark blue - Analog voltage domain ground (VSS), more distinct
    'PVSS3AC_H_G': '#4682B4',
    'PVSS3AC_V_G': '#4682B4',
    'PVDD3A': '#7EC8E3',  # Light blue - Analog voltage domain power (VDD), distinct from PVDD3AC
    'PVDD3A_H_G': '#7EC8E3',
    'PVDD3A_V_G': '#7EC8E3',
    'PVSS3A': '#3E7AB0',  # Dark blue - Analog voltage domain ground (VSS), distinct from PVSS3AC
    'PVSS3A_H_G': '#3E7AB0',
    'PVSS3A_V_G': '#3E7AB0',
    
    # Digital IO devices (Green shades)
    'PDDW16SDGZ': '#32CD32',  # Medium green - Digital IO
    'PDDW16SDGZ_H_G': '#32CD32',
    'PDDW16SDGZ_V_G': '#32CD32',
    
    # Digital power/ground (Green shades, different intensities)
    'PVDD1DGZ': '#90EE90',  # Light green - Digital power (VDD)
    'PVDD1DGZ_H_G': '#90EE90',
    'PVDD1DGZ_V_G': '#90EE90',
    'PVDD2POC': '#90EE90',  # Light green - Digital power (VDD)
    'PVDD2POC_V_G': '#90EE90',
    'PVSS1DGZ': '#228B22',  # Dark green - Digital ground (VSS)
    'PVSS1DGZ_H_G': '#228B22',
    'PVSS1DGZ_V_G': '#228B22',
    'PVSS2DGZ': '#228B22',  # Dark green - Digital ground (VSS)
    'PVSS2DGZ_H_G': '#228B22',
    'PVSS2DGZ_V_G': '#228B22',
    
    # Corner devices (Red shades - subtle difference for analog/digital)
    'PCORNERA': '#FF6B6B',  # Medium red - Analog corner
    'PCORNERA_G': '#FF6B6B',
    'PCORNER': '#FF8888',  # Slightly lighter red - Digital corner
    'PCORNER_G': '#FF8888',
    
    # Analog filler devices (Light gray - same color for 10 and 20)
    'PFILLER': '#D3D3D3',  # Light gray - Filler (default)
    'PFILLER10A_G': '#D8D8D8',  # Very light gray - Analog filler 10
    'PFILLER20A_G': '#D8D8D8',  # Very light gray - Analog filler 20
    
    # Digital filler devices (Light gray - same color for 10 and 20)
    'PFILLER10': '#C0C0C0',  # Light gray - Digital filler 10
    'PFILLER10_G': '#C0C0C0',
    'PFILLER20': '#C0C0C0',  # Light gray - Digital filler 20
    'PFILLER20_G': '#C0C0C0',
    'PRCUTA': '#A0A0A0',  # Gray - Separator
    'PRCUTA_G': '#A0A0A0',
    
    # Default
    'default': '#CCCCCC',  # Light gray
}

# Device dimensions (in SKILL units)
PAD_WIDTH = 20
PAD_HEIGHT = 110
CORNER_SIZE = 110  # Corner is square: 110×110
FILLER_WIDTH = 20  # Filler width: 20×110 (same as IO devices)
FILLER_HEIGHT = 110  # Filler height: 20×110 (same as IO devices)
INNER_PAD_WIDTH = 20  # Inner pad width: 20×110 (fills gap left by 10×110 filler)
INNER_PAD_HEIGHT = 110  # Inner pad height: 20×110
FILLER10_WIDTH = 10  # 10×110 filler (leaves 20×110 gap for inner pad)
FILLER10_HEIGHT = 110


def parse_skill_layout(il_file_path: str) -> List[Dict]:
    """
    Parse SKILL layout file and extract device information
    
    Returns list of device dictionaries with:
    - inst_name: instance name
    - cell_name: cell/master name
    - lib_name: library name
    - x, y: position coordinates
    - rotation: rotation angle (R0, R90, R180, R270)
    - device_type: extracted device type for coloring
    """
    devices = []
    
    with open(il_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match dbCreateParamInstByMasterName calls
    # dbCreateParamInstByMasterName(cv "lib" "cell" "view" "inst_name" list(x y) "rotation")
    pattern = r'dbCreateParamInstByMasterName\s*\(\s*cv\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"\s+list\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)\s+"([^"]+)"\s*\)'
    
    matches = re.findall(pattern, content)
    
    for match in matches:
        lib_name, cell_name, view_name, inst_name, x_str, y_str, rotation = match
        
        # Extract device type from cell name
        # Skip PAD60GU and PAD60NU (physical pad, not to be drawn)
        if cell_name == 'PAD60GU' or cell_name == 'PAD60NU' or \
           (cell_name.startswith('PAD') and ('60GU' in cell_name or '60NU' in cell_name)):
            # Skip physical pad devices
            continue
        
        device_type = cell_name
        device_category = 'io'  # Default category for IO devices
        
        # Check if this is an inner pad (dual ring pad)
        # Inner pads have instance names starting with "inner_pad_"
        is_inner_pad = inst_name.startswith('inner_pad_')
        
        # IO devices (PDB3AC, PVDD, PVSS, PDDW16SDGZ, PVDD1DGZ, PVSS1DGZ, etc.) - these are the actual IO cells to draw
        if 'PDB3AC' in cell_name or 'PVDD' in cell_name or 'PVSS' in cell_name or 'PDDW16SDGZ' in cell_name or 'PVDD1DGZ' in cell_name or 'PVSS1DGZ' in cell_name or 'PVSS2DGZ' in cell_name or 'PVDD2POC' in cell_name:
            device_type = cell_name
            if is_inner_pad:
                device_category = 'inner_pad'  # Inner pad (dual ring pad)
            else:
                device_category = 'io'  # IO device category
        elif 'CORNER' in cell_name or 'PCORNER' in cell_name:
            # Distinguish between analog corner (PCORNERA) and digital corner (PCORNER)
            if 'PCORNERA' in cell_name:
                device_type = 'PCORNERA'
            else:
                device_type = 'PCORNER'  # Digital corner
            device_category = 'corner'
        elif 'FILLER' in cell_name:
            # Distinguish between analog filler (PFILLER*A) and digital filler (PFILLER* without A)
            # Use the full cell_name as device_type so legend can distinguish them
            if 'A_G' in cell_name and 'PFILLER' in cell_name:
                device_type = cell_name  # Analog filler (PFILLER20A_G, PFILLER10A_G)
            else:
                device_type = cell_name  # Digital filler (PFILLER20_G, PFILLER10_G)
            device_category = 'filler'
            # Note: PFILLER10 and PFILLER10A are 10×110, PFILLER20 and PFILLER20A are 20×110
        elif 'RCUT' in cell_name:
            device_type = 'PRCUTA'
            device_category = 'filler'  # Separator is also a filler type
        
        devices.append({
            'inst_name': inst_name,
            'cell_name': cell_name,
            'lib_name': lib_name,
            'view_name': view_name,
            'x': float(x_str),
            'y': float(y_str),
            'rotation': rotation,
            'device_type': device_type,
            'device_category': device_category
        })
    
    return devices


def get_device_color(device_type: str) -> str:
    """Get color for device type"""
    # Try exact match first
    if device_type in DEVICE_COLORS:
        return DEVICE_COLORS[device_type]
    
    # Try prefix match
    for key, color in DEVICE_COLORS.items():
        if device_type.startswith(key):
            return color
    
    return DEVICE_COLORS['default']


def get_rectangle_for_rotation(x: float, y: float, rotation: str, width: float, height: float) -> Tuple[float, float, float, float]:
    """
    Calculate rectangle coordinates based on rotation
    Returns (x, y, width, height) for matplotlib Rectangle (bottom-left corner)
    
    All rectangles use R0 state's bottom-left corner as origin.
    In SKILL, the coordinate (x, y) needs to be converted to R0 state's bottom-left corner.
    
    Rotation meanings and coordinate conversion:
    - R0: horizontal, bottom-left at (x, y), width=20, height=110
    - R90: vertical up, SKILL coord (x,y) -> R0 bottom-left at (x-height, y), width=110, height=20
    - R180: horizontal left, SKILL coord (x,y) -> R0 bottom-left at (x-width, y-height), width=20, height=110
    - R270: vertical down, SKILL coord (x,y) -> R0 bottom-left at (x, y-height), width=110, height=20
    
    Based on actual SKILL coordinates:
    - R0 (bottom): y=0, x varies -> bottom-left at (x, 0)
    - R90 (right): x=400, y varies -> bottom-left at (400-height, y)
    - R180 (top): y=400, x varies -> bottom-left at (x-width, 400-height)
    - R270 (left): x=0, y varies -> bottom-left at (0, y-height)
    """
    is_square = (abs(width - height) < 0.1)  # Check if device is square (corner)
    
    if is_square:
        # Square device (corner): (x, y) is a specific corner position based on rotation
        # Need to convert to R0 state's bottom-left corner
        # Corner positions in SKILL:
        # - BL (bottom-left): (x, y) is bottom-left corner -> R0 bottom-left at (x, y)
        # - BR (bottom-right): (x, y) is bottom-right corner -> R0 bottom-left at (x - width, y)
        # - TL (top-left): (x, y) is top-left corner -> R0 bottom-left at (x, y - height)
        # - TR (top-right): (x, y) is top-right corner -> R0 bottom-left at (x - width, y - height)
        if rotation == 'R0':
            # BL corner: (x, y) is bottom-left
            return (x, y, width, height)
        elif rotation == 'R90':
            # BR corner: (x, y) is bottom-right, R0 bottom-left at (x - width, y)
            return (x - width, y, width, height)
        elif rotation == 'R180':
            # TR corner: (x, y) is top-right, R0 bottom-left at (x - width, y - height)
            return (x - width, y - height, width, height)
        elif rotation == 'R270':
            # TL corner: SKILL coord (x, y) is at top-left position
            # In SKILL: x is minimum (left), y is maximum (top)
            # R0 bottom-left at (x, y - height)
            return (x, y - height, width, height)
        else:
            return (x, y, width, height)
    else:
        # Rectangular device (IO, filler): convert SKILL coord to R0 bottom-left
        # SKILL coordinate system: x increases RIGHT, y increases UP
        if rotation == 'R0':
            # R0: SKILL coord (x, y) is at bottom edge (y is minimum)
            # Rectangle: horizontal, 20 wide x 110 high
            # R0 bottom-left at (x, y)
            return (x, y, width, height)
        elif rotation == 'R90':
            # R90: SKILL coord (x, y) is at right edge (x is maximum)
            # Rectangle: vertical, 110 wide x 20 high (rotated)
            # R0 bottom-left at (x - height, y)
            return (x - height, y, height, width)  # Swap dimensions
        elif rotation == 'R180':
            # R180: SKILL coord (x, y) is at top edge (y is maximum)
            # Rectangle: horizontal, 20 wide x 110 high (flipped)
            # R0 bottom-left at (x - width, y - height)
            return (x - width, y - height, width, height)
        elif rotation == 'R270':
            # R270: SKILL coord (x, y) is at left edge center
            # Rotated rectangle: vertical, 110 wide x 20 high, center at (x, y)
            # In R0 state: 20 wide x 110 high, horizontal
            # R0 left edge is at x, R0 center is at y_bl + height/2
            # So: y = y_bl + height/2 -> y_bl = y - height/2
            # Calculate offset mathematically:
            # Corner BL at (0, 0) R0 has top at y = 110
            # First filler at (0, 130) R270 should connect at y = 110
            # Formula: y_bl = y - height/2 + offset
            # So: 110 = 130 - 55 + offset -> offset = 35 (for 20x110 devices)
            # For 10x110 filler, offset needs to be adjusted: offset = 35 + 10 = 45
            if abs(width - 10) < 0.1:  # Check if this is a 10x110 filler
                offset = 45  # Adjusted offset for 10x110 filler (up by 10)
            else:
                offset = 35  # Offset for 20x110 devices
            return (x, y - height/2 + offset, height, width)  # Swap dimensions
        else:
            # Default to R0
            return (x, y, width, height)


def visualize_layout(il_file_path: str, output_path: Optional[str] = None) -> str:
    """
    Generate visual diagram from SKILL layout file
    
    Args:
        il_file_path: Path to SKILL layout file
        output_path: Optional output path for image (default: same directory as input with .png extension)
    
    Returns:
        Path to generated image file
    """
    # Parse SKILL file
    devices = parse_skill_layout(il_file_path)
    
    if not devices:
        raise ValueError(f"No devices found in {il_file_path}")
    
    # Include all devices: pads, corners, and fillers
    all_devices = devices
    
    # Calculate bounds from all devices
    all_x = [d['x'] for d in all_devices]
    all_y = [d['y'] for d in all_devices]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add padding for visualization
    padding = 50
    fig_width = max(max_x - min_x + 2 * padding, 400)
    fig_height = max(max_y - min_y + 2 * padding, 400)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(fig_width/50, fig_height/50))
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)
    ax.set_aspect('equal')
    # SKILL coordinates: x increases RIGHT, y increases UP (no inversion needed)
    ax.axis('off')
    
    # Sort pad devices by position to ensure proper ordering
    # Sort by side first (left, bottom, right, top), then by position along that side
    def get_sort_key(device):
        x, y = device['x'], device['y']
        rotation = device['rotation']
        # Determine which side based on rotation and position
        if rotation == 'R270':  # Left side
            return (0, y)  # Sort by y coordinate
        elif rotation == 'R0':  # Bottom side
            return (1, x)  # Sort by x coordinate
        elif rotation == 'R90':  # Right side
            return (2, -y)  # Sort by y coordinate (descending)
        elif rotation == 'R180':  # Top side
            return (3, -x)  # Sort by x coordinate (descending)
        else:
            return (4, 0)
    
    all_devices_sorted = sorted(all_devices, key=get_sort_key)
    
    # Draw each device (pads, corners, fillers)
    for device in all_devices_sorted:
        x, y = device['x'], device['y']
        rotation = device['rotation']
        device_type = device['device_type']
        device_category = device.get('device_category', 'pad')
        inst_name = device['inst_name']
        
        # Get color
        color = get_device_color(device_type)
        
        # Get device dimensions based on category
        if device_category == 'corner':
            width = CORNER_SIZE
            height = CORNER_SIZE
        elif device_category == 'inner_pad':
            # Inner pad (dual ring pad): 20×110 (fills gap left by 10×110 filler)
            width = INNER_PAD_WIDTH
            height = INNER_PAD_HEIGHT
        elif device_category == 'filler':
            # Filler size depends on type: PFILLER10/PFILLER10A are 10×110, PFILLER20/PFILLER20A are 20×110
            if 'PFILLER10' in device_type:
                width = FILLER10_WIDTH
                height = FILLER10_HEIGHT
            else:
                # PFILLER20 or default
                width = FILLER_WIDTH
                height = FILLER_HEIGHT
        else:  # io (IO devices like PDB3AC, PVDD, PVSS)
            # IO devices: 20×110
            width = PAD_WIDTH
            height = PAD_HEIGHT
        
        # Calculate rectangle based on rotation
        rect_x, rect_y, rect_w, rect_h = get_rectangle_for_rotation(
            x, y, rotation, width, height
        )
        
        # Create rectangle with thicker border for better visibility
        # Inner pads use dashed border to distinguish from regular IO devices
        if device_category == 'inner_pad':
            # Inner pad: dashed border using FancyBboxPatch for better style support
            rect = patches.FancyBboxPatch(
                (rect_x, rect_y), rect_w, rect_h,
                boxstyle='round,pad=0',
                linewidth=2, edgecolor='black', facecolor=color, alpha=0.8,
                linestyle='--'  # Dashed border for inner pad
            )
        else:
            rect = patches.Rectangle(
                (rect_x, rect_y), rect_w, rect_h,
                linewidth=2, edgecolor='black', facecolor=color, alpha=0.8
            )
        ax.add_patch(rect)
        
        # Add text label in center
        # Format: "信号名:设备类型" for IO devices, with full device type including suffixes
        if device_category == 'io' or device_category == 'inner_pad':
            # Extract signal name from instance name
            signal_name = inst_name
            # Clean up: remove side and position indicators if present
            # For regular IO: remove _(left|right|top|bottom)_\d+$
            # For inner pad: remove _(left|right|top|bottom)_\d+_\d+ (e.g., _left_0_1, _right_6_7)
            if device_category == 'inner_pad':
                # Remove "inner_pad_" prefix first
                signal_name = re.sub(r'^inner_pad_', '', signal_name)
                # Remove position indicators like _left_0_1, _right_6_7
                signal_name = re.sub(r'_(left|right|top|bottom)_\d+_\d+$', '', signal_name)
            else:
                # Regular IO: remove _(left|right|top|bottom)_\d+$
                signal_name = re.sub(r'_(left|right|top|bottom)_\d+$', '', signal_name)
            
            # Get device type (cell_name) - keep full format including suffixes for labels
            device_type_label = device['cell_name']
            
            # Format: "signal_name:device_type" (full format, including suffixes)
            label = f"{signal_name}:{device_type_label}"
        elif device_category == 'corner':
            # For corner devices, use the full cell name including suffixes (e.g., PCORNERA_G, PCORNER_G)
            label = device['cell_name']
        elif device_category == 'filler':
            # For fillers, use the full cell name including suffixes (e.g., PFILLER20A_G, PFILLER20_G, PRCUTA_G)
            label = device['cell_name']
        else:
            label = inst_name
            # Clean up label: remove side indicators if present
            label = re.sub(r'_(left|right|top|bottom)_\d+$', '', label)
        
        # Calculate center of rectangle
        center_x = rect_x + rect_w / 2
        center_y = rect_y + rect_h / 2
        
        # Adjust font size based on device size
        if device_category == 'corner':
            font_size = 8
        elif device_category == 'filler':
            font_size = 6
        elif device_category == 'inner_pad':
            font_size = 7  # Same as IO devices
        else:  # io (IO devices)
            font_size = 7
        
        # Determine text rotation to align with rectangle's long edge
        # In R0 state: rectangle is 20 wide x 110 high (long edge is vertical)
        # After rotation, we need to check the actual displayed dimensions
        # R0, R180: rectangle is horizontal (20 wide), long edge vertical -> text should be vertical (90 degrees)
        # R90, R270: rectangle is vertical (110 wide), long edge horizontal -> text should be horizontal (0 degrees)
        if rotation == 'R0' or rotation == 'R180':
            # Horizontal rectangle: long edge is vertical, text should be vertical
            text_rotation = 90
        elif rotation == 'R90' or rotation == 'R270':
            # Vertical rectangle: long edge is horizontal, text should be horizontal
            text_rotation = 0
        else:
            text_rotation = 0
        
        # Add text with better contrast and rotation aligned with long edge
        # Use single text label for all devices (simple and no overlap)
        ax.text(center_x, center_y, label, 
                ha='center', va='center', 
                rotation=text_rotation,
                fontsize=font_size, fontweight='bold',
                color='black', 
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
    
    # Add title
    ax.set_title('IO Ring Layout Visualization', fontsize=14, fontweight='bold', pad=20)
    
    # Add legend - separate digital and analog IO devices
    device_types_found = set(d['device_type'] for d in all_devices)
    
    # Categorize devices
    digital_io_types = []
    analog_io_types = []
    other_types = []
    
    for dev_type in sorted(device_types_found):
        # Check if it's a digital IO device
        if 'PDDW16SDGZ' in dev_type or 'PVDD1DGZ' in dev_type or 'PVSS1DGZ' in dev_type or 'PVSS2DGZ' in dev_type or 'PVDD2POC' in dev_type:
            digital_io_types.append(dev_type)
        # Check if it's an analog IO device
        elif 'PDB3AC' in dev_type or 'PVDD1AC' in dev_type or 'PVSS1AC' in dev_type or 'PVDD3AC' in dev_type or 'PVSS3AC' in dev_type or 'PVDD3A' in dev_type or 'PVSS3A' in dev_type:
            analog_io_types.append(dev_type)
        else:
            other_types.append(dev_type)
    
    # Build legend elements with grouping
    legend_elements = []
    
    # Add header for digital IO (green shades)
    if digital_io_types:
        legend_elements.append(patches.Patch(facecolor='none', edgecolor='none', label='Digital IO (Green Shades)'))
        for dev_type in sorted(digital_io_types):
            color = get_device_color(dev_type)
            legend_label = re.sub(r'_V_G$', '', dev_type)
            legend_label = re.sub(r'_H_G$', '', legend_label)
            legend_label = re.sub(r'_V$', '', legend_label)
            legend_label = re.sub(r'_H$', '', legend_label)
            legend_label = re.sub(r'_G$', '', legend_label)
            legend_elements.append(patches.Patch(facecolor=color, edgecolor='black', label=legend_label))
    
    # Add header for analog IO (blue shades)
    if analog_io_types:
        legend_elements.append(patches.Patch(facecolor='none', edgecolor='none', label='Analog IO (Blue Shades)'))
        for dev_type in sorted(analog_io_types):
            color = get_device_color(dev_type)
            legend_label = re.sub(r'_V_G$', '', dev_type)
            legend_label = re.sub(r'_H_G$', '', legend_label)
            legend_label = re.sub(r'_V$', '', legend_label)
            legend_label = re.sub(r'_H$', '', legend_label)
            legend_label = re.sub(r'_G$', '', legend_label)
            legend_elements.append(patches.Patch(facecolor=color, edgecolor='black', label=legend_label))
    
    # Add other devices (corners, fillers, etc.) with header
    if other_types:
        legend_elements.append(patches.Patch(facecolor='none', edgecolor='none', label='Other Components'))
        for dev_type in sorted(other_types):
            color = get_device_color(dev_type)
            legend_label = re.sub(r'_V_G$', '', dev_type)
            legend_label = re.sub(r'_H_G$', '', legend_label)
            legend_label = re.sub(r'_V$', '', legend_label)
            legend_label = re.sub(r'_H$', '', legend_label)
            legend_label = re.sub(r'_G$', '', legend_label)
            legend_elements.append(patches.Patch(facecolor=color, edgecolor='black', label=legend_label))
    
    if legend_elements:
        # Position legend in upper right, but outside the plot area to avoid overlap
        ax.legend(handles=legend_elements, 
                 loc='upper left',
                 bbox_to_anchor=(1.02, 1.0),
                 fontsize=8,
                 frameon=True,
                 fancybox=True,
                 shadow=False,
                 handlelength=1.5)
    
    # Save figure
    if output_path is None:
        il_path = Path(il_file_path)
        output_path = il_path.parent / f"{il_path.stem}_visualization.png"
    else:
        output_path = Path(output_path)
    
    # Adjust layout to make room for legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Leave 15% space on the right for legend
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return str(output_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python layout_visualizer.py <il_file_path> [output_path]")
        sys.exit(1)
    
    il_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result_path = visualize_layout(il_file, output_file)
        print(f"✅ Visualization saved to: {result_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

