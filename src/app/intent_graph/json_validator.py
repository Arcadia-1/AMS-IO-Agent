#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intent Graph Validator - Validates intent graph files
"""

import re
from typing import Dict, Any

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration completeness"""
    if not config:
        print("❌ Error: Configuration is empty")
        return False
    
    # Validate ring_config
    if 'ring_config' not in config:
        print("❌ Error: Missing ring_config field")
        return False
    
    ring_config = config['ring_config']
    if 'width' not in ring_config or 'height' not in ring_config:
        print("❌ Error: ring_config missing width or height field")
        return False
    
    width = ring_config['width']
    height = ring_config['height']
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        print("❌ Error: width and height must be positive integers")
        return False
    
    # Validate placement_order
    if 'placement_order' not in ring_config:
        print("❌ Error: ring_config missing placement_order field")
        return False
    
    placement_order = ring_config['placement_order']
    if placement_order not in ['clockwise', 'counterclockwise']:
        print("❌ Error: placement_order must be 'clockwise' or 'counterclockwise'")
        return False
    
    # Validate instances
    if 'instances' not in config:
        print("❌ Error: Missing instances field")
        return False
    
    instances = config['instances']
    if not instances or not isinstance(instances, list):
        print("❌ Error: instances must be a non-empty list")
        return False
    
    # Validate basic fields for each instance
    corner_positions = set()
    position_counts = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
    
    for i, instance in enumerate(instances):
        if not isinstance(instance, dict):
            print(f"❌ Error: instance[{i}] must be a dictionary")
            return False
        
        # Validate required fields
        if 'name' not in instance:
            print(f"❌ Error: instance[{i}] missing name field")
            return False
        
        if 'device' not in instance:
            print(f"❌ Error: instance[{i}] missing device field")
            return False
        
        if 'position' not in instance:
            print(f"❌ Error: instance[{i}] missing position field")
            return False
        
        name = instance['name']
        device = instance['device']
        position = instance['position']
        
        # Validate device suffix rules
        if not validate_device_suffix(device, position):
            print(f"❌ Error: instance[{i}] {name}'s device suffix doesn't match position")
            return False
        
        # Validate position format
        if not validate_position_format(position, width, height):
            print(f"❌ Error: instance[{i}] {name}'s position format is incorrect")
            return False
        
        # Count positions and corner points (only count outer ring pads, exclude inner ring pads)
        if position.startswith(('top_left', 'top_right', 'bottom_left', 'bottom_right')):
            corner_positions.add(position)
        else:
            # Only count outer ring pads, don't count inner ring pads
            instance_type = instance.get('type', 'pad')
            if instance_type != 'inner_pad':  # Exclude inner ring pads
                for side in ['left', 'right', 'top', 'bottom']:
                    if position.startswith(side + '_'):
                        position_counts[side] += 1
                        break
        
        # Validate type field (if exists)
        if 'type' in instance:
            instance_type = instance['type']
            if instance_type not in ['pad', 'inner_pad', 'corner']:
                print(f"❌ Error: instance[{i}] {name}'s type field value is incorrect")
                return False
            
            # Validate corner type
            if instance_type == 'corner':
                if not position.startswith(('top_left', 'top_right', 'bottom_left', 'bottom_right')):
                    print(f"❌ Error: instance[{i}] {name}'s corner type position format is incorrect")
                    return False
        
        # Validate direction field (required for digital IO)
        if device.startswith('PDDW16SDGZ'):
            if 'direction' not in instance:
                print(f"❌ Error: instance[{i}] {name}'s digital IO missing direction field")
                return False
            direction = instance['direction']
            if direction not in ['input', 'output']:
                print(f"❌ Error: instance[{i}] {name}'s direction must be 'input' or 'output'")
                return False
        
        # Validate pin_connection (if exists)
        if 'pin_connection' in instance:
            pin_connection = instance['pin_connection']
            if not isinstance(pin_connection, dict):
                print(f"❌ Error: instance[{i}] {name}'s pin_connection must be a dictionary")
                return False
            
            # Validate digital IO pin_connection
            if device.startswith('PDDW16SDGZ'):
                required_pins = ['VDD', 'VSS', 'VDDPST', 'VSSPST']
                for pin in required_pins:
                    if pin not in pin_connection:
                        print(f"❌ Error: instance[{i}] {name}'s digital IO missing {pin} pin configuration")
                        return False
            
            # Validate analog device VSS pin
            if device.startswith(('PDB3AC', 'PVDD', 'PVSS')):
                if 'VSS' not in pin_connection:
                    print(f"❌ Error: instance[{i}] {name}'s analog device missing VSS pin configuration")
                    return False
    
    # Validate corner count
    if len(corner_positions) != 4:
        print(f"❌ Error: Incorrect corner count, expected 4, actual {len(corner_positions)}")
        return False
    
    # Validate pad count for each side (judge each side separately)
    # width is pad count for each of top and bottom sides, height is pad count for each of left and right sides
    expected_left = height   # Left side pad count
    expected_right = height  # Right side pad count
    expected_top = width     # Top side pad count
    expected_bottom = width  # Bottom side pad count
    
    if position_counts['left'] != expected_left:
        print(f"❌ Error: Left side pad count incorrect, expected {expected_left}, actual {position_counts['left']}")
        return False
    
    if position_counts['right'] != expected_right:
        print(f"❌ Error: Right side pad count incorrect, expected {expected_right}, actual {position_counts['right']}")
        return False
    
    if position_counts['top'] != expected_top:
        print(f"❌ Error: Top side pad count incorrect, expected {expected_top}, actual {position_counts['top']}")
        return False
    
    if position_counts['bottom'] != expected_bottom:
        print(f"❌ Error: Bottom side pad count incorrect, expected {expected_bottom}, actual {position_counts['bottom']}")
        return False
    
    # Validation passed, display statistics
    print(f"📊 Validation statistics:")
    print(f"  - IO ring scale: {width} x {height}")
    print(f"  - Corner count: {len(corner_positions)}")
    print(f"  - Left side pad count: {position_counts['left']}")
    print(f"  - Right side pad count: {position_counts['right']}")
    print(f"  - Top side pad count: {position_counts['top']}")
    print(f"  - Bottom side pad count: {position_counts['bottom']}")
    print(f"  - Total outer ring pads: {sum(position_counts.values())}")
    print(f"  - Total instances: {len(instances)}")
    
    # Count device types
    device_types = {}
    for instance in instances:
        device = instance.get('device', 'unknown')
        device_types[device] = device_types.get(device, 0) + 1
    
    print(f"  - Device type statistics:")
    for device, count in sorted(device_types.items()):
        print(f"    * {device}: {count}")
    
    print("✅ Configuration validation passed")
    return True

def validate_device_suffix(device: str, position: str) -> bool:
    """Validate device suffix compatibility with position"""
    # Corner validation: only need to judge if position is a legal corner position
    if position.startswith(('top_left', 'top_right', 'bottom_left', 'bottom_right')):
        # Corner doesn't need to judge device suffix, only need position to be legal
        return True
    
    # Left and right side pads must use _H_G suffix
    if position.startswith(('left_', 'right_')):
        if not device.endswith('_H_G'):
            return False
    
    # Top and bottom side pads must use _V_G suffix
    elif position.startswith(('top_', 'bottom_')):
        if not device.endswith('_V_G'):
            return False
    
    return True

def validate_position_format(position: str, width: int, height: int) -> bool:
    """Validate position format correctness"""
    # Corner positions
    if position in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
        return True
    
    # Outer ring pad positions
    pattern = r'^(left|right|top|bottom)_(\d+)$'
    match = re.match(pattern, position)
    if match:
        side = match.group(1)
        index = int(match.group(2))
        
        if side in ['left', 'right']:
            return 0 <= index < height
        else:  # top, bottom
            return 0 <= index < width
    
    # Inner ring pad positions
    pattern = r'^(left|right|top|bottom)_(\d+)_(\d+)$'
    match = re.match(pattern, position)
    if match:
        side = match.group(1)
        index1 = int(match.group(2))
        index2 = int(match.group(3))
        
        if side in ['left', 'right']:
            return 0 <= index1 < height and 0 <= index2 < height and index1 != index2
        else:  # top, bottom
            return 0 <= index1 < width and 0 <= index2 < width and index1 != index2
    
    return False

def convert_config_to_list(config: Dict[str, Any]) -> list:
    """Convert intent graph to list format required by generator"""
    config_list = []
    
    # Add ring_config
    if 'ring_config' in config:
        ring_config = config['ring_config'].copy()
        ring_config['type'] = 'ring_config'
        config_list.append(ring_config)
    
    # Add instances
    if 'instances' in config:
        for instance in config['instances']:
            instance_config = instance.copy()
            # Keep original type field, don't override
            if 'type' not in instance_config:
                instance_config['type'] = 'instance'
            config_list.append(instance_config)
    
    return config_list

def get_config_statistics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get configuration statistics"""
    ring_config = config.get('ring_config', {})
    instances = config.get('instances', [])
    
    # Count different types of devices
    device_types = {}
    for instance in instances:
        device = instance.get('device', 'unknown')
        device_types[device] = device_types.get(device, 0) + 1
    
    # Count digital IO inputs/outputs
    digital_ios = [inst for inst in instances if inst.get('device') == 'PDDW16SDGZ']
    input_ios = [io for io in digital_ios if io.get('direction') == 'input']
    output_ios = [io for io in digital_ios if io.get('direction') == 'output']
    
    return {
        'ring_size': f"{ring_config.get('width', 'N/A')} x {ring_config.get('height', 'N/A')}",
        'total_pads': len(instances),
        'device_types': len(device_types),
        'digital_ios': len(digital_ios),
        'input_ios': len(input_ios),
        'output_ios': len(output_ios)
    } 