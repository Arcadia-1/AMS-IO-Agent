# CapArray-Bench: Capacitor Array Design Benchmark

A comprehensive benchmark dataset for automated capacitor array (CDAC) design using LLMs in Cadence Virtuoso.

## Quick Stats

| **Metric** | **Value** |
|------------|-----------|
| **Total Cases** | 135 (40 CDAC + 95 Capacitance/Shape) |
| **CDAC Cases** | 40 (20 sheets × 2 template types) |
| **Capacitance/Shape Cases** | 95 (19 capacitances × 5 shapes) |
| **Tech Node** | 28nm |
| **Template Types** | Full Flow, Array Only, Capacitance/Shape |
| **Capacitance Range** | 0.1 fF - 10 fF (19 values) |
| **Shape Types** | 5 shapes (H, H_shieldless, I, I_shield, sandwich_simplified_h_notch) |

## Structure

```
CapArray-Bench/
├── floorplan/                    # Excel files with CDAC array layouts
│   ├── CDAC_3-8bit.xlsx         # Main CDAC array configuration file
│   └── ...
├── cdac_full_flow/              # Full flow prompts (unit + dummy + array)
│   └── CDAC_3-8bit/             # Organized by Excel file name
│       └── [sheet_name].txt     # One prompt per Excel sheet
├── cdac_array_only/             # Array-only prompts (skip unit/dummy)
│   └── CDAC_3-8bit/
│       └── [sheet_name].txt
├── capacitance_shape/            # Capacitance/shape combination prompts
│   ├── H/                       # H-shape capacitor prompts
│   ├── H_shieldless/            # H-shape without shield
│   ├── I/                       # I-shape capacitor prompts
│   ├── I_shield/                # I-shape with shield
│   └── sandwich_simplified_h_notch/  # Sandwich capacitor prompts
└── README.md
```

## Template Types

### 1. Full Flow (`full`)
Complete CDAC capacitor system design in three phases:
- **Phase 1**: Design unit H-shape capacitor (6 fF target)
- **Phase 2**: Generate dummy capacitor based on unit
- **Phase 3**: Generate CDAC array using unit and dummy

**Cell Names:**
- Unit: `C_MAIN_6fF_{prefix}_full_flow_{sheet_name}`
- Dummy: `C_DUMMY_6fF_{prefix}_full_flow_{sheet_name}`
- Array: `C_CDAC_6fF_{prefix}_full_flow_{sheet_name}`

### 2. Array Only (`array`)
Generate CDAC array only (assumes unit and dummy already exist):
- Load knowledge base and perform IR
- Skip unit and dummy generation
- Generate and verify array directly

**Cell Names:**
- Array: `C_CDAC_6fF_{prefix}_only_array_{sheet_name}`

### 3. Capacitance/Shape (`capacitance_shape`)
Unit and dummy capacitor design for different capacitance values and shapes:
- **Capacitance Values**: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 fF (19 values)
- **Shapes**: H, H_shieldless, I, I_shield, sandwich_simplified_h_notch (5 shapes)
- **Total Combinations**: 19 × 5 = 95 experiments

**Cell Names:**
- Unit: `C_MAIN_{cap_str}fF_{shape_key}`
- Dummy: `C_DUMMY_{cap_str}fF_{shape_key}`

## File Naming

### CDAC Prompts
```
CDAC_[excel_name]_[template_type]_[sheet_name].txt

Examples:
- CDAC_3-8bit_full_flow_Sheet1.txt
- CDAC_3-8bit_only_array_Sheet2.txt
```

### Capacitance/Shape Prompts
```
Cap_{cap_value}fF_{shape_key}.txt

Examples:
- Cap_0_1fF_H.txt (0.1 fF, H-shape)
- Cap_1fF_I_shield.txt (1 fF, I-shape with shield)
- Cap_6fF_sandwich_simplified_h_notch.txt (6 fF, sandwich)
```

## File Format

Each prompt file contains structured task description with clear phases:

```
Task: Design a complete CDAC capacitor system in three phases:
1. Phase 1: Design unit H-shape capacitor with target capacitance of 6 fF
2. Phase 2: Generate dummy capacitor based on the unit capacitor
3. Phase 3: Generate capacitor array using the unit and dummy capacitors

Design constraints:
- Target capacitance: 6 fF
- Height constraint: less than 2 µm
- Low parasitic capacitance to ground required
...

Configuration:
- Technology: 28nm process node
- Library: LLM_Layout_Design
- Cell names: ...
- CDAC array layout file: [excel_file], Sheet name: [sheet_name]
```

## Usage

### Single Test Case
```bash
# CDAC full flow
python main.py --prompt-file CapArray-Bench/cdac_full_flow/CDAC_3-8bit/Sheet1.txt

# Capacitance/shape
python main.py --prompt-file CapArray-Bench/capacitance_shape/H/Cap_6fF_H.txt
```

### Batch Experiments
```bash
# CDAC experiments
python run_batch_experiments.py --prefix claude --model-name claude --template-type array
python run_batch_experiments.py --prefix claude --model-name claude --template-type full

# Capacitance/shape experiments
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --model-name claude
```

## Design Constraints

### Unit Capacitor (for CDAC)
- **Target Capacitance**: 6 fF
- **Shape**: H-shape
- **Dimensions**: 
  - unit_height = 1.920 µm
  - unit_width = 1.430 µm
  - frame_horizontal_width = 0.110 µm
  - frame_vertical_width = 0.110 µm
- **Metal Layers**: M7 M6 M5 M4 M3
- **BOT Terminal Offset**: bot_offset_x = 0 µm, bot_offset_y = 0 µm

### Capacitance/Shape Design
- **Capacitance Range**: 0.1 fF to 10 fF
- **Height Constraint**: less than 2 µm
- **Low Parasitic**: Low parasitic capacitance to ground required

## Verification Steps

All prompts include mandatory verification steps:
1. Generate SKILL code
2. Execute SKILL code using `run_il_file` or `run_il_with_screenshot`
3. Run DRC verification using `run_drc`
4. Run PEX extraction using `run_pex`
5. Verify results and iterate if necessary

## Benchmark Metrics

Evaluate LLM performance on:
1. **Correctness** - Accurate capacitor design
2. **Completeness** - All phases completed
3. **DRC/LVS Clean** - No violations
4. **Capacitance Accuracy** - Meets target capacitance
5. **Efficiency** - Time and iterations

## File Statistics

### CDAC Experiments
- **Full Flow**: 20 prompts (one per Excel sheet)
- **Array Only**: 20 prompts (one per Excel sheet)
- **Total CDAC**: 40 prompts

### Capacitance/Shape Experiments
- **H-shape**: 19 prompts (0.1 fF to 10 fF)
- **H-shieldless**: 19 prompts
- **I-shape**: 19 prompts
- **I-shield**: 19 prompts
- **Sandwich**: 19 prompts
- **Total Capacitance/Shape**: 95 prompts

### Grand Total
- **135 prompt files** organized by template type and configuration

## Excel File Structure

The benchmark uses `CDAC_3-8bit.xlsx` with 20 sheets:
- 3bit_1, 3bit_2 (3-bit CDAC arrays)
- 4bit_1, 4bit_2 (4-bit CDAC arrays)
- 5bit_1, 5bit_2 (5-bit CDAC arrays)
- 6bit_1, 6bit_2 (6-bit CDAC arrays)
- 8bit_1, 8bit_2 (8-bit CDAC arrays)
- 10bit_1, 10bit_2 (10-bit CDAC arrays)
- ... (additional configurations)

Each sheet contains the CDAC array layout configuration for that specific bit width and variant.

## Version

**v1.0** (2025-11-30) - Initial release with 135 test cases

---

**Dataset:** 135 cases | **Tech:** 28nm | **License:** AMS-IO-Agent Project

