# Technology Configuration Interface Specification

This document defines the interface contract that all technology configuration files must implement. Shape-specific modules rely on these parameters being available.

Purpose: Ensure consistent decoupling between shape structures and technology parameters. Any new technology config must follow this interface.

---

## Required Parameters

Every technology configuration file must define the following parameters:

### 1. DRC Rules

#### `min_spacing` (µm)
- **Type**: Number (≥ 0)
- **Description**: Minimum spacing between any two metal features
- **Used by**: Shape modules for spacing validation (finger_d, frame_to_finger_d, spacing)
- **Example**: 0.28 (180nm), 0.05 (28nm)

#### `min_width` (µm)
- **Type**: Number (≥ 0)
- **Description**: Minimum width for any metal feature
- **Used by**: Shape modules for width validation (finger_vertical_width, frame_vertical_width, etc.)
- **Example**: 0.28 (180nm), 0.05 (28nm)

#### `min_area` (µm²) - Optional
- **Type**: Number (≥ 0) or null
- **Description**: Minimum polygon area requirement (if applicable)
- **Used by**: Shape modules for area validation
- **Example**: 0.017 (28nm), null (180nm if not applicable)

### 2. Via Parameters

#### `via_pitch` (µm)
- **Type**: Number (> 0)
- **Description**: Pitch between via cuts (center-to-center distance)
- **Used by**: Shape modules for via array sizing calculations
- **Formula**: `cut_columns = max(1, floor((width + via_margin) / via_pitch))`
- **Example**: 0.52 (180nm), 0.13 (28nm)

#### `via_margin` (µm)
- **Type**: Number (≥ 0)
- **Description**: Margin added to metal widths for via array sizing
- **Used by**: Shape modules for via row/column count calculations
- **Formula**: `cut_rows = max(1, floor((metal_width + via_margin) / via_pitch))`
- **Example**: 0.14 (180nm), 0.02 (28nm)

### 3. Width Quantization

#### `width_quantization_base` (µm)
- **Type**: Number (> 0)
- **Description**: Base value for horizontal width quantization formula
- **Formula**: Width = `width_quantization_base + width_quantization_step × n` (where n ∈ N)
- **Used by**: Shape modules for quantized horizontal widths (frame_horizontal_width, middle_horizontal_width)
- **Example**: 0.38 (180nm), 0.11 (28nm)

#### `width_quantization_step` (µm)
- **Type**: Number (> 0)
- **Description**: Step size for width quantization formula
- **Formula**: Width = `width_quantization_base + width_quantization_step × n` (where n ∈ N)
- **Used by**: Shape modules for quantized horizontal widths
- **Example**: 0.52 (180nm), 0.13 (28nm)

### 4. Metal Layer Configuration

#### `allowed_metals` (list)
- **Type**: List of strings
- **Description**: List of allowed metal layer names (in order from lowest to highest)
- **Used by**: Shape modules for layer validation and via naming
- **Naming convention**: Must be consistent within a technology (either "METAL" or "M" prefix)
- **Example 180nm**: `["METAL1", "METAL2", "METAL3", "METAL4", "METAL5"]`
- **Example 28nm**: `["M1", "M2", "M3", "M4", "M5", "M6", "M7"]`

#### `metal_naming_style` (string)
- **Type**: "METAL" or "M"
- **Description**: Prefix style for metal layer names
- **Used by**: Shape modules for consistent via naming
- **Rules**:
  - If style is "METAL": Use `METAL5_METAL4` format for via names
  - If style is "M": Use `M7_M6` format for via names
- **Example**: "METAL" (180nm), "M" (28nm)

#### `low_parasitic_forbidden_metals` (list) - Optional
- **Type**: List of strings
- **Description**: Metal layers forbidden in low-parasitic mode (typically includes M1)
- **Used by**: Shape modules for low-parasitic constraint validation
- **Example 28nm**: `["M1"]`
- **Example 180nm**: `["METAL1"]` (if applicable)

---

## Parameter Usage by Shape Modules

### H-shape Structure Module (03_01_H_Shape_Structure.md)

**Required from Technology Config:**
- `min_spacing` → Validates: finger_d, frame_to_finger_d, spacing
- `min_width` → Validates: finger_vertical_width, frame_vertical_width, frame_horizontal_width, middle_horizontal_width
- `via_pitch` → Calculates: cut_columns, cut_rows_topbot, cut_rows_mid
- `via_margin` → Calculates: via array dimensions
- `width_quantization_base` + `width_quantization_step` → Quantizes: horizontal widths
- `allowed_metals` → Validates: layerList
- `metal_naming_style` → Formats: via definition names

**Example formula usage:**
```python
# Via column count
cut_columns = max(1, floor((h_right_x - h_left_x + via_margin) / via_pitch))

# Via row count for top/bottom
cut_rows_topbot = max(1, floor((frame_horizontal_width + via_margin) / via_pitch))

# Width quantization
quantized_width = width_quantization_base + width_quantization_step * n
```

---

## Validation Rules

### When AI loads a technology config, it must verify:

1. **All required parameters present**
   - min_spacing defined
   - min_width defined
   - via_pitch defined
   - via_margin defined
   - width_quantization_base defined
   - width_quantization_step defined
   - allowed_metals defined (non-empty list)
   - metal_naming_style defined ("METAL" or "M")

2. **Parameter values valid**
   - min_spacing > 0
   - min_width > 0
   - via_pitch > 0
   - via_margin ≥ 0
   - width_quantization_base > 0
   - width_quantization_step > 0
   - allowed_metals is non-empty list
   - metal_naming_style matches actual layer names in allowed_metals

3. **Consistency checks**
   - All layer names in allowed_metals use the same prefix (METAL or M)
   - metal_naming_style matches the prefix used in allowed_metals
   - If low_parasitic_forbidden_metals defined, all entries must be in allowed_metals

### When AI generates layout using shape + technology:

1. **Parameter application**
   - Use technology's min_spacing to validate all spacing parameters
   - Use technology's min_width to validate all width parameters
   - Use technology's via_pitch and via_margin in via calculations
   - Use technology's quantization rules for horizontal widths
   - Use technology's allowed_metals to validate layerList
   - Use technology's metal_naming_style for via names

2. **Constraint enforcement**
   - All spacings ≥ min_spacing
   - All widths ≥ min_width
   - Horizontal widths follow quantization formula
   - Layer names match allowed_metals
   - Via names use correct naming style

---

## Technology Config Template

When creating a new technology configuration, use this structure:

```markdown
# [TECHNOLOGY]nm Technology Configuration - Process-specific parameters (DRC: ≥[min_spacing]µm, Metals: [allowed_metals_list], Via pitch: [via_pitch]µm)

## DRC Rules
- min_spacing: ≥ [value] µm
- min_width: ≥ [value] µm
- min_area: [value] µm² (if applicable)

## Via Parameters
- via_pitch: [value] µm
- via_margin: [value] µm

## Width Quantization
- width_quantization_base: [value] µm
- width_quantization_step: [value] µm
- Formula: width = [base] + [step]×n

## Metal Layer Configuration
- allowed_metals: [list]
- metal_naming_style: "[METAL|M]"
- low_parasitic_forbidden_metals: [list] (if applicable)
```

---

## Parameter Naming Convention

### In Technology Configs
- Use descriptive names: `via_pitch`, `via_margin`, `min_spacing`
- Always include units in documentation: `(µm)`, `(µm²)`
- Provide clear examples and formulas

### In Shape Modules
- Reference technology parameters explicitly: "Use `via_pitch` from technology config"
- Never hardcode technology-specific values
- Always show formulas with parameter names, not numbers

### Example Pattern

**Technology Config:**
```markdown
## Via Parameters
- **via_pitch**: 0.52 µm
- **via_margin**: 0.14 µm
```

**Shape Module:**
```markdown
- Use `via_pitch` and `via_margin` from technology config
- Formula: `cut_columns = max(1, floor((width + via_margin) / via_pitch))`
```

---

## Adding a New Technology

### Checklist
- [ ] Create `[TECHNOLOGY]nm_Technology.md` following the template
- [ ] Define all required parameters (min_spacing, min_width, via_pitch, via_margin, width_quantization_base, width_quantization_step, allowed_metals, metal_naming_style)
- [ ] Verify parameter values are valid (positive numbers, non-empty lists)
- [ ] Ensure metal_naming_style matches allowed_metals prefix
- [ ] Add to Technology_Configs/INDEX.md
- [ ] Update KB_INDEX.md with example combinations using the new technology
- [ ] Test with existing shapes (H-shape) to verify compatibility

---

## Common Pitfalls

### Don't hardcode technology values in shape modules
```markdown
# BAD
cut_columns = max(1, floor((width + 0.14) / 0.52))  # 180nm-specific!

# GOOD
cut_columns = max(1, floor((width + via_margin) / via_pitch))  # Uses tech config
```

### Don't mix naming styles
```markdown
# BAD (inconsistent)
allowed_metals: ["M1", "METAL2", "M3"]

# GOOD (consistent)
allowed_metals: ["M1", "M2", "M3"]
metal_naming_style: "M"
```

### Don't omit required parameters
```markdown
# BAD - missing via_margin
## Via Parameters
- via_pitch: 0.13 µm

# GOOD - all required parameters defined
## Via Parameters
- via_pitch: 0.13 µm
- via_margin: 0.02 µm
```

---

## Related Documents

- **Technology_Configs/INDEX.md** - List of available technology configurations
- **03_Shape_Specifics/[SHAPE]/03_01_[SHAPE]_Structure.md** - Shape modules that consume these parameters
- **KB_INDEX.md** - Module combination examples
