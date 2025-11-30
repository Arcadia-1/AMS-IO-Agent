#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Filler Component Generation Module
"""

from typing import List
from .device_classifier import DeviceClassifier
from .voltage_domain import VoltageDomainHandler
from .filler_generator import FillerGenerator
from .position_calculator import PositionCalculator
from .inner_pad_handler import InnerPadHandler

class AutoFillerGenerator:
    """Auto Filler Component Generator"""
    
    def __init__(self, config: dict):
        self.config = config
        self.position_calculator = PositionCalculator(config)
        self.inner_pad_handler = InnerPadHandler(config)
    
    def auto_insert_fillers_with_inner_pads(self, layout_components: List[dict], inner_pads: List[dict]) -> List[dict]:
        """Auto-insert filler components, supporting inner pad space reservation, compatible with clockwise and counterclockwise placement"""
        # Check if filler components are already included
        existing_fillers = [comp for comp in layout_components if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", ""))]
        existing_separators = [comp for comp in layout_components if comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", ""))]
        
        if existing_fillers or existing_separators:
            print(f"🔍 Detected filler components in intent graph: {len(existing_fillers)} fillers, {len(existing_separators)} separators")
            print("📝 Skipping auto-filler generation, using components defined in intent graph")
            return layout_components
        
        # Get placement order
        placement_order = self.config.get("placement_order", "counterclockwise")
        
        # Sort components by position
        sorted_components = self.position_calculator.sort_components_by_position(layout_components, placement_order)
        
        # Separate pads and corners
        pads = [comp for comp in sorted_components if comp.get("type") == "pad"]
        corners = [comp for comp in sorted_components if comp.get("type") == "corner"]
        
        # Group pads by orientation
        oriented_pads = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pad in pads:
            orientation = pad.get("orientation", "")
            if orientation in oriented_pads:
                oriented_pads[orientation].append(pad)
        
        # Sort pads by orientation (adjust based on placement order)
        for orientation in oriented_pads:
            if placement_order == "clockwise":
                # Clockwise sorting
                if orientation == "R180":  # Top edge, left to right
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0])
                elif orientation == "R90":  # Right edge, top to bottom
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1], reverse=True)
                elif orientation == "R0":  # Bottom edge, right to left
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0], reverse=True)
                elif orientation == "R270":  # Left edge, bottom to top
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1])
            else:
                # Counterclockwise sorting
                if orientation == "R270":  # Left edge, bottom to top
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1])
                elif orientation == "R0":  # Bottom edge, right to left
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0], reverse=True)
                elif orientation == "R90":  # Right edge, top to bottom
                    oriented_pads[orientation].sort(key=lambda x: x["position"][1], reverse=True)
                elif orientation == "R180":  # Top edge, left to right
                    oriented_pads[orientation].sort(key=lambda x: x["position"][0])
        
        # Get configuration parameters
        pad_width = 20
        pad_height = 110
        corner_size = 110
        chip_width, chip_height = self.position_calculator.calculate_chip_size(sorted_components)
        
        fillers = []
        
        # Get pad information on both sides of corner to determine filler type
        def get_adjacent_pads_for_corner(corner_orientation, is_first_corner):
            """Get pads on both sides of corner"""
            if corner_orientation == "R180":  # Top edge
                if is_first_corner:  # Top-left corner
                    left_pads = oriented_pads.get("R270", [])
                    top_pads = oriented_pads.get("R180", [])
                    return (left_pads[-1] if left_pads else None, top_pads[0] if top_pads else None)
                else:  # Top-right corner
                    top_pads = oriented_pads.get("R180", [])
                    right_pads = oriented_pads.get("R90", [])
                    return (top_pads[-1] if top_pads else None, right_pads[0] if right_pads else None)
            elif corner_orientation == "R90":  # Right edge
                if is_first_corner:  # Top-right corner
                    top_pads = oriented_pads.get("R180", [])
                    right_pads = oriented_pads.get("R90", [])
                    return (top_pads[-1] if top_pads else None, right_pads[0] if right_pads else None)
                else:  # Bottom-right corner
                    right_pads = oriented_pads.get("R90", [])
                    bottom_pads = oriented_pads.get("R0", [])
                    return (right_pads[-1] if right_pads else None, bottom_pads[0] if bottom_pads else None)
            elif corner_orientation == "R0":  # Bottom edge
                if is_first_corner:  # Bottom-right corner
                    right_pads = oriented_pads.get("R90", [])
                    bottom_pads = oriented_pads.get("R0", [])
                    return (right_pads[-1] if right_pads else None, bottom_pads[0] if bottom_pads else None)
                else:  # Bottom-left corner
                    bottom_pads = oriented_pads.get("R0", [])
                    left_pads = oriented_pads.get("R270", [])
                    return (bottom_pads[-1] if bottom_pads else None, left_pads[0] if left_pads else None)
            elif corner_orientation == "R270":  # Left edge
                if is_first_corner:  # Bottom-left corner
                    bottom_pads = oriented_pads.get("R0", [])
                    left_pads = oriented_pads.get("R270", [])
                    return (bottom_pads[-1] if bottom_pads else None, left_pads[0] if left_pads else None)
                else:  # Top-left corner
                    left_pads = oriented_pads.get("R270", [])
                    top_pads = oriented_pads.get("R180", [])
                    return (left_pads[-1] if left_pads else None, top_pads[0] if top_pads else None)
            return (None, None)
        
        # Process each orientation's pads
        for orientation, pad_list in oriented_pads.items():
            if not pad_list:
                continue
            
            # 1. Filler between corner and first pad
            if orientation == "R180":  # Top edge
                # Between top-left corner and first pad
                first_pad = pad_list[0]
                x = first_pad["position"][0] - pad_width
                y = chip_height - pad_height
                pad1, pad2 = get_adjacent_pads_for_corner("R180", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "sep_top_left_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R180"
                })
                
                # Between last pad and top-right corner
                last_pad = pad_list[-1]
                x = last_pad["position"][0] + pad_width
                y = chip_height - pad_height
                pad1, pad2 = get_adjacent_pads_for_corner("R180", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "filler_top_right_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R180"
                })
                
            elif orientation == "R90":  # Right edge
                # Between top-right corner and first pad
                first_pad = pad_list[0]
                x = chip_width - pad_height
                y = first_pad["position"][1] + pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R90", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "filler_right_top_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R90"
                })
                
                # Between last pad and bottom-right corner
                last_pad = pad_list[-1]
                x = chip_width - pad_height
                y = last_pad["position"][1] - pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R90", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "filler_right_bottom_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R90"
                })
                
            elif orientation == "R0":  # Bottom edge
                # Between bottom-right corner and first pad
                first_pad = pad_list[0]
                x = first_pad["position"][0] + pad_width
                y = 0
                pad1, pad2 = get_adjacent_pads_for_corner("R0", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "sep_bottom_right_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R0"
                })
                
                # Between last pad and bottom-left corner
                last_pad = pad_list[-1]
                x = last_pad["position"][0] - pad_width
                y = 0
                pad1, pad2 = get_adjacent_pads_for_corner("R0", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNER_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "filler_bottom_left_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R0"
                })
                
            elif orientation == "R270":  # Left edge
                # Between bottom-left corner and first pad
                first_pad = pad_list[0]
                x = 0
                y = first_pad["position"][1] - pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R270", True)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNER_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "filler_left_bottom_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R270"
                })
                
                # Between last pad and top-left corner
                last_pad = pad_list[-1]
                x = 0
                y = last_pad["position"][1] + pad_width
                pad1, pad2 = get_adjacent_pads_for_corner("R270", False)
                filler_type = FillerGenerator.get_filler_type_for_corner_and_pad("PCORNERA_G", pad1, pad2)
                fillers.append({
                    "type": "filler",
                    "name": "sep_left_top_corner",
                    "device": filler_type,
                    "position": [x, y],
                    "orientation": "R270"
                })
            
            # 2. Filler between pads
            for i in range(len(pad_list) - 1):
                curr_pad = pad_list[i]
                next_pad = pad_list[i + 1]
                
                # Calculate filler position
                if orientation == "R0":  # Bottom edge
                    x = curr_pad["position"][0] - pad_width
                    y = 0
                elif orientation == "R90":  # Right edge
                    x = chip_width - pad_height
                    y = curr_pad["position"][1] - pad_width
                elif orientation == "R180":  # Top edge
                    x = curr_pad["position"][0] + pad_width
                    y = chip_height - pad_height
                elif orientation == "R270":  # Left edge
                    x = 0
                    y = curr_pad["position"][1] + pad_width
                
                # Check if it's an inner pad gap
                curr_index = sorted_components.index(curr_pad)
                next_index = sorted_components.index(next_pad)
                
                if self.inner_pad_handler.is_inner_pad_gap_by_index(curr_index, next_index, inner_pads, sorted_components):
                    # Reserve space for inner pad, use 10 unit filler
                    filler_type = FillerGenerator.get_filler_type(curr_pad, next_pad)
                    
                    # If in the same voltage domain, use 10 unit filler
                    if VoltageDomainHandler.get_voltage_domain(curr_pad) == VoltageDomainHandler.get_voltage_domain(next_pad):
                        if "PFILLER" in filler_type:
                            # Replace 20 unit filler with 10 unit
                            filler_type = filler_type.replace("PFILLER20", "PFILLER10")
                    
                    # Position of the second filler (move 10 units in counterclockwise direction)
                    if orientation == "R0":  # Bottom edge
                        x1 = x + 10
                        y1 = y
                    elif orientation == "R90":  # Right edge
                        x1 = x
                        y1 = y + 10
                    elif orientation == "R180":  # Top edge
                        x1 = x - 10
                        y1 = y
                    elif orientation == "R270":  # Left edge
                        x1 = x
                        y1 = y - 10

                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_1",
                        "device": filler_type,
                        "position": [x1, y1],
                        "orientation": orientation
                    })
                    
                    # Position of the second filler (move 10 units in counterclockwise direction)
                    if orientation == "R0":  # Bottom edge
                        x2 = x - 20
                        y2 = y
                    elif orientation == "R90":  # Right edge
                        x2 = x
                        y2 = y - 20  # Changed from 30 to 40
                    elif orientation == "R180":  # Top edge
                        x2 = x + 20  # Changed from 30 to 40
                        y2 = y
                    elif orientation == "R270":  # Left edge
                        x2 = x
                        y2 = y + 20
                    
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_2",
                        "device": filler_type,
                        "position": [x2, y2],
                        "orientation": orientation
                    })
                else:
                    # Normal spacing, use 20 unit filler
                    filler_type = FillerGenerator.get_filler_type(curr_pad, next_pad)
                    
                    # Insert two 20 unit fillers
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_1",
                        "device": filler_type,
                        "position": [x, y],
                        "orientation": orientation
                    })
                    
                    # Position of the second filler
                    if orientation == "R0":  # Bottom edge
                        x2 = x - 20
                        y2 = y
                    elif orientation == "R90":  # Right edge
                        x2 = x
                        y2 = y - 20
                    elif orientation == "R180":  # Top edge
                        x2 = x + 20
                        y2 = y
                    elif orientation == "R270":  # Left edge
                        x2 = x
                        y2 = y + 20
                    
                    fillers.append({
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_2",
                        "device": filler_type,
                        "position": [x2, y2],
                        "orientation": orientation
                    })
        
        return layout_components + fillers 