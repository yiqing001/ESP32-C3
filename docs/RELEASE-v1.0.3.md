# Release v1.0.3

## 改动摘要

### 新增：PC 上位机 `APP/serial_ota_tool`

- **串口调试**：端口刷新、波特率/数据位/停止位/校验、文本与十六进制收发、接收日志保存
- **OTA 升级**：按 IP / 设备名 / SN 查询设备、网段扫描、选择 `.bin` 上传（对接固件 `/api/info`、`/api/ota`）
- **设置** 标签页：界面主题切换（**白蓝** 默认、**黑金**、**科技蓝**）
- 分层结构：`app/` 界面、`core/` 业务、`ui/` 主题（见 `APP/设计框架.md`）
- 打包：`build_exe.ps1`、`scripts/build-app-exe.ps1` → `dist/ESP32-C3-Serial-OTA.exe`
- 参考：`APP/test/test.py`（历史 PyQt5 串口助手，只读）

### 工程与文档

- 根目录 `README.md`：PC 工具说明、目录结构、版本记录
- `.gitignore`：忽略 APP 的 `.venv`、`build`、`dist`、`.spec` 等
- `.vscode/tasks.json`：`APP: Run Python (dev)` 开发运行任务

### 说明

- 本版本主要为 **PC 端工具**，固件功能与 v1.0.2 一致（LCD、摇杆、LED、局域网 OTA 等）。

## 发布命令（网络可用时在本机执行）

```powershell
cd D:\Users\Administrator\Desktop\project\Firmware\ESP32\ESP32-C3
git push origin main
git push origin v1.0.3
gh release create v1.0.3 --title "v1.0.3" --notes-file docs/RELEASE-v1.0.3.md
```
