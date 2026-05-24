#pragma once

#include "esp_err.h"

/** D4 = GPIO12，高电平有效，周期 1s 翻转 */
#define LED_BLINK_GPIO_D4  12
/** D5 = GPIO13，高电平有效，周期 2s 翻转 */
#define LED_BLINK_GPIO_D5  13

/**
 * 初始化 GPIO 并启动闪烁任务（与 WiFi/界面并行）。
 * 由 CONFIG_LED_ENABLE_BLINK 控制，默认关闭，见 docs/LED.md。
 */
esp_err_t led_blink_start(void);
