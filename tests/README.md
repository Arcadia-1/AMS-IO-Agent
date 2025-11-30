# Tests Directory

This directory contains comprehensive test files for the AMS-IO-Agent project, covering various components and functionalities.

## Test Files Overview

### Core Test Files

#### `test_quick_flow.py` (12KB, 321 lines)
**Quick workflow testing**
- **Purpose**: Fast testing of essential workflows
- **Coverage**: 
  - Basic IO ring generation
  - Simplified verification processes
  - Quick validation of core features
- **Usage**: 
  ```bash
  python tests/test_quick_flow.py
  ```
- **Command Line Arguments**:
  ```bash
  python tests/test_quick_flow.py --help                   # Show help information
  python tests/test_quick_flow.py -a                       # Run all found files
  python tests/test_quick_flow.py -i                       # Interactive selection of files to run
  python tests/test_quick_flow.py -n 1                     # Run file with specified number
  python tests/test_quick_flow.py -l                       # Only list found files, do not execute
  python tests/test_quick_flow.py -t                       # Only run the latest Python code file
  ```

#### `test_il_system.py` (12KB, 332 lines)
**IL (Interactive Layout) system testing**
- **Purpose**: Testing Virtuoso integration and SKILL script execution
- **Coverage**: 
  - SKILL script generation and execution
  - Virtuoso environment interaction
  - Layout file operations
- **Usage**: 
  ```bash
  python tests/test_il_system.py
  ```
- **Command Line Arguments**:
  ```bash
  python tests/test_il_system.py --help                    # Show help information
  python tests/test_il_system.py -l                        # List all IL files
  python tests/test_il_system.py -r                        # Run the latest IL file
  python tests/test_il_system.py -s                        # Run the latest IL file and save screenshot
  python tests/test_il_system.py -i                        # Interactive selection and run IL file
  python tests/test_il_system.py -a                        # Execute all steps (default behavior)
  python tests/test_il_system.py -q                        # Quiet mode
  python tests/test_il_system.py -c                        # Clear all components in the current window
  python tests/test_il_system.py -S                        # Take screenshot of current Virtuoso window only, without running IL file
  ```

### Component-Specific Test Files

#### `test_io_ring_tool.py` (2.0KB, 73 lines)
**IO ring generation tool testing**
- **Purpose**: Testing the IO ring generation functionality
- **Coverage**: 
  - Schematic generation
  - Layout generation
  - Configuration validation
- **Usage**: 
  ```bash
  python tests/test_io_ring_tool.py
  ```
- **Features**: Automatically tests all IO ring generation functionality, no command line arguments required

#### `test_drc_runner_tool.py` (2.7KB, 91 lines)
**DRC (Design Rule Check) tool testing**
- **Purpose**: Testing design rule checking functionality
- **Coverage**: 
  - DRC execution
  - Rule violation detection
  - Report generation
- **Usage**: 
  ```bash
  python tests/test_drc_runner_tool.py
  ```
- **Command Line Arguments**:
  ```bash
  python tests/test_drc_runner_tool.py --help              # Show help information
  python tests/test_drc_runner_tool.py -i                  # Show only current design information
  python tests/test_drc_runner_tool.py -r                  # Run DRC check
  python tests/test_drc_runner_tool.py -a                  # Show design information and run DRC check (default behavior)
  python tests/test_drc_runner_tool.py -q                  # Quiet mode, show only error messages
  ```

#### `test_lvs_runner_tool.py` (2.7KB, 90 lines)
**LVS (Layout vs Schematic) tool testing**
- **Purpose**: Testing layout vs schematic verification
- **Coverage**: 
  - LVS execution
  - Netlist comparison
  - Verification reporting
- **Usage**: 
  ```bash
  python tests/test_lvs_runner_tool.py
  ```
- **Command Line Arguments**:
  ```bash
  python tests/test_lvs_runner_tool.py --help              # Show help information
  python tests/test_lvs_runner_tool.py -i                  # Show only current design information
  python tests/test_lvs_runner_tool.py -r                  # Run LVS check
  python tests/test_lvs_runner_tool.py -a                  # Show design information and run LVS check (default behavior)
  python tests/test_lvs_runner_tool.py -q                  # Quiet mode, show only error messages
  ```

#### `test_example_search_tool.py` (5.9KB, 191 lines)
**Example search functionality testing**
- **Purpose**: Testing the example search and retrieval system
- **Coverage**: 
  - Code example search
  - Pattern matching
  - Example retrieval and formatting
- **Usage**: 
  ```bash
  python tests/test_example_search_tool.py
  ```
- **Command Line Arguments**:
  ```bash
  python tests/test_example_search_tool.py --help           # Show help information
  python tests/test_example_search_tool.py -k "layout"      # Specify search keyword for testing
  python tests/test_example_search_tool.py -t layout        # Run specified test case
  python tests/test_example_search_tool.py -a               # Run all tests (default behavior)
  python tests/test_example_search_tool.py -v               # Verbose output mode
  ```

### Utility Files

#### `image_rating.py` (11KB, 340 lines)
**IC Design I/O Ring Layout Image Rating Tool**
- **Purpose**: Uses GPT-4o multimodal interface to rate IC design I/O ring layout images
- **Features**: 
  - Evaluate ring formation correctness
  - Routing accuracy assessment
  - Provides detailed scoring (1-10 points)
- **Usage**: 
  ```bash
  python tests/image_rating.py single test2.png
  python tests/image_rating.py latest /path/to/images
  python tests/image_rating.py batch /path/to/images output_results.txt
  python tests/image_rating.py list /path/to/images
  ```

## Command Line Arguments Reference

### Common Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--help` | Show help information and available options | `--help` |
| `-q, --quiet` | Quiet mode, reduce output | `-q` |
| `-v, --verbose` | Verbose output mode | `-v` |

### Quick Flow Test Related Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-a, --all` | Run all found files | `-a` |
| `-i, --interactive` | Interactive selection of files to run | `-i` |
| `-n` | Run file with specified number | `-n 1` |
| `-l, --list` | Only list found files, do not execute | `-l` |
| `-t, --latest` | Only run the latest Python code file | `-t` |

### IL System Related Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-l, --list` | List all IL files | `-l` |
| `-r, --run` | Run the latest IL file | `-r` |
| `-s, --screenshot` | Run the latest IL file and save screenshot | `-s` |
| `-i, --interactive` | Interactive selection and run IL file | `-i` |
| `-a, --all` | Execute all steps (default behavior) | `-a` |
| `-c, --clear` | Clear all components in the current window | `-c` |
| `-S, --only-screenshot` | Take screenshot of current Virtuoso window only, without running IL file | `-S` |

### DRC/LVS Related Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-i, --info` | Show only current design information | `-i` |
| `-r, --run` | Run check | `-r` |
| `-a, --all` | Show design information and run check (default behavior) | `-a` |

### Search Related Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-k, --keyword` | Specify search keyword for testing | `-k "layout"` |
| `-t, --test` | Run specified test case | `-t layout` |
| `-a, --all` | Run all tests (default behavior) | `-a` |

## Running Tests

### Prerequisites
1. Ensure all dependencies are installed
2. Configure environment variables (API keys, etc.)
3. Set up Virtuoso environment (for IL-related tests)

### Running All Tests
```bash
# Run all test files sequentially
python tests/test_io_ring_tool.py
python tests/test_drc_runner_tool.py
python tests/test_lvs_runner_tool.py
python tests/test_pex_runner_tool.py
python tests/test_example_search_tool.py
python tests/test_il_system.py
python tests/test_quick_flow.py
```

**Note**: For batch IO ring experiments, use `run_io_ring_batch.py` instead of the deprecated `test_automation.py`.

### Running Specific Test Categories

#### Quick Tests (Recommended for development)
```bash
python tests/test_quick_flow.py -t
```

#### Full Automation Tests (Comprehensive)
```bash
# Use run_io_ring_batch.py for batch IO ring experiments
python run_io_ring_batch.py --model-name deepseek
```

#### Component Tests
```bash
# IO ring generation
python tests/test_io_ring_tool.py

# DRC checking
python tests/test_drc_runner_tool.py -a

# LVS verification
python tests/test_lvs_runner_tool.py -a

# Example search
python tests/test_example_search_tool.py -k "DRC"

# IL system
python tests/test_il_system.py -s
```

### Common Command Line Patterns

#### Interactive Mode
```bash
# Interactive file selection
python tests/test_quick_flow.py -i

# Interactive IL file selection
python tests/test_il_system.py -i
```

#### List Options
```bash
# List all pad layout configurations (use run_io_ring_batch.py)
python run_io_ring_batch.py --list-layouts

# List all files
python tests/test_quick_flow.py -l
```

#### Batch Testing
```bash
# Run batch IO ring experiments (use run_io_ring_batch.py)
python run_io_ring_batch.py --model-name deepseek

# Run tests for specified range
python run_io_ring_batch.py --start-index 1 --stop-index 5 --model-name deepseek
```

## Test Configuration

### Environment Setup
Tests may require specific environment variables:
```bash
export DEEPSEEK_API_KEY="your_api_key"
export WANDOU_API_KEY="your_api_key"
```

### Test Data
Test files use sample configurations and data located in:
- `output/example/intent_graph.json` - Sample intent graph
- `output/` - Test data files in output directory

## Test Output

### Logs
Test execution logs are saved in:
- `logs/test_YYYYMMDD_HHMMSS.log` - Test execution logs
- `output/` - Test output files

### Reports
- Test results are displayed in console output
- Detailed logs saved to timestamped files

## Troubleshooting

### Common Issues

1. **Virtuoso Connection Failed**
   - Ensure Virtuoso is running
   - Check skillbridge configuration
   - Verify network connectivity

2. **API Key Issues**
   - Verify API key is set in environment
   - Check API key validity
   - Ensure sufficient API quota

3. **Test Timeout**
   - Increase timeout values for slow operations
   - Check system resources
   - Verify network connectivity

### Debug Mode
Run tests with detailed output:
```bash
python tests/test_quick_flow.py --help
python run_io_ring_batch.py --help
```

## Contributing

When adding new tests:
1. Follow the existing naming convention
2. Include comprehensive docstrings
3. Add appropriate error handling
4. Update this README with new test information

## Test Maintenance

- Regular test execution: Weekly
- Coverage monitoring: Continuous
- Test data updates: As needed
- Environment validation: Before major releases 