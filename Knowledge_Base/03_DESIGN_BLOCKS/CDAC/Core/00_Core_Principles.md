# Core Principles for Capacitor Design - Universal execution rules (all capacitor types, all technologies)

## Overview

This document defines the core principles that apply to all capacitor design workflows regardless of capacitor shape or technology node. These principles should be enforced in all automation implementations.

---

## Core Principles

1. **Execute step-by-step with single-step outputs and checks**
   - Each step produces independent outputs and records paths
   - Each step must be verifiable before proceeding to the next

2. **Pass criterion: absolute relative error ≤ ±1%**
   - Never treat "greater than target" as a pass
   - Only absolute relative error ≤ 1% counts as passing
   - Formula: `error_percentage = abs((measured_C - target_C) / target_C) * 100`

3. **All length units are micrometers (um)**
   - Consistent unit system across all calculations and outputs
   - Explicitly specify units when displaying values

4. **Output language: English**
   - This knowledge base guides automation; all runtime outputs should be in English
   - Console logs and comments should be in English
   - Documentation and reports should be in English

5. **Complete 5 iterations or meet ±1% error before ending**
   - Do not call `final_answer()` earlier
   - Iteration limit: maximum 5 rounds
   - Early termination only if absolute relative error ≤ 1%

6. **If error > 1% and iterations < 5, keep optimizing**
   - No early stop until convergence criterion is met
   - Continue tuning parameters until error ≤ 1% or iteration limit reached

7. **No user interaction during runs - Automatic Continuation**
   - The flow must be fully automated
   - All required inputs (library names, cell names) must be collected before starting the automated workflow
   - The program should automatically continue to the next iteration round without stopping or waiting for user input, unless:
     - Convergence achieved (absolute relative error ≤ 1%)
     - Iteration limit reached (5 rounds completed)
     - Truly blocking issue (information completely missing and cannot be inferred)
   - Do not pause for user input during iteration loops
   - Do not stop or display "[User prompt]:" between iteration rounds
   - Do not call `final_answer()` inside the iteration loop - only after convergence or 5 rounds
   - Execute all rounds automatically in sequence: generate → DRC → PEX → evaluate → update params → immediately proceed to next round

8. **Intent-first, minimal questioning**
   - Interpret user intent from natural language and map it to phases (Unit/Dummy/Array)
   - Ask only for inputs that are strictly required for the current phase(s)
   - Prefer executing with defaults derived from configs/previous context instead of broad questionnaires

9. **Lazy Knowledge Loading (Step-by-Step Loading)**
   - Do not preload all knowledge modules at the start - only load what's needed for the current step
   - Universal modules can be loaded early as they apply to all phases
   - Phase-specific modules should be loaded only when reaching the corresponding workflow step:
     - Phase 1: Load phase-specific modules only when starting the phase
     - Phase 2: Load phase-specific modules only when transitioning from Phase 1 to Phase 2
     - Phase 3: Load phase-specific modules only when starting Phase 3
   - Plan-based loading: You can identify which modules will be needed and add them to the execution plan, but do not load them until the corresponding step is reached
   - Rationale: Avoid knowledge overload, reduce generation errors, and maintain focus on the current task
   - Exception: Universal principles can be loaded early as they are foundational

---

## Convergence Criterion

**Pass condition**: Absolute relative error ≤ 1%, OR after 5 iterations

In code, the error judgement should print:
```python
if abs(error_percentage) <= 1:
    print("Capacitance meets the ±1% requirement")
else:
    print("Capacitance out of ±1%, need parameter adjustment")
```

When calling `final_answer()` at the end of Phase 1, summarize:
- Per-iteration parameters
- Measured capacitance and error for each iteration
- DRC status for each iteration
- Best iteration selection
- Final parameters

Do not call `final_answer()` early - wait until 5 rounds complete or ±1% target met.

---

## Related Documents

- **01_Workflow_Framework.md**: Detailed workflow steps that implement these principles
- **02_Python_SKILL_Integration.md**: Technical implementation details
- **Shape-specific modules**: Application of these principles to specific capacitor shapes
- **Technology_Configs/**: Technology-specific constraints and parameters
