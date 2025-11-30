#!/bin/csh -f

# Initialize environment
source /home/cshrc/.cshrc.cadence.IC618SP201
source /home/cshrc/.cshrc.mentor

# Usage: ./run_lvs.csh <library> <topCell> [view]
#   - <library>:   Cadence library name
#   - <topCell>:   cell name to export and run LVS on
#   - [view]:      view name for strmout (default: layout)
# Example:
#   ./run_lvs.csh LLM_Layout_Design test_v2
#   ./run_lvs.csh LLM_Layout_Design test_v2 layout

# Check input arguments
if ( $#argv < 2 || $#argv > 3 ) then
    echo "Usage: $0 <library> <topCell> [view]"
    echo "Default view: layout"
    exit 1
endif

# Assign input arguments to variables
set library = $argv[1]
set topCell = $argv[2]
if ($#argv == 3) then
    set view = $argv[3]
else
    set view = "layout"
endif

# Determine script/project root
set CURPWD = `pwd`
set SCRIPT_DIR = `dirname $0`
if ("$SCRIPT_DIR" == ".") then
    set SCRIPT_DIR = "$CURPWD"
else
    cd $SCRIPT_DIR
    set SCRIPT_DIR = "`pwd`"
    cd $CURPWD
endif

# Project root: go up from script directory until we find .env file
# Script is at: src/scripts/calibre/T28/run_lvs_T28.csh
# So we need to go up 4 levels: T28 -> calibre -> scripts -> src -> project root
set PROJECT_ROOT = "$SCRIPT_DIR"
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # T28 -> calibre
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"   # calibre -> scripts
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # scripts -> src
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # src -> project root

# Define other variables
set runDir = "$PROJECT_ROOT/output/lvs"
set layerMapFile = "/home/process/tsmc28n/PDK_mmWave/iPDK_CRN28HPC+ULL_v1.8_2p2a_20190531/tsmcN28/tsmcN28.layermap"
set logFile = "PIPO.LOG.${topCell}"
set summaryFile = "PIPO.SUM.${topCell}"
set strmFile = "${topCell}.calibre.db"
/* Determine cdsLibPath strictly from project .env */
if (-f "$PROJECT_ROOT/.env") then
    set cds_from_env = `grep -E "^CDS_LIB_PATH=" $PROJECT_ROOT/.env | sed -e 's/^CDS_LIB_PATH=//'`
    if ("$cds_from_env" != "") then
        set cdsLibPath = "$cds_from_env"
    else
        echo "Error: CDS_LIB_PATH not set in $PROJECT_ROOT/.env"
        echo "Please add: CDS_LIB_PATH=/absolute/path/to/cds.lib"
        exit 1
    endif
else
    echo "Error: $PROJECT_ROOT/.env not found. Please create it and set CDS_LIB_PATH=/absolute/path/to/cds.lib"
    exit 1
endif
set lvsRuleFile = "$PROJECT_ROOT/src/scripts/calibre/T28/_calibre_T28.lvs_"
set tmpRuleFile = "_calibre.lvs_tmp"
set netlistFile = "${topCell}.src.net"
set siEnvTemplate = "$PROJECT_ROOT/src/scripts/calibre/T28/si.env"
set siEnvFile = "si.env"

# Set environment variables
setenv MGC_HOME /home/mentor/calibre/calibre2022/aoj_cal_2022.1_36.16
# setenv LM_LICENSE_FILE 1717@lic_server2:5280@thu-han

# Create run directory if it does not exist
if (! -d $runDir) then
    mkdir -p $runDir
    chmod 755 $runDir
endif

# Verify the configured cds.lib exists and is readable
if (! -f "$cdsLibPath") then
    echo "Error: Configured cds.lib not found: $cdsLibPath"
    echo "Please ensure CDS_LIB_PATH in $PROJECT_ROOT/.env points to a valid cds.lib"
    exit 1
endif
if (! -r "$cdsLibPath") then
    echo "Error: Configured cds.lib is not readable: $cdsLibPath"
    exit 1
endif

# Create temporary rule file with replaced variables
echo "Creating temporary rule file: $runDir/$tmpRuleFile"
sed -e "s|@LAYOUT_PATH|${strmFile}|g" \
    -e "s|@LAYOUT_PRIMARY|${topCell}|g" \
    -e "s|@NETLIST_PATH|${netlistFile}|g" \
    -e "s|@NETLIST_PRIMARY|${topCell}|g" \
    -e "s|@RESULTS_DB|${topCell}.lvs.results|g" \
    -e "s|@SUMMARY_REPORT|${topCell}.lvs.summary|g" \
    $lvsRuleFile > $runDir/$tmpRuleFile

# Check if temporary rule file was created successfully
if (! -f $runDir/$tmpRuleFile) then
    echo "Error: Failed to create temporary rule file"
    exit 1
endif

# Make sure the temporary rule file is readable
chmod 644 $runDir/$tmpRuleFile

echo "Contents of temporary rule file:"
cat $runDir/$tmpRuleFile

# Create si.env file with replaced variables
echo "Creating si.env file: $runDir/$siEnvFile"
sed -e "s|test_v2|${topCell}|g" \
    -e "s|LLM_Layout_Design|${library}|g" \
    -e "s|/home/lixintian/TSMC28/TEST/lvs|${runDir}|g" \
    -e "s|test_v2.src.net|${netlistFile}|g" \
    $siEnvTemplate > $runDir/$siEnvFile

# Check if si.env file was created successfully
if (! -f $runDir/$siEnvFile) then
    echo "Error: Failed to create si.env file"
    exit 1
endif

# Make sure the si.env file is readable
chmod 644 $runDir/$siEnvFile

echo "Contents of si.env file:"
cat $runDir/$siEnvFile

# Create a local cds.lib file
echo "Current directory: `pwd`"
echo "Contents of current directory:"
ls -la
echo "Contents of configured cds.lib ($cdsLibPath):"
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
    if (-f $runDir/$logFile) then
        echo "Contents of $runDir/$logFile:"
        cat $runDir/$logFile
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
    -cdslib "$cdsLibPath" \

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

echo "Calibre LVS flow completed successfully."

# Launch RVE to view LVS results
# $MGC_HOME/bin/calibre -nowait -rve -lvs ${topCell}.lvs.results 