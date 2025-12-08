#!/bin/csh
# Shared environment variables for AMS-IO-Agent Calibre scripts
# Add real absolute paths for your environment where noted.

# Determine script directory and project root
set SCRIPT_DIR = `dirname "$0"`
if ( "$SCRIPT_DIR" == "." ) then
    set SCRIPT_DIR = "$cwd"
else
    set SCRIPT_DIR = `cd "$SCRIPT_DIR"; pwd`
endif

# Project root: go up from calibre directory
# Script is at: src/scripts/calibre/env_common.csh
# So we need to go up 3 levels: calibre -> scripts -> src -> project root
set PROJECT_ROOT = "$SCRIPT_DIR"
set PROJECT_ROOT = `dirname "$PROJECT_ROOT"`  # calibre -> scripts
set PROJECT_ROOT = `dirname "$PROJECT_ROOT"`  # scripts -> src
set PROJECT_ROOT = `dirname "$PROJECT_ROOT"`  # src -> project root

# === Calibre / PDK / run dirs - update these paths to your site defaults ===
# Layer map for strmout / XStream
# T28 layer map
setenv PDK_LAYERMAP_28 /home/process/tsmc28n/PDK_mmWave/iPDK_CRN28HPC+ULL_v1.8_2p2a_20190531/tsmcN28/tsmcN28.layermap
# T180 layer map
setenv PDK_LAYERMAP_180 /home/process/tsmc180bcd_gen2_2022/PDK/TSMC180BCD/tsmc18/tsmc18.layermap

# Setup Calibre environment
setenv MGC_HOME /home/mentor/calibre/calibre2022/aoj_cal_2022.1_36.16

# Include files for LVS (28nm / 180nm)
setenv incFILE_28 /home/process/tsmc28n/PDK_mmWave/iPDK_CRN28HPC+ULL_v1.8_2p2a_20190531/tsmcN28/../Calibre/lvs/source.added
setenv incFILE_180 /home/dmanager/shared_lib/TSMC180MS/calibre_rule/lvs/source.added

# Path to cds.lib used by strmout/si (technology node specific)
# The scripts will check in this order:
#   1. CDS_LIB_PATH_28 or CDS_LIB_PATH_180 (based on tech_node)
#   2. CDS_LIB_PATH (fallback for both nodes)
#   3. CDS_LIB_PATH_28/CDS_LIB_PATH_180 in $PROJECT_ROOT/.env file
#   4. CDS_LIB_PATH in $PROJECT_ROOT/.env file
#   5. Error if none found
#
# Technology node specific paths (recommended):
#setenv CDS_LIB_PATH_28 /path/to/your/T28/cds.lib
#setenv CDS_LIB_PATH_180 /path/to/your/T180/cds.lib
#
# Or set in project .env file:
# CDS_LIB_PATH_28=/absolute/path/to/T28/cds.lib
# CDS_LIB_PATH_180=/absolute/path/to/T180/cds.lib
#
# Fallback (if same cds.lib for both nodes):
#setenv CDS_LIB_PATH /path/to/your/cds.lib

# Calibre rule files (28nm / 180nm) - relative to calibre directory
setenv CALIBRE_RULE_FILE_28 ${SCRIPT_DIR}/T28/_calibre_T28.rcx_
setenv CALIBRE_RULE_FILE_180 ${SCRIPT_DIR}/T180/_calibre_T180.rcx_

# LVS rule files (28nm / 180nm)
setenv LVS_RULE_FILE_28 ${SCRIPT_DIR}/T28/_calibre_T28.lvs_
setenv LVS_RULE_FILE_180 ${SCRIPT_DIR}/T180/_calibre_T180.lvs_

# DRC rule files (28nm / 180nm)
setenv DRC_RULE_FILE_28 ${SCRIPT_DIR}/T28/_drc_rule_T28_cell_
setenv DRC_RULE_FILE_180 ${SCRIPT_DIR}/T180/_drc_rule_T180_cell_

# Run directories (relative to project root)
setenv PEX_RUN_DIR ${PROJECT_ROOT}/output/pex
setenv DRC_RUN_DIR ${PROJECT_ROOT}/output/drc
setenv LVS_RUN_DIR ${PROJECT_ROOT}/output/lvs

# End of env_common.csh

