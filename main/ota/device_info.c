/* 设备 SN / 名称 / 版本：SN 来自 WiFi MAC，名称前缀来自 menuconfig */

#include "device_info.h"

#include <stdio.h>
#include <string.h>

#include "esp_app_desc.h"
#include "esp_mac.h"
#include "sdkconfig.h"

static device_info_t s_info;

void device_info_init(void)
{
    uint8_t mac[6];
    esp_read_mac(mac, ESP_MAC_WIFI_STA);

    snprintf(s_info.sn, sizeof(s_info.sn), "%02X%02X%02X%02X%02X%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    snprintf(s_info.mac, sizeof(s_info.mac), "%02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    char tail[7];
    memcpy(tail, s_info.sn + 6, 6);
    tail[6] = '\0';

    snprintf(s_info.name, sizeof(s_info.name), "%.15s-%s",
             CONFIG_OTA_DEVICE_NAME_PREFIX, tail);
    snprintf(s_info.hostname, sizeof(s_info.hostname), "%.15s-%s",
             CONFIG_OTA_DEVICE_NAME_PREFIX, tail);

    const esp_app_desc_t *app = esp_app_get_description();
    snprintf(s_info.version, sizeof(s_info.version), "%s", app->version);

    strncpy(s_info.ip, "0.0.0.0", sizeof(s_info.ip));
}

void device_info_set_ip(const char *ip)
{
    if (ip) {
        strncpy(s_info.ip, ip, sizeof(s_info.ip) - 1);
        s_info.ip[sizeof(s_info.ip) - 1] = '\0';
    }
}

const device_info_t *device_info_get(void)
{
    return &s_info;
}
