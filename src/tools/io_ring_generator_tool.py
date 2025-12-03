from pathlib import Path
from typing import Optional, Dict, Any
import os
import sys
import json
from smolagents import tool

from src.app.schematic.schematic_generator import generate_multi_device_schematic
from src.app.intent_graph.json_validator import validate_config, convert_config_to_list, get_config_statistics
from src.app.layout.layout_generator import generate_layout_from_json, LayoutGenerator
from src.app.layout.layout_visualizer import visualize_layout, visualize_layout_from_components
from src.app.layout.device_classifier import DeviceClassifier

@tool
def generate_io_ring_schematic(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate IO ring schematic SKILL code from intent graph file
    
    Args:
        config_file_path: Path to intent graph file (REQUIRED - use absolute path for better file management)
        output_file_path: Complete path for output file (STRONGLY RECOMMENDED - specify explicit path for better file organization. If not provided, defaults to output directory based on config filename)
        
    Returns:
        String description of generation result, including file path and statistics
        
    Note:
        For better file management, it is STRONGLY RECOMMENDED to:
        1. Use absolute paths for both input and output files
        2. Explicitly specify output_file_path to organize files in timestamped directories
        3. Keep related files (intent graph, schematic, layout) in the same directory
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Check if template file exists (try multiple locations and filenames)
        template_file = None
        possible_paths = [
            # Standard filename in standard locations
            Path("src/schematic") / "device_templates.json",  # Preferred location
            Path("device_templates.json"),  # Current directory
            Path("src/scripts/devices") / "device_templates.json",  # Script output location
            # Alternative filename (IO_device_info_T28.json) in same locations
            Path("src/schematic") / "IO_device_info_T28.json",
            Path("IO_device_info_T28.json"),  # Current directory
            Path("src/scripts/devices") / "IO_device_info_T28.json",  # Actual file location
        ]
        
        for path in possible_paths:
            if path.exists():
                template_file = path
                break
        
        if template_file is None:
            return "❌ Error: device template file not found.\n" \
                   "Expected files: device_templates.json or IO_device_info_T28.json\n" \
                   "Please check if the file exists in one of these locations:\n" \
                   "  - src/schematic/device_templates.json\n" \
                   "  - src/scripts/devices/IO_device_info_T28.json\n" \
                   "  - project root directory\n" \
                   "Or generate it by running:\n" \
                   "  cd src/scripts/devices && python IO_device_info_T28_parser.py"
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load intent graph file {e}"
        
        # Convert configuration format
        config_list = convert_config_to_list(config)
        
        # Process output file path
        if output_file_path is None:
            # Default output to output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{config_path.stem}_generated.il"
        else:
            # Use user-specified output path
            output_path = Path(output_file_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # If user didn't specify file extension, automatically add .il
            if output_path.suffix.lower() != '.il':
                output_path = output_path.with_suffix('.il')
        
        # Generate schematic
        # Library name, cell name, and view name are read from config or use defaults
        try:
            generate_multi_device_schematic(config_list, str(output_path))
            
            # Get statistics from config_list (filter out ring_config items)
            device_instances = [item for item in config_list if isinstance(item, dict) and 'device' in item]
            device_count = len(device_instances)
            device_types = set()
            for item in device_instances:
                if 'device' in item:
                    device_types.add(item['device'])
            
            result = f"✅ Successfully generated schematic file: {output_path}\n"
            result += f"📊 Statistics:\n"
            result += f"  - Device instance count: {device_count}\n"
            if device_types:
                result += f"  - Device types used: {', '.join(sorted(device_types))}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Failed to generate schematic: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while generating IO ring schematic: {e}"

@tool
def generate_io_ring_layout(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate IO ring layout SKILL code from intent graph file
    
    Args:
        config_file_path: Path to intent graph file (REQUIRED - use absolute path for better file management)
        output_file_path: Complete path for output file (STRONGLY RECOMMENDED - specify explicit path for better file organization. If not provided, defaults to output directory based on config filename)
        
    Returns:
        String description of generation result, including file path and statistics
        
    Note:
        For better file management, it is STRONGLY RECOMMENDED to:
        1. Use absolute paths for both input and output files
        2. Explicitly specify output_file_path to organize files in timestamped directories
        3. Keep related files (intent graph, schematic, layout) in the same directory
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_file_path} does not exist"
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load intent graph file {e}"
        
        # Process output file path
        if output_file_path is None:
            # Default output to output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{config_path.stem}_layout.il"
        else:
            # Use user-specified output path
            output_path = Path(output_file_path)
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # If user didn't specify file extension, automatically add .il
            if output_path.suffix.lower() != '.il':
                output_path = output_path.with_suffix('.il')
        
        # Generate layout
        # Library name, cell name, and view name are read from config or use defaults
        try:
            result_file = generate_layout_from_json(str(config_path), str(output_path))
            
            # Automatically generate visualization
            vis_output_path = None
            try:
                vis_output_path = output_path.parent / f"{output_path.stem}_visualization.png"
                visualize_layout(str(output_path), str(vis_output_path))
            except Exception as vis_e:
                # Visualization is optional, don't fail if it doesn't work
                pass
            
            # Return success message with visualization info if generated
            if vis_output_path and vis_output_path.exists():
                return f"✅ Successfully generated layout file: {output_path}\n" \
                       f"📊 Layout visualization generated: {vis_output_path}\n" \
                       f"💡 Tip: Review the visualization image to verify the layout arrangement."
            else:
                return f"✅ Successfully generated layout file: {output_path}"
        except Exception as e:
            return f"❌ Failed to generate layout: {e}"
    except Exception as e:
        return f"❌ Error occurred while generating IO ring layout: {e}"

@tool
def list_intent_graphs(directory: str = "output") -> str:
    """
    List all intent graph files in the specified directory
    
    Args:
        directory: Directory path to search, defaults to output directory
        
    Returns:
        String containing list of intent graph files
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            # Try alternative locations
            alt_paths = [
                Path("output/generated"),
                Path("src/schematic"),
                Path("output"),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    dir_path = alt_path
                    break
            else:
                return f"❌ Error: Directory {directory} does not exist. Tried: {directory}, output/generated, src/schematic, output"
        
        # Collect all JSON files
        json_files = list(dir_path.glob("*.json"))
        
        if not json_files:
            return f"No JSON files found in directory {directory}"
        
        # Filter files that might be intent graphs
        intent_graphs = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'ring_config' in config and 'instances' in config:
                        ring_config = config['ring_config']
                        instances = config['instances']
                        intent_graphs.append({
                            'file': json_file.name,
                            'size': f"{ring_config.get('width', 'N/A')}x{ring_config.get('height', 'N/A')}",
                            'pads': len(instances)
                        })
            except:
                continue
        
        if not intent_graphs:
            return f"No valid intent graph files found in directory {directory}"
        
        result = f"Found the following intent graph files in directory {directory}:\n"
        for config in intent_graphs:
            result += f"  - {config['file']}: {config['size']} scale, {config['pads']} pads\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while listing intent graph files: {e}"

@tool
def visualize_io_ring_layout(il_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate visual diagram from SKILL layout file
    
    This tool creates a visual representation of the IO ring layout without requiring Virtuoso.
    It parses the SKILL code and generates a diagram with colored rectangles representing different device types.
    
    Args:
        il_file_path: Path to SKILL layout file (.il file)
        output_file_path: Optional path for output image (defaults to same directory as input with _visualization.png suffix)
        
    Returns:
        String description of visualization result, including file path
    """
    try:
        il_path = Path(il_file_path)
        if not il_path.exists():
            return f"❌ Error: Layout file {il_file_path} does not exist"
        
        if il_path.suffix.lower() != '.il':
            return f"❌ Error: File {il_file_path} is not a valid SKILL layout file (.il)"
        
        # Process output file path
        if output_file_path is None:
            output_path = il_path.parent / f"{il_path.stem}_visualization.png"
        else:
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.suffix.lower() != '.png':
                output_path = output_path.with_suffix('.png')
        
        # Generate visualization
        try:
            result_path = visualize_layout(str(il_path), str(output_path))
            return f"✅ Visualization generated successfully!\n📁 Output file: {result_path}\n\n" \
                   f"The visualization shows the IO ring layout with:\n" \
                   f"  - Colored rectangles representing different device types\n" \
                   f"  - Device names labeled in the center of each rectangle\n" \
                   f"  - Rectangles arranged in a ring formation (20×110 units each)"
        except Exception as e:
            return f"❌ Failed to generate visualization: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while visualizing layout: {e}"

@tool
def visualize_io_ring_from_json(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate visual diagram directly from JSON intent graph file (without generating SKILL file)
    
    This tool creates a visual representation of the IO ring layout directly from the JSON intent graph,
    without requiring an intermediate SKILL file. It's equivalent to generating layout and then visualizing,
    but more efficient when you only need the visualization.
    
    Args:
        config_file_path: Path to JSON intent graph file (can be relative or absolute path)
        output_file_path: Optional path for output image (defaults to same directory as config with _visualization.png suffix)
        
    Returns:
        String description of visualization result, including file path
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_file_path} does not exist"
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load intent graph file {e}"
        
        # Validate intent graph
        if not validate_config(config):
            return "❌ Error: Intent graph validation failed"
        
        # Get instances and ring_config
        instances = config.get("instances", [])
        ring_config = config.get("ring_config", {})
        
        # Merge top-level library_name and cell_name into ring_config if they exist
        if "library_name" in config and "library_name" not in ring_config:
            ring_config["library_name"] = config["library_name"]
        if "cell_name" in config and "cell_name" not in ring_config:
            ring_config["cell_name"] = config["cell_name"]
        
        # Initialize layout generator
        generator = LayoutGenerator()
        generator.set_config(ring_config)
        
        # Set defaults if not provided
        if "pad_width" not in ring_config:
            ring_config["pad_width"] = generator.config["pad_width"]
        if "pad_height" not in ring_config:
            ring_config["pad_height"] = generator.config["pad_height"]
        if "corner_size" not in ring_config:
            ring_config["corner_size"] = generator.config["corner_size"]
        if "pad_spacing" not in ring_config:
            ring_config["pad_spacing"] = generator.config["pad_spacing"]
        if "library_name" not in ring_config:
            ring_config["library_name"] = generator.config["library_name"]
        if "view_name" not in ring_config:
            ring_config["view_name"] = generator.config["view_name"]
        
        # Convert relative positions to absolute positions
        if any("position" in instance and "_" in str(instance["position"]) for instance in instances):
            instances = generator.convert_relative_to_absolute(instances, ring_config)
        
        # Separate components
        outer_pads = []
        inner_pads = []
        corners = []
        
        for instance in instances:
            if instance.get("type") == "inner_pad":
                inner_pads.append(instance)
            elif instance.get("type") == "pad":
                outer_pads.append(instance)
            elif instance.get("type") == "corner":
                corners.append(instance)
        
        # Check if filler components are already present
        all_instances = instances
        existing_fillers = [comp for comp in all_instances if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", ""))]
        existing_separators = [comp for comp in all_instances if comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", ""))]
        
        if existing_fillers or existing_separators:
            # Use existing fillers from JSON
            validation_components = outer_pads + corners
            all_components_with_fillers = validation_components
            # Add existing fillers and separators
            for comp in all_instances:
                if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", "")):
                    all_components_with_fillers.append(comp)
                elif comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", "")):
                    all_components_with_fillers.append(comp)
        else:
            # Auto-generate fillers
            validation_components = outer_pads + corners
            all_components_with_fillers = generator.auto_filler_generator.auto_insert_fillers_with_inner_pads(validation_components, inner_pads)
        
        # Add inner pads to components list
        all_components_with_fillers.extend(inner_pads)
        
        # Process output file path
        if output_file_path is None:
            output_path = config_path.parent / f"{config_path.stem}_visualization.png"
        else:
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.suffix.lower() != '.png':
                output_path = output_path.with_suffix('.png')
        
        # Generate visualization directly from components
        try:
            result_path = visualize_layout_from_components(all_components_with_fillers, str(output_path))
            return f"✅ Visualization generated successfully from JSON!\n📁 Output file: {result_path}\n\n" \
                   f"The visualization shows the IO ring layout with:\n" \
                   f"  - Colored rectangles representing different device types\n" \
                   f"  - Device names labeled in the center of each rectangle\n" \
                   f"  - Rectangles arranged in a ring formation"
        except Exception as e:
            return f"❌ Failed to generate visualization: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while visualizing layout from JSON: {e}"

@tool
def validate_intent_graph(config_file_path: str) -> str:
    """
    Validate the format and content of intent graph file
    
    Args:
        config_file_path: Path to JSON intent graph file
        
    Returns:
        String description of validation result
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        
        # Load intent graph
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ JSON format error: {e}"
        except Exception as e:
            return f"❌ Failed to load intent graph file: {e}"
        
        # Validate intent graph
        if not validate_config(config):
            return "❌ Intent graph validation failed"
        
        # Get intent graph statistics
        stats = get_config_statistics(config)
        
        result = f"✅ Intent graph file validation passed!\n"
        result += f"📊 Intent graph statistics:\n"
        result += f"  - IO ring scale: {stats['ring_size']}\n"
        result += f"  - Total pad count: {stats['total_pads']}\n"
        result += f"  - Device types: {stats['device_types']}\n"
        if stats['digital_ios'] > 0:
            result += f"  - Digital IOs: {stats['digital_ios']} ({stats['input_ios']} inputs, {stats['output_ios']} outputs)\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while validating intent graph file: {e}" 