#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL Script Generation Module
"""

from typing import List
from .device_classifier import DeviceClassifier
from .voltage_domain import VoltageDomainHandler
from .inner_pad_handler import InnerPadHandler

class SkillGenerator:
    """SKILL Script Generator"""
    
    def __init__(self, config: dict):
        self.config = config
        self.inner_pad_handler = InnerPadHandler(config)
    
    def generate_digital_io_features_with_inner(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[str]:
        """Generate digital IO features (configuration lines + secondary lines + pin labels), supporting inner pads. Configuration lines cover all digital pads, secondary lines and pins only for digital IO."""
        skill_commands = []
        # Get all digital pads (not distinguishing IO)
        all_digital_pads = self.inner_pad_handler.get_all_digital_pads_with_inner_any(outer_pads, inner_pads, ring_config)
        # Get all digital IO pads
        digital_io_pads = self.inner_pad_handler.get_all_digital_pads_with_inner(outer_pads, inner_pads, ring_config)
        if not all_digital_pads:
            return skill_commands
        
        # Generate configuration lines (grouped by orientation)
        oriented_pads = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pad in all_digital_pads:
            oriented_pads[pad["orientation"]].append(pad["position"])
        
        # Record which sides have configuration lines
        sides_with_lines = {}
        
        # Generate configuration lines for each orientation
        for orient, pad_positions in oriented_pads.items():
            if not pad_positions:
                continue
            
            sides_with_lines[orient] = True
            x_coords = [pos[0] for pos in pad_positions]
            y_coords = [pos[1] for pos in pad_positions]
            
            if orient == "R0":  # Bottom edge
                line_y_high = max(y_coords) + ring_config["pad_height"] + 0.5
                line_y_low = max(y_coords) + ring_config["pad_height"] - 0.76
                high_points = f'list(list({min(x_coords)} {line_y_high}) list({max(x_coords) + ring_config["pad_width"]} {line_y_high}))'
                low_points = f'list(list({min(x_coords)} {line_y_low}) list({max(x_coords) + ring_config["pad_width"]} {line_y_low}))'
            elif orient == "R90":  # Right edge
                line_x_high = min(x_coords) - ring_config["pad_height"] - 0.5
                line_x_low = min(x_coords) - ring_config["pad_height"] + 0.76
                high_points = f'list(list({line_x_high} {min(y_coords)}) list({line_x_high} {max(y_coords) + ring_config["pad_width"]}))'
                low_points = f'list(list({line_x_low} {min(y_coords)}) list({line_x_low} {max(y_coords) + ring_config["pad_width"]}))'
            elif orient == "R180":  # Top edge
                line_y_high = min(y_coords) - ring_config["pad_height"] - 0.5
                line_y_low = min(y_coords) - ring_config["pad_height"] + 0.76
                high_points = f'list(list({min(x_coords) - ring_config["pad_width"]} {line_y_high}) list({max(x_coords)} {line_y_high}))'
                low_points = f'list(list({min(x_coords) - ring_config["pad_width"]} {line_y_low}) list({max(x_coords)} {line_y_low}))'
            elif orient == "R270":  # Left edge
                line_x_high = max(x_coords) + ring_config["pad_height"] + 0.5
                line_x_low = max(x_coords) + ring_config["pad_height"] - 0.76
                high_points = f'list(list({line_x_high} {min(y_coords) - ring_config["pad_width"]}) list({line_x_high} {max(y_coords)}))'
                low_points = f'list(list({line_x_low} {min(y_coords) - ring_config["pad_width"]}) list({line_x_low} {max(y_coords)}))'
            
            # Create configuration lines
            skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") {high_points} 0.2)')
            skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") {low_points} 0.2)')
        
        # Connect configuration lines at corners
        if len(sides_with_lines) > 1:
            # Calculate actual end positions of configuration lines for each side
            side_endpoints = {}
            
            for orient, pad_positions in oriented_pads.items():
                if not pad_positions:
                    continue
                    
                x_coords = [pos[0] for pos in pad_positions]
                y_coords = [pos[1] for pos in pad_positions]
                
                if orient == "R0":  # Bottom edge
                    line_y_high = max(y_coords) + ring_config["pad_height"] + 0.5
                    line_y_low = max(y_coords) + ring_config["pad_height"] - 0.76
                    side_endpoints["R0"] = {
                        "high": {"x_range": [min(x_coords), max(x_coords) + ring_config["pad_width"]], "y": line_y_high},
                        "low": {"x_range": [min(x_coords), max(x_coords) + ring_config["pad_width"]], "y": line_y_low}
                    }
                elif orient == "R90":  # Right edge
                    line_x_high = min(x_coords) - ring_config["pad_height"] - 0.5
                    line_x_low = min(x_coords) - ring_config["pad_height"] + 0.76
                    side_endpoints["R90"] = {
                        "high": {"x": line_x_high, "y_range": [min(y_coords), max(y_coords) + ring_config["pad_width"]]},
                        "low": {"x": line_x_low, "y_range": [min(y_coords), max(y_coords) + ring_config["pad_width"]]}
                    }
                elif orient == "R180":  # Top edge
                    line_y_high = min(y_coords) - ring_config["pad_height"] - 0.5
                    line_y_low = min(y_coords) - ring_config["pad_height"] + 0.76
                    side_endpoints["R180"] = {
                        "high": {"x_range": [min(x_coords) - ring_config["pad_width"], max(x_coords)], "y": line_y_high},
                        "low": {"x_range": [min(x_coords) - ring_config["pad_width"], max(x_coords)], "y": line_y_low}
                    }
                elif orient == "R270":  # Left edge
                    line_x_high = max(x_coords) + ring_config["pad_height"] + 0.5
                    line_x_low = max(x_coords) + ring_config["pad_height"] - 0.76
                    side_endpoints["R270"] = {
                        "high": {"x": line_x_high, "y_range": [min(y_coords) - ring_config["pad_width"], max(y_coords)]},
                        "low": {"x": line_x_low, "y_range": [min(y_coords) - ring_config["pad_width"], max(y_coords)]}
                    }
            
            corner_connections = {
                "top_left": ["R180", "R270"],
                "top_right": ["R180", "R90"],
                "bottom_left": ["R0", "R270"],
                "bottom_right": ["R0", "R90"]
            }
            for corner_name, adjacent_sides in corner_connections.items():
                if adjacent_sides[0] in side_endpoints and adjacent_sides[1] in side_endpoints:
                    side1, side2 = adjacent_sides[0], adjacent_sides[1]
                    # High voltage line
                    if corner_name == "top_left":
                        x1 = side_endpoints["R180"]["high"]["x_range"][0]
                        y1 = side_endpoints["R180"]["high"]["y"]
                        x2 = side_endpoints["R270"]["high"]["x"]
                        y2 = side_endpoints["R270"]["high"]["y_range"][1]
                        # Line: first horizontal, then vertical
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1} {y1}) list({x2} {y1})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2} {y1}) list({x2} {y2})) 0.2 "extendExtend")')
                        # Low voltage line
                        x1l = side_endpoints["R180"]["low"]["x_range"][0]
                        y1l = side_endpoints["R180"]["low"]["y"]
                        x2l = side_endpoints["R270"]["low"]["x"]
                        y2l = side_endpoints["R270"]["low"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 0.2 "extendExtend")')
                    elif corner_name == "top_right":
                        x1 = side_endpoints["R180"]["high"]["x_range"][1]
                        y1 = side_endpoints["R180"]["high"]["y"]
                        x2 = side_endpoints["R90"]["high"]["x"]
                        y2 = side_endpoints["R90"]["high"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1} {y1}) list({x2} {y1})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2} {y1}) list({x2} {y2})) 0.2 "extendExtend")')
                        x1l = side_endpoints["R180"]["low"]["x_range"][1]
                        y1l = side_endpoints["R180"]["low"]["y"]
                        x2l = side_endpoints["R90"]["low"]["x"]
                        y2l = side_endpoints["R90"]["low"]["y_range"][1]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 0.2 "extendExtend")')
                    elif corner_name == "bottom_left":
                        x1 = side_endpoints["R0"]["high"]["x_range"][0]
                        y1 = side_endpoints["R0"]["high"]["y"]
                        x2 = side_endpoints["R270"]["high"]["x"]
                        y2 = side_endpoints["R270"]["high"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1} {y1}) list({x2} {y1})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2} {y1}) list({x2} {y2})) 0.2 "extendExtend")')
                        x1l = side_endpoints["R0"]["low"]["x_range"][0]
                        y1l = side_endpoints["R0"]["low"]["y"]
                        x2l = side_endpoints["R270"]["low"]["x"]
                        y2l = side_endpoints["R270"]["low"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 0.2 "extendExtend")')
                    elif corner_name == "bottom_right":
                        x1 = side_endpoints["R0"]["high"]["x_range"][1]
                        y1 = side_endpoints["R0"]["high"]["y"]
                        x2 = side_endpoints["R90"]["high"]["x"]
                        y2 = side_endpoints["R90"]["high"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1} {y1}) list({x2} {y1})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2} {y1}) list({x2} {y2})) 0.2 "extendExtend")')
                        x1l = side_endpoints["R0"]["low"]["x_range"][1]
                        y1l = side_endpoints["R0"]["low"]["y"]
                        x2l = side_endpoints["R90"]["low"]["x"]
                        y2l = side_endpoints["R90"]["low"]["y_range"][0]
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x1l} {y1l}) list({x2l} {y1l})) 0.2 "extendExtend")')
                        skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x2l} {y1l}) list({x2l} {y2l})) 0.2 "extendExtend")')
        
        # Secondary lines and pin labels only for digital IO pads
        offsets = {"I": 1.725, "OEN": 5.9, "REN": 10.2, "C": 14.33}
        
        # Place vias and connect to configuration lines for digital power pads
        for pad in all_digital_pads:
            device = pad["device"]
            if device in ["PVDD1DGZ_V_G", "PVDD1DGZ_H_G", "PVSS1DGZ_V_G", "PVSS1DGZ_H_G"]:
                x, y = pad["position"]
                orient = pad["orientation"]
                
                # Determine offset based on pad type
                if device.startswith("PVDD"):
                    offset = 2.345
                    is_vdd = True
                elif device.startswith("PVSS"):
                    offset = 2.39
                    is_vdd = False
                else:
                    continue
                
                # Calculate via position (based on orientation)
                if orient == "R0":  # Bottom edge
                    via_x = x + offset
                    via_y = y + 110.12
                    # Configuration line y-coordinate
                    config_y = y + ring_config["pad_height"] + (0.5 if is_vdd else -0.76)
                    config_x = via_x
                    # Draw line connecting via and configuration line
                    via_orientation = "R0"
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({via_x} {via_y}) list({config_x} {config_y})) 0.2)')
                elif orient == "R90":  # Right edge
                    via_x = x - 110.12
                    via_y = y + offset
                    config_x = x - ring_config["pad_height"] + (-0.5 if is_vdd else 0.76)
                    config_y = via_y
                    via_orientation = "R90"
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({via_x} {via_y}) list({config_x} {config_y})) 0.2)')
                elif orient == "R180":  # Top edge
                    via_x = x - offset
                    via_y = y - 110.12
                    config_y = y - ring_config["pad_height"] + (-0.5 if is_vdd else 0.76)
                    config_x = via_x
                    via_orientation = "R180"
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({via_x} {via_y}) list({config_x} {config_y})) 0.2)')
                elif orient == "R270":  # Left edge
                    via_x = x + 110.12
                    via_y = y - offset
                    config_x = x + ring_config["pad_height"] + (0.5 if is_vdd else -0.76)
                    config_y = via_y
                    via_orientation = "R270"
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({via_x} {via_y}) list({config_x} {config_y})) 0.2)')
                else:
                    continue
                
                # Place via
                skill_commands.append("tech = techGetTechFile(cv)")
                skill_commands.append('viaParams = list(list("cutRows" 2) list("cutColumns" 4))')
                skill_commands.append('viaDefId = techFindViaDefByName(tech "M3_M2")')
                skill_commands.append(f'newVia = dbCreateVia(cv viaDefId list({via_x} {via_y}) "{via_orientation}" viaParams)')
        
        for pad in digital_io_pads:
            x, y = pad["position"]
            orient = pad["orientation"]
            is_input = pad["io_direction"] == "input"
            
            if orient == "R0":  # Bottom edge pad
                base_y = y + ring_config["pad_height"] - 0.125
                high_y = y + ring_config["pad_height"] + 0.5
                low_y = y + ring_config["pad_height"] - 0.76
                
                # Create secondary line
                if is_input:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x + offsets["REN"]} {base_y}) list({x + offsets["REN"]} {low_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x + offsets["I"]} {base_y}) list({x + offsets["I"]} {low_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x + offsets["OEN"]} {base_y}) list({x + offsets["OEN"]} {high_y})) 0.26)')
                    pin_pos = f"list({x + offsets['C']} {base_y})"
                else:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x + offsets["REN"]} {base_y}) list({x + offsets["REN"]} {high_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x + offsets["OEN"]} {base_y}) list({x + offsets["OEN"]} {low_y})) 0.26)')
                    pin_pos = f"list({x + offsets['I']} {base_y})"
                
                # Create pin label
                skill_commands.append(f'dbCreateLabel(cv list("M4" "pin") {pin_pos} "{pad["name"]}_CORE" "centerLeft" "R90" "roman" 2)')
                
            elif orient == "R90":  # Right edge pad
                base_x = x - ring_config["pad_height"] + 0.125
                high_x = x - ring_config["pad_height"] - 0.5
                low_x = x - ring_config["pad_height"] + 0.76
                
                # Create secondary line
                if is_input:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({low_x} {y + offsets["REN"]}) list({base_x} {y + offsets["REN"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({low_x} {y + offsets["I"]}) list({base_x} {y + offsets["I"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({high_x} {y + offsets["OEN"]}) list({base_x} {y + offsets["OEN"]})) 0.26)')
                    pin_pos = f"list({base_x} {y + offsets['C']})"
                else:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({high_x} {y + offsets["REN"]}) list({base_x} {y + offsets["REN"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({low_x} {y + offsets["OEN"]}) list({base_x} {y + offsets["OEN"]})) 0.26)')
                    pin_pos = f"list({base_x} {y + offsets['I']})"
                
                # Create pin label
                skill_commands.append(f'dbCreateLabel(cv list("M4" "pin") {pin_pos} "{pad["name"]}_CORE" "centerRight" "R0" "roman" 2)')
            
            elif orient == "R180":  # Top edge pad
                base_y = y - ring_config["pad_height"] + 0.125
                high_y = y - ring_config["pad_height"] - 0.5
                low_y = y - ring_config["pad_height"] + 0.76
                
                # Create secondary line
                if is_input:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x - offsets["REN"]} {base_y}) list({x - offsets["REN"]} {low_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x - offsets["I"]} {base_y}) list({x - offsets["I"]} {low_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x - offsets["OEN"]} {base_y}) list({x - offsets["OEN"]} {high_y})) 0.26)')
                    pin_pos = f"list({x - offsets['C']} {base_y})"
                else:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x - offsets["REN"]} {base_y}) list({x - offsets["REN"]} {high_y})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({x - offsets["OEN"]} {base_y}) list({x - offsets["OEN"]} {low_y})) 0.26)')
                    pin_pos = f"list({x - offsets['I']} {base_y})"
                
                # Create pin label
                skill_commands.append(f'dbCreateLabel(cv list("M4" "pin") {pin_pos} "{pad["name"]}_CORE" "centerRight" "R90" "roman" 2)')
            
            elif orient == "R270":  # Left edge pad
                base_x = x + ring_config["pad_height"] - 0.125
                high_x = x + ring_config["pad_height"] + 0.5
                low_x = x + ring_config["pad_height"] - 0.76
                
                # Create secondary line
                if is_input:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({base_x} {y - offsets["REN"]}) list({low_x} {y - offsets["REN"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({base_x} {y - offsets["I"]}) list({low_x} {y - offsets["I"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({base_x} {y - offsets["OEN"]}) list({high_x} {y - offsets["OEN"]})) 0.26)')
                    pin_pos = f"list({base_x} {y - offsets['C']})"
                else:
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({base_x} {y - offsets["REN"]}) list({high_x} {y - offsets["REN"]})) 0.26)')
                    skill_commands.append(f'dbCreatePath(cv list("M3" "drawing") list(list({base_x} {y - offsets["OEN"]}) list({low_x} {y - offsets["OEN"]})) 0.26)')
                    pin_pos = f"list({base_x} {y - offsets['I']})"
                
                # Create pin label
                skill_commands.append(f'dbCreateLabel(cv list("M4" "pin") {pin_pos} "{pad["name"]}_CORE" "centerLeft" "R0" "roman" 2)')
        
        return skill_commands
    
    def generate_pin_labels_with_inner(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[str]:
        """Generate main pin labels, supporting inner pads"""
        skill_commands = []
        
        # Main pin labels for outer pads
        for pad in outer_pads:
            x, y = pad["position"]
            orient = pad["orientation"]
            name = pad["name"]
            device = pad.get("device", "")
            
            # Calculate pin label position (standard way)
            if orient == "R0":
                pin_pos = f'list({x + 10} {y - 11})'
                justification, pin_orient = "centerRight", "R90"
            elif orient == "R90":
                pin_pos = f'list({x + 11} {y + 10})'
                justification, pin_orient = "centerLeft", "R0"
            elif orient == "R180":
                pin_pos = f'list({x - 10} {y + 11})'
                justification, pin_orient = "centerLeft", "R90"
            elif orient == "R270":
                pin_pos = f'list({x - 11} {y - 10})'
                justification, pin_orient = "centerRight", "R0"
            
            skill_commands.append(f'dbCreateLabel(cv list("AP" "pin") {pin_pos} "{name}" "{justification}" "{pin_orient}" "roman" 10)')
            
            # Create core label for voltage domain components
            if VoltageDomainHandler.is_voltage_domain_provider(pad):
                # Calculate core label position (within the pad)
                if orient == "R0":
                    core_pos = f'list({x + 10} {y + ring_config["pad_height"] - 0.1})'
                    core_just, core_orient = "centerLeft", "R90"
                elif orient == "R90":
                    core_pos = f'list({x - ring_config["pad_height"] + 0.1} {y + 10})'
                    core_just, core_orient = "centerRight", "R0"
                elif orient == "R180":
                    core_pos = f'list({x - 10} {y - ring_config["pad_height"] + 0.1})'
                    core_just, core_orient = "centerRight", "R90"
                elif orient == "R270":
                    core_pos = f'list({x + ring_config["pad_height"] - 0.1} {y - 10})'
                    core_just, core_orient = "centerLeft", "R0"
                
                skill_commands.append(f'dbCreateLabel(cv list("M2" "pin") {core_pos} "{name}_CORE" "{core_just}" "{core_orient}" "roman" 2)')
        
        # Main pin labels for inner pads (move 152 units inward, opposite direction)
        for inner_pad in inner_pads:
            # If position is already absolute coordinates, use directly
            if isinstance(inner_pad["position"], list):
                position = inner_pad["position"]
                orient = inner_pad["orientation"]
            else:
                # Otherwise, recalculate position
                position, orient = self.inner_pad_handler.calculate_inner_pad_position(inner_pad["position"], outer_pads, ring_config)
            
            x, y = position
            name = inner_pad["name"]
            device = inner_pad.get("device", "")
            
            # Calculate pin label position for inner pads (move inward) and direction (opposite to outer)
            if orient == "R0":  # Bottom edge inner pad
                pin_pos = f'list({x + 10} {y + 152})'  # Move inward (up)
                justification, pin_orient = "centerLeft", "R90"  # Opposite direction
            elif orient == "R90":  # Right edge inner pad
                pin_pos = f'list({x - 152} {y + 10})'  # Move inward (left)
                justification, pin_orient = "centerRight", "R0"  # Opposite direction
            elif orient == "R180":  # Top edge inner pad
                pin_pos = f'list({x - 10} {y - 152})'  # Move inward (down)
                justification, pin_orient = "centerRight", "R90"  # Opposite direction
            elif orient == "R270":  # Left edge inner pad
                pin_pos = f'list({x + 152} {y - 10})'  # Move inward (right)
                justification, pin_orient = "centerLeft", "R0"  # Opposite direction
            
            skill_commands.append(f'dbCreateLabel(cv list("AP" "pin") {pin_pos} "{name}" "{justification}" "{pin_orient}" "roman" 10)')
            
            # Create core label for inner pad voltage domain components
            if VoltageDomainHandler.is_voltage_domain_provider(inner_pad):
                # Calculate core label position for inner pads (within the pad, opposite to outer)
                if orient == "R0":  # Bottom edge inner pad
                    core_pos = f'list({x + 10} {y + ring_config["pad_height"] - 0.1})'
                    core_just, core_orient = "centerLeft", "R90"
                elif orient == "R90":  # Right edge inner pad
                    core_pos = f'list({x - ring_config["pad_height"] + 0.1} {y + 10})'
                    core_just, core_orient = "centerRight", "R0"
                elif orient == "R180":  # Top edge inner pad
                    core_pos = f'list({x - 10} {y - ring_config["pad_height"] + 0.1})'
                    core_just, core_orient = "centerRight", "R90"
                elif orient == "R270":  # Left edge inner pad
                    core_pos = f'list({x + ring_config["pad_height"] - 0.1} {y - 10})'
                    core_just, core_orient = "centerLeft", "R0"
                
                skill_commands.append(f'dbCreateLabel(cv list("M2" "pin") {core_pos} "{name}_CORE" "{core_just}" "{core_orient}" "roman" 2)')
        
        return skill_commands 