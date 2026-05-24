# 新电脑部署与打包

> 从 [README-legacy.md](archive/README-legacy.md) 整理。根目录 [README.md](../README.md) 为快速入口。

**补充**：若使用 ESP-IDF **v5.5**，请用 `scripts/build-v55.ps1` 编译（避免与 `C:\Espressif` 旧工具链混用）。

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

**预期现象**：LCD 显示设备名、IP、SN 与 **MaiQing**（或开启摇杆测试时为 Joy Test 界面）。

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
├── main/                 # 应用、LCD、摇杆、OTA
├── docs/                 # 详细文档与 archive
├── CMakeLists.txt
├── sdkconfig.defaults    # 默认 Kconfig（WiFi 在本地 sdkconfig，不入库）
├── env.lock.json
├── .vscode/
├── scripts/
│   ├── setup-env.ps1
│   ├── build.ps1
│   ├── build-v55.ps1     # IDF v5.5
│   └── package-project.ps1
└── README.md
```

### 不要打包

| 路径 | 原因 |
|------|------|
| `build/` | 与本机路径、配置绑定，新电脑需重新生成 |
| `.cache/` | IDE 缓存 |
| `C:\Espressif\` | 工具链，在新电脑用 EIM 重装 |
| `%USERPROFILE%\.espressif\` | ESP-IDF 源码，由 EIM 下载 |

