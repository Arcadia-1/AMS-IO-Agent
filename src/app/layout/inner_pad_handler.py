#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inner Pad Processing Module
"""

from typing import List, Tuple
from .device_classifier import DeviceClassifier
from .position_calculator import PositionCalculator

class InnerPadHandler:
    """Inner Pad Handler"""
    
    def __init__(self, config: dict):
        self.config = config
        self.position_calculator = PositionCalculator(config)
    
    def calculate_inner_pad_position(self, position_str: str, outer_pads: List[dict], ring_config: dict) -> tuple:
        """Calculate inner pad position and orientation, supporting clockwise/counterclockwise"""
        parts = position_str.split('_')
        if len(parts) != 3:
            raise ValueError(f"Invalid inner pad position format: {position_str}")
        side = parts[0]  # top, bottom, left, right
        pad1_index = int(parts[1])
        pad2_index = int(parts[2])
        placement_order = ring_config.get("placement_order", "counterclockwise")

        # Calculate pad count per side
        width = ring_config.get("width", 3)
        height = ring_config.get("height", 3)
        side_pad_count = {
            "top": width,
            "bottom": width,
            "left": height,
            "right": height
        }
        N = side_pad_count.get(side, 0)
        if placement_order == "clockwise":
            real_pad1_index = pad1_index
            real_pad2_index = pad2_index
        else:
            real_pad1_index = (N - 1) - pad1_index
            real_pad2_index = (N - 1) - pad2_index

        # Sort outer pads by placement order
        sorted_outer_pads = self.position_calculator.sort_components_by_position(outer_pads, placement_order)
        
        # Determine pad starting index based on placement order
        if placement_order == "clockwise":
            # Clockwise: Top-left -> Top edge -> Top-right -> Right edge -> Bottom-right -> Bottom edge -> Bottom-left -> Left edge
            side_start_indices = {
                "top": 0,
                "right": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]),
                "bottom": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"]),
                "left": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"])
            }
        else:
            # Counterclockwise: Top-left -> Left edge -> Bottom-left -> Bottom edge -> Bottom-right -> Right edge -> Top-right -> Top edge
            side_start_indices = {
                "left": 0,
                "bottom": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]),
                "right": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"]),
                "top": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"])
            }
        
        if side not in side_start_indices:
            raise ValueError(f"Invalid side: {side}")
        start_index = side_start_indices[side]
        pad1_global_index = start_index + real_pad1_index
        pad2_global_index = start_index + real_pad2_index

        # Get positions of two outer pads
        pad1 = sorted_outer_pads[pad1_global_index]
        pad2 = sorted_outer_pads[pad2_global_index]

        # Calculate middle position
        x1, y1 = pad1["position"]
        x2, y2 = pad2["position"]
        orientation = pad1["orientation"]

        # Calculate middle position based on orientation
        if orientation == "R180":  # Top edge
            x = (x1 + x2) // 2
            y = y1
        elif orientation == "R0":  # Bottom edge
            x = (x1 + x2) // 2
            y = y1
        elif orientation == "R90":  # Right edge
            x = x1
            y = (y1 + y2) // 2
        elif orientation == "R270":  # Left edge
            x = x1
            y = (y1 + y2) // 2
        else:
            raise ValueError(f"Invalid orientation: {orientation}")

        return ([x, y], orientation)
    
    def generate_inner_pad_skill_commands(self, inner_pads: List[dict], outer_pads: List[dict], ring_config: dict) -> List[str]:
        """Generate SKILL commands for inner pads"""
        skill_commands = []
        
        for i, inner_pad in enumerate(inner_pads):
            name = inner_pad["name"]
            device = inner_pad["device"]
            
            # If position is already absolute coordinates, use directly
            if isinstance(inner_pad["position"], list):
                position = inner_pad["position"]
                orientation = inner_pad["orientation"]
            else:
                # Otherwise, recalculate position
                position_str = inner_pad["position"]
                position, orientation = self.calculate_inner_pad_position(position_str, outer_pads, ring_config)
            
            x, y = position
            position_str = inner_pad["position_str"]
            # Generate SKILL commands for inner pads
            library_name = ring_config.get("library_name", "tphn28hpcpgv18")
            view_name = ring_config.get("view_name", "layout")
            skill_commands.append(f'dbCreateParamInstByMasterName(cv "{library_name}" "{device}" "{view_name}" "inner_pad_{name}_{position_str}" list({x} {y}) "{orientation}")')
            skill_commands.append(f'dbCreateParamInstByMasterName(cv "PAD" "PAD60NU" "layout" "inner_pad60nu_{name}_{position_str}" list({x} {y}) "{orientation}")')
        
        return skill_commands
    
    def get_all_digital_pads_with_inner(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[dict]:
        """Get all digital IO pad information (including outer and inner rings)"""
        digital_pads = []
        
        # Outer ring digital IO pads
        for pad in outer_pads:
            if DeviceClassifier.is_digital_io_device(pad["device"]):
                digital_pads.append({
                    "position": pad["position"],
                    "orientation": pad["orientation"],
                    "name": pad["name"],
                    "device": pad["device"],
                    "io_direction": pad.get("io_direction", "unknown"),
                    "is_inner": False
                })
        
        # Inner ring digital IO pads
        for inner_pad in inner_pads:
            if DeviceClassifier.is_digital_io_device(inner_pad["device"]):
                # If position is already absolute coordinates, use directly
                if isinstance(inner_pad["position"], list):
                    position = inner_pad["position"]
                    orientation = inner_pad["orientation"]
                else:
                    # Otherwise, recalculate position
                    position, orientation = self.calculate_inner_pad_position(inner_pad["position"], outer_pads, ring_config)
                
                digital_pads.append({
                    "position": position,
                    "orientation": orientation,
                    "name": inner_pad["name"],
                    "device": inner_pad["device"],
                    "io_direction": inner_pad.get("io_direction", "unknown"),
                    "is_inner": True
                })
        
        return digital_pads
    
    def get_all_digital_pads_with_inner_any(self, outer_pads: List[dict], inner_pads: List[dict], ring_config: dict) -> List[dict]:
        """Get all digital pad information (including outer and inner rings, all digital pads, not limited to IO)"""
        digital_pads = []
        # Outer ring digital pads
        for pad in outer_pads:
            if DeviceClassifier.is_digital_device(pad["device"]):
                digital_pads.append({
                    "position": pad["position"],
                    "orientation": pad["orientation"],
                    "name": pad["name"],
                    "device": pad["device"],
                    "io_direction": pad.get("io_direction", "unknown"),
                    "is_inner": False
                })
        # Inner ring digital pads
        for inner_pad in inner_pads:
            if DeviceClassifier.is_digital_device(inner_pad["device"]):
                if isinstance(inner_pad["position"], list):
                    position = inner_pad["position"]
                    orientation = inner_pad["orientation"]
                else:
                    position, orientation = self.calculate_inner_pad_position(inner_pad["position"], outer_pads, ring_config)
                digital_pads.append({
                    "position": position,
                    "orientation": orientation,
                    "name": inner_pad["name"],
                    "device": inner_pad["device"],
                    "io_direction": inner_pad.get("io_direction", "unknown"),
                    "is_inner": True
                })
        return digital_pads
    
    def get_inner_pad_gap_indices(self, inner_pads: List[dict], outer_pads: List[dict]) -> List[tuple]:
        """Get index pairs that need to reserve space for inner pads, calculated based on placement order, supporting clockwise/counterclockwise"""
        placement_order = self.config.get("placement_order", "counterclockwise")
        gap_pairs = []
        
        # Sort outer pads by placement order
        sorted_outer_pads = self.position_calculator.sort_components_by_position(outer_pads, placement_order)
        
        for inner_pad in inner_pads:
            # Inner pad position may be absolute coordinates, need to get position_str from original configuration
            # Here we match by name, or directly use the position_str field
            position_str = inner_pad.get("position_str", "")
            if not position_str and isinstance(inner_pad.get("position"), str):
                position_str = inner_pad.get("position")
            
            # If position_str is empty, it means it's already absolute coordinates, skip this inner pad
            if not position_str or not isinstance(position_str, str):
                continue
                
            parts = position_str.split('_')
            if len(parts) == 3:
                side = parts[0]
                pad1_index = int(parts[1])
                pad2_index = int(parts[2])
                
                # Calculate pad count per side
                width = self.config.get("width", 3)
                height = self.config.get("height", 3)
                side_pad_count = {
                    "top": width,
                    "bottom": width,
                    "left": height,
                    "right": height
                }
                N = side_pad_count.get(side, 0)
                
                # Adjust index direction based on placement_order
                if placement_order == "clockwise":
                    real_pad1_index = pad1_index
                    real_pad2_index = pad2_index
                else:
                    real_pad1_index = (N - 1) - pad1_index
                    real_pad2_index = (N - 1) - pad2_index
                
                # Determine pad starting index based on placement order
                if placement_order == "clockwise":
                    # Clockwise: Top-left -> Top edge -> Top-right -> Right edge -> Bottom-right -> Bottom edge -> Bottom-left -> Left edge
                    side_start_indices = {
                        "top": 0,
                        "right": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]),
                        "bottom": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"]),
                        "left": len([p for p in sorted_outer_pads if p["orientation"] == "R180"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"])
                    }
                else:
                    # Counterclockwise: Top-left -> Left edge -> Bottom-left -> Bottom edge -> Bottom-right -> Right edge -> Top-right -> Top edge
                    side_start_indices = {
                        "left": 0,
                        "bottom": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]),
                        "right": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"]),
                        "top": len([p for p in sorted_outer_pads if p["orientation"] == "R270"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R0"]) + len([p for p in sorted_outer_pads if p["orientation"] == "R90"])
                    }
                
                if side in side_start_indices:
                    start_index = side_start_indices[side]
                    pad1_global_index = start_index + real_pad1_index
                    pad2_global_index = start_index + real_pad2_index
                    gap_pairs.append((pad1_global_index, pad2_global_index))
        
        return gap_pairs
    
    def is_inner_pad_gap_by_index(self, index1: int, index2: int, inner_pads: List[dict], outer_pads: List[dict]) -> bool:
        """Check if space needs to be reserved for inner pads between two pads based on index"""
        gap_pairs = self.get_inner_pad_gap_indices(inner_pads, outer_pads)
        return (index1, index2) in gap_pairs or (index2, index1) in gap_pairs 