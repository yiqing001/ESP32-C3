# 开发规范

> 从 [README-legacy.md](archive/README-legacy.md) 整理。

## 代码编写框架

> 后续在本项目写代码，按本节分层与注释规范来，保持**精简易懂、可维护**。

### 1. 分层原则

| 层级 | 目录/文件 | 职责 | 不要做的事 |
|------|-----------|------|------------|
| 应用层 | `main/app_main.c` | 启动顺序、模块调用、简单 UI 状态 | 不写 SPI/HTTP 细节 |
| 驱动层 | `main/lcd/` | 屏幕硬件、引脚、时序 | 不依赖 WiFi/OTA |
| 服务层 | `main/ota/` | 联网、HTTP、mDNS、设备信息 | 不操作 LCD 引脚 |
| 配置层 | `Kconfig.projbuild`、`sdkconfig` | SSID、端口、设备名前缀 | 不在代码里硬编码密码 |

**调用方向**：`app_main` → 各模块公开 API；模块之间尽量**不互相调用**，共用数据放 `device_info` 等独立模块。

### 1.1 固件运行逻辑

```
app_main
  ├─ st7735_init / 背光
  ├─ device_info_init          ← MAC → SN、设备名
  ├─ ota_boot_consume_success  ← 仅远程 OTA 后显示 OTA OK
  ├─ wifi_manager_start        ← STA、关省电、写 IP
  ├─ ota_server_start          ← HTTP 页 + POST /api/ota + mDNS
  └─ lcd_show_device_info      ← 常态界面

远程 OTA（浏览器 POST .bin）
  → esp_ota 写入备用分区 ota_0/ota_1
  → ota_boot_mark_remote_ota
  → 重启 → consume_success → 屏幕 OTA OK 5s → 设备信息
```

| 模块 | 文件 | 对外 API |
|------|------|----------|
| LCD | `lcd/st7735.c` | `st7735_init`, `fill_screen`, `draw_string` |
| 设备信息 | `ota/device_info.c` | `device_info_init`, `get`, `set_ip` |
| 摇杆 | `joystick/joystick.c` | `joystick_init`, `joystick_poll`；测试见根 README |
| WiFi | `ota/wifi_manager.c` | `wifi_manager_start` |
| OTA 启动标志 | `ota/ota_boot.c` | `mark_remote_ota`, `consume_success` |
| HTTP OTA | `ota/ota_server.c` | `ota_server_start` |

### 2. 新增功能放哪里

```
要加的功能              → 建议位置
─────────────────────────────────────────
LCD 显示/绘图           → main/lcd/st7735.c，头文件声明 API
WiFi / 网络 / OTA       → main/ota/
新业务（按键、传感器）   → main/xxx/ 新建文件夹 + .h/.c
menuconfig 可配置项     → main/Kconfig.projbuild
注册进编译              → main/CMakeLists.txt 的 SRCS / INCLUDE_DIRS
```

新增 `.c` 文件后，在 `main/CMakeLists.txt` 里补上文件名，否则不会参与编译。

### 3. 注释怎么写（精简）

**原则**：代码本身能看懂的少写；**硬件参数、协议、非 obvious 逻辑**必须写。

| 要写 | 不用写 |
|------|--------|
| 引脚含义、屏幕型号/偏移/MADCTL 取值原因 | `i++` 在循环里干什么 |
| 函数对外作用、参数单位（毫秒/像素） | 每个 `ESP_LOGI` 上方重复一句 |
| 协议字段、状态机切换条件 | 把代码逐行翻译成中文 |

**文件头**（可选，新模块建议写一行）：

```c
/* WiFi 连接管理：STA 模式，连接成功后写入 device_info IP */
```

**函数头**（公开 API 必写，一行即可）：

```c
/** 填充整屏颜色；color 为 RGB565，如 ST7735_COLOR_BLACK */
void st7735_fill_screen(uint16_t color);
```

**行内注释**（只解释「为什么」）：

```c
#define ST7735_COLSTART  26   /* Air101 PLUGIN 屏 colstart，勿加到 X 轴 */
wifi_cfg.sta.threshold.authmode = WIFI_AUTH_WPA_WPA2_PSK;  /* 路由器 WPA/WPA2 混合 */
```

**块注释**（初始化序列、多步流程）：

```c
/* 1. 复位  2. 发 GREENTAB160x80 序列  3. 设横向 MADCTL  4. DISPON */
```

### 4. 命名与风格

| 类型 | 规则 | 示例 |
|------|------|------|
| 源文件 | 小写 + 下划线，与模块名一致 | `wifi_manager.c` |
| 公开函数 | `模块前缀_动词` | `st7735_init()`、`ota_server_start()` |
| 模块内静态 | `s_` 前缀 | `static httpd_handle_t s_server` |
| 宏/引脚 | 大写 | `PIN_LCD_SCK`、`ST7735_LCD_WIDTH` |
| 日志 TAG | 与模块相关、≤16 字符 | `"wifi_mgr"`、`"st7735"` |

缩进 4 空格；花括号与现有 `st7735.c`、`app_main.c` 保持一致。

### 5. 错误与日志

```c
/* 初始化阶段：失败即无法继续 → 用 ESP_ERROR_CHECK */
ESP_ERROR_CHECK(st7735_init());

/* 运行阶段：可重试/可降级 → 判断返回值 + 日志 */
if (wifi_manager_start() != ESP_OK) {
    ESP_LOGE(TAG, "WiFi failed, check sdkconfig OTA_WIFI_*");
    lcd_show_status("WiFi FAIL", "check SSID");
    return;
}
```

| 级别 | 用途 |
|------|------|
| `ESP_LOGI` | 正常流程（连上 WiFi、OTA 成功、IP 地址） |
| `ESP_LOGW` | 可恢复异常（重试、断开 reason） |
| `ESP_LOGE` | 失败且功能不可用 |

### 6. 头文件约定

每个模块一对 `.h` / `.c`：

- **`.h`**：只放对外 `struct`、`#define`、函数声明；加 `#pragma once`
- **`.c`**：实现细节、`static` 函数、硬件寄存器操作

```c
/* st7735.h — 应用层只 include 这个 */
#pragma once
#include "esp_err.h"
esp_err_t st7735_init(void);
void st7735_fill_screen(uint16_t color);
```

### 7. 配置项约定

| 配置 | 改哪里 | 说明 |
|------|--------|------|
| WiFi SSID/密码 | `sdkconfig` 或 `idf.py menuconfig` | **改 defaults 不会覆盖已有 sdkconfig** |
| 设备名前缀、HTTP 端口 | `Remote OTA (WiFi)` | 对应 `CONFIG_OTA_*` |
| 引脚 | 驱动内 `#define PIN_*` | 改线时只改驱动文件并更新 README 接线表 |

代码里用 `CONFIG_OTA_WIFI_SSID` 等宏，**不要**在 `.c` 里写死密码。

### 8. 新增模块检查清单

- [ ] 新建 `main/xxx/xxx.h` + `xxx.c`，头文件写清 API 注释
- [ ] `main/CMakeLists.txt` 加入源文件与 `INCLUDE_DIRS`
- [ ] 在 `app_main.c` 按顺序调用：`init` → `start` → 业务
- [ ] 关键常量、引脚、协议处补充**一行**备注
- [ ] `idf.py build` 通过后再烧录验证

### 9. 示例：app_main 推荐结构

```c
void app_main(void)
{
    /* 1. 硬件与显示 */
    ESP_ERROR_CHECK(st7735_init());
    st7735_backlight(true);
    lcd_show_status("Boot", "...");

    /* 2. 设备信息与网络 */
    device_info_init();
    if (wifi_manager_start() != ESP_OK) { /* 失败处理 */ return; }

    /* 3. 网络服务 */
    ESP_ERROR_CHECK(ota_server_start());

    /* 4. 业务界面 */
    st7735_draw_string(...);

    /* 5. 主循环（如有） */
    while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }
}
```

