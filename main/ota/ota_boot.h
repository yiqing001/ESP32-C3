#pragma once

#include <stdbool.h>
#include "esp_partition.h"

/** HTTP OTA 写入完成、即将重启前调用（传入即将启动的分区） */
void ota_boot_mark_remote_ota(const esp_partition_t *boot_part);

/**
 * 启动时调用：仅当上次为远程 OTA 且当前从对应分区启动时返回 true（仅一次）。
 * USB 烧录不会调用 mark，也不会误显示 OTA OK。
 */
bool ota_boot_consume_success(void);
