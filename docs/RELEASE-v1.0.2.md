## 说明

增加 LED 控制。

### 新增

- D4（GPIO12）、D5（GPIO13）闪烁驱动（`main/led/`）
- D4 周期 1s、D5 周期 2s，高电平有效
- 文档 [docs/LED.md](LED.md)

### 配置

- menuconfig → **LED** 可开启测试，**默认关闭**
- 与摇杆 UP（IO13）共用 D5，勿同时开启摇杆测试
