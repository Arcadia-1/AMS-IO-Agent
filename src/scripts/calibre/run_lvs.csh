#!/bin/csh -f
# Combined LVS script supporting multiple technology nodes (T28/T180)
# Usage: ./run_lvs.csh <library> <topCell> [view] [tech_node]
#   - <library>:   Cadence library name
#   - <topCell>:   cell name to export and run LVS on
#   - [view]:      view name for strmout (default: layout)
#   - [tech_node]: technology node (T28 or T180, default from TECH_NODE env var)
# Example:
#   ./run_lvs.csh LLM_Layout_Design test_v2
#   ./run_lvs.csh LLM_Layout_Design test_v2 layout
#   ./run_lvs.csh LLM_Layout_Design test_v2 layout T28

# Initialize environment
source /home/cshrc/.cshrc.cadence.IC618SP201
source /home/cshrc/.cshrc.mentor

# Determine script directory
set SCRIPT_DIR = `dirname "$0"`
if ( "$SCRIPT_DIR" == "." ) then
    set SCRIPT_DIR = "$cwd"
else
    set SCRIPT_DIR = `cd "$SCRIPT_DIR"; pwd`
endif

# Always source project environment to ensure required variables are available
if ( -f "$SCRIPT_DIR/env_common.csh" ) then
    source "$SCRIPT_DIR/env_common.csh"
else
    echo "Error: $SCRIPT_DIR/env_common.csh not found"
    exit 1
endif

# Check input arguments
if ( $#argv < 2 || $#argv > 4 ) then
    echo "Usage: $0 <library> <topCell> [view] [tech_node]"
    echo "  <library>:   Cadence library name"
    echo "  <topCell>:   cell name to export and run LVS on"
    echo "  [view]:      view name for strmout (default: layout)"
    if ( $?TECH_NODE ) then
        echo "  [tech_node]: technology node (T28 or T180, default: $TECH_NODE)"
    else
        echo "  [tech_node]: technology node (T28 or T180, required if TECH_NODE not set)"
    endif
    exit 1
endif

set library = $argv[1]
set topCell = $argv[2]

# Determine view parameter
if ( $#argv >= 3 ) then
    set view = "$argv[3]"
else
    set view = "layout"
endif

# Determine technology node
if ( $#argv >= 4 ) then
    set tech_node = "$argv[4]"
else
    if ( $?TECH_NODE ) then
        set tech_node = "$TECH_NODE"
    else
        echo "Error: Technology node not specified. Please provide [tech_node] argument or set TECH_NODE environment variable."
        exit 1
    endif
endif

# Define variables based on technology node
if ( "$tech_node" =~ T180* || "$tech_node" =~ 180* ) then
    if ( $?PDK_LAYERMAP_180 ) then
        set layerMapFile = "$PDK_LAYERMAP_180"
    else
        echo "Error: PDK_LAYERMAP_180 is not set. Please set it in env_common.csh"
        exit 1
    endif
    set lvsRuleFile = "$LVS_RULE_FILE_180"
    if ( ! -f "$lvsRuleFile" ) then
        echo "Error: LVS rule file not found: $lvsRuleFile"
        echo "Please ensure the file exists or update LVS_RULE_FILE_180 in env_common.csh"
        exit 1
    endif
    if ( $?incFILE_180 ) then
        set incFile = "$incFILE_180"
    else
        echo "Error: incFILE_180 is not set. Please set it in env_common.csh"
        exit 1
    endif
else if ( "$tech_node" =~ T28* || "$tech_node" =~ 28* ) then
    if ( $?PDK_LAYERMAP_28 ) then
        set layerMapFile = "$PDK_LAYERMAP_28"
    else
        echo "Error: PDK_LAYERMAP_28 is not set. Please set it in env_common.csh"
        exit 1
    endif
    set lvsRuleFile = "$LVS_RULE_FILE_28"
    if ( ! -f "$lvsRuleFile" ) then
        echo "Error: LVS rule file not found: $lvsRuleFile"
        echo "Please ensure the file exists or update LVS_RULE_FILE_28 in env_common.csh"
        exit 1
    endif
    if ( $?incFILE_28 ) then
        set incFile = "$incFILE_28"
    else
        echo "Error: incFILE_28 is not set. Please set it in env_common.csh"
        exit 1
    endif
else
    echo "Error: Unsupported technology node '$tech_node'. Supported: T28, T180."
    exit 1
endif

echo "[run_lvs] TECH_NODE='$tech_node' -> using rule file: $lvsRuleFile"

# Check if CDS_LIB_PATH is set (technology node specific first, then fallback)
if ( "$tech_node" =~ T180* || "$tech_node" =~ 180* ) then
    # For T180
    if ( $?CDS_LIB_PATH_180 ) then
        set cdsLibPath = "$CDS_LIB_PATH_180"
    else if ( $?CDS_LIB_PATH ) then
        set cdsLibPath = "$CDS_LIB_PATH"
    else
        # Try to read from project .env file
        if ( -f "$PROJECT_ROOT/.env" ) then
            set cds_from_env = `grep -E "^CDS_LIB_PATH_180=" "$PROJECT_ROOT/.env" | sed -e 's/^CDS_LIB_PATH_180=//'`
            if ( "$cds_from_env" != "" ) then
                set cdsLibPath = "$cds_from_env"
            else
                set cds_from_env = `grep -E "^CDS_LIB_PATH=" "$PROJECT_ROOT/.env" | sed -e 's/^CDS_LIB_PATH=//'`
                if ( "$cds_from_env" != "" ) then
                    set cdsLibPath = "$cds_from_env"
                else
                    echo "Error: CDS_LIB_PATH_180 or CDS_LIB_PATH is not set. Please set it in $PROJECT_ROOT/.env or env_common.csh"
                    exit 1
                endif
            endif
        else
            echo "Error: CDS_LIB_PATH_180 or CDS_LIB_PATH is not set and $PROJECT_ROOT/.env not found"
            exit 1
        endif
    endif
else
    # For T28
    if ( $?CDS_LIB_PATH_28 ) then
        set cdsLibPath = "$CDS_LIB_PATH_28"
    else if ( $?CDS_LIB_PATH ) then
        set cdsLibPath = "$CDS_LIB_PATH"
    else
        # Try to read from project .env file
        if ( -f "$PROJECT_ROOT/.env" ) then
            set cds_from_env = `grep -E "^CDS_LIB_PATH_28=" "$PROJECT_ROOT/.env" | sed -e 's/^CDS_LIB_PATH_28=//'`
            if ( "$cds_from_env" != "" ) then
                set cdsLibPath = "$cds_from_env"
            else
                set cds_from_env = `grep -E "^CDS_LIB_PATH=" "$PROJECT_ROOT/.env" | sed -e 's/^CDS_LIB_PATH=//'`
                if ( "$cds_from_env" != "" ) then
                    set cdsLibPath = "$cds_from_env"
                else
                    echo "Error: CDS_LIB_PATH_28 or CDS_LIB_PATH is not set. Please set it in $PROJECT_ROOT/.env or env_common.csh"
                    exit 1
                endif
            endif
        else
            echo "Error: CDS_LIB_PATH_28 or CDS_LIB_PATH is not set and $PROJECT_ROOT/.env not found"
            exit 1
        endif
    endif
endif

# Set run directory
if ( $?LVS_RUN_DIR ) then
    set runDir = "$LVS_RUN_DIR"
else
    set runDir = "${PROJECT_ROOT}/output/lvs"
endif

set logFile = "PIPO.LOG.${topCell}"
set summaryFile = "PIPO.SUM.${topCell}"
set strmFile = "${topCell}.calibre.db"
set tmpRuleFile = "_calibre.lvs_tmp"
set netlistFile = "${topCell}.src.net"

# Determine si.env template location
if ( "$tech_node" =~ T28* || "$tech_node" =~ 28* ) then
    set siEnvTemplate = "${SCRIPT_DIR}/T28/si_T28.env"
else
    # For T180, use T28 template if T180 doesn't have one
    if ( -f "${SCRIPT_DIR}/T180/si_T180.env" ) then
        set siEnvTemplate = "${SCRIPT_DIR}/T180/si_T180.env"
    else
        set siEnvTemplate = "${SCRIPT_DIR}/T28/si_T28.env"
    endif
endif
set siEnvFile = "si.env"

# Create run directory if it does not exist
if (! -d $runDir) then
    mkdir -p $runDir
    chmod 755 $runDir
endif

# Verify the configured cds.lib exists and is readable
if (! -f "$cdsLibPath") then
    echo "Error: Configured cds.lib not found: $cdsLibPath"
    echo "Please ensure CDS_LIB_PATH points to a valid cds.lib"
    exit 1
endif
if (! -r "$cdsLibPath") then
    echo "Error: Configured cds.lib is not readable: $cdsLibPath"
    exit 1
endif

# Create temporary rule file with replaced variables
echo "Creating temporary rule file: $runDir/$tmpRuleFile"
if ( ! -f "$lvsRuleFile" ) then
    echo "Error: LVS rule file not found: $lvsRuleFile"
    exit 1
endif
sed -e "s|@LAYOUT_PATH|${strmFile}|g" \
    -e "s|@LAYOUT_PRIMARY|${topCell}|g" \
    -e "s|@NETLIST_PATH|${netlistFile}|g" \
    -e "s|@NETLIST_PRIMARY|${topCell}|g" \
    -e "s|@RESULTS_DB|${topCell}.lvs.results|g" \
    -e "s|@SUMMARY_REPORT|${topCell}.lvs.summary|g" \
    "$lvsRuleFile" > "$runDir/$tmpRuleFile"

# Check if temporary rule file was created successfully
if (! -f "$runDir/$tmpRuleFile") then
    echo "Error: Failed to create temporary rule file"
    exit 1
endif

# Make sure the temporary rule file is readable
chmod 644 "$runDir/$tmpRuleFile"

echo "Contents of temporary rule file:"
cat "$runDir/$tmpRuleFile"

# Create si.env file with replaced variables
echo "Creating si.env file: $runDir/$siEnvFile"
if ( ! -f "$siEnvTemplate" ) then
    echo "Error: si.env template not found: $siEnvTemplate"
    exit 1
endif
sed -e "s|test_v2|${topCell}|g" \
    -e "s|LLM_Layout_Design|${library}|g" \
    -e "s|/home/lixintian/TSMC28/TEST/lvs|${runDir}|g" \
    -e "s|test_v2.src.net|${netlistFile}|g" \
    -e "s|/home/process/tsmc28n/PDK_mmWave/iPDK_CRN28HPC+ULL_v1.8_2p2a_20190531/tsmcN28/../Calibre/lvs/source.added|${incFile}|g" \
    "$siEnvTemplate" > "$runDir/$siEnvFile"

# Check if si.env file was created successfully
if (! -f "$runDir/$siEnvFile") then
    echo "Error: Failed to create si.env file"
    exit 1
endif

# Make sure the si.env file is readable
chmod 644 "$runDir/$siEnvFile"

echo "Contents of si.env file:"
cat "$runDir/$siEnvFile"

echo "Current directory: `pwd`"
echo "Contents of current directory:"
ls -la
echo "Contents of cds.lib (from $cdsLibPath):"
cat "$cdsLibPath"

# Step 1: Export layout using strmout
echo "Step 1: Exporting layout using strmout..."
strmout -library $library \
        -strmFile $strmFile \
        -topCell $topCell \
        -view $view \
        -layerMap $layerMapFile \
        -logFile $logFile \
        -summaryFile $summaryFile \
        -cdslib "$cdsLibPath" \
        -runDir $runDir

# Check if XStream Out was successful
if ($status != 0) then
    echo "Error: XStream Out failed. Checking log file..."
    if (-f "$runDir/$logFile") then
        echo "Contents of $runDir/$logFile:"
        cat "$runDir/$logFile"
    else
        echo "Log file not found: $runDir/$logFile"
    endif
    exit 1
endif

echo "Step 1 completed. Layout exported successfully."

# Step 2: Export netlist from schematic
echo "Step 2: Exporting netlist from schematic..."
cd $runDir
si -batch -command netlist \
   -cdslib "$cdsLibPath"

# Check if netlist export was successful
if ($status != 0) then
    echo "Error: Netlist export failed."
    exit 1
endif

echo "Step 2 completed. Netlist exported successfully."

# Check generated files
echo "Checking generated files:"
ls -la

pwd

echo "LM_LICENSE_FILE: $LM_LICENSE_FILE"

# Step 3: Run Calibre LVS
echo "Step 3: Running Calibre LVS..."
$MGC_HOME/bin/calibre -lvs -hier -turbo -hyper -nowait $tmpRuleFile

# Check if Calibre LVS was successful
if ($status != 0) then
    echo "Error: Calibre LVS failed."
    exit 1
endif

echo "Calibre LVS flow (${tech_node}) completed successfully."

# Launch RVE to view LVS results
# $MGC_HOME/bin/calibre -nowait -rve -lvs ${topCell}.lvs.results

