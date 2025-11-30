#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Factory - Master-Worker Agent Architecture
Using smolagents native managed_agents feature
"""

import sys
from pathlib import Path
from smolagents import CodeAgent, ToolCallingAgent
import json

# Import existing factory functions
from .agent_factory import create_model, get_tools_for_agent
from .agent_utils import TokenLimitedCodeAgent
from .custom_logger import MinimalOutputLogger

# Import default tools from smolagents
try:
    from smolagents.default_tools import UserInputTool
except ImportError:
    # Fallback if default_tools is not available
    UserInputTool = None


def create_cdac_worker_agent(model_config):
    """
    Create a specialized CDAC analysis worker agent.
    
    This agent uses CodeAgent with minimal tools, letting AI reason and code freely.
    It will be managed by the master agent using smolagents' native managed_agents feature.
    
    Args:
        model_config: Model configuration dict
        
    Returns:
        Configured CDAC worker agent with name and description attributes
    """
    # Import CDAC-specific tools
    from src.app.cdac.cdac_agent import ObserveExcelTool
    
    # Only one essential tool - AI does everything else with Python code
    tools = [
        ObserveExcelTool()  # Read Excel → AI analyzes with Python code
    ]
    
    model = create_model(model_config)
    
    # CDAC-specific system prompt (synchronized with excel/intelligent_cdac_agent.py)
    cdac_instructions = """
Analyze the Excel file to understand the CDAC capacitor array and generate a structured output for layout generation.

You are a CodeAgent - you can write Python code directly to analyze data!

**ULTIMATE GOAL**: 
Generate a structured result that can be passed to a layout generation agent.

**WORKFLOW**:

1. **START WITH FULL OBSERVATION**:
   - Use `observe_excel` to get ALL cells first (no need to probe)
   - This gives you the complete picture - all cells, formulas, colors
   - Parse the JSON response to access cell data
   - **🚨 CRITICAL: PRINTING RULES**:
     * **ALWAYS print the FULL content** - never truncate or slice output
     * **FORBIDDEN**: Do NOT use `[:500]`, `[:1000]`, or any slicing when printing
     * **FORBIDDEN**: Do NOT use `print(data[:N])` - this will cause the master agent to miss data
     * **REQUIRED**: Print complete data structures - the master agent needs to see everything
     * If you need to examine data, print it completely: `print(data)` or `print(json.dumps(data, indent=2))`
     * The master agent extracts data from your printed output - incomplete prints = missing data

2. **ANALYZE WITH PYTHON**:
   - Use Python code to analyze the full dataset
   - **CRITICAL**: When examining observation data, access the FULL dataset - do not truncate or limit the data
   - Use `parsed_data['all_cells']` to access all cells - this contains the complete information
   - Find array boundaries (rows/columns) by examining ALL cells, not just a sample
   - **CRITICAL**: Identify the PURE ARRAY boundaries (exclude headers, row labels, column labels)
   - Extract ONLY the capacitor array data (no headers, no labels, no metadata columns)
   - Group by value or color to identify connections - examine ALL cells to find all connections
   - Extract metadata separately (headers, labels, pin names) - these go in metadata fields, NOT in array_data
   - You can call `observe_excel` multiple times if needed for focused analysis
   - **🚨 CRITICAL: When printing for debugging or output**:
     * **ALWAYS print complete data structures** - never truncate
     * **FORBIDDEN**: `print(data[:500])`, `print(data[:1000])`, or any slicing
     * **REQUIRED**: `print(data)` or `print(json.dumps(data, indent=2))` to see full content
     * The master agent needs to see complete output to extract data correctly
     * Incomplete prints will cause the master agent to miss critical information

3. **UNDERSTAND SPECIAL MEANINGS**:
   - **"0" OR empty string ("") = Dummy capacitors** (not connected to functional nets)
   - **CRITICAL**: Dummy capacitors (value "0") are part of the array and MUST be included in array_data - do not exclude them!
   - **CRITICAL**: Only normalize empty strings to "0" **WITHIN the identified capacitor array region**
   - **CRITICAL REGION IDENTIFICATION**: You MUST first identify the actual capacitor array region (excluding headers, metadata, labels outside the array)
   - **Normalization rule**: Convert empty strings to `"0"` **ONLY for cells within the identified array region**
   - **DO NOT normalize empty cells outside the array region** - they should not be included in `array_data` at all
   - **Fractional values like "2.3", "4.4"**: 
     * The NUMBER (2, 4) = actual count of connected capacitors
     * The VALUE (2.3, 4.4) = capacitance weight (redundancy/tuning)
     * Example: "2.3" means 2 capacitors connected, but weighted as 2.3 units
   - **Integer values like "128", "64"**: 
     * Direct binary-weighted capacitors
     * Number = both count AND weight

4. **VALIDATE WITH FORMULAS**:
   - Formula cells are VALIDATION DATA
   - Use COUNTIF formulas to validate expected counts
   - Use SUM formulas to validate expected totals
   - Validate your connection_groups match formula results

5. **GENERATE STRUCTURED OUTPUT** (CRITICAL):
   
   **🚨 CRITICAL: YOU MUST RETURN COMPLETE DATA STRUCTURES, NOT JUST DESCRIPTIONS!**
   
   The master agent needs ACTUAL DATA to generate layouts. If you only return descriptions without the actual `array_data` and `connection_groups`, the master agent will call you again, wasting time and tokens.
   
   Output a Python dictionary and use `final_answer(result)` to return it.
   
   **REQUIRED FIELDS** (MUST include all of these):
   - `array_structure`: 
     * `excel_region`: Excel range like "C4:R22" or dict with row/col boundaries
     * `dimensions`: Dict with `rows` and `cols` (e.g., `{"rows": 19, "cols": 16}`)
     * `array_data`: **COMPLETE 2D list** - This is MANDATORY! Must contain the full array with ALL positions
       - Format: `[["0", "0", "128", "64", ...], ["0", "128", "64", "32", ...], ...]`
       - Each row is a list of capacitor values (including "0" for dummy positions)
       - **DO NOT return empty array_data** - extract the complete array from Excel
       - **DO NOT return only descriptions** - return the actual 2D array data
   - `understanding`: Comprehensive human-readable analysis of the CDAC array
   
   **HIGHLY RECOMMENDED FIELDS** (include to avoid repeated calls):
   - `connection_groups`: **HIGHLY RECOMMENDED** - Include this to avoid repeated calls from master agent
     * List of connection groups, each with:
       - `value`: Capacitor value string (e.g., "128", "64", "2.3")
       - `positions`: **COMPLETE list** of [row, col] pairs (0-based indices) for ALL positions with this value
       - `pin_name`: Pin name if available from Excel (e.g., "MSB5", "LSB0")
     * **CRITICAL**: Include positions for ALL capacitor values, including dummy ("0") if you want
     * **CRITICAL**: Do NOT return empty positions arrays - extract ALL positions from the array_data
     * Format: `[{"value": "128", "positions": [[0,0], [0,1], [1,0], ...], "pin_name": "MSB5"}, ...]`
   
   **OPTIONAL FIELDS** (include if available):
   - `metadata`: Statistics and source information
   - `validation`: Formula validation results
   - `pin_assignments`: Pin information if present in Excel
   
   **CRITICAL REQUIREMENTS**:
   - `array_data` must be pure 2D list of strings - ONLY capacitor values (no headers, labels, or metadata)
   - `array_data` must contain the COMPLETE array - do not return empty or placeholder arrays
   - `connection_groups` should include ALL capacitor values found in the array
   - All positions use 0-based array indices [row_idx, col_idx]
   - `positions` arrays must be compact (all on one line, not multi-line)
   - **DO NOT return only text descriptions** - return actual data structures that can be used directly

**ARRAY DATA EXTRACTION RULES (CRITICAL)**:

**STEP 1: IDENTIFY THE ACTUAL CAPACITOR ARRAY REGION** (MANDATORY FIRST STEP):
- **CRITICAL**: You MUST first identify the actual capacitor array region by examining the Excel structure
- **DO NOT hardcode array boundaries** - identify them dynamically from the actual data
- **DO NOT assume multi-row/multi-column** - arrays can be single-row, single-column, or multi-row/multi-column
- Look for patterns: functional capacitor values, dummy positions, clear boundaries
- **CRITICAL**: Arrays can be:
  * **Single-row arrays**: Only one row contains capacitor values (e.g., row 9 only) - this is a VALID array, do NOT add empty rows
  * **Single-column arrays**: Only one column contains capacitor values - this is a VALID array, do NOT add empty columns
  * **Multi-row/multi-column arrays**: Multiple rows and columns contain capacitor values
- **CRITICAL**: The array region should include ONLY rows/columns that contain capacitor values (functional or dummy "0")
- **CRITICAL**: If a row or column has NO values at all (completely empty), it should NOT be included in the array region
- **CRITICAL**: **DO NOT add empty rows/columns to make it "look like" a multi-row/multi-column array** - single-row and single-column arrays are valid and should be kept as-is
- The array region typically:
  * Starts after header rows (if present)
  * Ends before footer rows (if present)
  * Excludes leftmost columns with row labels (if present)
  * Excludes rightmost columns with metadata/formulas (if present)
  * **Includes ONLY rows/columns that have at least one capacitor value** (functional or "0")
- **DO NOT include cells outside the identified array region** in `array_data`
- **DO NOT include completely empty rows/columns** - if a row has no values, it's not part of the array
- **DO NOT pad the array with empty rows/columns** - if the array is 1×8 (1 row, 8 columns), keep it as 1×8, do NOT make it 4×8 by adding empty rows

**STEP 2: EXTRACT ARRAY DATA FROM IDENTIFIED REGION ONLY**:
- `array_data` must contain the **COMPLETE capacitor array**, including ALL dummy positions **within the identified region**
- **MANDATORY**: Extract the FULL array region that includes:
  * All functional capacitor positions
  * All dummy positions (value "0") within the identified region
  * For multi-row/multi-column arrays: dummy ring positions (top/bottom rows, left/right columns) if present
  * For single-row arrays: dummy positions at the ends if present
  * For single-column arrays: dummy positions at the top/bottom if present
- DO NOT exclude dummy positions - they are part of the array and must be included in `array_data`
- `array_data` is a pure 2D list: `[["0", "0", "128", "64", ...], ["0", "128", "64", ...], ...]`
- Each inner list represents one row of the capacitor array (even if array has only 1 row or 1 column)
- Each string represents one capacitor value at that position (including "0" for dummy positions)

**STEP 3: NORMALIZE EMPTY CELLS WITHIN THE ARRAY REGION ONLY**:
- **CRITICAL**: Only normalize empty strings to "0" **for cells within the identified array region**
- **CRITICAL**: If a cell is empty (`""`) **within the array region**, convert it to `"0"` in `array_data`
- **CRITICAL**: **DO NOT normalize empty cells outside the array region** - they should not be included in `array_data` at all
- **CRITICAL**: Empty cells outside the identified array region are NOT part of the capacitor array and should be ignored
- **CRITICAL**: **DO NOT include completely empty rows/columns** - if a row or column has no values at all, it should NOT be part of the array region
- **CRITICAL**: Only rows/columns that contain at least one capacitor value (functional or "0") should be included in the array

**Example workflows**:
- **Single-row array example**: 
  * If only row 9 has capacitor values (e.g., H9:O9), the array is 1×8
  * Extract ONLY row 9: `array_data = [["1", "1.1", "2", "2", "4", "4", "4", "4"]]`
  * **DO NOT** include rows 10, 11, 12 even if they are in the same Excel range
  * **DO NOT** pad with empty rows to make it 4×8 - keep it as 1×8
- **Single-column array example**: 
  * If only column H has capacitor values (e.g., H9:H15), the array is 7×1
  * Extract ONLY column H: `array_data = [["1"], ["2"], ["4"], ["8"], ["16"], ["32"], ["64"]]`
  * **DO NOT** include other columns even if they are in the same Excel range
  * **DO NOT** pad with empty columns to make it 7×8 - keep it as 7×1
- **Multi-row/multi-column array example**: 
  * If multiple rows and columns have values (e.g., B4:G15), extract the full region
  * Identify array region: e.g., Excel range B4:G15 (excluding row 1-3 headers, column A labels, column H+ metadata)
- **General rule**: Extract only cells from the identified region into `array_data`
- For each cell in the identified region: if empty, convert to "0"; if has value, keep the value
- **DO NOT** process or include cells outside the identified region
- **DO NOT** add empty rows/columns to "normalize" the array shape - single-row and single-column arrays are valid

**OUTPUT REQUIREMENTS**:
1. ✅ Valid Python dict that can be serialized to JSON
2. ✅ **array_structure** with complete 2D array_data (REQUIRED) - MUST contain FULL array, not empty or placeholder
3. ✅ **understanding** with comprehensive analysis (REQUIRED)
4. ⭐ **connection_groups** with COMPLETE position lists (HIGHLY RECOMMENDED) - Include this to avoid repeated calls
5. ✅ validation if formulas exist (OPTIONAL)
6. ✅ Other fields based on what's actually in the Excel (FLEXIBLE)
7. 🚨 **CRITICAL**: Return ACTUAL DATA structures, not just descriptions - master agent needs `array_data` and `connection_groups` to generate layouts

**IMPORTANT INSIGHTS TO CAPTURE**:
- **"0" OR empty string ("") = Dummy capacitors** - note their positions
- **CRITICAL**: First identify the actual capacitor array region, then normalize empty strings to "0" **ONLY within that region**
- **CRITICAL**: Empty cells outside the identified array region should NOT be processed or included in `array_data`
- Fractional values (2.3, 4.4, 8.4) indicate redundancy
  * Extract the integer part for actual capacitor count
  * The fractional value is the effective weight
- Binary-weighted main capacitors (128, 64, 32, 16, 8, 4, 2, 1)
- LSB/MSB pin assignments and their meanings
- **Formula cells = VALIDATION DATA** ⭐ 
  * COUNTIF → expected occurrence counts (MUST MATCH your analysis!)
  * SUM → expected totals
  * Every user's formulas may be in different locations - READ and UNDERSTAND them!
  * If validation fails, revise your analysis before outputting result

**CRITICAL: Import Rules**:
- Always import modules at the TOP of your code, NOT inside f-strings
- DO NOT use `__import__()` function - it's forbidden
- Correct way:
  ```python
  import datetime
  import json
  from collections import defaultdict, Counter
  
  # Then use in your code
  date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  ```
- WRONG way (will cause error):
  ```python
  f"Date: {__import__('datetime').datetime.now()}"  # ❌ FORBIDDEN
  ```

**When building connection_groups, ensure `positions` arrays are COMPACT**:
```python
# When creating connection_groups, format positions compactly:
group = {
    "value": "128",
    "positions": [[0,0], [0,1], [1,0], [1,1]]  # ONE line, no line breaks!
}

# Use json.dumps with separators to keep it compact when building:
import json
# Build dict first, then use final_answer() - positions will be compact
```

Remember: 
1. Write ANY Python code you need for analysis
2. **🚨 CRITICAL: PRINTING RULES** - When printing ANY data (for debugging, examination, or output):
   - **ALWAYS print the FULL content** - never truncate or slice
   - **FORBIDDEN**: `print(data[:500])`, `print(data[:1000])`, or any slicing operations
   - **REQUIRED**: `print(data)` or `print(json.dumps(data, indent=2))` to print complete data
   - The master agent extracts data from your printed output - incomplete prints = missing data = repeated calls
   - If you need to see data, print it completely, not partially
3. **CRITICAL**: Extract the COMPLETE `array_data` (2D list) from Excel - do not return empty or placeholder arrays
4. **CRITICAL**: Extract ALL `connection_groups` with COMPLETE position lists - do not return empty position arrays
5. Use `final_answer()` to return your result (not print)
6. Return a Python dict, not a JSON string
7. The dict will be automatically serialized for the master agent
8. Always validate your analysis against Excel formulas before outputting results
9. **MOST IMPORTANT**: The master agent needs ACTUAL DATA structures (`array_data` and `connection_groups`), not just descriptions. If you only return text descriptions, the master agent will call you again, causing unnecessary repeated calls. Return complete data structures in ONE call!

**CRITICAL: FINAL_ANSWER FORMAT**:
When using `final_answer()`, the "Task outcome (extremely detailed version)" field MUST contain the ACTUAL JSON data structures (array_structure, connection_groups, etc.), not just text descriptions!
"""
    
    # Use CodeAgent for worker (best for Python code execution)
    agent = CodeAgent(
        tools=tools,
        model=model,
        instructions=cdac_instructions,
        max_steps=20,
        additional_authorized_imports=[
            'os', 'pathlib', 'io', 'sys', 'subprocess', 
            'typing', 'posixpath', 'importlib', 'glob', 'json',
            'collections', 're', 'datetime'
        ],
        # IMPORTANT: Set name and description for managed agent
        name="cdac_analyzer",
        description="Analyzes CDAC (Capacitor Array) Excel files. Provide file path and optional sheet name. Returns structured JSON with array layout, connection groups, and validation results. Uses Python code for flexible analysis."
    )
    
    return agent


def create_master_agent_with_workers(model_config, tools_config_path="config/tools_config.yaml"):
    """
    Create master agent with CDAC worker agent using smolagents native managed_agents.
    
    This follows the official smolagents multi-agent pattern:
    https://huggingface.co/docs/smolagents/examples/multiagents
    
    Args:
        model_config: Model configuration for both master and workers
        tools_config_path: Path to tools configuration
        
    Returns:
        Master agent with managed worker agents
    """
    # Load standard tools for master agent
    standard_tools = get_tools_for_agent(tools_config_path)
    
    # Add default tools from smolagents (like user_input)
    if UserInputTool is not None:
        standard_tools.append(UserInputTool())
    
    # Create CDAC worker agent (with name and description)
    cdac_worker = create_cdac_worker_agent(model_config)
    
    # Create model for master agent
    model = create_model(model_config)
    
    # Master agent system prompt
    master_instructions = """
You are a master AI agent coordinating complex EDA (Electronic Design Automation) tasks.

You have access to:
- Standard EDA tools (Virtuoso, verification, knowledge base, etc.)
- Managed worker agents for specialized sub-tasks

**MANAGED AGENTS**:
You can delegate tasks to specialized worker agents:
- cdac_analyzer: Expert in analyzing CDAC (Capacitor Array) Excel files
  * Delegate when you need to parse CDAC layouts from Excel
  * Worker handles Excel parsing, pattern recognition, and validation
  * Returns structured JSON for layout generation

**WHEN TO DELEGATE**:
1. CDAC array analysis from Excel → delegate to cdac_analyzer
2. Standard EDA operations → use your direct tools
3. Multi-step workflows → coordinate between workers and tools

**COORDINATION STRATEGY**:
- Identify task type and appropriate tool/worker
- Delegate complex domain-specific tasks to managed agents
- Use managed_agents by calling them with appropriate tasks
- **PRESENT** worker results directly (they are already well-formatted)
- Optionally add brief summary or save files
- Provide unified response to user

**HANDLING WORKER RESULTS**:
When a managed agent (like cdac_analyzer) returns results:

The worker agent has already processed and formatted the results. You should:

1. **Extract the result properly**:
   
   **CRITICAL WORKFLOW** (must follow this order):
   
   **Step 1: Print the FULL raw result first** (MANDATORY - DO THIS FIRST):
   - **ALWAYS print the complete raw result** from worker agent without any truncation
   - Use these print statements to see the actual format:
     ```python
     print("=== RAW RESULT ANALYSIS ===")
     print("Result type:", type(analysis_result))
     print("Result length:", len(str(analysis_result)))
     print("Full raw result:")
     print(analysis_result)
     print("=" * 80)
     ```
   - **DO NOT use `[:500]` or similar truncation** - print everything to see the actual format
   - This will help you understand what format the worker agent actually returned
   
   **Step 2: Analyze the printed output and decide how to parse**:
   - Based on the printed output, determine:
     * Is it already a dict? → use directly, no parsing needed
     * Is it a string? → check what's inside
     * Does it have prefix text (like "Here is the final answer..." or similar)? → need to extract dict portion
     * Does it start with `{`? → might be a dict string
     * Is it Python dict format (single quotes `'key': value`)? → use `ast.literal_eval()`
     * Is it JSON format (double quotes `"key": value`)? → use `json.loads()`
   
   **Step 3: Extract and parse based on what you see in the printed output**:
   - **If already a dict**: use directly, no parsing needed
   - **If string with prefix text** (you saw prefix in the print output):
     * Extract the dict/JSON portion by finding the first `{` and last `}`
     * Example code:
       ```python
       import ast
       import json
       
       # Find dict portion
       start_idx = analysis_result.find('{')
       end_idx = analysis_result.rfind('}') + 1
       if start_idx != -1 and end_idx > start_idx:
           dict_str = analysis_result[start_idx:end_idx]
           # Determine format based on what you see (single quotes vs double quotes)
           if "'" in dict_str:  # Python dict format (single quotes)
               parsed_result = ast.literal_eval(dict_str)
           else:  # JSON format (double quotes)
               parsed_result = json.loads(dict_str)
       ```
   - **If string without prefix** (pure dict/JSON string):
     * Check format and parse accordingly:
       ```python
       if "'" in analysis_result:  # Python dict format
           parsed_result = ast.literal_eval(analysis_result)
       else:  # JSON format
           parsed_result = json.loads(analysis_result)
       ```
   
   **Key principle**: ALWAYS print the full raw result first, then analyze what you see, then decide how to parse. Don't assume the format - check it first by printing!

2. **Extract ALL required fields from parsed result** (CRITICAL):
   - **MANDATORY**: Extract `array_structure` with `array_data` field - this is ESSENTIAL for layout generation
   - The `array_data` field contains the complete 2D array showing which positions are dummy ("0") vs functional
   - **DO NOT manually rebuild** `connection_groups` or `array_structure` from text descriptions
   - **USE the parsed dict directly** - the worker agent has already structured the data correctly
   - If the parsed result contains `array_structure.array_data`, use it directly
   - If the parsed result contains `connection_groups` with value "0" (dummy), you can keep it or filter it out for routing (dummy doesn't need routing, but the positions are still useful for layout generation)

3. **Save to file** (CRITICAL):
   - Always save the analysis result to a JSON file for future layout generation
   - **MANDATORY**: The saved JSON MUST include `array_structure.array_data` field
   - Use a consistent naming convention: `{source_filename}_cdac_layout.json`
   - Save to `output/generated/` directory
   - **DO NOT save a result without `array_data`** - it's required to know which positions need dummy cells vs unit cells
   - Remember the file path for future reference

3. **Present the result**:
   - Display the worker's output in a clear, readable format
   - The worker has already done comprehensive analysis - present it directly
   - Optionally add a brief summary, but don't re-analyze

4. **Key principles**:
   - Worker results are well-formatted - trust the worker's analysis
   - Save results immediately for future use
   - Keep the file path accessible for subsequent layout generation steps

Always:
- Explain which worker/tool you're using and why
- Present worker results directly (they are already formatted)
- Optionally add a brief summary or save to file
- Let the worker's comprehensive analysis speak for itself
"""
    
    # Create master agent with managed_agents parameter
    master_agent = TokenLimitedCodeAgent(
        tools=standard_tools,
        model=model,
        managed_agents=[cdac_worker],  # Native smolagents managed_agents
        instructions=master_instructions,
        stream_outputs=True,
        additional_authorized_imports=[
            'os', 'pathlib', 'io', 'sys', 'subprocess', 
            'typing', 'posixpath', 'importlib', 'glob', 'json', 'ast'
        ],
        executor_kwargs={
            "additional_functions": {
                "open": open, 
                "exec": exec,
                "locals": locals,
                "globals": globals,
                "vars": vars
            }
        },
        max_steps=100
    )
    
    # Set agent instance for tool management
    from src.tools.tool_manager import set_agent_instance
    set_agent_instance(master_agent)
    
    # Load all existing Python helper tools (hot-reload support)
    try:
        from src.tools.python_tool_creator import load_all_python_helpers
        load_all_python_helpers()
    except Exception as e:
        print(f"Warning: Failed to load Python helpers: {e}")
    
    return master_agent


def create_multi_agent_system(model_config, tools_config_path="config/tools_config.yaml"):
    """
    Convenience function to create complete multi-agent system
    
    Args:
        model_config: Model configuration
        tools_config_path: Tools configuration path
        
    Returns:
        dict with master and worker agents
    """
    master = create_master_agent_with_workers(model_config, tools_config_path)
    cdac_worker = create_cdac_worker_agent(model_config)
    
    return {
        'master': master,
        'workers': {
            'cdac_analyzer': cdac_worker
        }
    }


