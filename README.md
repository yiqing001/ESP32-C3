# ESP32-C3 + Air101-LCD

合宙 **ESP32-C3** 开发板 + **Air101-LCD**（ST7735，160×80）固件工程。

## 当前功能

| 功能 | 说明 |
|------|------|
| LCD | 设备名、IP、SN（后 6 位）、MaiQing |
| 局域网 OTA | HTTP 上传固件、双分区切换 |
| mDNS | `http://<hostname>.local/` |
| 摇杆 | 五向按键驱动（`main/joystick/`），可选测试，默认关 |
| LED | D4/D5 闪烁驱动（`main/led/`），可选测试，默认关 |

## 快速开始

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1 -Port COM6 -Flash
```

1. 复制 `.vscode/settings.json.example` → `settings.json`，填写串口  
2. `idf.py menuconfig` → **Remote OTA (WiFi)** 配置 SSID/密码（`sdkconfig` 不入库）  
3. 烧录后显示设备信息；浏览器 `http://<IP>/` 或 `tools/ota_console/` OTA  

## 目录结构

```
├── main/
│   ├── app_main.c
│   ├── lcd/             # ST7735
│   ├── joystick/        # 摇杆 + 可选测试
│   ├── led/             # LED 闪烁 + 可选测试
│   └── ota/             # WiFi / HTTP OTA
├── scripts/             # build.ps1、build-v55.ps1 等
├── tools/ota_console/
├── docs/                # 详细文档（见 docs/README.md）
└── sdkconfig.defaults
```

## 可选硬件测试

| 测试 | 开启方式 | 文档 |
|------|----------|------|
| 摇杆 | menuconfig → **Joystick** | [docs/HARDWARE.md](docs/HARDWARE.md) |
| LED D4/D5 | menuconfig → **LED** | [docs/LED.md](docs/LED.md) |

默认均为关闭，上电为 **WiFi → 设备信息界面**。摇杆 UP(IO13) 与 LED D5 共用引脚，勿同时测。

## 固件启动流程

```
LCD → [OTA OK 5s] → WiFi → HTTP/mDNS → 设备信息界面
```

## 文档

| 文档 | 内容 |
|------|------|
| [docs/README.md](docs/README.md) | 文档索引 |
| [docs/DEPLOY.md](docs/DEPLOY.md) | 新电脑部署 |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | 开发规范 |
| [docs/HARDWARE.md](docs/HARDWARE.md) | LCD / 摇杆引脚 |
| [docs/LED.md](docs/LED.md) | LED 测试说明 |
| [docs/archive/](docs/archive/) | 历史 README 归档 |

## 版本历史

| 版本 | 说明 |
|------|------|
| v1.0.2 | LED 控制（D4/D5 闪烁测试，默认关） |
| v1.0.1 | 摇杆驱动；LCD 标定；OTA OK 5s |
| v1.0.0 | 设备信息界面、局域网 OTA、mDNS |

仓库：<https://github.com/yiqing001/ESP32-C3>
