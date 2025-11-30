#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test IO Ring Generation Tool
"""

import sys
from pathlib import Path

# Add tools directory to Python path
tools_dir = Path(__file__).parent.parent
sys.path.append(str(tools_dir))

from src.tools.io_ring_generator_tool import generate_io_ring_schematic, list_intent_graphs, validate_intent_graph, generate_io_ring_layout

def test_list_configs():
    """Test list configuration files functionality"""
    print("🔍 Testing list IO ring configuration files...")
    result = list_intent_graphs()
    print(result)
    print()

def test_validate_config():
    """Test configuration validation functionality"""
    print("✅ Testing configuration validation functionality...")
    
    # Test simple configuration
    result = validate_intent_graph("output/example/intent_graph.json")
    print()

def test_generate_schematic():
    """Test generate schematic functionality"""
    print("🎨 Testing generate IO ring schematic...")
    
    # Test 3: Specify complete output path
    print("Test 3: Specify complete output path")
    result = generate_io_ring_schematic("output/example/intent_graph.json", "output/example/io_ring_schematic.il")
    print(result)
    print()

def test_generate_layout():
    """Test generate layout functionality"""
    print("🏗️ Testing generate IO ring layout...")
    

    
    # Test 3: Specify complete output path
    print("Test 3: Specify complete output path")
    result = generate_io_ring_layout("output/example/intent_graph.json", "output/example/io_ring_layout.il")
    print(result)
    print()

def main():
    """Main function"""
    print("🧪 IO Ring Generation Tool Test")
    print("="*50)
    
    # Test list configuration files
    test_list_configs()
    
    # Test configuration validation
    test_validate_config()
    
    # Test generate schematic
    test_generate_schematic()
    
    # Test generate layout
    test_generate_layout()
    
    print("🎉 Test completed!")

if __name__ == "__main__":
    main() 