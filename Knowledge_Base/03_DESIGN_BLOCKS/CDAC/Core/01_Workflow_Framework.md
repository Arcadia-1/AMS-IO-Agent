# Capacitor Design Workflow Framework - Three-phase automation (Unit → Dummy → Array, universal)

## Overview

This document defines the generic three-phase workflow framework that applies to all capacitor design automation. The framework is shape-agnostic and technology-agnostic; specific implementations reference technology configurations and shape-specific structure definitions.

---

## Workflow Overview

The complete capacitor design workflow consists of three sequential phases:

**Phase 1: Unit Capacitor Iterative Design** — Steps 0-6  
**Phase 2: Dummy Capacitor Generation** — After Phase 1 completion  
**Phase 3: Capacitor Array Generation** — After Phase 2 DRC pass 

---

## Requirements (Apply to All Phases)

### Knowledge Loading Policy

Execution order when starting a new phase (each step must be in a separate code execution block):

1. **Step 1 (Load only)**: Load phase-specific knowledge modules
   - Print the full content of loaded modules
   - Stop here - do not execute tasks, do not generate code

2. **Step 2 (Understand only)**: Review and understand the loaded knowledge
   - Stop here - do not execute tasks, do not generate code

3. **Step 3 (Execute)**: Execute the phase tasks using the loaded and understood knowledge
   - Generate code, create files, or perform actions based on the loaded knowledge
   - Reference the loaded knowledge modules when making decisions

**Loading rules:**
- Load Phase 1 modules when starting Phase 1
- Load Phase 2 modules only when starting Phase 2
- Load Phase 3 modules only when starting Phase 3
- Do not load future phase modules early

### Report Handling Policy

For all DRC/PEX operations:
- After calling `run_drc()` or `run_pex()`, print the complete returned report content in full
- Print the entire report text verbatim
- AI interprets reports directly from the complete printed content

### Automatic Continuation Policy

- Execute all rounds/phases automatically in sequence without pausing
- Only stop for truly blocking information (technology node, target capacitance if completely missing)
- Do not call `final_answer()` during phase transitions
- Only call `final_answer()` at the very end of the complete workflow (after Phase 3)

### Library/Cell Naming Policy

**Automatic inference (do not ask unless truly blocking):**
- **Library name**: Extract from user input or use default (e.g., "LLM_Layout_Design")
- **Cell names**: Auto-generate based on capacitance and phase:
  - Phase 1: `C_MAIN_{capacitance}` (e.g., `C_MAIN_6fF`)
  - Phase 2: `C_DUMMY_{capacitance}` (e.g., `C_DUMMY_6fF`)
  - Phase 3: `C_CDAC_{capacitance}` (e.g., `C_CDAC_6fF`)

**Only ask for (if completely missing):**
- Technology node (e.g., "28nm", "40nm")
- Target capacitance value (e.g., "6 fF")
- Shape type (if ambiguous and cannot be inferred from context)

### View Naming Convention

- **Iteration views**: Save each round to `layout1`, `layout2`, `layout3`, `layout4`, `layout5` of the same cell
- **Final view (required)**: After selecting best round, generate SKILL script and execute it to create canonical `layout` view
  - This is not optional - Phase 2 and Phase 3 will fail if `layout` view doesn't exist
  - Steps: Generate SKILL script with best parameters → Execute SKILL to `layout` view → Verify `layout` view exists
  - Do not skip this step - downstream phases depend on the `layout` view being available and correct
- **Downstream use**: Phase 2 and Phase 3 consume the best result from `layout` view
- **View type**: Any view name starting with "layout" is treated as `maskLayout`

---

## Phase 1: Unit Capacitor Iterative Design

### Step 0: Environment initialization
- Create a timestamped output directory
- Initialize logging and reporting structures

### Step 1: Requirement analysis
- Load Phase 1-specific knowledge modules (structure definition, technology config)
- Collect target capacitance, size limits, available metal layers, precision (default 1%), structure type
- Determine iteration count (default 5) and precision (default 1%)
- Consult technology and shape modules for:
  - Height limits → dimensional bounds per shape structure
  - Allowed metal set and adjacency rules
  - DRC baselines (minimum spacing/width)
  - Low-parasitic requirements
  - Shield layer decision (infer from user intent, default to include shield)
- Synthesize initial parameter set (minimal viable geometry satisfying DRC minima)
- Save as Round 1 candidate

### Step 2: Generate SKILL script
- Use Python `compute_geometry()` function to compute all geometry from parameters
- Use Python `render_skill()` function to generate flattened SKILL script
- **Round 1**: Define `compute_geometry()` and `render_skill()` functions
- **Rounds 2-5**: Reuse the same functions (do not redefine)
- Generate complete SKILL script with all geometry and all via arrays in every round
- SKILL must contain only flat, literal creation statements (no loops/conditionals)
- Use whitelisted commands: `dbCreatePath`, `dbCreateRect`, `dbCreateVia`, `dbCreateLabel`, `techGetTechFile`, `techFindViaDefByName`, `dbSave`, `dbClose`

### Step 3: Run SKILL to generate layout
- Call `run_il_with_screenshot` to execute SKILL
- For round k (1-based), set destination view to `layoutk`
- Do not delete or overwrite previous rounds

### Step 4: DRC check
- Call `run_drc()`
- Print complete DRC report content in full
- If violations exist, analyze and prioritize increasing relevant spacings

### Step 5: PEX extraction
- Call `run_pex()`
- Print complete PEX report content in full
- Extract TOP-BOT capacitance value (e.g., `cc_1` or `("BOT" "TOP")`)

### Step 6: Result judgement and iteration
- Calculate error: `error_percentage = abs((measured_C - target_C) / target_C) * 100`
- If error > 1% and iterations < 5: Update parameters and go back to Step 2
- If error ≤ 1% OR iterations = 5: Proceed to finalization

### Step 7: Finalization (required before Phase 2)

This step is required - Phase 2 and Phase 3 will fail if skipped.

- Select best round (lowest error or best result)
- Generate SKILL script using the best round's parameters
  - Use the best round's parameters from `geometry_round*.json` file
  - Generate complete SKILL script with all geometry and all via arrays
  - Use the same `compute_geometry()` and `render_skill()` functions (reuse from previous rounds)
- Execute SKILL script to generate the final layout in canonical `layout` view
  - Call `run_il_with_screenshot` with destination view set to `layout` (not layout1, layout2, etc.)
  - This creates/overwrites the `layout` view with the best round's geometry
  - Phase 2 and Phase 3 depend on this `layout` view - if it doesn't exist or is incorrect, Phase 3 will fail
- Record final result and proceed directly to Phase 2 (do not call `final_answer()`)

**Why this is important**: Phase 2 (Dummy generation) and Phase 3 (Array generation) read the unit capacitor from the `layout` view. If the `layout` view doesn't exist or contains incorrect geometry, downstream phases will fail with errors.

### Parameter Optimization Strategy

**Two-Phase Optimization Strategy**

#### Early Rounds (error > 20%) - Large-Step Adjustment

**Primary parameters:**
- **Count/replication parameters**: Increase by +2 to +6 elements per round
  - Examples: 3→5→7→9 (consult shape module for specific parameter names)
  - Step size: +4 to +6 elements if error > 50%, +2 to +4 if error 20-50%
- **Metal layer count**: Add +1 to +3 layers per round
  - Ensure valid metal adjacency per technology config

**Strategy**: Adjust both parameters together in same round for maximum impact. Monitor DRC compliance.

#### Late Rounds (error ≤ 20%) - Fine-Tuning

**Primary parameters (in priority order):**
1. **Height**: Adjust by ±0.05 to ±0.1 µm (preferred - continuous control)
   - Step size: ±0.1 µm if error 10-20%, ±0.05 µm if error < 10%
2. **Count/replication parameters**: Adjust by ±1 to ±2 elements (if height at limits)
3. **Metal layer count**: Adjust by ±1 layer (if other adjustments insufficient)

**Strategy**: Adjust one parameter at a time to understand effect. Height preferred for fine control.

#### General Guidelines

**Parameter priority (all rounds):**
1. Count/replication parameters (directly increase plate area)
2. Metal layer count (increase stacked capacitance, maintain valid adjacency)
3. Primary dimensions (height, width, length - respect size limits)
4. Inter-plate spacings (reduce within DRC minima - use with caution)
5. Width parameters (use only for DRC compliance or actual plate area increase)

**Important notes:**
- Via row count is not a capacitance optimization parameter
  - One row of vias is generally sufficient for connectivity
  - Do not use two rows unless user explicitly requires it
- Width changes have smaller impact - use count/replication parameters and layers first
- Consult shape module for specific parameter names and technology module for constraints

#### Area-Matching Trade-off

**Principle**: Mismatch ∝ 1/√(Area)

**When matching is critical**: Increase spacing parameters beyond minimum DRC to increase area without proportionally increasing capacitance. Trade-off: larger footprint for better matching. Use for ADC/DAC applications or when matching spec is tight.

---

## Phase 2: Dummy Capacitor Generation

**Prerequisite**: Phase 1 must be completed with final `layout` view generated. Phase 2 will fail if `layout` view doesn't exist.

### Step 1: Load Phase 2 knowledge modules
- Load dummy generation module for the selected shape structure
- Follow knowledge loading policy (LOAD → UNDERSTAND → EXECUTE)

### Step 2: Generate dummy capacitor
- Library: Reuse from Phase 1
- Cell name: Auto-generate based on unit capacitor (e.g., `C_MAIN_6fF` → `C_DUMMY_6fF`)
- Base on: Best unit capacitor from `layout` view (Phase 1 final result)
  - The `layout` view must exist and contain the final unit capacitor geometry
  - If `layout` view doesn't exist, Phase 1 finalization (Step 7) was not completed correctly
- Inherit shield rendering decision from unit capacitor
- Apply dummy-specific geometric transformations per shape module

### Step 3: DRC verification
- Run DRC on generated dummy capacitor
- Print complete DRC report content
- If violations exist:
  - For minimum area violations on routing wires: Delete problematic routing wires
  - Regenerate and re-run DRC until pass
- If DRC passes: Proceed to Phase 3

---

## Phase 3: Capacitor Array Generation

**Prerequisite**: Phase 1 must be completed with final `layout` view generated. Phase 3 will fail if `layout` view doesn't exist.

### Step 1: Load Phase 3 knowledge modules
- Load array generation module (`04_Array_Generation.md`)
- Follow knowledge loading policy (LOAD → UNDERSTAND → EXECUTE)

### Step 2: CDAC array analysis
- Analyze Excel file structure (array dimensions, connection groups, capacitor positions, pin assignments)
- Extract complete array structure needed for generation

### Step 3: Generate capacitor array
- Use CDAC analysis results to identify continuous regions
- Use `dbCreateParamSimpleMosaic` for each continuous region
- Implement routing connections for all connection groups
- Place dummy capacitors according to array configuration
- Follow rules in `04_Array_Generation.md`

### Step 4: Verification (all steps required)

**4a. DRC check:**
- Run DRC on generated array
- Print complete DRC report content
- If violations: Fix and re-run until pass
- Common issues: routing wire spacing violations, minimum area violations, via placement issues

**4b. PEX extraction:**
- Run PEX on generated array (only after DRC passes)
- Print complete PEX report content

**4c. Capacitance analysis:**
- Extract capacitance values from PEX report
- Compare with expected values from CDAC analysis
- Verify connection groups have correct capacitance values (1C, 2C, 4C, etc.)
- If incorrect: Fix and re-run PEX until values match expected

**Phase 3 is not complete until DRC passes, PEX is performed, and capacitance values are verified as correct.**

---

## Execution Principles (Apply to All Phases)

### Code Generation
- **Python functions**: Define `compute_geometry()` and `render_skill()` in Round 1, reuse in subsequent rounds
- **SKILL flattening**: All repetition/logic in Python; SKILL contains only flat statements
- **Complete generation**: Every round must generate complete SKILL with all geometry and all via arrays
- **Template reuse**: Cache SKILL template structure, only update parameter values between rounds

### View Management
- Each iteration uses a new view (`layout1`, `layout2`, etc.) - no clearing needed
- Do not use UI-dependent APIs (`ge*`) or selection-based deletion
- Only use `clear_all_figures_in_window()` when deliberately redrawing in the same view

### Parameter Updates
- Update parameter values in SKILL via string replacement
- Explain why parameters are adjusted and why step size is appropriate
- AI chooses parameters; Python validates constraints but does not choose parameters
- All updates must satisfy requirement analysis and parameter constraints

### Error Handling
- Prefer minimal fixes over full rewrites
- Locate issue and fix with minimal edits
- Ensure no new errors are introduced

### Iteration Control
- Execute all rounds automatically in sequence
- End after 5 rounds OR when absolute relative error ≤ 1%
- Do not terminate earlier
- Continue automatically between rounds without pausing

---

## Related Documents

- **00_Core_Principles.md**: Core principles referenced by this workflow
- **02_Python_SKILL_Integration.md**: Python/SKILL integration details for Step 2
- **04_Array_Generation.md**: Detailed array generation rules for Phase 3
- **Shape structure modules**: Structure-specific implementation details
- **Technology_Configs/**: Technology-specific constraints and parameters
