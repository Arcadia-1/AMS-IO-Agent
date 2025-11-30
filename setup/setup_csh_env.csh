#!/bin/csh
# -*- coding: utf-8 -*-
#
# UTF-8 环境变量配置脚本
# 
# 使用方法：
#   1. 临时设置（仅当前会话有效）：
#      source setup/setup_csh_env.csh
#
#   2. 永久设置（所有 csh 会话有效）- 推荐：
#      ./setup/setup_csh_env.csh --permanent
#      或者
#      csh setup/setup_csh_env.csh --permanent
#
#   注意：运行 setup/setup.csh 时会自动执行永久配置，无需手动运行此脚本

# 检查是否要永久配置
if ("$1" == "--permanent") then
    set utf8_marker = "# AMS-IO-Agent UTF-8 Encoding Setup"
    if (`grep -c "$utf8_marker" ~/.cshrc` == 0) then
        echo "" >> ~/.cshrc
        echo "$utf8_marker" >> ~/.cshrc
        echo "setenv PYTHONIOENCODING utf-8" >> ~/.cshrc
        echo "setenv LC_ALL en_US.UTF-8" >> ~/.cshrc
        echo "setenv LANG en_US.UTF-8" >> ~/.cshrc
        echo "[SUCCESS] UTF-8 环境变量已添加到 ~/.cshrc"
        echo "         所有新的 csh 会话将自动启用 UTF-8 编码"
        echo ""
        echo "要使当前会话生效，请运行："
        echo "  source ~/.cshrc"
        echo "  或"
        echo "  source setup/setup_csh_env.csh"
    else
        echo "[INFO] UTF-8 配置已存在于 ~/.cshrc，无需重复添加"
    endif
    exit 0
endif

# 临时设置（当前会话）
setenv PYTHONIOENCODING utf-8
setenv LC_ALL en_US.UTF-8
setenv LANG en_US.UTF-8

# 显示设置信息
echo "[AMS-IO-Agent] UTF-8 环境变量已配置（当前会话）"
echo "  PYTHONIOENCODING = $PYTHONIOENCODING"
echo "  LC_ALL = $LC_ALL"
echo "  LANG = $LANG"
echo ""
echo "提示：要使所有 csh 会话都生效，请运行："
echo "  ./setup/setup_csh_env.csh --permanent"

