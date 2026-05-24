# ESP32-C3 串口调试 & OTA 上位机

基于 **PyQt5** 的 PC 工具，界面与架构借鉴 `APP/test`（金瓷超声波串口助手），并增加 ESP32-C3 局域网 OTA。

设计分层见 [设计框架.md](../设计框架.md)。

## 目录结构

```
serial_ota_tool/
├── main.py
├── app/mainwindow.py    # 主窗口（串口 / OTA / 设置）
├── core/                # 串口、OTA、工具函数
├── ui/theme.py          # 三套主题
├── build_exe.ps1        # 打包 EXE（手动）
└── requirements.txt
```

参考实现（只读）：`APP/test/test.py`

## 安装与运行

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 打包 EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

输出：`dist\ESP32-C3-Serial-OTA.exe`

## 功能

### 设置

**「设置」** 标签页：选择 **界面主题**（白蓝 / 黑金 / 科技蓝）。

### 串口调试

- 端口刷新、波特率/数据位/停止位/校验
- 文本与十六进制发送、行尾选项
- 接收区：十六进制或文本、时间戳、自动滚屏、保存日志
- 状态栏收发字节统计

### OTA 升级

- 按 IP / 设备名 / SN 查询 `/api/info`
- 网段扫描、选择 `.bin` 上传 `/api/ota`
- 与固件 `tools/ota_console` 协议一致
