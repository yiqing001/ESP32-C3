/* 应用入口：LCD → 远程 OTA 提示 → WiFi → HTTP OTA → 设备信息界面 */

#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lcd/st7735.h"
#include "ota/device_info.h"
#include "ota/ota_boot.h"
#include "ota/ota_server.h"
#include "ota/wifi_manager.h"

static const char *TAG = "app_main";

/** 启动/错误两行提示，scale=1 */
static void lcd_show_status(const char *line1, const char *line2)
{
    st7735_fill_screen(ST7735_COLOR_BLACK);
    st7735_draw_string(4, 8, line1, ST7735_COLOR_CYAN, ST7735_COLOR_BLACK, 1);
    if (line2 && line2[0]) {
        st7735_draw_string(4, 24, line2, ST7735_COLOR_YELLOW, ST7735_COLOR_BLACK, 1);
    }
}

/** 常态界面：设备名、IP、SN 后 6 位、MaiQing */
static void lcd_show_device_info(const device_info_t *info)
{
    char ip_line[20];
    char sn_line[16];

    snprintf(ip_line, sizeof(ip_line), "IP:%s", info->ip);
    snprintf(sn_line, sizeof(sn_line), "SN:%s", info->sn + 6);

    st7735_fill_screen(ST7735_COLOR_BLACK);
    st7735_draw_string(4, 4, info->name, ST7735_COLOR_CYAN, ST7735_COLOR_BLACK, 1);
    st7735_draw_string(4, 18, ip_line, ST7735_COLOR_YELLOW, ST7735_COLOR_BLACK, 1);
    st7735_draw_string(4, 32, sn_line, ST7735_COLOR_GREEN, ST7735_COLOR_BLACK, 1);
    st7735_draw_string(4, 52, "MaiQing", ST7735_COLOR_CYAN, ST7735_COLOR_BLACK, 1);
}

void app_main(void)
{
    /* 1. LCD */
    ESP_ERROR_CHECK(st7735_init());
    st7735_backlight(true);
    device_info_init();

    /* 2. 仅远程 OTA 后首次启动显示（USB 烧录不触发） */
    if (ota_boot_consume_success()) {
        lcd_show_status("OTA OK", "");
        vTaskDelay(pdMS_TO_TICKS(10000));
    }

    /* 3. WiFi */
    lcd_show_status("WiFi OTA", "connecting...");
    if (wifi_manager_start() != ESP_OK) {
        ESP_LOGE(TAG, "WiFi failed, check OTA_WIFI_* in sdkconfig");
        lcd_show_status("WiFi FAIL", "check SSID");
        return;
    }

    const device_info_t *info = device_info_get();

    /* 4. HTTP + mDNS */
    ESP_ERROR_CHECK(ota_server_start());
    ESP_LOGI(TAG, "device=%s sn=%s ip=%s", info->name, info->sn, info->ip);
    ESP_LOGI(TAG, "http://%s/  mdns://%s.local/", info->ip, info->hostname);

    /* 5. 设备信息界面 */
    lcd_show_device_info(info);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
