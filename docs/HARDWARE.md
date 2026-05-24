# 硬件连接

> 从 [README-legacy.md](archive/README-legacy.md) 整理；引脚复用详见归档全文「芯片引脚功能分配」。

## LCD（Air101-LCD / ST7735）

| LCD 引脚 | ESP32-C3 | 功能 |
|----------|----------|------|
| VCC | 3.3V | 电源 |
| GND | GND | 地 |
| SCK | GPIO2 | SPI 时钟 |
| SDA (MOSI) | GPIO3 | SPI 数据 |
| RESET | GPIO10 | 复位 |
| DC | GPIO6 | 数据/命令 |
| CS | GPIO7 | 片选 |
| BL | GPIO11 | 背光 |

逻辑分辨率：**160×80** 横屏；驱动见 `main/lcd/st7735.c`（含 PLUGIN 屏 `colstart` 偏移与坐标 Y 翻转）。

## 摇杆五向键（v1.0.1）

丝印与实机方向经标定，**软件 GPIO 映射如下**（低电平=按下，内部上拉）：

| 方向 | GPIO | 丝印参考 |
|------|------|----------|
| UP | 13 | UPKEY=IO08 与 DOWN 已对调 |
| DOWN | 8 | DWKEY=IO05 |
| LEFT | 9 | LKEY |
| RIGHT | 5 | RKEY=IO13 |
| CENTER | 4 | CENTER |

驱动：`main/joystick/joystick.c`。测试见根目录 README「摇杆」章节。

## LED（D4 / D5）

| LED | GPIO | 有效电平 | 周期 |
|-----|------|----------|------|
| D4 | 12 | 高 | 1 s |
| D5 | 13 | 高 | 2 s |

驱动 `main/led/led_blink.c`；**默认不运行**，启用与说明见 [LED.md](LED.md)。

## 板载其它

| 引脚 | 功能 |
|------|------|
| GPIO0 | BOOT（下载模式） |
