## 说明

增加摇杆功能。

### 新增

- 五向摇杆驱动（`main/joystick/`），GPIO 经实机标定
- 可选上电摇杆测试（menuconfig 开启，默认关闭）
- `scripts/build-v55.ps1`：ESP-IDF v5.5 编译脚本

### 改进

- LCD 文字显示方向标定
- 远程 OTA 成功后 **OTA OK** 提示 5 秒
- 文档整理：根目录 README 精简，详情见 `docs/`
