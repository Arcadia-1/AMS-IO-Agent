#!/usr/bin/env python3
"""
Batch experiment runner for IO Ring pad layout experiments
Similar structure to run_batch_experiments.py

Usage:
    # Run all pad layout experiments
    python run_io_ring_batch.py --model-name deepseek
    
    # Run specific pad layout
    python run_io_ring_batch.py --pad-layout 3x3_single_ring_digital --model-name deepseek
    
    # Run range of experiments
    python run_io_ring_batch.py --start-index 1 --stop-index 10 --model-name deepseek
"""

# ============================================================================
# Pad Layout Templates Registry
# ============================================================================

PAD_LAYOUTS = {
    "3x3_single_ring_digital": {
        "description": "3 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "RSTN SCK SDI SDO D4 D3 D2 D1 VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}\n\nSignal names: {signals}\n\nVoltage domain requirements:\n- Digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH)\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}"
    },
    "3x3_single_ring_analog": {
        "description": "3 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VCM IBAMP IBREF AVDD AVSS VIN VIP VAMP IBAMP IBREF VDDIB VSSIB",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (VDDIB/VSSIB).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "4x4_single_ring_digital": {
        "description": "4 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "RSTN SCK SDI SDO D8 D7 D6 D5 D4 D3 D2 D1 IOVDDH IOVSS IOVDDL VSS",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital IO signals need to connect to digital domain voltage domain (IOVDDH/IOVSS/IOVDDL/VSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "4x4_single_ring_analog": {
        "description": "4 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS IB0 IB1 IB2 IB3 IBIAS IBIAS2 VAMP VAMP2",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "5x5_single_ring_digital": {
        "description": "5 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "5x5_single_ring_analog": {
        "description": "5 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS VREF1 VREF2 VREF3 VREF4 IBIAS IBIAS2 VAMP VAMP2 VAMP3 VAMP4 VAMP5 VAMP6",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "6x6_single_ring_digital": {
        "description": "6 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "6x6_single_ring_analog": {
        "description": "6 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS VREF1 VREF2 VREF3 VREF4 IBIAS IBIAS2 VAMP VAMP2 VAMP3 VAMP4 VAMP5 VAMP6 VAMP7 VAMP8 VAMP9 VAMP10",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "7x7_single_ring_digital": {
        "description": "7 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "7x7_single_ring_analog": {
        "description": "7 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS VREF1 VREF2 VREF3 VREF4 IBIAS IBIAS2 VAMP VAMP2 VAMP3 VAMP4 VAMP5 VAMP6 VAMP7 VAMP8 VAMP9 VAMP10 VAMP11 VAMP12 VAMP13 VAMP14",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "3x3_single_ring_mixed": {
        "description": "3 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VIN VSSIB VDDIB VCM D4 D3 D2 D1 VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (VDDIB/VSSIB), digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "4x4_single_ring_mixed": {
        "description": "4 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VIN VIP VCM AVDD AVSS D0 D1 D2 D3 VIOL GIOL VIOH GIOH RSTN SCK SDI",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS), digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "5x5_single_ring_mixed": {
        "description": "5 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 SCK SDI SDO RST SYNC IBREF AVDD AVSS VIN VIP VSSSAR VDDSAR VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH), analog signals use analog domain voltage domain (VSSSAR/VDDSAR).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "10x6_single_ring_mixed_1": {
        "description": "10 pads on left and right sides, 6 pads on top and bottom sides. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 SCK SDI SDO RST SYNC CLKO VIOL GIOL VIOH GIOH VCM3 VCM2 VCM IBAMP IBREF AVDD AVSS VIN VIP GND VDDI VSSI",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH), analog signals use analog domain voltage domain (AVDD/AVSS).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "10x6_single_ring_mixed_2": {
        "description": "10 pads on left and right sides, 6 pads on top and bottom sides. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 SDI SDO VIOL GIOL VIOH GIOH",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, analog signals use analog domain voltage domain (AVDD/AVSS), digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "8x8_double_ring_analog": {
        "description": "8 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS VREF1 VREF2 VREF3 VREF4 IBIAS IBIAS2 VAMP VAMP2 VAMP3 VAMP4 VAMP5 VAMP6 VAMP7 VAMP8 VAMP9 VAMP10 VAMP11 VAMP12 VAMP13 VAMP14 VAMP15 VAMP16 VAMP17 VAMP18",
        "inner_pads": [
            {"signal": "VREF_CORE", "between": ["VREF", "AVDD"]},
            {"signal": "VAMP_CORE", "between": ["VAMP", "VAMP2"]},
            {"signal": "IBIAS_CORE", "between": ["IBIAS", "IBIAS2"]},
            {"signal": "VCM_CORE", "between": ["VIM", "VCM"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VREF_CORE between VREF and AVDD, insert an inner ring pad VAMP_CORE between VAMP and VAMP2, insert an inner ring pad IBIAS_CORE between IBIAS and IBIAS2, insert an inner ring pad VCM_CORE between VIM and VCM. Among them, analog signals use analog domain voltage domain (AVDD/AVSS), digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "8x8_double_ring_digital": {
        "description": "8 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24 D25 D26 D27 VIOL GIOL VIOH GIOH",
        "inner_pads": [
            {"signal": "D28", "between": ["D26", "D27"]},
            {"signal": "D29", "between": ["D27", "VIOL"]},
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad D28 between D26 and D27, insert an inner ring pad D29 between D27 and VIOL. Among them digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "8x8_double_ring_mixed": {
        "description": "8 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 VIOL GIOL VIOH GIOH",
        "inner_pads": [
            {"signal": "VREF_CORE", "between": ["VCM", "VREF"]},
            {"signal": "D24", "between": ["D22", "D23"]},
            {"signal": "VAMP_CORE", "between": ["VINP", "VINN"]},
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VREF_CORE between VCM and VREF, insert an inner ring pad D24 between D22 and D23, insert an inner ring pad VAMP_CORE between VINP and VINN. Among them, analog signals use analog domain voltage domain (AVDD/AVSS), digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x12_single_ring_multi_voltage_domain_1": {
        "description": "12 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "DCLK SYNC VIOL GIOL VIOH GIOH VDD3 IB3 VDD12 IB12 VDD_CDAC VREFDES IBREF VSS IBUF_IBIAS VSS VDDIB VSSIB VINP VINN VSSIB VINCM GND_CKB VDD_CKB CLKP CLKN VDD_DAT GND_DAT VCM VSSCLK VDDCLK VDDSAR VSSSAR VREFH VREFM VREFN VREFDES2 IBREF2 SLP SDI SCK SDO RST D0 D1 D2 D3 D4",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, from VDD3 to VINCM use VSSIB and VDDIB as voltage domain, from GND_CKB to CLKN use GND_CKB and VDD_CKB as voltage domain, from VDD_DAT to VSSSAR use VDD_DAT and GND_DAT as voltage domain, from VREFH to IBREF2 use VREFH and VREFN as voltage domain. these voltage domains use PVDD3AC and PVSS3AC. Digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH)\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x12_single_ring_multi_voltage_domain_2": {
        "description": "12 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "RSTN SCK SDI SDO D8 D7 D6 D5 D4 D3 D2 D1 D0 SLP IOVDDH IOVSS IOVDDL VSS DVSS DVDD VCALB VCALF IBIAS3N IBIAS2N VAMP IBIAS1P VCM AVDD AVSS VINN VINP AVDDBUF IBUF1P IBUF2N IBUF3N IBVREF CBVDD CKVSS CLKINN CLKINP CKVDD RVSS REFIN IBIAS_REF RVDD RVDDH IBIAS IBIAS2",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Among them, from DVSS to VCALF use DVSS and DVDD as voltage domain, from IBIAS3N to CBVDD use AVDD and AVSS as voltage domain, from CKVSS to CKVDD use CKVSS and CKVDD as voltage domain, from RVSS to IBIAS2 use RVSS and RVDD as voltage domain, these all use PVSS3AC and PVSS3AC. Digital IO signals need to connect to digital domain voltage domain (IOVDDH/IOVSS/IOVDDL/VSS)\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "8x8_double_ring_multi_voltage_domain": {
        "description": "8 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF IBVREF VDDIB VSSIB VDD_CKB CLKN CLKP VSS_CKB  D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 VIOL GIOL VIOH GIOH",
        "inner_pads": [
            {"signal": "VREF_CORE", "between": ["VCM", "VREF"]},
            {"signal": "D16", "between": ["D14", "D15"]},
            {"signal": "VAMP_CORE", "between": ["VINP", "VINN"]},
            {"signal": "IBIAS_CORE", "between": ["VIP", "VIM"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VREF_CORE between VCM and VREF, insert an inner ring pad D16 between D14 and D15, insert an inner ring pad VAMP_CORE between VINP and VINN, insert an inner ring pad IBIAS_CORE between VIP and VIM. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VINP to VSSIB uses VDDIB and VSSIB as voltage domain. From VDD_CKB to VSS_CKB uses VDD_CKB and VSS_CKB as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "10x10_double_ring_multi_voltage_domain": {
        "description": "10 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS VDDIB VSSIB VDD_CKB VSS_CKB VDD_DAT VSS_DAT VREFH VREFN VDD_ADC VSS_ADC VDD_DAC VSS_DAC D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 VIOL GIOL VIOH GIOH",
        "inner_pads": [
            {"signal": "VREF_CORE", "between": ["VCM", "VREF"]},
            {"signal": "VAMP_CORE", "between": ["VINP", "VINN"]},
            {"signal": "ADC_CORE", "between": ["VDD_ADC", "VSS_ADC"]},
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VREF_CORE between VCM and VREF, insert an inner ring pad VAMP_CORE between VINP and VINN, insert an inner ring pad IBIAS_CORE between VIP and VIM, insert an inner ring pad ADC_CORE between VDD_ADC and VSS_ADC. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VINP to VREF uses AVDD and AVSS as voltage domain. From VDDIB to VSSIB uses VDDIB and VSSIB as voltage domain. From VDD_CKB to VSS_CKB uses VDD_CKB and VSS_CKB as voltage domain. From VDD_DAT to VSS_DAT uses VDD_DAT and VSS_DAT as voltage domain. From VREFH to VREFN uses VREFH and VREFN as voltage domain. From VDD_ADC to VSS_ADC uses VDD_ADC and VSS_ADC as voltage domain. From VDD_DAC to VSS_DAC uses VDD_DAC and VSS_DAC as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x12_double_ring_mixed": {
        "description": "12 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "VINP VINN VIP VIM VCM VREF AVDD AVSS D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24 D25 D26 D27 D28 D29 D30 D31 D32 D33 D34 D35 VIOL GIOL VIOH GIOH",
        "inner_pads": [
            {"signal": "VREF_CORE", "between": ["VCM", "VREF"]},
            {"signal": "VAMP_CORE", "between": ["VINP", "VINN"]},
            {"signal": "IBIAS_CORE", "between": ["VIP", "VIM"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VREF_CORE between VCM and VREF, insert an inner ring pad VAMP_CORE between VINP and VINN, insert an inner ring pad IBIAS_CORE between VIP and VIM. Among them, analog signals use analog domain voltage domain (AVDD/AVSS), digital signals use digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x18_double_ring_mixed": {
        "description": "12 pads on left and right sides, 18 pads on top and bottom sides. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "IB0 IB1 IB2 IB3 IB4 IB5 IB6 IB7 VDDGM VSSGM VCMGM VDDA09 VSSA VDDA18 VCM GND VIP VIN GND VCM09 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 CLKO SLP RST SCK SDI SDO VIOH VIOL GIOH GIOL VAMP IBIAS IBIAS2 VREFIB VREFIB2",
        "inner_pads": [
            {"signal": "D14", "between": ["D13", "D12"]},
            {"signal": "MARKER", "between": ["D12", "D11"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad D14 between D13 and D12, insert an inner ring pad MARKER between D12 and D11. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. Analog signals use analog domain voltage domain (VDDGM/VSSGM).\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "18x12_single_ring_mixed": {
        "description": "18 pads on left and right sides, 12 pads on top and bottom sides. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 CS EN TEST VIOH VIOL GIOH GIOL VSSSAR VDDSAR VIP VIN VCM VINCM IBIAS IBIAS2 VREF VREF2 IB0 IB1 IB2 IB3 IB4 IB5 IB6 IB7 IB8 IB9 IB10 IB11 IB12 IB13 IB14 IB15 IB16 IB17 IB18 IB19 IB20 IB21 IB22 IB23 IB24 IB25 IB26",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. Analogs domain uses VDDSAR/VSSSAR as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x12_double_ring_multi_voltage_domain_1": {
        "description": "12 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 SCK SDI SDO RST SYNC VIOH GIOH VIOL GIOL VCM IBAMP IBREF AVDD AVSS VIN VIP IB1 IB2 IB3 IB4 IB5 IB6 IB7 IB8 VDD_CKB VSS_CKB CLKP CLKN IBIAS IBIAS2 IBIAS3 IBIAS4 VDDSAR VSSSAR IBIAS5 IBIAS6 IBIAS7 IBIAS8",
        "inner_pads": [
            {"signal": "VCM2", "between": ["VCM", "IBAMP"]},
            {"signal": "D10", "between": ["D8", "D9"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VCM2 between VCM and IBAMP, insert an inner ring pad D10 between D8 and D9. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VCM to IB8 uses AVDD and AVSS as voltage domain. From VDD_CKB to CLKN uses VDD_CKB and VSS_CKB as voltage domain. From IBIAS to IBIAS8 uses VDDSAR and VSSSAR as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x12_double_ring_multi_voltage_domain_2": {
        "description": "12 pads on left and right sides, 12 pads on top and bottom sides. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "AVDD AVSS VIN VIP GND VCM VCM2 VCM3 IBREF IBREF2 IBVIAS IBVIAS2 VCM4 VCM5 VCM6 VSSIB VDDIB IB0 IB1 IB2 IB3 IB4 IB5 IB6 IB7 D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 SCK SDI SDO RST SYNC CLKO FLAG GIOL VIOL GIOH VIOH",
        "inner_pads": [
            {"signal": "D12", "between": ["D9", "D10"]},
            {"signal": "VCM1", "between": ["VCM", "VCM2"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad D12 between D9 and D10, insert an inner ring pad VCM1 between VCM and VCM2. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From AVDD to IB7 uses AVDD and AVSS as voltage domain. From IBREF to VDDIB uses VDDIB and VSSIB as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "12x18_double_ring_multi_voltage_domain": {
        "description": "12 pads on left and right sides, 18 pads on top and bottom sides. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "DCLK SYNC VIOL GIOL VIOH GIOH VDD3 IB3 VDD12 IB12 VDD_CDAC VREFDES IBREF VSS IBUF_IBIAS VDDIB VSSIB VINP VINN VINCM GND_CKB VDD_CKB CLKP CLKN VDD_DAT GND_DAT VCM VSSCLK VDDCLK AVDD AVSS VDDSAR VSSSAR VREFDES2 IBREF2 VREFDES3 IBREF3 SLP SDI SCK SDO RST D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 CS EN RSTN MCLK SCLK LRCK",
        "inner_pads": [
            {"signal": "VSS_CDAC", "between": ["VDD_CDAC", "VREFDES"]},
            {"signal": "D12", "between": ["D10", "D11"]},
            {"signal": "BIAS2", "between": ["IBUF_IBIAS", "VDDIB"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VSS_CDAC between VDD_CDAC and VREFDES, insert an inner ring pad D12 between D10 and D11, insert an inner ring pad BIAS2 between IBUF_IBIAS and VDDIB. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VDD3 to VINCM uses VDDIB and VSSIB as voltage domain. From GND_CKB to CLKN uses VDD_CKB and GND_CKB as voltage domain. From VDD_DAT to IBREF3 uses VDD_DAT and GND_DAT as voltage domain. these voltage domains use PVDD3AC and PVSS3AC. Digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH)\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "18x18_single_ring_multi_voltage_domain": {
        "description": "18 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "DCLK SYNC VIOL GIOL VIOH GIOH VDD3 IB3 VDD12 IB12 VDD_CDAC VREFDES IBREF VSS IBUF_IBIAS VDDIB VSSIB VINP VINN VINCM GND_CKB VDD_CKB CLKP CLKN VDD_DAT GND_DAT VCM VSSCLK VDDCLK VDDSAR VSSSAR VREFDES2 IBREF2 VREFDES3 IBREF3 SLP SDI SCK SDO RST D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 CS EN TEST RSTN MCLK SCLK LRCK DIN DOUT DOUT1 DOUT2 DOUT3 DOUT4 DOUT5 DOUT6 DOUT7",
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VDD3 to VINCM uses VDDIB and VSSIB as voltage domain. From GND_CKB to CLKN uses VDD_CKB and GND_CKB as voltage domain. From VDD_DAT to IBREF3 uses VDD_DAT and GND_DAT as voltage domain.\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
    "18x18_double_ring_multi_voltage_domain": {
        "description": "18 pads per side. Double ring layout. Order: counterclockwise through left side, bottom side, right side, top side.",
        "signals": "DCLK SYNC VIOL GIOL VIOH GIOH VDD3 IB3 VDD12 IB12 VDD_CDAC VREFDES IBREF VSS IBUF_IBIAS VDDIB VSSIB VINP VINN VINCM GND_CKB VDD_CKB CLKP CLKN VDD_DAT GND_DAT VCM VSSCLK VDDCLK AVDD AVSS VDDSAR VSSSAR VREFDES2 IBREF2 VREFDES3 IBREF3 SLP SDI SCK SDO RST D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 CS EN TEST RSTN MCLK SCLK LRCK DIN DOUT DOUT1 DOUT2 DOUT3 DOUT4 DOUT5",
        "inner_pads": [
            {"signal": "VSS_CORE", "between": ["VDDSAR", "VSSSAR"]},
            {"signal": "D16", "between": ["D14", "D15"]},
            {"signal": "AVDD_CORE", "between": ["AVDD", "AVSS"]},
            {"signal": "DCLK", "between": ["MCLK", "SCLK"]}
        ],
        "template": "Task: Generate IO ring schematic and layout design for Cadence Virtuoso.\n\nDesign requirements:\n{description}Signal names: {signals}. Additionally, please insert an inner ring pad VSS_CORE between VDDSAR and VSSSAR, insert an inner ring pad D16 between D14 and D15, insert an inner ring pad AVDD_CORE between AVDD and AVSS, insert an inner ring pad DCLK between MCLK and SCLK. Voltage domains: Digital domain uses VIOH, GIOH, VIOL, GIOL as voltage domain. From VDD3 to VINCM uses VDDIB and VSSIB as voltage domain. From GND_CKB to CLKN uses VDD_CKB and GND_CKB as voltage domain. From VDD_DAT to IBREF3 uses VDD_DAT and GND_DAT as voltage domain\n\nConfiguration:\n- Technology: 28nm process node\n- Library: {library_name}\n- Cell name: {cell_name}\n- View: {view_name}\n\nSteps to complete:\n1. Generate intent graph file based on the pad layout requirements\n2. Generate IO ring schematic SKILL code using generate_io_ring_schematic tool\n3. Generate IO ring layout SKILL code using generate_io_ring_layout tool\n4. Execute the generated SKILL code in Virtuoso to create the schematic and layout\n5. Verify the design meets the requirements"
    },
}

import subprocess
import sys
import os
import signal
from pathlib import Path
from datetime import datetime
import time
import yaml

# Import run_experiment from run_batch_experiments.py
# We'll reuse the same experiment running logic
# Note: We need to import it at runtime to avoid circular imports

# ============================================================================
# Helper Functions
# ============================================================================

def generate_prompt_text(pad_layout_name, prefix="", library_name="LLM_Layout_Design", cell_name=None, view_name="schematic"):
    """
    Generate prompt text from pad layout template
    
    Args:
        pad_layout_name: Name of the pad layout configuration
        prefix: Prefix for prompt keys (optional)
        library_name: Library name (default: "LLM_Layout_Design")
        cell_name: Cell name (default: auto-generated from pad_layout_name)
        view_name: View name (default: "schematic" for schematic, "layout" for layout)
    
    Returns:
        Formatted prompt string
    """
    if pad_layout_name not in PAD_LAYOUTS:
        raise ValueError(f"Unknown pad layout: {pad_layout_name}")
    
    layout = PAD_LAYOUTS[pad_layout_name]
    # Ensure description ends with a space if it doesn't end with punctuation
    description = layout["description"]
    if not description.endswith(('.', '!', '?', ' ')):
        description += " "
    elif description.endswith('.'):
        description += " "
    
    # Generate cell name if not provided
    if cell_name is None:
        # Convert pad_layout_name to cell name format (e.g., "3x3_single_ring_digital" -> "IO_RING_3x3_single_ring_digital")
        cell_name = f"IO_RING_{pad_layout_name}"
        if prefix:
            cell_name = f"{prefix}_{cell_name}"
    
    prompt = layout["template"].format(
        description=description,
        signals=layout["signals"],
        library_name=library_name,
        cell_name=cell_name,
        view_name=view_name
    )
    
    # Remove "Steps to complete" section if present
    if "\n\nSteps to complete:" in prompt:
        prompt = prompt.split("\n\nSteps to complete:")[0].rstrip()
    
    # Improve formatting: ensure description and signals are separated, and extract voltage domain info
    if "Design requirements:" in prompt and "Signal names:" in prompt:
        lines = prompt.split('\n')
        new_lines = []
        i = 0
        voltage_domain_info = []
        
        while i < len(lines):
            line = lines[i]
            # Look for "Design requirements:" line
            if "Design requirements:" in line:
                new_lines.append(line)
                i += 1
                # Next line should be description
                if i < len(lines):
                    desc_line = lines[i]
                    # If description line contains "Signal names:", split them
                    if "Signal names:" in desc_line:
                        # Split description and signals
                        parts = desc_line.split("Signal names:", 1)
                        if parts[0].strip():
                            new_lines.append(parts[0].strip())
                        new_lines.append("")
                        
                        # Process signals part - extract voltage domain info
                        signals_part = parts[1] if len(parts) > 1 else ""
                        # Check for voltage domain patterns
                        if "Among them" in signals_part or "voltage domain" in signals_part.lower():
                            # Extract voltage domain info
                            if "Among them" in signals_part:
                                # Split signals and voltage domain info
                                signals_clean = signals_part.split("Among them")[0].strip()
                                # Remove trailing period from signals
                                signals_clean = signals_clean.rstrip('.')
                                
                                voltage_text = signals_part.split("Among them", 1)[1] if "Among them" in signals_part else ""
                                # Clean up voltage domain text
                                if voltage_text:
                                    # Remove leading/trailing whitespace, comma, and period
                                    voltage_text = voltage_text.strip().lstrip(',').strip().rstrip('.')
                                    # Remove "Among them" prefix if present in the extracted text
                                    if voltage_text.lower().startswith("among them"):
                                        voltage_text = voltage_text[10:].strip().lstrip(',').strip()
                                    if voltage_text:
                                        voltage_domain_info.append(voltage_text)
                                
                                new_lines.append("Signal names: " + signals_clean)
                            else:
                                # Clean signals part
                                signals_clean = signals_part.strip().rstrip('.')
                                new_lines.append("Signal names: " + signals_clean)
                        else:
                            # Clean signals part
                            signals_clean = signals_part.strip().rstrip('.')
                            new_lines.append("Signal names: " + signals_clean)
                    else:
                        new_lines.append(desc_line)
                    i += 1
            else:
                new_lines.append(line)
                i += 1
        
        # Insert voltage domain requirements section if we extracted any
        if voltage_domain_info:
            # Find where to insert (before Configuration section)
            final_lines = []
            inserted = False
            for line in new_lines:
                if not inserted and line.strip().startswith("Configuration:"):
                    # Insert voltage domain section before Configuration
                    final_lines.append("")
                    final_lines.append("Voltage domain requirements:")
                    for vd_info in voltage_domain_info:
                        # Format as bullet point
                        vd_clean = vd_info.strip()
                        if not vd_clean.startswith("-"):
                            vd_clean = "- " + vd_clean
                        final_lines.append(vd_clean)
                    final_lines.append("")
                    inserted = True
                final_lines.append(line)
            prompt = '\n'.join(final_lines)
        else:
            prompt = '\n'.join(new_lines)
    
    return prompt

def generate_prompt_key(pad_layout_name, prefix=""):
    """Generate prompt key from pad layout name"""
    if prefix:
        prefix = prefix.rstrip('_') + '_'
    return f"{prefix}io_ring_{pad_layout_name}"

def get_available_pad_layouts():
    """Get list of available pad layout names"""
    return list(PAD_LAYOUTS.keys())

def generate_io_ring_yaml(output_file="user_prompt/IO_RING.yaml", prefix="", library_name="LLM_Layout_Design", view_name="schematic"):
    """
    Generate IO_RING.yaml file with all pad layout prompts
    
    Args:
        output_file: Path to output YAML file
        prefix: Prefix for prompt keys (optional)
        library_name: Library name to use in prompts (default: "LLM_Layout_Design")
        view_name: View name to use in prompts (default: "schematic")
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate YAML content
    yaml_content = {}
    yaml_content["# User Prompt Configuration"] = None
    yaml_content["# IO Ring pad layout prompts"] = None
    yaml_content["# Generated automatically from run_io_ring_batch.py"] = None
    yaml_content[""] = None
    
    # Add each pad layout as a prompt
    for layout_name in get_available_pad_layouts():
        prompt_key = generate_prompt_key(layout_name, prefix)
        prompt_text = generate_prompt_text(layout_name, prefix)
        yaml_content[prompt_key] = prompt_text
    
    # Write YAML file
    # We need to write it manually to handle comments and empty lines
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# User Prompt Configuration\n")
        f.write("# IO Ring pad layout prompts\n")
        f.write("# Generated automatically from run_io_ring_batch.py\n")
        f.write("# Use this file to define reusable prompts that can be selected via --prompt key\n")
        f.write("# Example: python src/main.py --prompt io_ring_3x3_single_ring_digital\n")
        f.write("\n")
        
        for layout_name in get_available_pad_layouts():
            prompt_key = generate_prompt_key(layout_name, prefix)
            # Generate cell name from layout name
            cell_name = f"IO_RING_{layout_name}"
            if prefix:
                cell_name = f"{prefix}_{cell_name}"
            prompt_text = generate_prompt_text(layout_name, prefix, library_name=library_name, cell_name=cell_name, view_name=view_name)
            
            f.write(f"{prompt_key}: |\n")
            # Indent each line of the prompt text
            for line in prompt_text.split('\n'):
                if line.strip():  # Only write non-empty lines
                    f.write(f"  {line}\n")
                else:
                    f.write("\n")
            f.write("\n")
    
    print(f"✅ Generated {output_path}")
    print(f"   Total prompts: {len(get_available_pad_layouts())}")
    return output_path

# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main function to run IO ring batch experiments"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run batch experiments for IO Ring pad layouts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all pad layout experiments
  python run_io_ring_batch.py --model-name deepseek
  
  # Run specific pad layout
  python run_io_ring_batch.py --pad-layout 3x3_single_ring_digital --model-name deepseek
  
  # Run range of experiments
  python run_io_ring_batch.py --start-index 1 --stop-index 10 --model-name deepseek
        """
    )
    parser.add_argument(
        "--pad-layout",
        type=str,
        default=None,
        help="Specific pad layout to run (if not specified, runs all)"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix for prompt keys and cell names (e.g., 'claude', 'gpt', 'deepseek'). Default: no prefix"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Model name to use (e.g., deepseek, gpt-4o, claude). If not specified, uses default."
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=None,
        help="Start from a specific experiment index (1-based)"
    )
    parser.add_argument(
        "--stop-index",
        type=int,
        default=None,
        help="Stop at a specific experiment index (1-based, inclusive)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list the experiments that would be run, without executing them"
    )
    parser.add_argument(
        "--preview-prompt",
        type=str,
        nargs='?',
        const="first",
        help="Preview generated prompt(s). Use 'first' to preview first prompt, 'all' to preview all, or specify a pad layout name."
    )
    parser.add_argument(
        "--ramic-host",
        type=str,
        default=None,
        help="RAMIC bridge host (default: from RB_HOST env var or 127.0.0.1)"
    )
    parser.add_argument(
        "--ramic-port-start",
        type=int,
        default=None,
        help="Starting RAMIC port number (each experiment will use port_start + index)"
    )
    parser.add_argument(
        "--ramic-port",
        type=int,
        default=None,
        help="RAMIC bridge port (used for all experiments if --ramic-port-start is not specified)"
    )
    parser.add_argument(
        "--list-layouts",
        action="store_true",
        help="List all available pad layout configurations"
    )
    parser.add_argument(
        "--generate-yaml",
        action="store_true",
        help="Generate IO_RING.yaml file in user_prompt directory with all pad layout prompts"
    )
    
    args = parser.parse_args()
    
    # Generate YAML file if requested
    if args.generate_yaml:
        output_file = Path("user_prompt/IO_RING.yaml")
        generate_io_ring_yaml(output_file, args.prefix)
        return
    
    # List layouts if requested
    if args.list_layouts:
        print("Available pad layout configurations:")
        print("=" * 80)
        for i, layout_name in enumerate(get_available_pad_layouts(), 1):
            layout = PAD_LAYOUTS[layout_name]
            signal_count = len(layout['signals'].split())
            print(f"{i:2d}. {layout_name:<50} | Signals: {signal_count:2d}")
            print(f"    Description: {layout['description']}")
            if 'inner_pads' in layout:
                inner_pad_count = len(layout['inner_pads'])
                print(f"    Inner pads: {inner_pad_count}")
            print()
        print("=" * 80)
        
        # If preview is also requested, continue to preview section
        if not args.preview_prompt:
            return
    
    # Determine log directory
    if args.prefix:
        log_dir = f"logs/batch_io_ring_{args.prefix}"
    else:
        log_dir = "logs/batch_io_ring"
    
    # Generate experiment list
    if args.pad_layout:
        if args.pad_layout not in PAD_LAYOUTS:
            print(f"Error: Unknown pad layout '{args.pad_layout}'")
            print(f"Available layouts: {', '.join(get_available_pad_layouts())}")
            return
        pad_layouts = [args.pad_layout]
    else:
        pad_layouts = get_available_pad_layouts()
    
    # Generate experiments
    experiments = []
    for pad_layout_name in pad_layouts:
        prompt_key = generate_prompt_key(pad_layout_name, args.prefix)
        experiments.append({
            "pad_layout_name": pad_layout_name,
            "prompt_key": prompt_key
        })
    
    print(f"Generated {len(experiments)} IO ring experiments:")
    if args.prefix:
        print(f"Using prefix: '{args.prefix}'")
    if args.model_name:
        print(f"Using model: '{args.model_name}'")
    print(f"Log directory: {log_dir}")
    for i, exp in enumerate(experiments, 1):
        print(f"  {i}. {exp['pad_layout_name']} -> {exp['prompt_key']}")
    
    # Filter by start/stop index
    if args.start_index is not None:
        if args.start_index < 1:
            print(f"Warning: Start index must be >= 1, ignoring --start-index")
        elif args.start_index > len(experiments):
            print(f"Warning: Start index {args.start_index} exceeds total experiments ({len(experiments)})")
        else:
            experiments = experiments[args.start_index - 1:]
            print(f"\nStarting from experiment index: {args.start_index}")
    
    if args.stop_index is not None:
        if args.stop_index < 1:
            print(f"Warning: Stop index must be >= 1, ignoring --stop-index")
        elif args.stop_index > len(experiments):
            print(f"Warning: Stop index {args.stop_index} exceeds remaining experiments ({len(experiments)})")
        else:
            experiments = experiments[:args.stop_index]
            print(f"Stopping at experiment index: {args.stop_index}")
    
    if args.dry_run:
        print("\n[DRY RUN] Would run the following experiments:")
        for exp in experiments:
            print(f"  - {exp['pad_layout_name']} -> {exp['prompt_key']}")
        return
    
    if args.preview_prompt:
        # If we only have list_layouts, we need to generate experiments list first
        if args.list_layouts and not args.pad_layout:
            # Generate all experiments for preview
            pad_layouts = get_available_pad_layouts()
            experiments = []
            for pad_layout_name in pad_layouts:
                prompt_key = generate_prompt_key(pad_layout_name, args.prefix)
                experiments.append({
                    "pad_layout_name": pad_layout_name,
                    "prompt_key": prompt_key
                })
        
        print("\n" + "="*80)
        print("PROMPT PREVIEW")
        print("="*80)
        
        preview_value = args.preview_prompt.lower() if args.preview_prompt else "first"
        
        if preview_value == "first":
            if experiments:
                exp = experiments[0]
                prompt_text = generate_prompt_text(exp["pad_layout_name"], args.prefix)
                print(f"\nPad Layout: {exp['pad_layout_name']}")
                print(f"Prompt Key: {exp['prompt_key']}")
                print("-"*80)
                print(prompt_text)
                print("="*80)
            else:
                print("No experiments to preview.")
        elif preview_value == "all":
            if experiments:
                for i, exp in enumerate(experiments, 1):
                    prompt_text = generate_prompt_text(exp["pad_layout_name"], args.prefix)
                    print(f"\n[{i}/{len(experiments)}] {exp['pad_layout_name']}")
                    print(f"Prompt Key: {exp['prompt_key']}")
                    print("-"*80)
                    print(prompt_text)
                    if i < len(experiments):
                        print("\n" + "="*80)
                print("="*80)
            else:
                print("No experiments to preview.")
        else:
            # Preview specific pad layout
            found = False
            for exp in experiments:
                if exp["pad_layout_name"] == args.preview_prompt:
                    prompt_text = generate_prompt_text(exp["pad_layout_name"], args.prefix)
                    print(f"\nPad Layout: {exp['pad_layout_name']}")
                    print(f"Prompt Key: {exp['prompt_key']}")
                    print("-"*80)
                    print(prompt_text)
                    print("="*80)
                    found = True
                    break
            if not found:
                print(f"Error: Pad layout '{args.preview_prompt}' not found.")
                print(f"Available layouts: {', '.join([e['pad_layout_name'] for e in experiments])}")
        
        # If only preview was requested (not list_layouts), return here
        if not args.list_layouts:
            return
    
    # Show summary before running
    print(f"\n{'='*80}")
    print(f"About to run {len(experiments)} experiments")
    if args.model_name:
        print(f"Model: {args.model_name}")
    print(f"Each experiment will timeout after 50 minutes if not completed")
    print(f"All experiments will run automatically without user intervention")
    print(f"{'='*80}")
    print("Starting batch execution in 3 seconds...")
    time.sleep(3)
    
    # Global flag for batch interruption
    batch_interrupted = {'flag': False}
    current_process = {'process': None}
    
    # Global signal handler for batch interruption
    def batch_signal_handler(signum, frame):
        if not batch_interrupted['flag']:
            batch_interrupted['flag'] = True
            print(f"\n\n{'='*80}")
            print(f"[BATCH INTERRUPTED] Received signal {signum}")
            print(f"Terminating current experiment and stopping batch...")
            print(f"{'='*80}\n")
            if current_process['process'] is not None:
                try:
                    if sys.platform.startswith('win'):
                        current_process['process'].kill()
                    else:
                        os.killpg(os.getpgid(current_process['process'].pid), signal.SIGKILL)
                except Exception:
                    pass
    
    # Register global signal handlers
    original_sigint = signal.signal(signal.SIGINT, batch_signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, batch_signal_handler)
    
    # Run experiments
    results = []
    total_start_time = time.time()
    
    print(f"Press Ctrl+C once to stop the entire batch immediately")
    
    try:
        for i, exp in enumerate(experiments, 1):
            if batch_interrupted['flag']:
                print(f"\n[BATCH STOPPED] Stopping batch execution after {len(results)} experiments")
                break
            
            prompt_key = exp["prompt_key"]
            pad_layout_name = exp["pad_layout_name"]
            
            # Generate prompt text
            prompt_text = generate_prompt_text(pad_layout_name, args.prefix)
            
            # Determine RAMIC port
            ramic_port = None
            if args.ramic_port_start is not None:
                ramic_port = args.ramic_port_start + (i - 1)
            elif args.ramic_port is not None:
                ramic_port = args.ramic_port
            
            print(f"\n[{i}/{len(experiments)}] Processing: {prompt_key} ({pad_layout_name})")
            
            # Import run_experiment here to avoid circular imports
            from run_batch_experiments import run_experiment
            
            # Use run_experiment with prompt_text directly
            result = run_experiment(
                excel_file=None,  # Not used for IO ring
                sheet_name=pad_layout_name,  # Use pad_layout_name for experiment info
                prefix=args.prefix,
                template_type="io_ring",  # Custom type
                model_name=args.model_name,
                ramic_port=ramic_port,
                ramic_host=args.ramic_host,
                log_dir=log_dir,
                batch_interrupted_flag=batch_interrupted,
                current_process_ref=current_process,
                prompt_text=prompt_text,  # Pass prompt text directly
                prompt_key=prompt_key  # Pass prompt key for logging
            )
            results.append(result)
            
            if batch_interrupted['flag']:
                print(f"\n[BATCH STOPPED] Stopping batch execution after {len(results)} experiments")
                break
            
            if not result["success"]:
                is_timeout = result.get("error", "").startswith("Experiment timed out")
                if is_timeout:
                    print(f"\n⚠️  Experiment '{prompt_key}' timed out after 50 minutes, automatically continuing...")
                else:
                    print(f"\n⚠️  Experiment '{prompt_key}' failed: {result.get('error', 'Unknown error')}")
                    print(f"Automatically continuing to next experiment...")
    except KeyboardInterrupt:
        batch_interrupted['flag'] = True
        print(f"\n[BATCH INTERRUPTED] Stopping batch execution...")
    finally:
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)
    
    # Print summary
    total_time = time.time() - total_start_time
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\n{'='*80}")
    if batch_interrupted['flag']:
        print("BATCH EXPERIMENT SUMMARY (INTERRUPTED)")
    else:
        print("BATCH EXPERIMENT SUMMARY")
    print(f"{'='*80}")
    print(f"Total experiments completed: {len(results)}/{len(experiments)}")
    if batch_interrupted['flag']:
        print(f"Remaining experiments: {len(experiments) - len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time/3600:.2f} hours ({total_time/60:.2f} minutes)")
    print(f"\nResults:")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['prompt_key']} ({result['elapsed_time']/60:.2f} min)")
        if not result["success"] and result["error"]:
            print(f"      Error: {result['error']}")
    
    if batch_interrupted['flag'] and len(results) < len(experiments):
        print(f"\nInterrupted experiments (not run):")
        for exp in experiments[len(results):]:
            print(f"  - {exp['prompt_key']}")
    
    print(f"{'='*80}\n")
    
    # Save summary to file
    summary_file = os.path.join(log_dir, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    os.makedirs(log_dir, exist_ok=True)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("BATCH EXPERIMENT SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Experiment type: IO Ring pad layouts\n")
        f.write(f"Total experiments: {len(results)}/{len(experiments)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Total time: {total_time/3600:.2f} hours ({total_time/60:.2f} minutes)\n\n")
        f.write("Results:\n")
        for result in results:
            status = "✓" if result["success"] else "✗"
            f.write(f"  {status} {result['prompt_key']} ({result['elapsed_time']/60:.2f} min)\n")
            if not result["success"] and result["error"]:
                f.write(f"      Error: {result['error']}\n")
            f.write(f"      Log: {result['log_file']}\n")
    
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()

