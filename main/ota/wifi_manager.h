#pragma once

#include "esp_err.h"

/** 连接 menuconfig 中配置的 WiFi（STA），成功后将 IP 写入 device_info */
esp_err_t wifi_manager_start(void);
