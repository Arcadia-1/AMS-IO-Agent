# 中文使用说明

推荐使用方式
- 在本地计算机的 IDE（如 VS Code 或 Cursor）中通过 SSH 连接至 thu-sui 服务器，在该服务器上进行代码维护。
- Virtuoso 应运行在计算服务器上；若需跨服务器访问，可使用 ramic_bridge 工具，详见后续章节。
- 使用 csh （而不是bash等），使用下面介绍的 setup.csh 配置环境。

## 快速上手（基于 csh）
1) 克隆仓库（私有仓库，如果没有权限访问，请找管理员要权限）并进入目录
```csh
git clone https://github.com/Arcadia-1/RAMIC.git
```

2) 进入项目目录
以下步骤假设你在 AMS-IO-Agent 目录（包含 `setup.csh`、`README.md` 等文件）下操作。
```csh
cd RAMIC/AMS-IO-Agent
```

3) 运行自动化配置脚本（此时不应该进入虚拟环境，应该在AMS-IO-Agent文件夹下直接运行）

**快速启动（推荐）：**
```csh
./quick_start.csh
```
这个脚本会自动修复权限并运行完整的设置流程。

**手动设置：**
```csh
./setup/setup.csh
```

**注意：** 如果遇到 "Permission denied" 错误，运行：
```csh
chmod +x quick_start.csh setup/*.csh
./quick_start.csh
```

**脚本执行过程：**
- 自动搭建 Python 开发环境（安装 uv、创建 .venv 虚拟环境、安装 requirements.txt 依赖）
- 调用 generate_env_config.csh 生成 .env 配置文件
- 调用 generate_virtuoso_ramicbridge.csh 或 generate_virtuoso_skillbridge.csh 生成 virtuoso_setup.il 文件
- 全程零交互，一键完成从零到可运行的初始化

**生成的关键文件：**
- **`.env`**：存储项目配置和敏感信息（API密钥、CDS路径等），供程序运行时读取；包含敏感信息，不会上传到 Git；如果路径设置错误，可直接编辑此文件修改；cd到自己的设计文件夹中，用realpath cds.lib 可以快速拿到完整的绝对路径
- **`virtuoso_setup.il`**：自动生成的 SKILL 脚本，包含在 Virtuoso CIW 中加载 Python 桥接（skillbridge 或 RAMIC Bridge）所需的完整命令和绝对路径
- **`.venv/`**：Python 虚拟环境目录，隔离项目依赖

**注意事项：**
- `setup.csh` 生成的所有路径都是绝对路径，按照提示执行可避免路径错误
- 脚本需在**全局环境**（非虚拟环境）中运行

4) 连接Virtuoso

目前有两种方法可以连接virtuoso： ramic bridge和 skillbridge。
 - 推荐使用ramic bridge。它能够跨服务器连接，例如 代码运行在 thu-sui， 而 virtuoso 运行在 thu-tang。
 - 日后如果在thu-sui上面安装了完整的virtuoso，那么可以用skillbridge

#### 方式 A：RAMIC Bridge（推荐）

在 Virtuoso CIW 中执行：

```skill
load("/path/to/AMS-IO-Agent/virtuoso_setup.il")
```

**环境变量设置说明**：

生成的 `virtuoso_setup.il` 已自动包含环境变量设置（使用 `setShellEnvVar()`），无需手动配置。

如果遇到问题，也可以在启动 Virtuoso 前手动设置（可选）：
```csh
# 在启动 Virtuoso 的终端中执行
setenv RB_DAEMON_PATH "/path/to/AMS-IO-Agent/src/tools/ramic_bridge/ramic_bridge_daemon_27.py"
virtuoso &
```

**跨服务器连接**：需要 SSH 端口转发

由于服务器防火墙原因，连接到计算服务器需要使用 ssh 转发
命令行示例：
```csh
ssh -N -L 65432:127.0.0.1:65432 lixintian@thu-wei
```
或
```csh
ssh -N -L 65434:127.0.0.1:65432 zhangz@thu-tang
```
需要在CIW中的RAMIC菜单栏中，点击start开启服务


#### 方式 B：skillbridge

在 Virtuoso CIW 中执行：

```skill
load("/path/to/AMS-IO-Agent/virtuoso_setup.il")
```

**说明**：`virtuoso_setup.il` 会自动加载 skillbridge 服务器并启动 `pyStartServer`。



5) 测试桥接是否配置成功


测试通信
```csh
source .venv/bin/activate.csh（如尚未激活）
python -X utf8 src/tools/ramic_bridge/ramic_bridge.py
```

执行成功，CIW返回多行空行，则说明配置成功。

6) 启动主程序（AI 助手）

在确认桥接可用后，按以下步骤启动主程序（此时务必在虚拟环境中！）：

```csh
# 启动 AI 助手
python src/main.py

AI交互示例：3 pads per side. Single ring layout. Order: counterclockwise through left side, bottom side, right side, top side.Signal names: RSTN SCK SDI SDO D4 D3 D2 D1 VIOL GIOL VIOH GIOH. Among them, digital IO signals need to connect to digital domain voltage domain (VIOL/GIOL/VIOH/GIOH).

# 如需 Web UI
python src/main.py --model-name deepseek --prompt-name structured --webui
```

7) 运行项目内测试和示例

项目包含若干测试文件与示例，可以用来验证功能完整性：

```csh
# 运行单个测试
python tests/test_il_system.py
python tests/test_io_ring_tool.py

python src/main.py --prompt C_PEX_28nm_python_SKILL_en
```

如果测试中出现 Virtuoso 相关失败，请回到第 3、4 步检查 Virtuoso/ramic_bridge 连接与 CIW 中加载的 il 脚本。

---
---

## Virtuoso Bridge 配置（skillbridge 与 RAMIC）

`setup.csh` 会生成 `virtuoso_setup.il`，包含针对选择的桥（skillbridge 或 RAMIC）的说明。下面是两种常见配置的 csh 使用要点。

A) 使用 skillbridge（默认）
- 在主机上安装并能运行 `skillbridge`，获取其路径（脚本会尝试自动探测）。
- 在 Virtuoso CIW 中运行（CIW 内）：
  - load(skillbridge 的 server il 路径)
  - load 项目中的 `scripts/screenshot_complete.il`
  - 在 CIW 中执行 `pyStartServer` 启动 Python server

B) 使用 RAMIC Bridge（基于 socket 的轻量桥）
- 编辑 `.env`：将 `USE_RAMIC_BRIDGE=true`
- 在 csh 中设置 bridge daemon 路径环境变量（示例）：
```csh
setenv RB_DAEMON_PATH "/full/path/to/AMS-IO-Agent/src/tools/ramic_bridge/ramic_bridge_daemon_27.py"
```
- 在 Virtuoso CIW 中加载 `src/tools/ramic_bridge/ramic_bridge.il` 和 `scripts/screenshot_complete.il`
- 启动（或确保）ramic_bridge daemon 在主机上运行并监听 `.env` 中配置的 `RB_HOST` / `RB_PORT`

提示：`setup.csh` 会在 `virtuoso_setup.il` 中写入对应的步骤，你可以打开并按注释在 Virtuoso CIW 中执行。

---

## 启动项目 / 常用命令（csh）

- 激活 venv（如果没在当前会话激活）
```csh
source .venv/bin/activate.csh
```

- 运行 AI 助手（示例）
```csh
python src/main.py --model-name deepseek --prompt-name structured
```

- 使用 web 界面（如支持）
```csh
python src/main.py --model-name deepseek --prompt-name structured --webui
```

---

## 常见问题 & 小贴士

- Q: 虚拟环境创建完成后如何保持激活？
  - A: 在你的交互 shell 中执行：
    ```csh
    source .venv/bin/activate.csh
    ```
    如果你只是使用 `setup.csh` 子进程创建 venv，那么需要手动在父 shell 中激活。

- Q: Virtuoso 无法写入截图或 load 脚本失败
  - A:
    - 检查 `scripts/screenshot.il` 路径是否存在且可读；
    - 确保 `virtuoso_setup.il` 中的路径是绝对路径或与 Virtuoso 的当前工作目录一致；
    - 如果使用 RAMIC Bridge，确保 daemon（`ramic_bridge_daemon_27.py`）已在指定主机 & 端口启动。

- Q: 为什么 `setup.csh` 要求输入 cds.lib 路径？
  - A: 项目需要知道 Cadence CDS 库文件（cds.lib）位置以便 CIW 或脚本引用对应库路径；若不准确可能导致加载库失败。

- Q：为什么git出错？
  - A: 网络问题，多尝试几次，或采用ssh连接。

- Q: 报错 UnicodeEncodeError: 'gbk' codec can't encode character
  - A: 这是编码错误。`setup/setup.csh` 会自动配置 UTF-8 编码环境变量。
    
    如果已经运行过 `setup.csh`，配置会自动添加到 `~/.cshrc`，重新打开终端即可。
    
    如果需要手动配置，可以运行：
    ```csh
    # 永久配置（推荐，添加到 ~/.cshrc）
    ./setup/setup_csh_env.csh --permanent
    source ~/.cshrc
    
    # 或临时设置（仅当前会话）
    source setup/setup_csh_env.csh
    ```
    
    这将设置以下环境变量：
    - `PYTHONIOENCODING=utf-8`
    - `LC_ALL=en_US.UTF-8`
    - `LANG=en_US.UTF-8`
---

## 关键文件（快速参考）
- `setup/setup.csh` — csh 自动化安装与配置脚本
- `setup/setup_csh_env.csh` — UTF-8 编码环境变量配置脚本（通常由 setup.csh 自动调用）
- `setup/generate_env_config.csh` — 生成 .env 配置文件
- `setup/generate_virtuoso_*.csh` — 生成 Virtuoso 桥接配置文件
- `.env` — 运行时环境变量（API keys、USE_RAMIC_BRIDGE 等）
- `virtuoso_setup.il` — 由 `setup.csh` 生成，包含 Virtuoso CIW 加载脚本指令
- `scripts/` — 包含 `screenshot.il`、`screenshot_complete.il` 等 SKILL 脚本
- `src/main.py` — 程序入口
- `src/tools/bridge_utils.py` — Virtuoso bridge 帮助函数（skillbridge / ramic 切换）

---