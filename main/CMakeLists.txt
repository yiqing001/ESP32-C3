# main 组件：应用 + LCD 驱动 + OTA 服务
idf_component_register(
    SRCS "app_main.c"
         "lcd/st7735.c"
         "lcd/font8x8.c"
         "joystick/joystick.c"
         "joystick/joystick_test.c"
         "ota/device_info.c"
         "ota/wifi_manager.c"
         "ota/ota_server.c"
         "ota/ota_boot.c"
    INCLUDE_DIRS "." "lcd" "joystick" "ota"
    REQUIRES esp_driver_gpio esp_driver_spi esp_wifi esp_http_server app_update mdns
             nvs_flash esp_netif esp_event
)
