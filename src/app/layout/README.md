# Layout Generation

Layout generation module for IO rings and other IC components.

## Components

- `layout_generator.py` - Main layout generation orchestrator
- `position_calculator.py` - Calculate pad positions for IO rings
- `voltage_domain.py` - Handle voltage domain logic
- `device_classifier.py` - Classify and categorize devices
- `filler_generator.py` - Generate filler cells
- `auto_filler.py` - Automatic filler generation
- `inner_pad_handler.py` - Handle inner pad placement
- `layout_validator.py` - Validate generated layouts
- `layout_visualizer.py` - Visualize layouts
- `skill_generator.py` - Generate SKILL code for layouts

## Usage

Used by the IO ring generator tool to create layout SKILL code from configuration files.

