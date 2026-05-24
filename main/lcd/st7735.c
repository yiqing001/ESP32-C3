/* ST7735 驱动：Air101-LCD 160×80，SPI，横向显示 */

#include "st7735.h"
#include "font8x8.h"

#include <string.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "st7735";

/* README 接线表 */
#define PIN_LCD_SCK   2
#define PIN_LCD_MOSI  3
#define PIN_LCD_RST   10
#define PIN_LCD_DC    6
#define PIN_LCD_CS    7
#define PIN_LCD_BL    11

#define ST7735_CMD_SWRESET  0x01
#define ST7735_CMD_SLPOUT     0x11
#define ST7735_CMD_DISPON     0x29
#define ST7735_CMD_CASET      0x2A
#define ST7735_CMD_RASET      0x2B
#define ST7735_CMD_RAMWR      0x2C
#define ST7735_CMD_COLMOD     0x3A
#define ST7735_CMD_MADCTL     0x36
#define ST7735_CMD_INVOFF     0x20
#define ST7735_CMD_INVON      0x21
#define ST7735_CMD_NORON      0x13
#define ST7735_CMD_FRMCTR1    0xB1
#define ST7735_CMD_FRMCTR2    0xB2
#define ST7735_CMD_FRMCTR3    0xB3
#define ST7735_CMD_INVCTR     0xB4
#define ST7735_CMD_PWCTR1     0xC0
#define ST7735_CMD_PWCTR2     0xC1
#define ST7735_CMD_PWCTR3     0xC2
#define ST7735_CMD_PWCTR4     0xC3
#define ST7735_CMD_PWCTR5     0xC4
#define ST7735_CMD_VMCTR1     0xC5
#define ST7735_CMD_GMCTRP1    0xE0
#define ST7735_CMD_GMCTRN1    0xE1

#define ST7735_MADCTL_MY  0x80
#define ST7735_MADCTL_MX  0x40
#define ST7735_MADCTL_MV  0x20
#define ST7735_MADCTL_BGR 0x08

/*
 * Air101-LCD ≈ Adafruit INITR_MINI160x80_PLUGIN (160×80, GREENTAB plugin FPC)
 * 横向 160×80，MADCTL=0xE8 (MY|MV|MX|BGR)
 * 偏移：rowstart=1 → CASET，colstart=26 → RASET（勿把 26 加到 X）
 */
#define ST7735_MADCTL_LANDSCAPE  (ST7735_MADCTL_MY | ST7735_MADCTL_MV | ST7735_MADCTL_MX | ST7735_MADCTL_BGR)

#define ST7735_ROWSTART  1
#define ST7735_COLSTART  26

static spi_device_handle_t s_spi;
static uint8_t s_madctl = ST7735_MADCTL_LANDSCAPE;

static void st7735_gpio_init(void)
{
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_LCD_RST) | (1ULL << PIN_LCD_DC) | (1ULL << PIN_LCD_BL),
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&io);
    gpio_set_level(PIN_LCD_RST, 1);
    gpio_set_level(PIN_LCD_DC, 1);
    gpio_set_level(PIN_LCD_BL, 0);
}

/** DC=0 命令 / DC=1 数据，SPI 轮询发送 */
static void st7735_spi_send(const uint8_t *data, size_t len, bool is_data)
{
    gpio_set_level(PIN_LCD_DC, is_data ? 1 : 0);
    spi_transaction_t t = {
        .length = len * 8,
        .tx_buffer = data,
    };
    ESP_ERROR_CHECK(spi_device_polling_transmit(s_spi, &t));
}

static void st7735_write_cmd(uint8_t cmd)
{
    st7735_spi_send(&cmd, 1, false);
}

static void st7735_write_data(const uint8_t *data, size_t len)
{
    st7735_spi_send(data, len, true);
}

static void st7735_write_data_byte(uint8_t byte)
{
    st7735_write_data(&byte, 1);
}

static void st7735_reset(void)
{
    gpio_set_level(PIN_LCD_RST, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(PIN_LCD_RST, 1);
    vTaskDelay(pdMS_TO_TICKS(120));
}

/** GREENTAB160x80 PLUGIN 初始化序列 */
static void st7735_init_sequence(void)
{
    st7735_reset();

    st7735_write_cmd(ST7735_CMD_SWRESET);
    vTaskDelay(pdMS_TO_TICKS(150));

    st7735_write_cmd(ST7735_CMD_SLPOUT);
    vTaskDelay(pdMS_TO_TICKS(255));

    const uint8_t frmctr1[] = {0x01, 0x2C, 0x2D};
    st7735_write_cmd(ST7735_CMD_FRMCTR1);
    st7735_write_data(frmctr1, sizeof(frmctr1));

    const uint8_t frmctr2[] = {0x01, 0x2C, 0x2D};
    st7735_write_cmd(ST7735_CMD_FRMCTR2);
    st7735_write_data(frmctr2, sizeof(frmctr2));

    const uint8_t frmctr3[] = {0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D};
    st7735_write_cmd(ST7735_CMD_FRMCTR3);
    st7735_write_data(frmctr3, sizeof(frmctr3));

    st7735_write_cmd(ST7735_CMD_INVCTR);
    st7735_write_data_byte(0x07);

    const uint8_t pwctr1[] = {0xA2, 0x02, 0x84};
    st7735_write_cmd(ST7735_CMD_PWCTR1);
    st7735_write_data(pwctr1, sizeof(pwctr1));

    st7735_write_cmd(ST7735_CMD_PWCTR2);
    st7735_write_data_byte(0xC5);

    const uint8_t pwctr3[] = {0x0A, 0x00};
    st7735_write_cmd(ST7735_CMD_PWCTR3);
    st7735_write_data(pwctr3, sizeof(pwctr3));

    const uint8_t pwctr4[] = {0x8A, 0x2A};
    st7735_write_cmd(ST7735_CMD_PWCTR4);
    st7735_write_data(pwctr4, sizeof(pwctr4));

    const uint8_t pwctr5[] = {0x8A, 0xEE};
    st7735_write_cmd(ST7735_CMD_PWCTR5);
    st7735_write_data(pwctr5, sizeof(pwctr5));

    st7735_write_cmd(ST7735_CMD_VMCTR1);
    st7735_write_data_byte(0x0E);

    st7735_write_cmd(ST7735_CMD_INVOFF);

    st7735_write_cmd(ST7735_CMD_MADCTL);
    st7735_write_data_byte(s_madctl);

    st7735_write_cmd(ST7735_CMD_COLMOD);
    st7735_write_data_byte(0x05);  /* 16-bit RGB565 */

    st7735_write_cmd(ST7735_CMD_INVON);

    /* 物理窗口 80×160，配合 MADCTL 呈现 160×80 横向 */
    const uint8_t caset[] = {0x00, 0x00, 0x00, 0x4F};
    st7735_write_cmd(ST7735_CMD_CASET);
    st7735_write_data(caset, sizeof(caset));

    const uint8_t raset[] = {0x00, 0x00, 0x00, 0x9F};
    st7735_write_cmd(ST7735_CMD_RASET);
    st7735_write_data(raset, sizeof(raset));

    const uint8_t gmctrp[] = {
        0x02, 0x1c, 0x07, 0x12, 0x37, 0x32, 0x29, 0x2d,
        0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10,
    };
    st7735_write_cmd(ST7735_CMD_GMCTRP1);
    st7735_write_data(gmctrp, sizeof(gmctrp));

    const uint8_t gmctrn[] = {
        0x03, 0x1d, 0x07, 0x06, 0x2E, 0x2C, 0x29, 0x2D,
        0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10,
    };
    st7735_write_cmd(ST7735_CMD_GMCTRN1);
    st7735_write_data(gmctrn, sizeof(gmctrn));

    st7735_write_cmd(ST7735_CMD_NORON);
    vTaskDelay(pdMS_TO_TICKS(10));

    st7735_write_cmd(ST7735_CMD_DISPON);
    vTaskDelay(pdMS_TO_TICKS(100));
}

/** 设置逻辑坐标绘图窗口，自动加 PLUGIN 屏 row/col 偏移 */
static void st7735_set_window(uint16_t x, uint16_t y, uint16_t w, uint16_t h)
{
    uint16_t x0 = x + ST7735_ROWSTART;
    uint16_t x1 = x + w - 1 + ST7735_ROWSTART;
    uint16_t y0 = y + ST7735_COLSTART;
    uint16_t y1 = y + h - 1 + ST7735_COLSTART;

    uint8_t caset[] = {
        (uint8_t)(x0 >> 8), (uint8_t)(x0 & 0xFF),
        (uint8_t)(x1 >> 8), (uint8_t)(x1 & 0xFF),
    };
    uint8_t raset[] = {
        (uint8_t)(y0 >> 8), (uint8_t)(y0 & 0xFF),
        (uint8_t)(y1 >> 8), (uint8_t)(y1 & 0xFF),
    };

    st7735_write_cmd(ST7735_CMD_CASET);
    st7735_write_data(caset, sizeof(caset));
    st7735_write_cmd(ST7735_CMD_RASET);
    st7735_write_data(raset, sizeof(raset));
    st7735_write_cmd(ST7735_CMD_RAMWR);
}

/** RGB565 高字节在前，分块写入显存 */
static void st7735_write_pixels(const uint16_t *pixels, size_t count)
{
    const size_t chunk = 128;
    uint8_t buf[chunk * 2];

    while (count > 0) {
        size_t n = count > chunk ? chunk : count;
        for (size_t i = 0; i < n; i++) {
            buf[i * 2] = (uint8_t)(pixels[i] >> 8);
            buf[i * 2 + 1] = (uint8_t)(pixels[i] & 0xFF);
        }
        st7735_write_data(buf, n * 2);
        pixels += n;
        count -= n;
    }
}

esp_err_t st7735_init(void)
{
    st7735_gpio_init();

    spi_bus_config_t buscfg = {
        .mosi_io_num = PIN_LCD_MOSI,
        .miso_io_num = -1,
        .sclk_io_num = PIN_LCD_SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = ST7735_LCD_WIDTH * ST7735_LCD_HEIGHT * 2,
    };
    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "spi_bus_initialize failed: %s", esp_err_to_name(ret));
        return ret;
    }

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 10 * 1000 * 1000,
        .mode = 0,
        .spics_io_num = PIN_LCD_CS,
        .queue_size = 1,
    };
    ret = spi_bus_add_device(SPI2_HOST, &devcfg, &s_spi);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "spi_bus_add_device failed: %s", esp_err_to_name(ret));
        return ret;
    }

    st7735_init_sequence();
    ESP_LOGI(TAG, "ST7735 init (PLUGIN 160x80, MADCTL=0x%02X)", s_madctl);
    return ESP_OK;
}

void st7735_backlight(bool on)
{
    gpio_set_level(PIN_LCD_BL, on ? 1 : 0);
}

void st7735_fill_screen(uint16_t color)
{
    st7735_set_window(0, 0, ST7735_LCD_WIDTH, ST7735_LCD_HEIGHT);

    const size_t pixels = (size_t)ST7735_LCD_WIDTH * ST7735_LCD_HEIGHT;
    uint16_t chunk[64];
    for (size_t i = 0; i < sizeof(chunk) / sizeof(chunk[0]); i++) {
        chunk[i] = color;
    }

    size_t left = pixels;
    while (left > 0) {
        size_t n = left > (sizeof(chunk) / sizeof(chunk[0])) ? (sizeof(chunk) / sizeof(chunk[0])) : left;
        st7735_write_pixels(chunk, n);
        left -= n;
    }
}

static const uint8_t *font_glyph(char c)
{
    if (c < 32 || c > 126) {
        c = '?';
    }
    return font8x8_basic[c - 32];
}

void st7735_draw_string(uint16_t x, uint16_t y, const char *text,
                        uint16_t fg, uint16_t bg, uint8_t scale)
{
    if (!text || scale == 0) {
        return;
    }

    const size_t len = strlen(text);
    if (len == 0) {
        return;
    }

    const uint16_t char_w = (uint16_t)(8 * scale);
    const uint16_t char_h = (uint16_t)(8 * scale);
    const uint16_t total_w = (uint16_t)(len * char_w);
    const uint16_t total_h = char_h;

    if (x >= ST7735_LCD_WIDTH || y >= ST7735_LCD_HEIGHT) {
        return;
    }

    uint16_t draw_w = total_w;
    uint16_t draw_h = total_h;
    if (x + draw_w > ST7735_LCD_WIDTH) {
        draw_w = ST7735_LCD_WIDTH - x;
    }
    if (y + draw_h > ST7735_LCD_HEIGHT) {
        draw_h = ST7735_LCD_HEIGHT - y;
    }

    static uint16_t s_fb[ST7735_LCD_WIDTH * 32];
    const size_t buf_pixels = (size_t)draw_w * draw_h;
    if (buf_pixels > sizeof(s_fb) / sizeof(s_fb[0])) {
        ESP_LOGW(TAG, "draw_string buffer overflow");
        return;
    }

    for (size_t i = 0; i < buf_pixels; i++) {
        s_fb[i] = bg;
    }

    /* 先渲染到缓冲区，再一次 set_window 写入，减少 SPI 窗口切换 */
    uint16_t pen_x = 0;
    for (size_t ci = 0; text[ci] != '\0' && pen_x < draw_w; ci++) {
        const uint8_t *glyph = font_glyph(text[ci]);
        for (uint8_t row = 0; row < 8; row++) {
            uint8_t bits = glyph[row];
            for (uint8_t col = 0; col < 8; col++) {
                if (bits & (0x80 >> col)) {
                    const uint16_t px = pen_x + (uint16_t)(col * scale);
                    const uint16_t py = (uint16_t)(row * scale);
                    for (uint8_t sy = 0; sy < scale; sy++) {
                        for (uint8_t sx = 0; sx < scale; sx++) {
                            const uint16_t dx = px + sx;
                            const uint16_t dy = py + sy;
                            if (dx < draw_w && dy < draw_h) {
                                s_fb[(size_t)dy * draw_w + dx] = fg;
                            }
                        }
                    }
                }
            }
        }
        pen_x += char_w;
    }

    st7735_set_window(x, y, draw_w, draw_h);
    st7735_write_pixels(s_fb, buf_pixels);
}
