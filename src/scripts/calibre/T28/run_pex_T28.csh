#!/bin/csh -f

# Usage: ./run_pex.csh <library> <topCell> [view]
# Example:
#   ./run_pex.csh LLM_Layout_Design test_PEX
#   ./run_pex.csh LLM_Layout_Design test_PEX layout

# Initialize environment
source /home/cshrc/.cshrc.cadence.IC618SP201
source /home/cshrc/.cshrc.mentor

# Determine script directory and project root (make paths relative)
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
# Script is at: src/scripts/calibre/T28/run_pex_T28.csh
# So we need to go up 4 levels: T28 -> calibre -> scripts -> src -> project root
set PROJECT_ROOT = "$SCRIPT_DIR"
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # T28 -> calibre
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"   # calibre -> scripts
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # scripts -> src
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # src -> project root

# Check input arguments
if ( $#argv < 2 || $#argv > 4 ) then
    echo "Usage: $0 <library> <topCell> [view] [runDir]"
    echo "Default view: layout"
    echo "Default runDir: $PROJECT_ROOT/output/pex"
    exit 1
endif

# Assign input arguments to variables
set library = $argv[1]
set topCell = $argv[2]
if ($#argv >= 3) then
    set view = $argv[3]
else
    set view = "layout"
endif

# Define run directory (use provided directory or default)
if ($#argv == 4) then
    # If absolute path provided, use it; otherwise make it relative to project root
    if ( `echo $argv[4] | cut -c1` == "/" ) then
        set runDir = "$argv[4]"
    else
        set runDir = "$PROJECT_ROOT/$argv[4]"
    endif
else
    set runDir = "$PROJECT_ROOT/output/pex"
endif
set layerMapFile = "/home/process/tsmc28n/PDK_mmWave/iPDK_CRN28HPC+ULL_v1.8_2p2a_20190531/tsmcN28/tsmcN28.layermap"
set logFile = "PIPO.LOG.${topCell}"
set summaryFile = "PIPO.SUM.${topCell}"
set strmFile = "${topCell}.calibre.db"
set calibreRuleFile = "$PROJECT_ROOT/src/scripts/calibre/T28/_calibre_T28.rcx_"
# Determine cds.lib location: strictly require CDS_LIB_PATH in project .env (no defaults, no env fallback)
if (-f "$PROJECT_ROOT/.env") then
    set cds_from_env = `grep -E "^CDS_LIB_PATH=" $PROJECT_ROOT/.env | sed -e 's/^CDS_LIB_PATH=//'`
    if ("$cds_from_env" != "") then
        set cdsLibPath = "$cds_from_env"
    else
        echo "Error: CDS_LIB_PATH not set in $PROJECT_ROOT/.env"
        echo "Please add a line like: CDS_LIB_PATH=/absolute/path/to/cds.lib"
        exit 1
    endif
else
    echo "Error: $PROJECT_ROOT/.env not found. Please create it and set CDS_LIB_PATH=/absolute/path/to/cds.lib"
    exit 1
endif

# Fail fast if cds.lib does not exist at the configured path
if (! -f "$cdsLibPath") then
    echo "Error: cds.lib not found at $cdsLibPath"
    echo "Please ensure the file exists, or update CDS_LIB_PATH in $PROJECT_ROOT/.env"
    exit 1
endif

# 定义临时规则文件名
set tmpRuleFile = "_calibre.rcx_tmp_${topCell}_"

# Set environment variables
setenv MGC_HOME /home/mentor/calibre/calibre2022/aoj_cal_2022.1_36.16
# setenv LM_LICENSE_FILE 1717@lic_server2:5280@thu-han

# Create run directory if it does not exist
if (! -d $runDir) then
    mkdir -p $runDir
endif

# Verify the configured cds.lib exists and is readable
if (! -f "$cdsLibPath") then
    echo "Error: cds.lib not found at $cdsLibPath"
    echo "Please ensure the file exists, or update CDS_LIB_PATH in $PROJECT_ROOT/.env"
    exit 1
endif
if (! -r "$cdsLibPath") then
    echo "Error: cds.lib at $cdsLibPath is not readable"
    exit 1
endif

# 生成临时规则文件，替换变量
sed -e "s|@LAYOUT_PATH@|${strmFile}|g" \
    -e "s|@LAYOUT_PRIMARY@|${topCell}|g" \
    -e "s|@PEX_NETLIST@|${topCell}.pex.netlist|g" \
    -e "s|@SVDB_DIR@|svdb|g" \
    -e "s|@LVS_REPORT@|${topCell}.lvs.report|g" \
    $calibreRuleFile > $runDir/$tmpRuleFile

# 检查临时规则文件是否生成成功
if (! -f $runDir/$tmpRuleFile) then
    echo "Error: Failed to create temporary rule file"
    exit 1
endif

# 后续calibre命令全部用$runDir/$tmpRuleFile

# Run XStream Out to generate .db file
strmout -library $library \
    -strmFile $strmFile \
    -topCell $topCell \
    -view $view \
    -layerMap $layerMapFile \
    -logFile $logFile \
    -summaryFile $summaryFile \
    -runDir $runDir

# Check if XStream Out was successful
if ($status != 0) then
    echo "Error: XStream Out failed. Check $logFile for details."
    exit 1
endif

# Change to run directory
cd $runDir

pwd

echo "LM_LICENSE_FILE: $LM_LICENSE_FILE"

# Run Calibre PEX
$MGC_HOME/bin/calibre -xrc -phdb -turbo -nowait $tmpRuleFile

# Check if Calibre PEX was successful
if ($status != 0) then
    echo "Error: Calibre PEX failed."
    exit 1
endif

# Run Calibre PEX database processing
$MGC_HOME/bin/calibre -xrc -pdb -rcc -turbo -nowait $tmpRuleFile

# Check if Calibre PEX database processing was successful
if ($status != 0) then
    echo "Error: Calibre PEX database processing failed."
    exit 1
endif

# Generate formatted PEX results
$MGC_HOME/bin/calibre -xrc -fmt -all -nowait $tmpRuleFile

# Check if formatted results generation was successful
if ($status != 0) then
    echo "Error: Calibre PEX formatting failed."
    exit 1
endif

pwd

# Run Calibre Review
#$MGC_HOME/bin/calibre -nowait -rve -pex svdb $topCell

# Check if Calibre Review was successful
#if ($status != 0) then
#    echo "Error: Calibre Review failed."
#    exit 1
#endif

echo "Calibre flow completed successfully."