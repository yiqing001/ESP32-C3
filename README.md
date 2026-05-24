# ESP32-C3 + Air101-LCD

合宙 **ESP32-C3** 开发板 + **Air101-LCD**（ST7735，160×80）固件工程。

## 当前功能（v1.0.1）

| 功能 | 说明 |
|------|------|
| LCD | 设备名、IP、SN（后 6 位）、MaiQing |
| 局域网 OTA | HTTP 上传固件、双分区切换 |
| mDNS | `http://<hostname>.local/` |
| 摇杆 | 五向按键驱动（`main/joystick/`），可选上电测试 |

## 快速开始

```powershell
# 推荐：ESP-IDF v5.5（与 Cursor 扩展一致）
powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1 -Port COM6 -Flash

# 或 EIM / v5.3.2 环境
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Port COM6 -Flash
```

1. 复制 `.vscode/settings.json.example` → `settings.json`，填写串口  
2. `idf.py menuconfig` → **Remote OTA (WiFi)** 配置 SSID/密码（`sdkconfig` 不入库）  
3. 烧录后屏幕显示设备信息；浏览器打开 `http://<IP>/` 或 `tools/ota_console/` 进行 OTA  

## 目录结构

```
├── main/
│   ├── app_main.c       # 启动流程
│   ├── lcd/             # ST7735 + 字库
│   ├── joystick/        # 摇杆驱动与测试
│   └── ota/             # WiFi、HTTP OTA、设备信息
├── scripts/             # 编译、打包、环境脚本
├── tools/ota_console/   # OTA 网页控制台
├── partitions.csv       # OTA 分区表
├── sdkconfig.defaults   # 默认 Kconfig（不含 WiFi 密码）
└── docs/                # 详细文档（见 docs/README.md）
```

## 摇杆（v1.0.1 新增）

| 方向 | GPIO | 说明 |
|------|------|------|
| UP | 13 | 低电平有效，内部上拉 |
| DOWN | 8 | 与 PCB 丝印经实机对调 |
| LEFT | 9 | |
| RIGHT | 5 | |
| CENTER | 4 | |

**启用测试**：`idf.py menuconfig` → **Joystick** → `Boot into joystick test`，或在本地 `sdkconfig` 设 `CONFIG_JOYSTICK_ENABLE_TEST=y` 后编译。默认关闭，正常为设备信息界面。

## 固件启动流程

```
LCD 初始化 → [OTA OK 5s] → WiFi → HTTP/mDNS → 设备信息界面
```

远程 OTA 成功后重启，仅远程升级会显示 **OTA OK**（USB 直烧不显示）。

## 文档

| 文档 | 内容 |
|------|------|
| [docs/README.md](docs/README.md) | 文档索引 |
| [docs/DEPLOY.md](docs/DEPLOY.md) | 新电脑部署、打包迁移 |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | 代码分层、注释规范、新增模块 |
| [docs/HARDWARE.md](docs/HARDWARE.md) | LCD/摇杆接线、引脚表 |
| [docs/archive/README-legacy.md](docs/archive/README-legacy.md) | 原完整 README 归档 |

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.1 | 2026-05-20 | 增加摇杆驱动与可选测试；LCD 文字方向标定；OTA OK 5s |
| v1.0.0 | 2026-05-20 | LCD 设备信息、局域网 HTTP OTA、mDNS |
| v0.2 | 2026-05-20 | ST7735 显示；部署脚本与文档 |
| v0.1 | 2026-05-20 | 项目初始化 |

仓库：<https://github.com/yiqing001/ESP32-C3>
