#!/bin/csh -f
# Combined PEX script supporting multiple technology nodes (T28/T180)
# Usage: ./run_pex.csh <library> <topCell> [view] [tech_node] [runDir]
#   - <library>:   Cadence library name
#   - <topCell>:   cell name to export and run PEX on
#   - [view]:      view name for strmout (default: layout)
#   - [tech_node]: technology node (T28 or T180, default from TECH_NODE env var)
#   - [runDir]:    run directory (optional, default from PEX_RUN_DIR or output/pex)
# Example:
#   ./run_pex.csh LLM_Layout_Design test_PEX
#   ./run_pex.csh LLM_Layout_Design test_PEX layout
#   ./run_pex.csh LLM_Layout_Design test_PEX layout T28

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
if ( $#argv < 2 || $#argv > 5 ) then
    echo "Usage: $0 <library> <topCell> [view] [tech_node] [runDir]"
    echo "  <library>:   Cadence library name"
    echo "  <topCell>:   cell name to export and run PEX on"
    echo "  [view]:      view name for strmout (default: layout)"
    if ( $?TECH_NODE ) then
        echo "  [tech_node]: technology node (T28 or T180, default: $TECH_NODE)"
    else
        echo "  [tech_node]: technology node (T28 or T180, required if TECH_NODE not set)"
    endif
    echo "  [runDir]:    run directory (optional)"
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
    set calibreRuleFile = "$CALIBRE_RULE_FILE_180"
    if ( ! -f "$calibreRuleFile" ) then
        echo "Error: PEX rule file not found: $calibreRuleFile"
        echo "Please ensure the file exists or update CALIBRE_RULE_FILE_180 in env_common.csh"
        exit 1
    endif
else if ( "$tech_node" =~ T28* || "$tech_node" =~ 28* ) then
    if ( $?PDK_LAYERMAP_28 ) then
        set layerMapFile = "$PDK_LAYERMAP_28"
    else
        echo "Error: PDK_LAYERMAP_28 is not set. Please set it in env_common.csh"
        exit 1
    endif
    set calibreRuleFile = "$CALIBRE_RULE_FILE_28"
    if ( ! -f "$calibreRuleFile" ) then
        echo "Error: PEX rule file not found: $calibreRuleFile"
        echo "Please ensure the file exists or update CALIBRE_RULE_FILE_28 in env_common.csh"
        exit 1
    endif
else
    echo "Error: Unsupported technology node '$tech_node'. Supported: T28, T180."
    exit 1
endif

echo "[run_pex] TECH_NODE='$tech_node' -> using rule file: $calibreRuleFile"

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

# Set run directory (use provided directory or default)
if ( $#argv == 5 ) then
    # If absolute path provided, use it; otherwise make it relative to project root
    if ( `echo $argv[5] | cut -c1` == "/" ) then
        set runDir = "$argv[5]"
    else
        set runDir = "$PROJECT_ROOT/$argv[5]"
    endif
else
    if ( $?PEX_RUN_DIR ) then
        set runDir = "$PEX_RUN_DIR"
    else
        set runDir = "${PROJECT_ROOT}/output/pex"
    endif
endif

set logFile = "PIPO.LOG.${topCell}"
set summaryFile = "PIPO.SUM.${topCell}"
set strmFile = "${topCell}.calibre.db"
set tmpRuleFile = "_calibre.rcx_tmp_${topCell}_"

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

# Create temporary rule file by replacing placeholders
echo "Creating temporary rule file: $runDir/$tmpRuleFile"
if ( ! -f "$calibreRuleFile" ) then
    echo "Error: PEX rule file not found: $calibreRuleFile"
    exit 1
endif
sed -e "s|@LAYOUT_PATH@|${strmFile}|g" \
    -e "s|@LAYOUT_PRIMARY@|${topCell}|g" \
    -e "s|@PEX_NETLIST@|${topCell}.pex.netlist|g" \
    -e "s|@SVDB_DIR@|svdb|g" \
    -e "s|@LVS_REPORT@|${topCell}.lvs.report|g" \
    "$calibreRuleFile" > "$runDir/$tmpRuleFile"

if (! -f "$runDir/$tmpRuleFile") then
    echo "Error: Failed to create temporary rule file"
    exit 1
endif

chmod 644 "$runDir/$tmpRuleFile"

echo "Running strmout..."

# Run XStream Out to generate .db file
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
    echo "Error: XStream Out failed. Check $runDir/$logFile for details."
    exit 1
endif

cd $runDir

pwd

echo "LM_LICENSE_FILE: $LM_LICENSE_FILE"

# Run Calibre PEX
$MGC_HOME/bin/calibre -xrc -phdb -turbo -nowait $tmpRuleFile
if ($status != 0) then
    echo "Error: Calibre PEX failed."
    exit 1
endif

# PEX DB processing
$MGC_HOME/bin/calibre -xrc -pdb -rcc -turbo -nowait $tmpRuleFile

# Check if Calibre PEX DB processing was successful
if ($status != 0) then
    echo "Error: Calibre PEX database processing failed."
    exit 1
endif

# Generate formatted results
$MGC_HOME/bin/calibre -xrc -fmt -all -nowait $tmpRuleFile

# Check if Calibre PEX formatting was successful
if ($status != 0) then
    echo "Error: Calibre PEX formatting failed."
    exit 1
endif

pwd

echo "Calibre flow completed successfully."

# Launch RVE to view PEX results
# $MGC_HOME/bin/calibre -nowait -rve -pex svdb $topCell

