#include "led_blink.h"

#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "led_blink";

/* 原理图：D4/D5 均为高电平有效 */
#define LED_LEVEL_ON   1
#define LED_LEVEL_OFF  0

static void led_set_level(gpio_num_t gpio, bool on)
{
    gpio_set_level(gpio, on ? LED_LEVEL_ON : LED_LEVEL_OFF);
}

static void led_blink_task(void *arg)
{
    bool on_d4 = false;
    bool on_d5 = false;
    TickType_t last_d4 = xTaskGetTickCount();
    TickType_t last_d5 = xTaskGetTickCount();

    ESP_LOGI(TAG, "blink: D4(GPIO%d)=1s, D5(GPIO%d)=2s", LED_BLINK_GPIO_D4, LED_BLINK_GPIO_D5);

    while (1) {
        const TickType_t now = xTaskGetTickCount();

        if ((now - last_d4) >= pdMS_TO_TICKS(1000)) {
            on_d4 = !on_d4;
            led_set_level(LED_BLINK_GPIO_D4, on_d4);
            last_d4 = now;
        }
        if ((now - last_d5) >= pdMS_TO_TICKS(2000)) {
            on_d5 = !on_d5;
            led_set_level(LED_BLINK_GPIO_D5, on_d5);
            last_d5 = now;
        }

        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

esp_err_t led_blink_start(void)
{
    const gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << LED_BLINK_GPIO_D4) | (1ULL << LED_BLINK_GPIO_D5),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    esp_err_t err = gpio_config(&cfg);
    if (err != ESP_OK) {
        return err;
    }

    led_set_level(LED_BLINK_GPIO_D4, false);
    led_set_level(LED_BLINK_GPIO_D5, false);

    const BaseType_t ok = xTaskCreate(led_blink_task, "led_blink", 2048, NULL, 5, NULL);
    return (ok == pdPASS) ? ESP_OK : ESP_FAIL;
}
