#!/bin/csh -f

# Usage: ./run_pex_180.csh <library> <topCell> [view]
# Example:
#   ./run_pex_180.csh LLM_Layout_Design_180 test_PEX_180
#   ./run_pex_180.csh LLM_Layout_Design_180 test_PEX_180 layout

# 初始化环境
source /home/cshrc/.cshrc.cadence.IC618SP201
source /home/cshrc/.cshrc.mentor

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

# Set work directory (hardcoded)
set workDir = "/home/lixintian/TSMC180/SAR_ADC/ZJU_Graduation"
echo "Using work directory: $workDir"
cd $workDir
if ($status != 0) then
    echo "Error: Cannot change to directory $workDir"
    exit 1
endif

# Define other variables for 180nm process
set runDir = "$PROJECT_ROOT/output/pex_180"
set layerMapFile = "/home/process/tsmc180bcd_gen2_2022/PDK/TSMC180BCD/tsmc18/tsmc18.layermap"
set logFile = "PIPO.LOG.${topCell}"
set summaryFile = "PIPO.SUM.${topCell}"
set strmFile = "${topCell}.calibre.db"
set calibreRuleFile = "$PROJECT_ROOT/src/scripts/calibre/T180/_calibre_T180.rcx_"

# 定义临时规则文件名
set tmpRuleFile = "_calibre_180.rcx_tmp_"

# Set environment variables
setenv MGC_HOME /home/mentor/calibre/calibre2022/aoj_cal_2022.1_36.16
# setenv LM_LICENSE_FILE 1717@lic_server2:5280@thu-han

# Create run directory if it does not exist
if (! -d $runDir) then
    mkdir -p $runDir
endif

# For automation: require CDS_LIB_PATH_180 in project .env and create symlink
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
# Script is at: src/scripts/calibre/T180/run_pex_T180.csh
# So we need to go up 4 levels: T180 -> calibre -> scripts -> src -> project root
set PROJECT_ROOT = "$SCRIPT_DIR"
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # T180 -> calibre
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"   # calibre -> scripts
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # scripts -> src
set PROJECT_ROOT = "`dirname $PROJECT_ROOT`"  # src -> project root
if (-f "$PROJECT_ROOT/.env") then
    set cds_from_env = `grep -E "^CDS_LIB_PATH_180=" $PROJECT_ROOT/.env | sed -e 's/^CDS_LIB_PATH_180=//'`
    if ("$cds_from_env" != "") then
        set cdsLibPath = "$cds_from_env"
    else
        echo "Error: CDS_LIB_PATH_180 not set in $PROJECT_ROOT/.env"
        echo "Please add: CDS_LIB_PATH_180=/absolute/path/to/cds.lib"
        exit 1
    endif
else
    echo "Error: $PROJECT_ROOT/.env not found. Please create it and set CDS_LIB_PATH_180=/absolute/path/to/cds.lib"
    exit 1
endif
if (! -f "$cdsLibPath") then
    echo "Error: cds.lib not found at $cdsLibPath"
    exit 1
endif
if (! -r "$cdsLibPath") then
    echo "Error: cds.lib at $cdsLibPath is not readable"
    exit 1
endif
echo "Using cds.lib from: $cdsLibPath"

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
# Note: Calibre may return non-zero status even when netlist is generated successfully
# So we check if the netlist file was actually created
if (! -f "${topCell}.pex.netlist") then
    echo "Error: Calibre PEX formatting failed - netlist file not found."
    exit 1
else
    echo "PEX netlist file generated successfully: ${topCell}.pex.netlist"
endif

pwd

# Run Calibre Review
#$MGC_HOME/bin/calibre -nowait -rve -pex svdb $topCell

# Check if Calibre Review was successful
#if ($status != 0) then
#    echo "Error: Calibre Review failed."
#    exit 1
#endif

echo "Calibre PEX flow for 180nm process completed successfully."