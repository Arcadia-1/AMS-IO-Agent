# AMS-IO-Agent

An AI-powered integrated circuit (IC) design automation agent specialized for Cadence Virtuoso EDA environments. This system automates IO ring generation, CDAC (Capacitor Digital-to-Analog Converter) array design, and verification workflows using LLM-driven intelligent agents.

## Overview

AMS-IO-Agent leverages large language models to automate complex analog and mixed-signal IC design tasks. It combines domain knowledge bases, specialized tools, and multi-agent architectures to generate schematic and layout designs for IO rings and capacitor arrays while ensuring design rule compliance.

## Key Features

- **Automated IO Ring Generation** - Generate IO pad ring schematics and layouts automatically based on requirements
- **CDAC Capacitor Design** - Unit capacitor, dummy capacitor, and array assembly automation with multiple shape support
- **Verification Automation** - Integrated DRC, LVS, and PEX verification workflows
- **Multi-Model Support** - Compatible with Claude, GPT-4, DeepSeek, and other OpenAI-compatible APIs
- **Knowledge-Driven Design** - Structured knowledge bases for different capacitor shapes and technology nodes
- **Multi-Agent Architecture** - Master-worker system with specialized agents for complex tasks
- **Batch Experimentation** - Run large-scale experiments across configurations for benchmarking
- **Web UI** - Optional Gradio-based web interface for interactive use
- **Benchmark Suite** - Comprehensive test cases in AMS-IO-Bench for validation

## Quick Start

### Prerequisites

- Python 3.8 or higher
- `csh` (C Shell) - usually pre-installed on Linux/macOS
- Cadence Virtuoso (for actual design execution)
- API key for supported LLM providers (Claude, OpenAI, DeepSeek, etc.)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AMS-IO-Agent.git
   cd AMS-IO-Agent
   ```

2. **Run the quick setup script (Recommended):**
   
   **For Linux/macOS (csh):**
   ```csh
   ./quick_start.csh
   ```
   
   **For Windows (PowerShell - Recommended):**
   ```powershell
   .\quick_start.ps1
   ```
   
   **For Windows (CMD):**
   ```cmd
   quick_start.bat
   ```
   
   This one-command script will:
   - ✅ Automatically fix executable permissions (Linux/macOS)
   - ✅ Create Python virtual environment
   - ✅ Install all dependencies
   - ✅ Generate configuration files
   - ✅ Set up Virtuoso integration
   
   **Alternative - Manual Setup:**
   
   **Linux/macOS:**
   ```bash
   ./setup/setup.csh
   ```
   
   **Windows PowerShell:**
   ```powershell
   .\setup\setup_powershell.ps1
   ```
   
   **Windows CMD:**
   ```cmd
   setup\setup_cmd.bat
   ```
   
   **Troubleshooting:** If you encounter "Permission denied" error (Linux/macOS):
   ```csh
   chmod +x quick_start.csh setup/*.csh
   ./quick_start.csh
   ```

   The setup script will:
   - Create a Python virtual environment using `uv`
   - Install all dependencies from `requirements.txt`
   - Generate a `.env` configuration file template
   - Set up Virtuoso integration files

3. **Configure environment variables:**

   Copy `.env.example` to `.env` and add your API credentials:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your API keys:
   ```env
   # Choose your preferred LLM provider
   CLAUDE_API_BASE=https://api.anthropic.com/v1
   CLAUDE_MODEL_ID=claude-sonnet-4-20250514
   CLAUDE_API_KEY=your_api_key_here

   # Or use OpenAI
   GPT4_API_BASE=https://api.openai.com/v1
   GPT4_MODEL_ID=gpt-4-turbo
   GPT4_API_KEY=your_openai_key_here

   # Virtuoso bridge configuration (optional)
   RB_HOST=localhost
   RB_PORT=9123
   ```

4. **Configure the agent:**

   Edit `config.yaml` to set your preferences:
   ```yaml
   model:
     active: "claude"  # or "gpt4", "deepseek", etc.
     temperature: 1.0

   interface:
     mode: "cli"  # or "webui" for web interface
     logging: true
   ```

### Basic Usage

**Run the agent in CLI mode:**
```bash
python main.py
```

**Run with web interface:**
```bash
# Edit config.yaml and set interface.mode: "webui"
python main.py
```

**Auto-load a benchmark prompt:**
```bash
# Edit config.yaml:
# prompt:
#   key: "IO_28nm_3x3_single_ring_digital"
python main.py
```

## Project Structure

```
AMS-IO-Agent/
├── main.py                           # Main entry point for multi-agent system
├── config.yaml                       # Main configuration file (safe to commit)
├── .env                              # API keys and secrets (gitignored)
├── requirements.txt                  # Python dependencies
│
├── src/                              # Core source code
│   ├── app/
│   │   ├── cdac/                     # CDAC analysis module
│   │   ├── layout/                   # Layout generation components
│   │   ├── schematic/                # Schematic generation components
│   │   └── utils/                    # Utilities and agent factories
│   │
│   ├── tools/                        # AI agent tools
│   │   ├── il_runner_tool.py         # Execute SKILL files in Virtuoso
│   │   ├── drc_runner_tool.py        # Run DRC verification
│   │   ├── lvs_runner_tool.py        # Run LVS verification
│   │   ├── pex_runner_tool.py        # Run PEX extraction
│   │   ├── io_ring_generator_tool.py # Generate IO ring designs
│   │   ├── knowledge_loader_tool.py  # Dynamic knowledge base loading
│   │   └── skill_tools_manager.py    # Manage reusable SKILL tools
│   │
│   └── scripts/                      # Helper scripts and bridges
│       └── ramic_bridge/             # RAMIC bridge for Virtuoso communication
│
├── Knowledge_Base/                   # Structured design knowledge
│   ├── 00_META/                      # Knowledge base index and metadata
│   ├── 01_CORE/                      # Core design principles and workflows
│   ├── 02_TECHNOLOGY/                # Technology-specific parameters
│   ├── 03_DESIGN_BLOCKS/             # IO Ring and CDAC design knowledge
│   ├── 04_VERIFICATION/              # DRC, LVS, PEX knowledge
│   ├── 05_EXAMPLES/                  # Example code and templates
│   └── 06_ERRORS/                    # Common errors and solutions
│
├── AMS-IO-Bench/                     # Benchmark test suite
│   ├── 28nm_wirebonding/             # 28nm IO ring test cases
│   └── 180nm_wirebonding/            # 180nm IO ring test cases
│
├── CapArray-Bench/                   # CDAC capacitor array benchmarks
│
├── tests/                            # Unit and integration tests
│   ├── run_CDAC_batch.py             # Batch CDAC experiment runner
│   └── run_IO_Ring_batch.py          # Batch IO ring experiment runner
│
├── setup/                            # Installation and setup scripts
│   └── setup.csh                     # Main setup script
│
├── output/                           # Generated designs output
└── logs/                             # Execution logs
```

## Core Components

### Entry Point

- **`main.py`** - Multi-agent system entry point with master-worker architecture

### Agent Tools

| Tool | Purpose |
|------|---------|
| `il_runner_tool.py` | Execute SKILL files in Cadence Virtuoso |
| `drc_runner_tool.py` | Run Design Rule Check verification |
| `lvs_runner_tool.py` | Run Layout vs Schematic verification |
| `pex_runner_tool.py` | Run parasitic extraction |
| `io_ring_generator_tool.py` | Generate IO ring schematics and layouts |
| `knowledge_loader_tool.py` | Dynamically load knowledge from markdown files |
| `skill_tools_manager.py` | Manage and execute reusable SKILL utilities |
| `bridge_utils.py` | Virtuoso communication (RAMIC/skillbridge) |

### Layout Generation (`src/app/layout/`)

| Module | Purpose |
|--------|---------|
| `layout_generator.py` | Main layout generation orchestrator |
| `position_calculator.py` | Calculate pad positions for IO rings |
| `voltage_domain.py` | Handle voltage domain logic |
| `skill_generator.py` | Generate SKILL code for layouts |
| `auto_filler.py` | Automatic filler cell generation |

### Schematic Generation (`src/app/schematic/`)

| Module | Purpose |
|--------|---------|
| `schematic_generator.py` | Generate SKILL code for schematics |
| `json_validator.py` | Validate intent graph files |

## Workflows

### CDAC Three-Phase Workflow

The CDAC design follows a structured three-phase approach:

1. **Phase 1: Unit Capacitor Design**
   - Design unit H-shape/I-type capacitor structures
   - Iterative parameter synthesis to meet capacitance targets
   - DRC and PEX verification

2. **Phase 2: Dummy Capacitor Generation**
   - Generate dummy capacitors based on unit cell
   - Verify with DRC/PEX

3. **Phase 3: Array Generation**
   - Generate complete CDAC array from Excel specification
   - Full array verification

### IO Ring Generation Workflow

1. Generate JSON configuration from natural language requirements
2. Validate configuration against templates
3. Generate schematic SKILL code
4. Generate layout SKILL code
5. Execute in Virtuoso via bridge
6. Run DRC/LVS verification
7. Iterate if errors detected

## Knowledge Bases

The system uses a unified Knowledge_Base folder with specialized modules:

### 01_CORE - Core Design Knowledge
- Universal design principles
- Three-phase CDAC workflow
- Python-SKILL integration patterns

### 02_TECHNOLOGY - Technology-Specific Parameters
- 28nm process parameters
- 180nm process parameters
- Technology-specific design rules

### 03_DESIGN_BLOCKS - Design-Specific Knowledge
- **IO_RING**: IO pad selection, corner devices, voltage domains
- **CDAC**: Capacitor shapes (H-shape, I-type, Sandwich), array generation

### 04_VERIFICATION
- DRC, LVS, and PEX verification procedures
- Common verification errors and solutions

### 05_EXAMPLES
- Example SKILL code templates
- Reference implementations

### 06_ERRORS
- Common error documentation
- Error patterns and solutions learned during development

## Technologies

| Technology | Usage |
|------------|-------|
| **Python 3.x** | Main programming language |
| **smolagents** | AI agent framework from Hugging Face |
| **OpenAI-compatible APIs** | LLM backend (Claude, GPT-4, DeepSeek) |
| **Cadence Virtuoso** | Target EDA environment |
| **SKILL** | Virtuoso scripting language |
| **Gradio** | Optional web UI interface |

### Virtuoso Bridge Options

- **RAMIC Bridge** (Recommended) - Socket-based communication, supports cross-server connections
- **skillbridge** - Direct Python-Virtuoso integration via IPC

## Supported Models

The system supports any OpenAI-compatible API. Pre-configured models include:

- Claude Sonnet 4 (via Anthropic or proxies)
- GPT-4 / GPT-4o (via OpenAI or proxies)
- DeepSeek Chat v3 (via OpenRouter)
- Custom models (add to `.env`)

To add a new model, simply add three environment variables to `.env`:
```env
MYMODEL_API_BASE=https://api.provider.com/v1
MYMODEL_MODEL_ID=model-name
MYMODEL_API_KEY=your_key_here
```

Then use it in `config.yaml`:
```yaml
model:
  active: "mymodel"
```

## Batch Experiments

### CDAC Experiments

Run batch capacitor array experiments:

```bash
python tests/run_CDAC_batch.py
```

Features:
- Multiple capacitance values and shapes
- Parallel execution
- Timeout handling
- Automatic result logging

### IO Ring Experiments

Run batch IO ring experiments:

```bash
python tests/run_IO_Ring_batch.py
```

Features:
- Test cases from 3x3 to 18x18 pad configurations
- Single and double ring topologies
- Digital, analog, and mixed-signal designs
- Multi-voltage domain support

## Testing

Run individual tests from the project root:

```bash
# Quick flow test
python tests/test_quick_flow.py

# IO ring tool test
python tests/test_io_ring_tool.py

# Verification tests
python tests/test_drc_runner_tool.py
python tests/test_lvs_runner_tool.py
python tests/test_pex_runner_tool.py
```

## Configuration

### Main Configuration (`config.yaml`)

All non-sensitive configuration is in `config.yaml`:

```yaml
model:
  active: "claude"      # Model to use
  temperature: 1.0      # Creativity level (0.0-2.0)

interface:
  mode: "cli"           # "cli" or "webui"
  logging: true         # Save conversation logs
  show_code: false      # Show code execution details

prompt:
  key: null             # Auto-load benchmark (e.g., "IO_28nm_3x3_single_ring_digital")
  text: null            # Or provide direct prompt text
  config_path: "user_prompt"  # Directory for custom prompts

ramic_bridge:
  host: null            # RAMIC server host (null = use RB_HOST env var)
  port: null            # RAMIC server port (null = use RB_PORT env var)
```

### Environment Variables (`.env`)

All sensitive data and API keys go in `.env`:

```env
# Model API Keys
CLAUDE_API_KEY=your_key
GPT4_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Model Endpoints
CLAUDE_API_BASE=https://api.anthropic.com/v1
CLAUDE_MODEL_ID=claude-sonnet-4-20250514

# Virtuoso Bridge
RB_HOST=localhost
RB_PORT=9123

# User Profile
USER_PROFILE_PATH=user_data/default_user_profile.md
```

## Architecture

### Multi-Agent System

The system uses a master-worker architecture:

- **Master Agent**: Coordinates overall workflow, has access to standard tools
- **Worker Agents**: Specialized agents for specific tasks (e.g., CDAC analysis)

Benefits:
- Separation of concerns
- Specialized expertise for complex subtasks
- Parallel execution capabilities

### Tool Loading

Tools are configured via `src/tools/tools_config.yaml` and loaded dynamically based on the use case. This allows flexible tool composition for different agent types.

### Dynamic Knowledge Loading

Knowledge modules are loaded on-demand from markdown files in the knowledge bases, enabling:
- Efficient memory usage
- Targeted expertise injection
- Easy knowledge base updates without code changes

## Contributing

This project is under active development. Contributions are welcome in the following areas:

- Additional technology node support
- New capacitor shapes and structures
- Improved error handling and recovery
- Documentation and examples
- Test coverage

## Troubleshooting

### Common Issues

**API Connection Errors:**
- Verify API keys in `.env`
- Check API base URLs
- Ensure network connectivity

**Virtuoso Bridge Issues:**
- Verify RAMIC bridge is running
- Check `RB_HOST` and `RB_PORT` settings
- Test with `tests/test_il_runner_ramicbridge.py`

**Tool Loading Errors:**
- Check `src/tools/tools_config.yaml` syntax
- Verify all tool files exist
- Review logs in `logs/` directory

**Knowledge Base Not Loading:**
- Verify Knowledge_Base directory structure
- Check markdown file syntax
- Review knowledge loader tool logs

## License

Proprietary - All rights reserved.

## Acknowledgments

- Built with [smolagents](https://github.com/huggingface/smolagents) from Hugging Face
- Uses [skillbridge](https://github.com/unihd-cag/skillbridge) for Virtuoso integration
- Powered by large language models from Anthropic, OpenAI, and DeepSeek

## Contact

For questions, issues, or collaboration inquiries, please open an issue on GitHub.

---

**Note:** This tool is designed for research and development purposes in IC design automation. Always verify generated designs meet your specific requirements and design rules before fabrication.
