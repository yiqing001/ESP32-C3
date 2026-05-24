#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

/**
 * 摇杆 GPIO（低电平=按下，内部上拉）
 * 实机标定：UP/DOWN 对调(IO5/IO8)，UP/RIGHT 对调(IO5/IO13)
 */
#define JOYSTICK_GPIO_LEFT    9
#define JOYSTICK_GPIO_UP      13
#define JOYSTICK_GPIO_CENTER  4
#define JOYSTICK_GPIO_DOWN    8
#define JOYSTICK_GPIO_RIGHT   5

/** 按键位掩码 */
typedef enum {
    JOYSTICK_MASK_UP     = (1u << 0),
    JOYSTICK_MASK_DOWN   = (1u << 1),
    JOYSTICK_MASK_LEFT   = (1u << 2),
    JOYSTICK_MASK_RIGHT  = (1u << 3),
    JOYSTICK_MASK_CENTER = (1u << 4),
} joystick_mask_t;

typedef struct {
    uint32_t held;     /**< 当前稳定按下的键 */
    uint32_t pressed;  /**< 本周期新按下 */
    uint32_t released; /**< 本周期新松开 */
} joystick_event_t;

/** 初始化五路输入（上拉） */
esp_err_t joystick_init(void);

/** 读取当前按下状态（已消抖） */
uint32_t joystick_read(void);

/** 轮询边沿事件，建议 20~50ms 调用一次 */
void joystick_poll(joystick_event_t *event);

/** 将掩码转为可读字符串，写入 buf（如 "UP+LEFT" 或 "-"） */
void joystick_mask_to_string(uint32_t mask, char *buf, size_t buf_len);
