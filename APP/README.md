# PC 端工具（APP）

| 目录 | 说明 |
|------|------|
| [test/](test/) | **历史参考**：金瓷超声波 PyQt5 串口助手（只读，勿改） |
| [serial_ota_tool/](serial_ota_tool/) | **当前工具**：ESP32-C3 串口调试 + OTA（PyQt5，可打包 EXE） |
| [设计框架.md](设计框架.md) | 分层结构与扩展说明 |

## 快速使用

```powershell
cd serial_ota_tool
pip install -r requirements.txt
python main.py
```

**EXE**：`serial_ota_tool\dist\ESP32-C3-Serial-OTA.exe`（手动执行 `build_exe.ps1` 生成）
