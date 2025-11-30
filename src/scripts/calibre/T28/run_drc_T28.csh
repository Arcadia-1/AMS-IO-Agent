#!/bin/csh -f

# Initialize environment
source /home/cshrc/.cshrc.cadence.IC618SP201
source /home/cshrc/.cshrc.mentor

# Usage: ./run_drc.csh <library> <topCell> [view]
#   - <library>:   Cadence library name
#   - <topCell>:   cell name to export and run DRC on
#   - [view]:      view name for strmout (default: layout)
# Example:
#   ./run_drc.csh LLM_Layout_Design test_DRC
#   ./run_drc.csh LLM_Layout_Design test_DRC layout
#   ./run_drc.csh LLM_Layout_Design test_DRC myLayoutView

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
# Script is at: src/scripts/calibre/T28/run_drc_T28.csh
# So we need to go up 4 levels: T28 -> calibre -> scripts -> src -> project root
set PROJECT_ROOT = "$SCRIPT_DIR"
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # T28 -> calibre
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"   # calibre -> scripts
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # scripts -> src
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # src -> project root

# Define other variables
set runDir = "$PROJECT_ROOT/output/drc"
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
set drcRuleFile = "$PROJECT_ROOT/src/scripts/calibre/T28/_drc_rule_T28_cell_"
set tmpRuleFile = "_drc_rule_T28_cell_tmp"

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
    -e "s|@RESULTS_DB|${topCell}.drc.results|g" \
    -e "s|@SUMMARY_REPORT|${topCell}.drc.summary|g" \
    $drcRuleFile > $runDir/$tmpRuleFile

# Check if temporary rule file was created successfully
if (! -f $runDir/$tmpRuleFile) then
    echo "Error: Failed to create temporary rule file"
    exit 1
endif

# Make sure the temporary rule file is readable
chmod 644 $runDir/$tmpRuleFile

echo "Contents of temporary rule file:"
cat $runDir/$tmpRuleFile

# (cds.lib is provided via the configured CDS_LIB_PATH and linked above)
echo "Current directory: `pwd`"
echo "Contents of current directory:"
ls -la
echo "Contents of cds.lib (from $cdsLibPath):"
cat "$cdsLibPath"
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
    echo "Error: XStream Out failed. Checking log file..."
    if (-f $runDir/$logFile) then
        echo "Contents of $runDir/$logFile:"
        cat $runDir/$logFile
    else
        echo "Log file not found: $runDir/$logFile"
    endif
    exit 1
endif

echo "Strmout completed. Checking generated files:"
ls -la $runDir/

# Change to run directory
cd $runDir

pwd

echo "LM_LICENSE_FILE: $LM_LICENSE_FILE"

# Run Calibre DRC with correct parameter order
$MGC_HOME/bin/calibre -drc -hier -turbo -turbo_litho -hyper -nowait $tmpRuleFile

# Check if Calibre DRC was successful
if ($status != 0) then
    echo "Error: Calibre DRC failed."
    exit 1
endif

echo "Calibre DRC flow completed successfully."

# Launch RVE to view DRC results
# $MGC_HOME/bin/calibre -nowait -rve -drc ${topCell}.drc.results 