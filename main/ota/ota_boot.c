/* 远程 OTA 首次启动检测：NVS 记录目标分区或 PENDING_VERIFY 状态 */

#include "ota_boot.h"

#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_partition.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "ota_boot";
static const char *NS = "app";
static const char *KEY = "ota_tgt";
static const char *LEGACY_KEY = "ota_ok";
static const uint32_t MAGIC = 0x4F544141u;

typedef struct {
    uint32_t magic;
    uint32_t part_addr;
} ota_pending_t;

static esp_err_t nvs_ensure(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    return ret;
}

/** 清除旧版 ota_ok 标志，避免 USB 烧录后误显示 OTA OK */
static void nvs_clear_legacy(void)
{
    nvs_handle_t h;
    if (nvs_open(NS, NVS_READWRITE, &h) != ESP_OK) {
        return;
    }
    if (nvs_erase_key(h, LEGACY_KEY) == ESP_OK) {
        nvs_commit(h);
    }
    nvs_close(h);
}

void ota_boot_mark_remote_ota(const esp_partition_t *boot_part)
{
    if (!boot_part || nvs_ensure() != ESP_OK) {
        return;
    }

    ota_pending_t rec = { .magic = MAGIC, .part_addr = boot_part->address };
    nvs_handle_t h;
    if (nvs_open(NS, NVS_READWRITE, &h) != ESP_OK) {
        return;
    }
    nvs_set_blob(h, KEY, &rec, sizeof(rec));
    nvs_commit(h);
    nvs_close(h);
    ESP_LOGI(TAG, "mark boot @0x%lx", (unsigned long)rec.part_addr);
}

bool ota_boot_consume_success(void)
{
    if (nvs_ensure() != ESP_OK) {
        return false;
    }
    nvs_clear_legacy();

    const esp_partition_t *running = esp_ota_get_running_partition();
    esp_ota_img_states_t state;

    if (esp_ota_get_state_partition(running, &state) == ESP_OK &&
        state == ESP_OTA_IMG_PENDING_VERIFY) {
        if (esp_ota_mark_app_valid_cancel_rollback() != ESP_OK) {
            return false;
        }
        ESP_LOGI(TAG, "remote OTA (pending verify)");
        return true;
    }

    ota_pending_t rec = {0};
    nvs_handle_t h;
    if (nvs_open(NS, NVS_READWRITE, &h) != ESP_OK) {
        return false;
    }
    size_t len = sizeof(rec);
    esp_err_t err = nvs_get_blob(h, KEY, &rec, &len);
    nvs_erase_key(h, KEY);
    nvs_commit(h);
    nvs_close(h);

    if (err != ESP_OK || len != sizeof(rec) || rec.magic != MAGIC) {
        return false;
    }
    if (running->address != rec.part_addr) {
        return false;
    }
    ESP_LOGI(TAG, "remote OTA (nvs match)");
    return true;
}
