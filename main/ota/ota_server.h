#pragma once

#include "esp_err.h"

/** 启动 HTTP 服务与 mDNS，供网页 OTA 与设备发现 */
esp_err_t ota_server_start(void);
