# Technology Configurations Index

This directory contains process-specific technology configuration files for different technology nodes.

## Available Technologies

### 180nm Technology
- **File**: `180nm_Technology.md`
- **Domain name**: `Technology_Configs_180nm_Technology`
- **Key parameters**:
  - DRC minima: ≥0.28µm
  - Metals: METAL1-METAL5
  - Via pitch: 0.52µm
  - Width quantization: 0.38 + 0.52×n

### 28nm Technology
- **File**: `28nm_Technology.md`
- **Domain name**: `Technology_Configs_28nm_Technology`
- **Key parameters**:
  - DRC minima: ≥0.05µm
  - Metals: M1-M7
  - Via pitch: 0.13µm
  - Width quantization: 0.11 + 0.13×n

## Usage

Each technology configuration file defines:
- DRC rules (minimum spacing/width)
- Width quantization rules
- Via parameters (pitch, margin)
- Metal layer restrictions
- Constraint validation rules

Note: Initial parameters are synthesized in Phase 1 from structure rules and technology constraints.

## Technology Configuration Interface

All technology configurations must implement the interface defined in `INTERFACE_SPEC.md`. This ensures:
- Consistent parameter names across all technologies
- Shape modules can reliably access required parameters
- Validation rules are clear and enforceable

See `INTERFACE_SPEC.md` for:
- Complete list of required parameters
- Parameter usage by shape modules
- Validation rules and checklists
- Template for creating new technology configs

## Adding New Technologies

To add a new technology node:
1. Read `INTERFACE_SPEC.md` first - Understand the required interface contract
2. Create `[TECHNOLOGY]nm_Technology.md` following the interface specification
3. Verify all required parameters are defined (use checklist in INTERFACE_SPEC.md)
4. Update this INDEX.md with the new technology entry
5. Update `KB_INDEX.md` with example combinations using the new technology

## Related Documents

- **INTERFACE_SPEC.md** - Technology configuration interface specification (required reading)
- **KB_INDEX.md** - Main knowledge base index with module combinations
