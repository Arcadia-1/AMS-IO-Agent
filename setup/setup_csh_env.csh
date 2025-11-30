#!/bin/csh
# -*- coding: utf-8 -*-
#
# UTF-8 Environment Variables Configuration Script
# 
# Usage:
#   1. Temporary setup (current session only):
#      source setup/setup_csh_env.csh
#
#   2. Permanent setup (all csh sessions) - Recommended:
#      ./setup/setup_csh_env.csh --permanent
#      or
#      csh setup/setup_csh_env.csh --permanent
#
#   Note: Running setup/setup.csh will automatically perform permanent configuration, no need to run this script manually

# Check if permanent configuration is requested
if ("$1" == "--permanent") then
    set utf8_marker = "# AMS-IO-Agent UTF-8 Encoding Setup"
    if (`grep -c "$utf8_marker" ~/.cshrc` == 0) then
        echo "" >> ~/.cshrc
        echo "$utf8_marker" >> ~/.cshrc
        echo "setenv PYTHONIOENCODING utf-8" >> ~/.cshrc
        echo "setenv LC_ALL en_US.UTF-8" >> ~/.cshrc
        echo "setenv LANG en_US.UTF-8" >> ~/.cshrc
        echo "[SUCCESS] UTF-8 environment variables added to ~/.cshrc"
        echo "         All new csh sessions will automatically enable UTF-8 encoding"
        echo ""
        echo "To apply to current session, run:"
        echo "  source ~/.cshrc"
        echo "  or"
        echo "  source setup/setup_csh_env.csh"
    else
        echo "[INFO] UTF-8 configuration already exists in ~/.cshrc, no need to add again"
    endif
    exit 0
endif

# Temporary setup (current session)
setenv PYTHONIOENCODING utf-8
setenv LC_ALL en_US.UTF-8
setenv LANG en_US.UTF-8

# Display setup information
echo "[AMS-IO-Agent] UTF-8 environment variables configured (current session)"
echo "  PYTHONIOENCODING = $PYTHONIOENCODING"
echo "  LC_ALL = $LC_ALL"
echo "  LANG = $LANG"
echo ""
echo "Tip: To apply to all csh sessions, run:"
echo "  ./setup/setup_csh_env.csh --permanent"

