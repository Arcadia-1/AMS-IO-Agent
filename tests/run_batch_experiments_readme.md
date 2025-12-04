# Batch Experiments - Unified Experiment Script

This project uses a unified batch experiment script `run_batch_experiments.py` that supports multiple experiment types. All experiment prompts are dynamically generated at runtime, eliminating the need to predefine them in YAML files.

## Improvements

### Previous Issues
1. **Code Duplication**: Maintained nearly identical scripts for each model (claude, gpt, deepseek)
2. **Bloated YAML Files**: Needed to predefine prompts for each sheet in `user_prompts.yaml`, resulting in huge files that were difficult to maintain
3. **Maintenance Difficulties**: Modifying prompt templates required updating multiple files and YAML entries
4. **Scattered Scripts**: Multiple different batch scripts with duplicate functionality

### Current Solution
1. **Unified Script**: Only one `run_batch_experiments.py` needed, supporting all experiment types
2. **Dynamic Prompt Generation**: No longer depends on YAML files; prompts are dynamically generated at runtime
3. **Easy Maintenance**: Prompt templates are centrally managed in code (dictionary registry pattern), modify once to update all
4. **Easy Extension**: Adding new templates only requires adding entries to the dictionary

## Experiment Types

The script supports two experiment types:

1. **`cdac`** (default): CDAC array experiments based on sheets in Excel files
2. **`capacitance_shape`**: Capacitance value and shape combination experiments (19 capacitance values × 5 shapes = 95 experiments)

## Usage

### 1. CDAC Experiments

Run CDAC array experiments based on sheets in Excel files.

#### Basic Usage

```bash
# Run default experiments (array-only mode, no prefix)
python run_batch_experiments.py

# Run Claude model experiments (array-only mode, using 'claude_' prefix)
python run_batch_experiments.py --prefix claude --model-name claude

# Run full flow experiments (unit + dummy + array) using Claude model
python run_batch_experiments.py --prefix claude --model-name claude --template-type full

# Run GPT model experiments (array-only mode, using 'gpt_' prefix)
python run_batch_experiments.py --prefix gpt --model-name gpt-4o

# Run DeepSeek model experiments (array-only mode, using 'deepseek_' prefix)
python run_batch_experiments.py --prefix deepseek --model-name deepseek

# Preview generated prompt
python run_batch_experiments.py --prefix claude --template-type full --preview-prompt first

# Start from the 5th experiment
python run_batch_experiments.py --prefix claude --start-index 5

# Run only the first 10 experiments
python run_batch_experiments.py --prefix claude --stop-index 10

# Run in parallel (using different RAMIC ports)
python run_batch_experiments.py --prefix claude --ramic-port-start 65432
```

### 2. Capacitance/Shape Experiments

Run combination experiments of different capacitance values and unit capacitor shapes.

#### Experiment Configuration
- **Capacitance Values**: 19 values (0.1, 0.2, ..., 0.9, 1, 2, ..., 10 fF)
- **Shapes**: 5 shapes (H, H_shieldless, I, I_shield, sandwich_simplified_h_notch)
- **Total Experiments**: 95 (19 × 5)
- **Timeout per Experiment**: 50 minutes

#### Basic Usage

```bash
# Run all capacitance value and shape combinations (95 experiments)
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --model-name claude

# Preview first prompt
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --preview-prompt first

# Start from the 10th experiment
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 10

# Run only the first 20 experiments
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --stop-index 20

# Run in parallel (using different RAMIC ports)
# Terminal 1: Run first 32 experiments
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 1 --stop-index 32 --ramic-port-start 65432

# Terminal 2: Run experiments 33 to 64
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 33 --stop-index 64 --ramic-port-start 65433

# Terminal 3: Run remaining experiments
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 65 --ramic-port-start 65434
```

## Template Types

The script supports three prompt template types:

1. **`array`** (CDAC default): Only generate CDAC array, skip unit cell and dummy generation
   - Suitable when unit and dummy already exist
   - Faster, only executes Phase 3

2. **`full`** (CDAC): Complete flow with three phases
   - Phase 1: Generate unit H-shape capacitor
   - Phase 2: Generate dummy capacitor
   - Phase 3: Generate CDAC array
   - Suitable for complete design from scratch

3. **`capacitance_shape`** (automatic): Capacitance value and shape combination experiments
   - Phase 1: Generate unit capacitor (specified capacitance value and shape)
   - Phase 2: Generate dummy capacitor
   - Suitable for testing different combinations of capacitance values and shapes

## Common Parameters

All experiment types support the following parameters:

### Model and Prefix
- `--prefix`: Prefix (e.g., 'claude', 'gpt', 'deepseek')
- `--model-name`: Model name (e.g., 'claude', 'gpt-4o', 'deepseek')

### Experiment Range
- `--start-index`: Start from the Nth experiment (1-based)
- `--stop-index`: Run up to the Nth experiment (inclusive)
- `--start-from`: Start from specific sheet name (CDAC experiments only)
- `--stop-at`: Run up to specific sheet name (CDAC experiments only)

### Preview and Testing
- `--dry-run`: Preview mode, only list experiments to be run
- `--preview-prompt`: Preview generated prompt ('first', 'all', or specific sheet name)

### RAMIC Configuration
- `--ramic-port`: All experiments use the same port
- `--ramic-port-start`: Each experiment uses an incremental port (port_start + index)
- `--ramic-host`: RAMIC host address

### Others
- `--excel-file`: Excel file path (CDAC experiments only, default: excel/CDAC_3-8bit.xlsx)
- `--experiment-type`: Experiment type ('cdac' or 'capacitance_shape', default: 'cdac')
- `--template-type`: Template type ('array', 'full', 'capacitance_shape')

### Advanced Option Examples

```bash
# Specify Excel file
python run_batch_experiments.py --excel-file path/to/file.xlsx --prefix claude

# Start from specific sheet
python run_batch_experiments.py --prefix claude --start-from "Sheet3"

# Run up to specific sheet
python run_batch_experiments.py --prefix claude --stop-at "Sheet10"

# Preview all prompts
python run_batch_experiments.py --prefix claude --preview-prompt all

# Preview prompt for specific sheet
python run_batch_experiments.py --prefix claude --preview-prompt "Sheet3"
```

## Prompt Generation

Prompts are now defined in the `PROMPT_TEMPLATES` dictionary in `run_batch_experiments.py` and dynamically generated through the `generate_prompt_text()` function. Modifying templates in the dictionary updates prompts for all experiments.

### Prompt Template Location
- File: `run_batch_experiments.py`
- Location: `PROMPT_TEMPLATES` dictionary at the top of the file
- Function: `generate_prompt_text()`

### Preview Prompts

Before running experiments, you can preview generated prompts:

```bash
# Preview first prompt (as example)
python run_batch_experiments.py --prefix claude --preview-prompt first

# Preview all prompts
python run_batch_experiments.py --prefix claude --preview-prompt all

# Preview prompt for specific sheet
python run_batch_experiments.py --prefix claude --preview-prompt "Sheet3"
```

This is very useful for verifying that prompt templates are correct.

## Log Files

All experiment logs are saved in:
- CDAC experiments: `logs/batch_cdac_{prefix}_{template_type}/`
- Capacitance/Shape experiments: `logs/batch_capacitance_shape_{prefix}_capacitance_shape/`

Log file naming format: `{prompt_key}_{timestamp}.log`

## Running Recommendations

### Single Machine Run
```bash
# Run all experiments directly (sequential execution)
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --model-name claude
```

### Parallel Run (Recommended)

If you have multiple machines or can start multiple Virtuoso instances, you can run in parallel:

```bash
# Divide 95 experiments into 3 groups, approximately 32 each
# Terminal 1
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 1 --stop-index 32 --ramic-port-start 65432

# Terminal 2
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 33 --stop-index 64 --ramic-port-start 65433

# Terminal 3
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 65 --ramic-port-start 65434
```

## Notes

1. **Timeout Setting**: Each experiment runs for a maximum of 50 minutes, automatically terminates and continues to the next after timeout
2. **Auto Exit**: Script automatically sends "exit" command, no manual intervention needed
3. **Error Handling**: If an experiment fails, script automatically continues to the next experiment
4. **Parallel Run**: If running in parallel, ensure each instance uses a different RAMIC port
5. **Resource Usage**: Each experiment consumes some CPU and memory, monitor system resources
6. **Dynamic Prompt Generation**: No longer need to predefine prompts in YAML; all prompts are dynamically generated at runtime

## Time Estimates

### Capacitance/Shape Experiments (95 experiments)
- **Single Thread**: 95 experiments × 20 minutes ≈ 32 hours
- **3 Threads Parallel**: ≈ 11 hours
- **5 Threads Parallel**: ≈ 6.5 hours

### CDAC Experiments (20 sheets)
- **Single Thread**: 20 experiments × 40 minutes ≈ 13 hours
- **3 Threads Parallel**: ≈ 4.5 hours

## Resume Running

If experiments are interrupted, you can continue from a specified position:

```bash
# Continue from the 50th experiment
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 50

# CDAC experiments: Continue from specific sheet
python run_batch_experiments.py --prefix claude --start-from "6bit_1"
```

## Technical Details

### Prompt Passing Method
1. Dynamically generate prompt text
2. Write to temporary file `user_prompt.txt`
3. `multi_agent_main.py` automatically reads this file
4. Automatically clean up temporary file after experiment ends

### New CLI Parameters
- `--prompt-text`: Directly pass prompt text (available in `multi_agent_main.py`, but batch script uses file method which is more reliable)

## Advantages Summary

✅ **Clean Code**: Reduced from multiple duplicate scripts to 1 unified script  
✅ **Easy Maintenance**: Prompt templates use dictionary registry pattern, centralized management, easy to extend  
✅ **No YAML Needed**: No longer need to predefine large amounts of prompts in YAML  
✅ **Flexible Configuration**: Easily switch models, experiment types, and configurations via command line parameters  
✅ **Easy Extension**: Adding new templates only requires adding entries to `PROMPT_TEMPLATES` dictionary  
✅ **Unified Interface**: All experiment types use the same command line interface  
✅ **Backward Compatible**: Still supports using prompts from YAML via `--prompt` (for other scenarios)

## Deprecated Files

The following files have been integrated into `run_batch_experiments.py` and can be safely deleted:
- ✅ `run_batch_experiments_claude.py` - Deleted
- ✅ `run_batch_experiments_gpt.py` - Deleted
- ✅ `run_batch_experiments_deepseek.py` - Deleted
- ✅ `run_capacitance_shape_batch.py` - Deleted
- ✅ `generate_test_array_prompts.py` - Deleted
- ✅ `generate_test_array_deepseek_prompts.py` - Deleted
- ✅ `generate_capacitance_shape_prompts.py` - Deleted

All functionality is now managed through `run_batch_experiments.py`.
