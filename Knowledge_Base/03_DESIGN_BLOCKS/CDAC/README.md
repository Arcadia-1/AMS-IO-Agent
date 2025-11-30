# Capacitor Knowledge Base

This directory contains a modularized knowledge base for capacitor design automation, designed specifically for AI agents.

## Purpose

This knowledge base provides structured knowledge modules for automated capacitor design, including:
- Universal design principles and workflows
- Shape-specific capacitor structures (H-shape, I-type, Sandwich, etc.)
- Technology-specific process parameters (180nm, 28nm, etc.)
- Initial parameter sets for shape-technology combinations

## For AI Agents

AI agents should:
1. Start with `KB_INDEX.md` to understand the module structure
2. Use `scan_knowledge_base()` to discover available modules
3. Load required modules based on design requirements (shape + technology)

See `KB_INDEX.md` for module combinations and usage patterns.

## Directory Structure

```
KB_Capacitor/
├── KB_INDEX.md                    # Main index (start here)
├── 00_Core_Principles.md          # Universal: Core rules
├── 01_Workflow_Framework.md       # Universal: Workflow
├── 02_Python_SKILL_Integration.md # Universal: Python/SKILL
├── 03_Shape_Specifics/            # Shape-specific modules
├── 04_Array_Generation.md         # Universal: Array generation
└── Technology_Configs/            # Technology-specific configs
```

## For Human Developers

- This knowledge base is optimized for AI consumption
- All `.md` files (except `README.md`) are loaded by AI agents
- `README.md` files are skipped during knowledge loading
- Use `INDEX.md` files for subdirectory navigation (loaded by AI)
- For development notes, use `README.md` naming

## Maintenance

When adding new modules:
- Use numbered prefixes (00-04) for core modules
- Place shape-specific modules in `03_Shape_Specifics/[SHAPE]/`
- Use `03_01_` and `03_02_` prefixes for structure and dummy modules
- Add technology configs to `Technology_Configs/`
- Initial parameters are synthesized automatically in Phase 1 based on structure rules and technology constraints (see `01_Workflow_Framework.md`)
- Update `KB_INDEX.md` with new combinations
