#!/bin/csh -f
# AMS-IO-Agent 自动化配置脚本 (csh版本)
# Auto Setup Script for AMS-IO-Agent (csh)
# 作者: AMS-IO-Agent Team
# 版本: 2.0.0 - 模块化版本

# 设置错误时退出
set exit_on_error

# 日志函数
alias print_info 'echo "[INFO]" \!*'
alias print_success 'echo "[SUCCESS]" \!*'
alias print_error 'echo "[ERROR]" \!*'

# 获取项目根目录（脚本在 setup/ 子目录中）
set CURPWD = `pwd`
set SCRIPT_DIR = `dirname $0`

# 获取脚本所在目录的绝对路径
if ("$SCRIPT_DIR" == ".") then
    set SCRIPT_ABS = "$CURPWD"
else
    cd $SCRIPT_DIR
    set SCRIPT_ABS = "`pwd`"
    cd $CURPWD
endif

# 项目根目录是脚本目录的上一级（因为脚本在 setup/ 中）
cd "$SCRIPT_ABS/.."
set PROJECT_ROOT = "`pwd`"
cd $CURPWD

main:
    echo ""
    echo "================================="
    echo "  AMS-IO-Agent Auto Setup Script"
    echo "  See /setup/README.md for more details"
    echo "  v2.0.0"
    echo "================================="
    echo ""
    
    cd "$PROJECT_ROOT"    
    goto check_requirements

check_requirements:
    if (`uname -s` != "Linux") then
        print_error "仅支持 Linux 系统，当前系统: `uname -s`"
        exit 1
    endif
    
    if (`which git` == "") then
        print_error "未检测到 Git，请先安装"
        exit 1
    endif
    
    print_success "系统检查 [✓ Linux] [✓ Git]"
    goto install_uv

install_uv:
    if (`which uv` != "") then
        print_info "[uv] 已安装"
        goto create_venv
    endif
    
    print_info "[uv] 正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    setenv PATH "$HOME/.cargo/bin:$PATH"
    echo 'setenv PATH "$HOME/.cargo/bin:$PATH"' >> ~/.cshrc
    print_success "[uv] 安装完成"
    goto create_venv

create_venv:
    if (-d ".venv") then
        print_info "[venv] 已存在"
        goto install_dependencies
    endif
    
    print_info "[venv] 创建 Python 3.11..."
    uv venv --python 3.11.11 .venv
    print_success "[venv] 创建完成"
    goto install_dependencies

install_dependencies:
    if (! -f ".venv/bin/activate.csh") then
        print_error "[venv] 激活脚本不存在"
        exit 1
    endif
    
    source .venv/bin/activate.csh
    
    if (! -f "requirements.txt") then
        print_error "[依赖] requirements.txt 未找到"
        exit 1
    endif
    
    print_info "[依赖] 安装 Python 包..."
    uv pip install -r requirements.txt
    print_success "[依赖] 安装完成"
    goto setup_utf8_env

setup_utf8_env:
    echo ""
    print_info "[UTF-8] 配置编码环境变量..."
    
    # 检查 ~/.cshrc 是否已包含 UTF-8 配置
    set utf8_marker = "# AMS-IO-Agent UTF-8 Encoding Setup"
    if (`grep -c "$utf8_marker" ~/.cshrc` == 0) then
        # 追加到 ~/.cshrc
        echo "" >> ~/.cshrc
        echo "$utf8_marker" >> ~/.cshrc
        echo "setenv PYTHONIOENCODING utf-8" >> ~/.cshrc
        echo "setenv LC_ALL en_US.UTF-8" >> ~/.cshrc
        echo "setenv LANG en_US.UTF-8" >> ~/.cshrc
        print_success "[UTF-8] 已添加到 ~/.cshrc，所有新 csh 会话将自动启用"
    else
        print_info "[UTF-8] 配置已存在，跳过"
    endif
    
    # 在当前会话中立即生效
    setenv PYTHONIOENCODING utf-8
    setenv LC_ALL en_US.UTF-8
    setenv LANG en_US.UTF-8
    print_success "[UTF-8] 当前会话已启用"
    goto generate_env_config

generate_env_config:
    echo ""
    print_info "[1/2] 生成 .env 配置..."
    $PROJECT_ROOT/setup/generate_env_config.csh
    goto generate_virtuoso_setup

generate_virtuoso_setup:
    echo ""
    print_info "[2/2] 生成 virtuoso_setup.il..."
    
    # Bridge 类型选择（默认: RAMIC Bridge 跨服务器推荐，修改为 2 使用 skillbridge 同服务器）
    set bridge_choice = "1"
    
    if ("$bridge_choice" == "1") then
        $PROJECT_ROOT/setup/generate_virtuoso_ramicbridge.csh
    else
        $PROJECT_ROOT/setup/generate_virtuoso_skillbridge.csh
    endif
    
    goto show_completion_info

show_completion_info:
    print_success "配置完成 [✓ venv] [✓ 依赖] [✓ UTF-8] [✓ .env] [✓ virtuoso_setup.il]"
    echo ""
    echo "[后续] 1) [.env] 填入配置  2) 查看virtuoso_setup.il  3) source .venv/bin/activate.csh"
    echo "[UTF-8] 已添加到 ~/.cshrc，所有新 csh 会话将自动启用 UTF-8 编码"
    echo ""
    exit 0

goto main