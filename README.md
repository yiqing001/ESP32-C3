# ESP32-C3 + Air101-LCD 开发项目

## 项目概述

本项目基于 **合宙ESP32C3开发板** 搭配 **Air101-LCD屏幕** 构建，旨在搭建一个可编译运行的模板工程，为后续嵌入式应用开发提供基础框架。

**当前固件功能**：LCD 显示设备信息（名称 / IP / SN）；局域网 HTTP 远程 OTA；mDNS 发现。

### 文档导航

| 章节 | 说明 |
|------|------|
| [新电脑部署指南（Cursor）](#新电脑部署指南cursor) | **换电脑必读**：打包、安装环境、编译烧录 |
| [打包与迁移清单](#打包与迁移清单) | 哪些文件要拷、哪些不要拷 |
| [硬件连接](#硬件连接) | Air101-LCD 接线 |
| [环境搭建详细步骤](#环境搭建详细步骤) | ESP-IDF 安装方式补充说明 |
| [编译与烧录](#编译与烧录) | 命令行与快捷键 |
| [代码编写框架](#代码编写框架) | **开发必读**：目录分层、注释规范、新增功能步骤 |

---

## 新电脑部署指南（Cursor）

> 在**另一台 Windows 电脑**上，用 Cursor 打开本项目并完成编译烧录。按顺序执行，每步完成后再做下一步。

### 0. 你需要准备

| 项目 | 要求 |
|------|------|
| 系统 | Windows 10/11 64 位 |
| 磁盘 | 至少 **10 GB** 空闲（ESP-IDF + 工具链） |
| 网络 | 可访问 GitHub / Espressif 下载源 |
| 软件 | [Cursor](https://cursor.com/)、[Git](https://git-scm.com/)（脚本可自动装） |
| 硬件 | ESP32-C3 开发板 + USB 线；LCD 按 [接线表](#esp32-c3-与-air101-lcd-连接表) 连接 |

**版本锁定**（与 `env.lock.json` 一致，避免环境不一致）：

| 组件 | 版本 |
|------|------|
| ESP-IDF | **v5.3.2** |
| 目标芯片 | **esp32c3** |
| EIM CLI | 0.12.x |
| Cursor 扩展 | `espressif.esp-idf-extension` |

---

### 1. 获取项目文件

**方式 A：打包 zip（推荐，由源电脑生成）**

在**已能编译的电脑**上，于项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package-project.ps1
```

会在项目**上一级目录**生成 `ESP32-C3-src-日期时间.zip`（仅源码与配置，不含 `build`）。

将 zip 拷到新电脑后解压，例如：`D:\work\ESP32-C3\`。

**方式 B：Git 克隆**

```powershell
git clone <你的仓库地址> ESP32-C3
cd ESP32-C3
```

**不要**从旧电脑复制以下内容（体积大且路径绑定本机）：

- `build/`、`.cache/`
- `C:\Espressif\`、`%USERPROFILE%\.espressif\`（工具链在新电脑重新安装）

---

### 2. 安装 Cursor 与扩展

1. 安装并打开 [Cursor](https://cursor.com/)。
2. `文件` → `打开文件夹` → 选择解压后的 `ESP32-C3` 目录。
3. 若提示安装推荐扩展，点击 **安装**（见 `.vscode/extensions.json` 中的 `espressif.esp-idf-extension`）。
4. 或手动：`Ctrl+Shift+X` → 搜索 **ESP-IDF** → 安装 **Espressif Systems** 发布的扩展 → **重新加载窗口**。

---

### 3. 安装 ESP-IDF 工具链（EIM，约 15–30 分钟）

在**管理员或普通** PowerShell 中进入项目目录，执行：

```powershell
cd D:\work\ESP32-C3   # 改成你的实际路径
powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1
```

脚本将自动：

- 安装 Git（若未安装）
- 安装 **EIM CLI**（`winget install Espressif.EIM-CLI`）
- 下载并安装 **ESP-IDF v5.3.2** 与 **esp32c3** 工具链

安装完成后，默认路径为：

| 内容 | 路径 |
|------|------|
| ESP-IDF 源码 | `%USERPROFILE%\.espressif\v5.3.2\esp-idf` |
| 编译工具 | `C:\Espressif\tools` |
| 版本注册表 | `C:\Espressif\tools\eim_idf.json` |

**不用 Cursor 图形界面时**，也可在命令面板用：`ESP-IDF: Open ESP-IDF Installation Manager`。

---

### 4. 在 Cursor 中绑定 ESP-IDF

1. `Ctrl+Shift+P` 打开命令面板。
2. 输入并选择：**`ESP-IDF: Select Current ESP-IDF Version`**。
3. 在列表中选择 **v5.3.2**（或名称类似 `9d7f2d6` / 含 `5.3.2` 的项）。
4. 再执行：**`ESP-IDF: Set Target`** → 选择 **`esp32c3`**。  
   （项目已包含 `sdkconfig` 与 `sdkconfig.defaults`，一般会自动识别。）
5. 可选：执行 **`ESP-IDF: Doctor Command`**，确认无报错。

---

### 5. 配置串口

1. 开发板 USB 插入电脑，在 **设备管理器** 中查看 **COM 口**（如 `COM5`）。
2. 打开项目内 `.vscode/settings.json`，修改：

```json
"idf.portWin": "COM5"
```

（可参考 `.vscode/settings.json.example`。）

---

### 6. 编译、烧录、看日志

**在 Cursor 中（推荐）**

| 操作 | 快捷键 |
|------|--------|
| 编译 | `Ctrl+Alt+B` |
| 烧录 | `Ctrl+Alt+F` |
| 串口监视 | `Ctrl+Alt+M` |

**在终端中**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Port COM5 -Flash
```

或手动激活环境后：

```powershell
. (Get-ChildItem C:\Espressif\tools\Microsoft.*.PowerShell_profile.ps1 | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
cd D:\work\ESP32-C3
idf.py build
idf.py -p COM5 flash monitor
```

**预期现象**：LCD 黑底，横向青色 **MaiQing**，无右侧彩噪。

---

### 7. 部署验收清单

- [ ] `ESP-IDF: Doctor Command` 通过
- [ ] `idf.py build` 无错误，生成 `build/esp32-c3-lcd.bin`
- [ ] `idf.py flash` 成功
- [ ] 屏幕显示横向 **MaiQing**

---

### 8. 新电脑常见问题

| 现象 | 处理 |
|------|------|
| 扩展找不到 ESP-IDF | 先跑 `setup-env.ps1`，再执行 **Select Current ESP-IDF Version** |
| `cmake` / `idf.py` 找不到 | 不要用 `-e` 参数执行激活脚本；用 `scripts\build.ps1` 或扩展内置终端 |
| 编译目标变成 esp32 | `idf.py set-target esp32c3`，删除 `build` 后重新 `build` |
| 字竖排、屏幕半边噪点 | 确认使用仓库内最新 `main/lcd/st7735.c`（`MADCTL` 横向 `0x60`） |
| 烧录失败 | 按住 **BOOT** 再点 **RESET** 进入下载模式后重试 |
| 工具链 `cc1` 缺失 | `eim fix %USERPROFILE%\.espressif\v5.3.2\esp-idf` |

---

## 打包与迁移清单

### 必须包含（已在仓库 / zip 中）

```
ESP32-C3/
├── main/                 # 应用与 ST7735 驱动
├── CMakeLists.txt
├── sdkconfig             # 已锁定 esp32c3
├── sdkconfig.defaults
├── env.lock.json         # 环境版本说明
├── .vscode/
│   ├── extensions.json
│   ├── settings.json.example
│   └── launch.json
├── scripts/
│   ├── setup-env.ps1     # 新电脑装环境
│   ├── package-project.ps1
│   └── build.ps1
└── README.md
```

### 不要打包

| 路径 | 原因 |
|------|------|
| `build/` | 与本机路径、配置绑定，新电脑需重新生成 |
| `.cache/` | IDE 缓存 |
| `C:\Espressif\` | 工具链，在新电脑用 EIM 重装 |
| `%USERPROFILE%\.espressif\` | ESP-IDF 源码，由 EIM 下载 |

---

## 硬件配置

### 核心开发板

| 项目 | 规格 |
|------|------|
| 主控芯片 | 合宙 ESP32-C3 |
| 架构 | RISC-V 32位单核 |
| 主频 | 最高 160 MHz |
| 内存 | 400KB SRAM + 384KB ROM |
| 无线功能 | WiFi 4 (802.11b/g/n) + BLE 5.0 |

### LCD屏幕

| 项目 | 规格 |
|------|------|
| 型号 | Air101-LCD |
| 尺寸 | 0.96 英寸 |
| 分辨率 | 160 x 80 像素 |
| 驱动芯片 | ST7735 |
| 接口 | SPI |
| 颜色 | 全彩 65K色 |

---

## 开发背景

> **⚠️ 重要说明**
>
> 由于官方已下架 Air101-LCD 相关开发资料，本项目所需的驱动代码、硬件连接说明等均通过互联网开源社区收集整理，主要来源包括：
> - GitHub 开源项目
> - 电子论坛技术帖
> - 个人开发者分享
> - ST7735 芯片官方 datasheet

---

## 项目目标

1. **搭建基础开发环境**：配置 ESP-IDF 编译环境，确保项目可正常编译
2. **实现 LCD 驱动**：移植并调试 ST7735 驱动代码，实现屏幕显示功能
3. **提供模板工程**：创建可复用的项目模板，便于后续功能扩展
4. **文档完善**：记录硬件连接方式、编译步骤、使用方法等关键信息

---

## 目录结构

```
.
├── main/                    # 主应用代码
│   ├── app_main.c           # 入口：初始化各模块、主流程
│   ├── lcd/                 # ST7735 驱动与字库
│   ├── ota/                 # WiFi + HTTP OTA + 设备信息
│   ├── Kconfig.projbuild    # menuconfig 可配置项（WiFi 等）
│   └── CMakeLists.txt
├── scripts/                 # 部署与编译脚本
├── tools/ota_console/       # 局域网 OTA 网页控制台
├── components/              # 自定义组件（可扩展）
├── partitions.csv           # OTA 分区表
├── sdkconfig                # 当前工程配置（改 WiFi 等优先改此文件）
├── sdkconfig.defaults       # 新工程默认配置
├── env.lock.json
├── CMakeLists.txt
└── README.md
```

---

## 代码编写框架

> 后续在本项目写代码，按本节分层与注释规范来，保持**精简易懂、可维护**。

### 1. 分层原则

| 层级 | 目录/文件 | 职责 | 不要做的事 |
|------|-----------|------|------------|
| 应用层 | `main/app_main.c` | 启动顺序、模块调用、简单 UI 状态 | 不写 SPI/HTTP 细节 |
| 驱动层 | `main/lcd/` | 屏幕硬件、引脚、时序 | 不依赖 WiFi/OTA |
| 服务层 | `main/ota/` | 联网、HTTP、mDNS、设备信息 | 不操作 LCD 引脚 |
| 配置层 | `Kconfig.projbuild`、`sdkconfig` | SSID、端口、设备名前缀 | 不在代码里硬编码密码 |

**调用方向**：`app_main` → 各模块公开 API；模块之间尽量**不互相调用**，共用数据放 `device_info` 等独立模块。

### 1.1 固件运行逻辑

```
app_main
  ├─ st7735_init / 背光
  ├─ device_info_init          ← MAC → SN、设备名
  ├─ ota_boot_consume_success  ← 仅远程 OTA 后显示 OTA OK
  ├─ wifi_manager_start        ← STA、关省电、写 IP
  ├─ ota_server_start          ← HTTP 页 + POST /api/ota + mDNS
  └─ lcd_show_device_info      ← 常态界面

远程 OTA（浏览器 POST .bin）
  → esp_ota 写入备用分区 ota_0/ota_1
  → ota_boot_mark_remote_ota
  → 重启 → consume_success → 屏幕 OTA OK 10s → 设备信息
```

| 模块 | 文件 | 对外 API |
|------|------|----------|
| LCD | `lcd/st7735.c` | `st7735_init`, `fill_screen`, `draw_string` |
| 设备信息 | `ota/device_info.c` | `device_info_init`, `get`, `set_ip` |
| WiFi | `ota/wifi_manager.c` | `wifi_manager_start` |
| OTA 启动标志 | `ota/ota_boot.c` | `mark_remote_ota`, `consume_success` |
| HTTP OTA | `ota/ota_server.c` | `ota_server_start` |

### 2. 新增功能放哪里

```
要加的功能              → 建议位置
─────────────────────────────────────────
LCD 显示/绘图           → main/lcd/st7735.c，头文件声明 API
WiFi / 网络 / OTA       → main/ota/
新业务（按键、传感器）   → main/xxx/ 新建文件夹 + .h/.c
menuconfig 可配置项     → main/Kconfig.projbuild
注册进编译              → main/CMakeLists.txt 的 SRCS / INCLUDE_DIRS
```

新增 `.c` 文件后，在 `main/CMakeLists.txt` 里补上文件名，否则不会参与编译。

### 3. 注释怎么写（精简）

**原则**：代码本身能看懂的少写；**硬件参数、协议、非 obvious 逻辑**必须写。

| 要写 | 不用写 |
|------|--------|
| 引脚含义、屏幕型号/偏移/MADCTL 取值原因 | `i++` 在循环里干什么 |
| 函数对外作用、参数单位（毫秒/像素） | 每个 `ESP_LOGI` 上方重复一句 |
| 协议字段、状态机切换条件 | 把代码逐行翻译成中文 |

**文件头**（可选，新模块建议写一行）：

```c
/* WiFi 连接管理：STA 模式，连接成功后写入 device_info IP */
```

**函数头**（公开 API 必写，一行即可）：

```c
/** 填充整屏颜色；color 为 RGB565，如 ST7735_COLOR_BLACK */
void st7735_fill_screen(uint16_t color);
```

**行内注释**（只解释「为什么」）：

```c
#define ST7735_COLSTART  26   /* Air101 PLUGIN 屏 colstart，勿加到 X 轴 */
wifi_cfg.sta.threshold.authmode = WIFI_AUTH_WPA_WPA2_PSK;  /* 路由器 WPA/WPA2 混合 */
```

**块注释**（初始化序列、多步流程）：

```c
/* 1. 复位  2. 发 GREENTAB160x80 序列  3. 设横向 MADCTL  4. DISPON */
```

### 4. 命名与风格

| 类型 | 规则 | 示例 |
|------|------|------|
| 源文件 | 小写 + 下划线，与模块名一致 | `wifi_manager.c` |
| 公开函数 | `模块前缀_动词` | `st7735_init()`、`ota_server_start()` |
| 模块内静态 | `s_` 前缀 | `static httpd_handle_t s_server` |
| 宏/引脚 | 大写 | `PIN_LCD_SCK`、`ST7735_LCD_WIDTH` |
| 日志 TAG | 与模块相关、≤16 字符 | `"wifi_mgr"`、`"st7735"` |

缩进 4 空格；花括号与现有 `st7735.c`、`app_main.c` 保持一致。

### 5. 错误与日志

```c
/* 初始化阶段：失败即无法继续 → 用 ESP_ERROR_CHECK */
ESP_ERROR_CHECK(st7735_init());

/* 运行阶段：可重试/可降级 → 判断返回值 + 日志 */
if (wifi_manager_start() != ESP_OK) {
    ESP_LOGE(TAG, "WiFi failed, check sdkconfig OTA_WIFI_*");
    lcd_show_status("WiFi FAIL", "check SSID");
    return;
}
```

| 级别 | 用途 |
|------|------|
| `ESP_LOGI` | 正常流程（连上 WiFi、OTA 成功、IP 地址） |
| `ESP_LOGW` | 可恢复异常（重试、断开 reason） |
| `ESP_LOGE` | 失败且功能不可用 |

### 6. 头文件约定

每个模块一对 `.h` / `.c`：

- **`.h`**：只放对外 `struct`、`#define`、函数声明；加 `#pragma once`
- **`.c`**：实现细节、`static` 函数、硬件寄存器操作

```c
/* st7735.h — 应用层只 include 这个 */
#pragma once
#include "esp_err.h"
esp_err_t st7735_init(void);
void st7735_fill_screen(uint16_t color);
```

### 7. 配置项约定

| 配置 | 改哪里 | 说明 |
|------|--------|------|
| WiFi SSID/密码 | `sdkconfig` 或 `idf.py menuconfig` | **改 defaults 不会覆盖已有 sdkconfig** |
| 设备名前缀、HTTP 端口 | `Remote OTA (WiFi)` | 对应 `CONFIG_OTA_*` |
| 引脚 | 驱动内 `#define PIN_*` | 改线时只改驱动文件并更新 README 接线表 |

代码里用 `CONFIG_OTA_WIFI_SSID` 等宏，**不要**在 `.c` 里写死密码。

### 8. 新增模块检查清单

- [ ] 新建 `main/xxx/xxx.h` + `xxx.c`，头文件写清 API 注释
- [ ] `main/CMakeLists.txt` 加入源文件与 `INCLUDE_DIRS`
- [ ] 在 `app_main.c` 按顺序调用：`init` → `start` → 业务
- [ ] 关键常量、引脚、协议处补充**一行**备注
- [ ] `idf.py build` 通过后再烧录验证

### 9. 示例：app_main 推荐结构

```c
void app_main(void)
{
    /* 1. 硬件与显示 */
    ESP_ERROR_CHECK(st7735_init());
    st7735_backlight(true);
    lcd_show_status("Boot", "...");

    /* 2. 设备信息与网络 */
    device_info_init();
    if (wifi_manager_start() != ESP_OK) { /* 失败处理 */ return; }

    /* 3. 网络服务 */
    ESP_ERROR_CHECK(ota_server_start());

    /* 4. 业务界面 */
    st7735_draw_string(...);

    /* 5. 主循环（如有） */
    while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
```

---

## 硬件连接

### ESP32-C3 与 Air101-LCD 连接表

| Air101-LCD 引脚 | ESP32-C3 引脚 | 功能说明 |
|-----------------|---------------|----------|
| VCC             | 3.3V          | 电源正极 |
| GND             | GND           | 电源负极 |
| SCK             | GPIO2         | SPI时钟 |
| SDA (MOSI)      | GPIO3         | SPI数据 |
| RESET           | GPIO10        | 复位引脚 |
| DC              | GPIO6         | 数据/命令选择 |
| CS              | GPIO7         | 片选引脚 |
| BL              | GPIO11        | 背光控制 |

### 接线示意图

```
ESP32 C3引脚   LCD屏引脚
GPIO2        -> SCK
GPIO3        -> MOSI(SDA)
GPIO10       -> RESET
GPIO6        -> DC(数据/命令选择)
GPIO7        -> CS(片选)
GPIO11       -> BL(背光控制)
3.3V        -> VCC
GND         -> GND
```

> **注意**：具体引脚分配需根据实际硬件设计调整，此为推荐配置。

---

## 开发环境

### 软件依赖

| 软件 | 版本 | 说明 |
|------|------|------|
| ESP-IDF | 5.x | Espressif IoT Development Framework |
| Python | 3.8+ | 构建工具依赖 |
| CMake | 3.16+ | 跨平台构建系统 |
| Ninja | 1.10+ | 快速构建工具 |
| Git | 2.20+ | 版本控制工具 |

---

## 环境搭建详细步骤

### 1. 安装 ESP-IDF（Windows 环境）

#### 方法一：使用 ESP-IDF 安装器（推荐）

1. 下载 ESP-IDF 安装器：[ESP-IDF Tools Installer](https://dl.espressif.com/dl/esp-idf/?idf=5.x)
2. 运行安装器，选择安装路径（建议不要包含中文和空格）
3. 选择安装 ESP-IDF 5.x 版本及相关工具链
4. 等待安装完成（约 10-20 分钟，取决于网络速度）

#### 方法二：手动安装（高级用户）

```powershell
# 克隆 ESP-IDF 仓库
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
git checkout release/v5.1  # 切换到稳定版本

# 安装依赖工具
python -m pip install -r requirements.txt

# 安装工具链（Windows）
./install.bat
```

#### 方法三：使用 Cursor + ESP-IDF 插件（推荐）

Cursor 是一款基于 VS Code 的 AI 辅助编程工具，内置对 ESP-IDF 的良好支持。

##### 步骤 1：安装 Cursor

1. 下载 Cursor：[Cursor 官方网站](https://cursor.sh/)
2. 安装并启动 Cursor
3. 进入 Settings（设置）→ Extension（扩展）

##### 步骤 2：安装 ESP-IDF 插件

1. 在扩展市场搜索 **ESP-IDF**
2. 安装由 Espressif Systems 提供的 **ESP-IDF** 插件
3. 重启 Cursor 使插件生效

##### 步骤 3：配置 ESP-IDF 环境

1. 打开命令面板（Ctrl+Shift+P）
2. 输入 `ESP-IDF: Configure ESP-IDF`
3. 选择 **Express Installation**（快速安装）或 **Advanced Installation**（高级安装）

##### 快速安装模式

```
1. 选择 ESP-IDF 版本（推荐 5.x）
2. 选择安装路径（建议：C:\Users\<用户名>\.espressif\esp-idf）
3. 等待安装完成（自动下载工具链和依赖）
```

##### 高级安装模式（使用已安装的 ESP-IDF）

```
1. 选择 **Use existing ESP-IDF**
2. 浏览并选择已安装的 ESP-IDF 目录
3. 配置工具链路径（自动检测）
```

##### 步骤 4：创建 ESP-IDF 项目

1. 打开命令面板（Ctrl+Shift+P）
2. 输入 `ESP-IDF: New Project`
3. 选择项目模板（如 `hello_world`）
4. 指定项目保存路径
5. 等待项目初始化完成

##### 步骤 5：配置项目目标芯片

1. 打开命令面板（Ctrl+Shift+P）
2. 输入 `ESP-IDF: Set Target`
3. 选择 `esp32c3` 作为目标芯片

##### 步骤 6：编译与烧录

```
快捷键操作：
- Ctrl+Alt+B：编译项目（Build）
- Ctrl+Alt+F：烧录固件（Flash）
- Ctrl+Alt+M：启动串口监控（Monitor）
- Ctrl+Alt+D：调试（Debug）
```

##### Cursor ESP-IDF 插件功能

| 功能 | 说明 |
|------|------|
| 项目模板 | 提供多种官方示例模板 |
| 智能补全 | ESP-IDF API 代码补全 |
| 配置管理 | 可视化 menuconfig 配置 |
| 一键编译 | 快速编译项目 |
| 一键烧录 | 自动识别串口并烧录 |
| 串口监控 | 内置串口终端 |
| 调试支持 | JTAG 调试集成 |

##### 配置文件说明

Cursor ESP-IDF 插件会自动生成以下配置文件：

| 文件 | 说明 |
|------|------|
| `.vscode/settings.json` | 项目配置（IDF路径、目标芯片等） |
| `.vscode/c_cpp_properties.json` | C/C++ 语言配置 |
| `.vscode/launch.json` | 调试配置 |
| `sdkconfig` | ESP-IDF 配置文件 |

##### 常见问题

**问题**：插件无法找到 ESP-IDF 路径

**解决方案**：
```
1. 打开命令面板 → ESP-IDF: Configure ESP-IDF
2. 选择 Advanced Installation
3. 手动指定 ESP-IDF 安装目录
4. 确保工具链已正确安装
```

**问题**：编译时提示缺少 Python 依赖

**解决方案**：
```powershell
# 激活虚拟环境（如果使用）
cd <ESP-IDF路径>
./export.bat

# 安装缺失的依赖
python -m pip install <依赖包名>
```

---

### 2. 配置环境变量

安装完成后，每次打开新的终端都需要执行以下命令来配置环境：

```powershell
# 进入 ESP-IDF 目录
cd C:\esp\esp-idf  # 根据实际安装路径调整

# 执行环境配置脚本
./export.bat
```

> **提示**：可以将上述命令添加到 PowerShell 配置文件中，实现自动配置。

### 3. 验证环境

```powershell
# 验证 idf.py 是否可用
idf.py --version

# 验证工具链
xtensa-esp32c3-elf-gcc --version
```

### 4. 创建项目

```powershell
# 创建新项目
idf.py create-project --path .

# 或从现有模板复制
cp -r $IDF_PATH/examples/get-started/hello_world/* .
```

### 5. 配置目标芯片

```powershell
# 设置目标芯片为 ESP32-C3
idf.py set-target esp32c3

# 查看当前目标配置
idf.py show-target
```

### 6. 配置串口

确保开发板已连接到电脑，然后查看设备管理器中的串口编号（如 COM3）。

---

## 编译与烧录

### 编译命令

```bash
# 清理构建目录（可选）
idf.py fullclean

# 配置项目（可选，使用图形界面）
idf.py menuconfig

# 编译项目
idf.py build
```

### 编译输出说明

| 输出文件 | 路径 | 说明 |
|---------|------|------|
| 固件镜像 | `build/hello-world.bin` | 主应用固件 |
| Bootloader | `build/bootloader/bootloader.bin` | 引导程序 |
| 分区表 | `build/partition_table/partition-table.bin` | Flash 分区表 |
| ELF 文件 | `build/hello-world.elf` | 调试符号文件 |

### 烧录命令

```bash
# 烧录到设备（替换为实际串口）
idf.py -p COM3 flash

# 烧录并启动监控
idf.py -p COM3 flash monitor

# 仅烧录应用固件
idf.py -p COM3 app-flash

# 烧录特定文件
idf.py -p COM3 flash --flash_mode dio --flash_size 4MB
```

### 串口监控

```bash
# 启动串口监控
idf.py -p COM3 monitor

# 监控快捷键
# Ctrl+] 退出监控
# Ctrl+T 打开命令菜单
# Ctrl+R 软复位设备
```

### 常用构建选项

| 选项 | 说明 |
|------|------|
| `-p, --port` | 指定串口端口（如 COM3） |
| `-b, --baud` | 指定串口波特率（默认 115200） |
| `--flash_mode` | Flash 模式：qio, qout, dio, dout |
| `--flash_size` | Flash 大小：2MB, 4MB, 8MB |
| `--flash_freq` | Flash 频率：40m, 80m |

### 构建配置（menuconfig）

使用 `idf.py menuconfig` 可以配置以下关键选项：

| 配置项 | 路径 | 说明 |
|--------|------|------|
| 串口波特率 | Component config → ESP32C3-specific → UART0 default baud rate |
| Flash 配置 | Serial flasher config |
| 分区表 | Partition Table |
| WiFi 配置 | Component config → WiFi |
| 日志级别 | Component config → Log output |

---

## 常见问题与解决方案

### 问题 1：找不到串口设备

**现象**：`idf.py flash` 提示找不到串口

**解决方案**：
1. 检查 USB 连接线是否正常
2. 安装 CH340/CP210x 串口驱动
3. 在设备管理器中确认串口编号
4. 尝试更换 USB 端口

### 问题 2：编译错误 - 缺少工具链

**现象**：`xtensa-esp32c3-elf-gcc` 命令找不到

**解决方案**：
1. 确保已执行 `export.bat`
2. 检查 ESP-IDF 安装是否完整
3. 重新运行安装器修复工具链

### 问题 3：烧录失败 - 设备未进入下载模式

**现象**：`Failed to connect to ESP32-C3`

**解决方案**：
1. 按住 BOOT 按键不放
2. 按下 RESET 按键
3. 松开 RESET 按键
4. 松开 BOOT 按键
5. 重新执行烧录命令

### 问题 4：日志输出乱码

**现象**：串口监控显示乱码

**解决方案**：
1. 确认波特率设置正确（默认 115200）
2. 检查串口监控工具的编码设置
3. 确保使用支持 UTF-8 的终端

### 问题 5：编译错误 - Python 依赖缺失

**现象**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
# 安装缺失的依赖
python -m pip install xxx

# 或重新安装所有依赖
python -m pip install -r $IDF_PATH/requirements.txt
```

---

## 开发工具推荐

| 工具 | 用途 | 说明 |
|------|------|------|
| VS Code | 代码编辑器 | 支持 ESP-IDF 插件 |
| ESP-IDF Explorer | 项目管理 | VS Code 扩展 |
| PuTTY | 串口工具 | Windows 串口监控 |
| ESP Flash Download Tool | 烧录工具 | 官方图形化烧录工具 |

---

## 功能特性

- [ ] ST7735 LCD 驱动初始化
- [ ] 基础图形绘制（点、线、矩形、圆形）
- [ ] 文字显示功能
- [ ] 屏幕清屏与刷新
- [ ] 背光亮度控制

---

## 注意事项

1. **资料缺失**：官方文档已下架，部分硬件细节可能需要自行验证
2. **驱动兼容性**：ST7735 驱动可能需要根据实际屏幕参数微调
3. **电源稳定性**：建议使用 3.3V 稳压电源，避免信号干扰
4. **SPI时序**：确保 SPI 时钟频率与屏幕规格匹配

---

## 参考资料

- ST7735 芯片 datasheet
- ESP-IDF 官方文档
- 合宙 ESP32C3 开发板原理图
- 开源 ST7735 驱动代码仓库

---

## 附录：项目需求与验收标准

### 核心需求

| 需求编号 | 需求描述 |
|---------|---------|
| REQ-01 | 搭建基于合宙ESP32C3的开发环境 |
| REQ-02 | 实现Air101-LCD屏幕（ST7735）驱动 |
| REQ-03 | 创建可复用的模板工程结构 |
| REQ-04 | 文档化硬件连接与编译流程 |

### 验收标准

| 验收项 | 验收条件 |
|--------|---------|
| 编译通过 | `idf.py build` 无错误 |
| 烧录成功 | 固件可正常写入ESP32-C3 |
| LCD显示 | 屏幕可正常显示测试图案 |
| 功能完整 | 支持清屏、绘图、文字、背光控制 |

---

## 原理图拆解

### 功能模块划分

```
┌─────────────────────────────────────────────────────────────┐
│                     ESP32-C3 开发板                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   电源模块      │   主控模块       │   外设接口模块          │
│  (PWR)          │  (MCU)          │   (PERIPHERAL)          │
├─────────────────┼─────────────────┼─────────────────────────┤
│ 3.3V/1.8V稳压  │ ESP32-C3芯片    │ SPI接口 → LCD           │
│ 电源管理        │ 4MB Flash       │ UART → 串口             │
│                │ 400KB SRAM      │ GPIO → 用户按键/LED     │
│                │ RISC-V 160MHz   │ USB-C → 调试/供电       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### 模块参数表

#### 电源模块 (PWR)

| 参数 | 规格 |
|------|------|
| 输入电压 | 4.5V - 5.5V (USB-C) |
| 输出电压 | 3.3V (主电源), 1.8V (内部) |
| 最大电流 | 500mA |

#### 主控模块 (MCU)

| 参数 | 规格 |
|------|------|
| 芯片型号 | ESP32-C3-WROOM-02 |
| CPU | RISC-V 32位单核 @ 160MHz |
| Flash | 4MB (可扩展至 16MB) |
| SRAM | 400KB |

#### LCD接口模块

| 参数 | 规格 |
|------|------|
| 接口类型 | SPI (3线/4线) |
| 时钟频率 | 最高 20MHz |
| 分辨率 | 160 x 80 |
| 颜色深度 | 65K色 (16-bit) |

### 芯片引脚功能分配

#### LCD屏幕连接引脚

| ESP32-C3 引脚 | 功能 | 连接对象 | 复用功能 |
|--------------|------|----------|----------|
| GPIO2 | SCK (SPI时钟) | LCD_SCK | SPI_CLK / U0TXD |
| GPIO3 | MOSI (SPI数据) | LCD_SDA | SPI_MOSI / U0RXD |
| GPIO6 | DC (数据/命令选择) | LCD_DC | SPI_CS0 |
| GPIO7 | CS (片选) | LCD_CS | SPI_HD |
| GPIO10 | RESET (复位) | LCD_RESET | I2C_SDA / ADC2_CH0 |
| GPIO11 | BL (背光控制) | LCD_BL | I2C_SCL / ADC2_CH1 |

#### 板载硬件控制引脚

| ESP32-C3 引脚 | 功能 | 连接对象 | 说明 |
|--------------|------|----------|------|
| GPIO12 | LED控制 | 板载LED | 低电平点亮 |
| GPIO0 | BOOT | 启动按键 | 下拉，按下进入下载模式 |
| GPIO9 | 用户按键 | 按键输入 | 可选外接按键 |

#### 通信接口引脚

| ESP32-C3 引脚 | 功能 | 连接对象 | 复用功能 |
|--------------|------|----------|----------|
| GPIO4 | U0_TXD | 串口输出 | ADC1_CH0 / RTC_GPIO4 |
| GPIO5 | U0_RXD | 串口输入 | ADC1_CH1 / RTC_GPIO5 |
| GPIO13 | U1_TXD | UART1输出 | - |
| GPIO14 | U1_RXD | UART1输入 | - |
| GPIO10 | I2C_SDA | I2C数据 | LCD_RESET / ADC2_CH0 |
| GPIO11 | I2C_SCL | I2C时钟 | LCD_BL / ADC2_CH1 |
| GPIO20 | USB_D+ | USB差分正 | USB-C接口 |
| GPIO21 | USB_D- | USB差分负 | USB-C接口 |

#### SPI扩展引脚

| ESP32-C3 引脚 | 功能 | 复用功能 |
|--------------|------|----------|
| GPIO6 | SPI_CS0 | LCD_DC |
| GPIO7 | SPI_HD | LCD_CS |
| GPIO8 | SPI_WP | - |
| GPIO9 | SPI_CS1 | 用户按键 |

#### ADC模拟输入引脚

| ESP32-C3 引脚 | ADC通道 | 复用功能 |
|--------------|--------|----------|
| GPIO4 | ADC1_CH0 | U0TXD / RTC_GPIO4 |
| GPIO5 | ADC1_CH1 | U0RXD / RTC_GPIO5 |
| GPIO10 | ADC2_CH0 | I2C_SDA / LCD_RESET |
| GPIO11 | ADC2_CH1 | I2C_SCL / LCD_BL |
| GPIO15 | ADC2_CH3 | - |
| GPIO16 | ADC2_CH4 | - |
| GPIO17 | ADC2_CH5 | - |
| GPIO18 | ADC2_CH6 | - |
| GPIO19 | ADC2_CH7 | - |

---

## PCB设计分析

### 层叠结构

| 层 | 功能 |
|----|------|
| Top | 元件面，信号层 |
| GND | 完整地平面 |
| Power | 电源层 (3.3V/1.8V) |
| Bottom | 信号层，部分元件 |

### 阻抗要求

| 信号类型 | 特性阻抗 | 公差 |
|---------|---------|------|
| USB 2.0 | 90Ω | ±10% |
| SPI信号线 | 50Ω | ±10% |
| 差分对 | 100Ω (差分) | ±10% |

### 关键布线规则

| 规则 | 要求 |
|------|------|
| 电源走线 | ≥20mil (电源线)，≥10mil (信号线) |
| 过孔 | 最小0.3mm钻孔，0.6mm焊盘 |
| 线宽间距 | 信号线≥4mil，间距≥4mil |
| 高频信号 | 最短路径，避免锐角弯折 |

### EMC/EMI设计要点

| 设计项 | 措施 |
|--------|------|
| 去耦电容 | 每个电源引脚就近放置0.1μF陶瓷电容 |
| 晶体振荡器 | 靠近芯片放置，接地隔离区 |
| RF天线 | 远离高速数字信号线，预留净空区 |
| USB接口 | 串联RC滤波，ESD保护器件 |
| 电源平面 | 完整覆铜，减少电流环路面积 |

---

## 固件架构

### 启动流程

```
┌────────────────────────────────────────────────────────────────┐
│                        启动流程                               │
├────────────────────────────────────────────────────────────────┤
│  1. 硬件复位 → 2. 芯片内部ROM启动 → 3. Bootloader加载         │
│       ↓                                                       │
│  4. 系统初始化 (时钟/内存/外设) → 5. 用户应用启动              │
│       ↓                                                       │
│  6. app_main() → 7. 驱动初始化 → 8. 主任务循环               │
└────────────────────────────────────────────────────────────────┘
```

### 驱动框架层次

```
┌─────────────────────────────────────────────────────────────┐
│                     固件架构层次                            │
├─────────────────────────────────────────────────────────────┤
│  应用层 (Application Layer)                                │
│  ├── 主任务 (app_main)                                     │
│  ├── 图形库 (Graphics)                                     │
│  └── 用户界面 (UI)                                         │
├─────────────────────────────────────────────────────────────┤
│  驱动层 (Driver Layer)                                     │
│  ├── ST7735 LCD驱动                                        │
│  ├── SPI总线驱动                                           │
│  └── GPIO控制驱动                                          │
├─────────────────────────────────────────────────────────────┤
│  HAL层 (Hardware Abstraction)                              │
│  ├── ESP-IDF HAL                                           │
│  └── 外设抽象接口                                          │
├─────────────────────────────────────────────────────────────┤
│  硬件层 (Hardware Layer)                                   │
│  ├── ESP32-C3 MCU                                         │
│  ├── ST7735 LCD                                           │
│  └── 其他外设                                              │
└─────────────────────────────────────────────────────────────┘
```

### 核心任务

| 任务名称 | 优先级 | 功能描述 |
|---------|--------|---------|
| `main_task` | 高 | 系统初始化、驱动加载 |
| `lcd_refresh_task` | 中 | LCD屏幕刷新、显示更新 |
| `input_task` | 低 | 用户输入事件处理 |
| `system_monitor` | 低 | 系统状态监控 |

### 中断处理机制

| 中断源 | 优先级 | 用途 |
|--------|--------|------|
| TIMER0 | 高 | 定时触发、PWM |
| UART0 | 中 | 串口数据接收 |
| GPIO | 低 | 按键中断 |
| SPI | 低 | 数据传输完成 |

---

## 风险评估

| 风险 | 等级 | 说明 |
|------|------|------|
| 官方资料缺失 | 高 | Air101-LCD官方文档已下架，需依赖开源资源 |
| 驱动兼容性 | 中 | ST7735配置需根据实际屏幕微调 |
| 电源稳定性 | 低 | 需注意3.3V电源纹波 |

---

## 项目进度

### 已完成项

- [x] 项目文档框架搭建
- [x] 硬件连接方案设计
- [x] ESP-IDF 工程与 ST7735 驱动
- [x] LCD 显示 MaiQing
- [x] Cursor + ESP-IDF 编译环境
- [x] 新电脑部署文档与打包脚本

### 待实现项

- [ ] 更多图形/ UI 功能扩展

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-05-20 | 项目初始化，基础框架搭建 |
| v0.2 | 2026-05-20 | ST7735 显示 MaiQing；新电脑部署与打包流程 |

---

**项目状态**：开发中 🚧

*持续更新中，欢迎贡献代码和建议！*
