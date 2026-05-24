#include "joystick_test.h"

#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "joystick.h"
#include "lcd/st7735.h"

static const char *TAG = "joy_test";

static void draw_key_label(uint16_t x, uint16_t y, const char *label, bool active)
{
    const uint16_t fg = active ? ST7735_COLOR_GREEN : ST7735_COLOR_WHITE;
    const uint16_t bg = ST7735_COLOR_BLACK;
    st7735_draw_string(x, y, label, fg, bg, 1);
}

static void lcd_show_joystick(uint32_t held)
{
    st7735_fill_screen(ST7735_COLOR_BLACK);
    st7735_draw_string(4, 4, "Joy Test", ST7735_COLOR_CYAN, ST7735_COLOR_BLACK, 1);

    draw_key_label(68, 14, "UP", (held & JOYSTICK_MASK_UP) != 0);
    draw_key_label(60, 34, "CT", (held & JOYSTICK_MASK_CENTER) != 0);
    draw_key_label(68, 54, "DN", (held & JOYSTICK_MASK_DOWN) != 0);
    draw_key_label(8, 34, "LF", (held & JOYSTICK_MASK_LEFT) != 0);
    draw_key_label(120, 34, "RT", (held & JOYSTICK_MASK_RIGHT) != 0);

    char line[32];
    joystick_mask_to_string(held, line, sizeof(line));
    st7735_draw_string(4, 68, line, ST7735_COLOR_YELLOW, ST7735_COLOR_BLACK, 1);
}

void joystick_test_run(void)
{
    ESP_ERROR_CHECK(joystick_init());
    ESP_LOGI(TAG, "pins: UP=IO%d DN=IO%d LF=IO%d RT=IO%d CT=IO%d (active low)",
             JOYSTICK_GPIO_UP, JOYSTICK_GPIO_DOWN, JOYSTICK_GPIO_LEFT,
             JOYSTICK_GPIO_RIGHT, JOYSTICK_GPIO_CENTER);

    joystick_event_t ev;
    uint32_t last_lcd = UINT32_MAX;

    while (1) {
        joystick_poll(&ev);

        if (ev.pressed != 0) {
            char msg[32];
            joystick_mask_to_string(ev.pressed, msg, sizeof(msg));
            ESP_LOGI(TAG, "pressed: %s", msg);
        }
        if (ev.released != 0) {
            char msg[32];
            joystick_mask_to_string(ev.released, msg, sizeof(msg));
            ESP_LOGI(TAG, "released: %s", msg);
        }

        if (ev.held != last_lcd) {
            lcd_show_joystick(ev.held);
            last_lcd = ev.held;
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
