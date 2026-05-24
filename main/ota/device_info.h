#pragma once

#include <stddef.h>

#define DEVICE_SN_LEN   13
#define DEVICE_NAME_LEN 32
#define DEVICE_IP_LEN   16

/** 设备标识与网络信息，供 LCD / HTTP / mDNS 共用 */
typedef struct {
    char sn[DEVICE_SN_LEN];           /* MAC 12 位十六进制 */
    char name[DEVICE_NAME_LEN];       /* 前缀-SN后6位 */
    char hostname[DEVICE_NAME_LEN];   /* mDNS 主机名（同 name） */
    char ip[DEVICE_IP_LEN];
    char mac[18];
    char version[32];
} device_info_t;

/** 从芯片 MAC 生成 SN、设备名；IP 初始为 0.0.0.0 */
void device_info_init(void);

/** WiFi 获 IP 后更新 */
void device_info_set_ip(const char *ip);

const device_info_t *device_info_get(void);
