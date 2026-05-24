#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"

/** 逻辑分辨率（横向），与 Air101-LCD 可视区域一致 */
#define ST7735_LCD_WIDTH   160
#define ST7735_LCD_HEIGHT  80

/** RGB565 常用色 */
#define ST7735_COLOR_BLACK   0x0000
#define ST7735_COLOR_WHITE   0xFFFF
#define ST7735_COLOR_BLUE    0x001F
#define ST7735_COLOR_CYAN    0x07FF
#define ST7735_COLOR_GREEN   0x07E0
#define ST7735_COLOR_YELLOW  0xFFE0

/** 初始化 SPI 与 ST7735 寄存器，返回后可直接绘图 */
esp_err_t st7735_init(void);

/** 背光开关，on=true 点亮 GPIO11 */
void st7735_backlight(bool on);

/** 整屏填充单色（RGB565） */
void st7735_fill_screen(uint16_t color);

/**
 * 绘制 ASCII 字符串（8x8 字库，可放大 scale 倍）
 * @param x,y  左上角逻辑坐标
 * @param fg,bg 前景/背景色
 */
void st7735_draw_string(uint16_t x, uint16_t y, const char *text,
                        uint16_t fg, uint16_t bg, uint8_t scale);
