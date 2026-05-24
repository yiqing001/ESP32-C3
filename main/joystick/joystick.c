#include "joystick.h"

#include <stdio.h>
#include <string.h>

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    gpio_num_t gpio;
    uint32_t mask;
    const char *name;
} joystick_pin_t;

static const joystick_pin_t s_pins[] = {
    { JOYSTICK_GPIO_UP,     JOYSTICK_MASK_UP,     "UP" },
    { JOYSTICK_GPIO_DOWN,   JOYSTICK_MASK_DOWN,   "DOWN" },
    { JOYSTICK_GPIO_LEFT,   JOYSTICK_MASK_LEFT,   "LEFT" },
    { JOYSTICK_GPIO_RIGHT,  JOYSTICK_MASK_RIGHT,  "RIGHT" },
    { JOYSTICK_GPIO_CENTER, JOYSTICK_MASK_CENTER, "CENTER" },
};

static uint32_t s_stable;
static uint32_t s_prev_stable;
static uint32_t s_raw;
static TickType_t s_raw_change_tick;

static uint32_t joystick_read_raw(void)
{
    uint32_t mask = 0;
    for (size_t i = 0; i < sizeof(s_pins) / sizeof(s_pins[0]); i++) {
        if (gpio_get_level(s_pins[i].gpio) == 0) {
            mask |= s_pins[i].mask;
        }
    }
    return mask;
}

esp_err_t joystick_init(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = 0,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    for (size_t i = 0; i < sizeof(s_pins) / sizeof(s_pins[0]); i++) {
        cfg.pin_bit_mask |= (1ULL << s_pins[i].gpio);
    }

    esp_err_t err = gpio_config(&cfg);
    if (err != ESP_OK) {
        return err;
    }

    s_raw = joystick_read_raw();
    s_stable = s_raw;
    s_prev_stable = s_raw;
    s_raw_change_tick = xTaskGetTickCount();
    return ESP_OK;
}

uint32_t joystick_read(void)
{
    return s_stable;
}

void joystick_poll(joystick_event_t *event)
{
    const uint32_t raw = joystick_read_raw();
    const TickType_t now = xTaskGetTickCount();

    if (raw != s_raw) {
        s_raw = raw;
        s_raw_change_tick = now;
    } else if ((now - s_raw_change_tick) >= pdMS_TO_TICKS(20)) {
        s_stable = raw;
    }

    event->held = s_stable;
    event->pressed = s_stable & ~s_prev_stable;
    event->released = s_prev_stable & ~s_stable;
    s_prev_stable = s_stable;
}

void joystick_mask_to_string(uint32_t mask, char *buf, size_t buf_len)
{
    if (!buf || buf_len == 0) {
        return;
    }
    if (mask == 0) {
        snprintf(buf, buf_len, "-");
        return;
    }

    buf[0] = '\0';
    for (size_t i = 0; i < sizeof(s_pins) / sizeof(s_pins[0]); i++) {
        if ((mask & s_pins[i].mask) == 0) {
            continue;
        }
        const size_t len = strlen(buf);
        if (len > 0 && len + 1 < buf_len) {
            strlcat(buf, "+", buf_len);
        }
        strlcat(buf, s_pins[i].name, buf_len);
    }
}
