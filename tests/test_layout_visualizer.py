#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Layout Visualizer - Test pad ring visualization from layout SKILL code
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.schematic.layout_visualizer import visualize_layout_ring
from src.tools.io_ring_generator_tool import visualize_layout_ring_from_skill


def test_visualize_layout():
    """Test layout visualization"""
    print("🧪 Testing Layout Visualizer")
    print("=" * 50)
    
    # Test with example layout file
    layout_file = "output/example/io_ring_layout.il"
    output_file = "output/example/io_ring_layout_diagram.png"
    
    if not Path(layout_file).exists():
        print(f"❌ Layout file not found: {layout_file}")
        print("💡 Tip: Run generate_io_ring_layout first to create the layout file")
        return
    
    print(f"📄 Input layout file: {layout_file}")
    print(f"🖼️  Output diagram: {output_file}")
    print()
    
    try:
        # Test direct function
        print("Test 1: Direct visualization function")
        result = visualize_layout_ring(layout_file, output_file)
        print(result)
        print()
        
        # Test tool function
        print("Test 2: Tool function")
        result2 = visualize_layout_ring_from_skill(layout_file, output_file.replace('.png', '_tool.png'))
        print(result2)
        print()
        
        print("✅ All tests completed successfully!")
        print(f"📊 Check the generated diagrams:")
        print(f"   - {output_file}")
        print(f"   - {output_file.replace('.png', '_tool.png')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_with_generated_layout():
    """Test with a generated layout file if available"""
    print("\n" + "=" * 50)
    print("🧪 Testing with generated layout files")
    print("=" * 50)
    
    # Look for generated layout files
    generated_dir = Path("output/generated")
    if not generated_dir.exists():
        print("⚠️  No generated directory found")
        return
    
    # Find latest generated layout file
    layout_files = list(generated_dir.rglob("io_ring_layout.il"))
    if not layout_files:
        print("⚠️  No generated layout files found")
        print("💡 Tip: Run generate_io_ring_layout to create layout files")
        return
    
    # Sort by modification time
    layout_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest_file = layout_files[0]
    
    print(f"📄 Found generated layout file: {latest_file}")
    
    output_file = latest_file.with_suffix('.png')
    print(f"🖼️  Output diagram: {output_file}")
    print()
    
    try:
        result = visualize_layout_ring(str(latest_file), str(output_file))
        print(result)
        print("✅ Generated layout visualization completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_visualize_layout()
    test_with_generated_layout()

