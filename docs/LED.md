# LED 闪烁测试（D4 / D5）

> 驱动代码：`main/led/led_blink.c`。默认**不启用**，与正常 WiFi/设备信息界面并行无关。

## 引脚（原理图）

| LED | GPIO | 有效电平 | 闪烁周期 |
|-----|------|----------|----------|
| D4 | 12 | 高 | 1 s 翻转一次 |
| D5 | 13 | 高 | 2 s 翻转一次 |

## 如何启用

1. `idf.py menuconfig` → **LED** → 勾选 `Enable D4/D5 LED blink test task`  
2. 或在本地 `sdkconfig` 增加：`CONFIG_LED_ENABLE_BLINK=y`（**改 defaults 不会覆盖已有 sdkconfig**）  
3. 重新 `idf.py build` 并烧录  

关闭：取消勾选或 `# CONFIG_LED_ENABLE_BLINK is not set`。

## 现象

- 上电后后台任务翻转 GPIO，LCD 仍为设备信息界面（未开摇杆测试时）。  
- 串口日志：`led_blink: blink: D4(GPIO12)=1s, D5(GPIO13)=2s`

## 注意

- **D5（IO13）** 与摇杆 **UP** 共用，勿与 `CONFIG_JOYSTICK_ENABLE_TEST` 同时开启。  
- 极性已在代码中设为高电平亮；若硬件相反，修改 `led_blink.c` 中 `LED_LEVEL_ON` / `LED_LEVEL_OFF`。
