/* HTTP OTA：设备网页 /api/ota、JSON /api/info、mDNS 广播 */

#include "ota_server.h"

#include <stdio.h>
#include <string.h>
#include <sys/param.h>

#include "ota_boot.h"
#include "device_info.h"
#include "esp_heap_caps.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "mdns.h"
#include "sdkconfig.h"

static const char *TAG = "ota_server";

#define OTA_RX_BUF_SIZE   4096
#define OTA_OK_MSG        "烧录成功，请重启"

static httpd_handle_t s_server;
static uint8_t *s_ota_rx_buf;

static void add_cors(httpd_req_t *req)
{
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
}

static esp_err_t handler_options(httpd_req_t *req)
{
    add_cors(req);
    httpd_resp_set_status(req, "204 No Content");
    return httpd_resp_send(req, NULL, 0);
}

static esp_err_t handler_info(httpd_req_t *req)
{
    const device_info_t *info = device_info_get();
    char body[384];
    snprintf(body, sizeof(body),
             "{\"name\":\"%s\",\"hostname\":\"%s\",\"sn\":\"%s\",\"ip\":\"%s\","
             "\"mac\":\"%s\",\"version\":\"%s\",\"ota_url\":\"http://%s/api/ota\"}",
             info->name, info->hostname, info->sn, info->ip,
             info->mac, info->version, info->ip);

    add_cors(req);
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_sendstr(req, body);
}

/* 设备内置 OTA 页（与 tools/ota_console 协议一致：POST /api/ota） */
static const char *DEVICE_PAGE =
    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>ESP32-C3 OTA</title>"
    "<style>body{font-family:sans-serif;max-width:480px;margin:2rem auto;padding:0 1rem}"
    "input,button{width:100%;padding:.6rem;margin:.4rem 0;box-sizing:border-box}"
    "button{background:#0a7;color:#fff;border:0;border-radius:4px;cursor:pointer}"
    "button:disabled{opacity:.6;cursor:not-allowed}"
    ".info{background:#f4f4f4;padding:1rem;border-radius:6px;font-size:.9rem}"
    "progress{width:100%;height:8px}</style>"
    "</head><body><h2>设备 OTA</h2><div class='info' id='info'>加载中...</div>"
    "<input type='file' id='fw' accept='.bin'>"
    "<button id='btn' onclick='upload()'>上传固件</button>"
    "<progress id='prog' value='0' max='100'></progress>"
    "<p id='st'></p><script>"
    "fetch('/api/info').then(r=>r.json()).then(d=>{"
    "document.getElementById('info').innerHTML="
    "'SN: '+d.sn+'<br>名称: '+d.name+'<br>IP: '+d.ip+'<br>版本: '+d.version;});"
    "function upload(){"
    "var f=document.getElementById('fw').files[0];"
    "if(!f){alert('请选择 .bin 文件');return;}"
    "var st=document.getElementById('st'),btn=document.getElementById('btn'),"
    "prog=document.getElementById('prog');"
    "btn.disabled=true;st.textContent='上传中...';prog.value=0;"
    "var xhr=new XMLHttpRequest();"
    "xhr.open('POST','/api/ota');"
    "xhr.setRequestHeader('Content-Type','application/octet-stream');"
    "xhr.timeout=600000;"
    "xhr.upload.onprogress=function(e){"
    "if(e.lengthComputable)prog.value=Math.round(e.loaded/e.total*100);};"
    "xhr.onload=function(){btn.disabled=false;"
    "if(xhr.status>=200&&xhr.status<300){st.textContent=xhr.responseText;}"
    "else{st.textContent='失败 HTTP '+xhr.status+' '+xhr.responseText;}};"
    "xhr.onerror=function(){btn.disabled=false;"
    "st.textContent='网络错误(连接中断,请查看设备串口)';};"
    "xhr.ontimeout=function(){btn.disabled=false;st.textContent='上传超时';};"
    "xhr.send(f);}</script></body></html>";

static esp_err_t handler_root(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_sendstr(req, DEVICE_PAGE);
}

/** 将 mDNS 主机名转为小写（RFC 要求） */
static void hostname_to_lower(char *host, size_t len)
{
    for (size_t i = 0; i < len && host[i]; i++) {
        if (host[i] >= 'A' && host[i] <= 'Z') {
            host[i] = (char)(host[i] - 'A' + 'a');
        }
    }
}

static esp_err_t ota_recv_and_write(httpd_req_t *req, esp_ota_handle_t ota_handle,
                                    int content_len, bool feed_wdt)
{
    int total = 0;
    int last_pct = -1;
    int timeout_streak = 0;

    while (total < content_len) {
#if CONFIG_ESP_TASK_WDT_EN
        if (feed_wdt) {
            esp_task_wdt_reset();
        }
#endif
        const int to_read = MIN(OTA_RX_BUF_SIZE, content_len - total);
        const int received = httpd_req_recv(req, (char *)s_ota_rx_buf, to_read);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) {
            if (++timeout_streak > 60) {
                return ESP_ERR_TIMEOUT;
            }
            continue;
        }
        timeout_streak = 0;
        if (received <= 0) {
            ESP_LOGE(TAG, "recv aborted at %d/%d", total, content_len);
            return ESP_FAIL;
        }

        esp_err_t err = esp_ota_write(ota_handle, s_ota_rx_buf, received);
        if (err != ESP_OK) {
            return err;
        }
        total += received;
        taskYIELD();

        const int pct = (total * 100) / content_len;
        if (pct >= last_pct + 10) {
            ESP_LOGI(TAG, "OTA progress %d%%", pct);
            last_pct = pct;
        }
    }
    return ESP_OK;
}

static esp_err_t handler_ota_upload(httpd_req_t *req)
{
    add_cors(req);
    esp_err_t err = ESP_OK;
    bool wdt_added = false;
    esp_ota_handle_t ota_handle = 0;

    if (req->content_len <= 0) {
        httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "missing Content-Length");
        return ESP_FAIL;
    }

    if (!s_ota_rx_buf) {
        s_ota_rx_buf = heap_caps_malloc(OTA_RX_BUF_SIZE, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
        if (!s_ota_rx_buf) {
            httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "no memory");
            return ESP_FAIL;
        }
    }

    const esp_partition_t *update_part = esp_ota_get_next_update_partition(NULL);
    if (!update_part) {
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "no OTA partition");
        return ESP_FAIL;
    }
    if ((size_t)req->content_len > update_part->size) {
        httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "firmware too large");
        return ESP_FAIL;
    }

#if CONFIG_ESP_TASK_WDT_EN
    if (esp_task_wdt_add(NULL) == ESP_OK) {
        wdt_added = true;
    }
#endif

    ESP_LOGI(TAG, "OTA %d bytes -> %s", req->content_len, update_part->label);

    err = esp_ota_begin(update_part, req->content_len, &ota_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "ota_begin: %s", esp_err_to_name(err));
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "ota begin failed");
        goto done;
    }

    err = ota_recv_and_write(req, ota_handle, req->content_len, wdt_added);
    if (err != ESP_OK) {
        esp_ota_abort(ota_handle);
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "ota write failed");
        goto done;
    }

    err = esp_ota_end(ota_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "ota_end: %s", esp_err_to_name(err));
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "ota end failed");
        goto done;
    }

    err = esp_ota_set_boot_partition(update_part);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "set_boot: %s", esp_err_to_name(err));
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "set boot failed");
        goto done;
    }

    ESP_LOGI(TAG, "OTA done, %d bytes", req->content_len);
    httpd_resp_set_type(req, "text/plain; charset=utf-8");
    httpd_resp_sendstr(req, OTA_OK_MSG);
    ota_boot_mark_remote_ota(update_part);
    vTaskDelay(pdMS_TO_TICKS(500));
    esp_restart();

done:
#if CONFIG_ESP_TASK_WDT_EN
    if (wdt_added) {
        esp_task_wdt_delete(NULL);
    }
#endif
    return err;
}

static esp_err_t start_mdns(void)
{
    const device_info_t *info = device_info_get();
    char hostname[DEVICE_NAME_LEN];

    strncpy(hostname, info->hostname, sizeof(hostname) - 1);
    hostname[sizeof(hostname) - 1] = '\0';
    hostname_to_lower(hostname, sizeof(hostname));

    ESP_ERROR_CHECK(mdns_init());
    ESP_ERROR_CHECK(mdns_hostname_set(hostname));

    mdns_txt_item_t txt[] = {
        {"sn", info->sn},
        {"name", info->name},
        {"version", info->version},
    };
    ESP_ERROR_CHECK(mdns_service_add(info->name, "_http", "_tcp",
                                     CONFIG_OTA_HTTP_PORT, txt, 3));
    ESP_LOGI(TAG, "mDNS http://%s.local", hostname);
    return ESP_OK;
}

static void log_ota_partitions(void)
{
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = esp_ota_get_next_update_partition(NULL);

    if (running) {
        ESP_LOGI(TAG, "running=%s @0x%lx", running->label, (unsigned long)running->address);
    }
    if (next) {
        ESP_LOGI(TAG, "OTA slot=%s @0x%lx", next->label, (unsigned long)next->address);
    } else {
        ESP_LOGE(TAG, "no OTA slot; USB flash partitions.csv");
    }
}

esp_err_t ota_server_start(void)
{
    httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
    cfg.server_port = CONFIG_OTA_HTTP_PORT;
    cfg.max_uri_handlers = 8;
    cfg.recv_wait_timeout = 120;
    cfg.send_wait_timeout = 120;
    cfg.stack_size = 24576;
    cfg.lru_purge_enable = true;

    ESP_ERROR_CHECK(httpd_start(&s_server, &cfg));

    const httpd_uri_t routes[] = {
        { .uri = "/",           .method = HTTP_GET,  .handler = handler_root },
        { .uri = "/api/info",   .method = HTTP_GET,  .handler = handler_info },
        { .uri = "/api/info",   .method = HTTP_OPTIONS, .handler = handler_options },
        { .uri = "/api/ota",    .method = HTTP_POST, .handler = handler_ota_upload },
        { .uri = "/api/ota",    .method = HTTP_OPTIONS, .handler = handler_options },
    };
    for (size_t i = 0; i < sizeof(routes) / sizeof(routes[0]); i++) {
        httpd_register_uri_handler(s_server, &routes[i]);
    }

    ESP_ERROR_CHECK(start_mdns());
    log_ota_partitions();

    const device_info_t *dev = device_info_get();
    ESP_LOGI(TAG, "HTTP http://%s/ port %d", dev->ip, CONFIG_OTA_HTTP_PORT);
    return ESP_OK;
}
