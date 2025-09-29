#include "hstx_display.h"
#include "hardware/resets.h"
#include "hardware/clocks.h"
#include "hardware/structs/hstx_ctrl.h"
#include "hardware/structs/hstx_fifo.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"
#include "pico/time.h"

#include <string.h>

// HSTX pin defs (Pimoroni Display Pack 2.0)
#define HSTX_DC_PIN 16
#define HSTX_CS_PIN 17
#define HSTX_SCK_PIN 18
#define HSTX_MOSI_PIN 19
#define HSTX_RESET_PIN 21
#define HSTX_BL_PIN 20

// Button pins
#define HSTX_BUTTON_A_PIN 12
#define HSTX_BUTTON_B_PIN 13
#define HSTX_BUTTON_X_PIN 14
#define HSTX_BUTTON_Y_PIN 15

// HSTX configuration
#define FIRST_HSTX_PIN 12
#define HSTX_BASE_PIN 16  // Our starting pin (DC=16 -> HSTX bit 4)

// Internal state
static bool hstx_display_initialized = false;
static volatile bool hstx_busy = false;
static bool hstx_buttons_initialized = false;

// Button state
static hstx_button_callback_t hstx_button_callbacks[HSTX_BUTTON_COUNT] = {NULL};
static volatile bool hstx_button_state[HSTX_BUTTON_COUNT] = {false};
static volatile bool hstx_button_last_state[HSTX_BUTTON_COUNT] = {false};
static volatile uint32_t hstx_last_button_check = 0;

// Button pin mapping
static const uint8_t hstx_button_pins[HSTX_BUTTON_COUNT] = {
    HSTX_BUTTON_A_PIN, HSTX_BUTTON_B_PIN, HSTX_BUTTON_X_PIN, HSTX_BUTTON_Y_PIN
};

// Fixed 5x8 font (copied from original)
static const uint8_t hstx_font5x8[][5] = {
    {0x00, 0x00, 0x00, 0x00, 0x00}, // Space
    {0x00, 0x00, 0x5F, 0x00, 0x00}, // !
    // ... (full font array from original display.c - omitted for brevity, copy all 59 entries)
    {0x43, 0x45, 0x49, 0x51, 0x61}, // Z
};

// Error strings (copied)
static const char* hstx_error_strings[] = {
    "OK",
    "Init failed",
    "HSTX operation failed",
    "Invalid parameter",
    "Display not initialised"
};

// Get time ms
static inline uint32_t hstx_get_time_ms(void) {
    return to_ms_since_boot(get_absolute_time());
}

// HSTX FIFO write (blocking)
static inline void hstx_put_word(uint32_t data) {
    while (hstx_fifo_hw->stat & HSTX_FIFO_STAT_FULL_BITS) tight_loop_contents();
    hstx_fifo_hw->fifo = data;
}

// HSTX pack for DC/CS/data (adapted from example, with DC invert note)
static inline void hstx_put_dc_cs_data(bool dc, bool cs_low, uint8_t data) {
    // Data in low 8 bits; masks generate SPI waveform (8 clocks per byte)
    // Masks adjusted? No - bit crossbar remaps to match example logic
    hstx_put_word(
        (cs_low ? 0x0FF00000u : 0x00000000u) |
        (dc ? 0x00000000u : 0x0003FC00u) |  // DC inverted in HSTX
        (uint32_t)data
    );
}

// Start command (CS low, DC low)
static inline void hstx_start_cmd(uint8_t cmd) {
    hstx_put_dc_cs_data(false, true, 0);   // CS low prep
    hstx_put_dc_cs_data(false, false, cmd); // Send cmd
}

// Send data byte (CS low, DC high)
static inline void hstx_put_data(uint8_t data) {
    hstx_put_dc_cs_data(true, false, data);
}

// HSTX init
static hstx_display_error_t hstx_init(void) {
    if (hstx_display_initialized) return HSTX_DISPLAY_OK;

    // Reset HSTX
    reset_block(RESETS_RESET_HSTX_BITS);
    unreset_block_wait(RESETS_RESET_HSTX_BITS);

    // Clock: Use USB PLL (~48 MHz base), enable
    hw_write_masked(&clocks_hw->clk[clk_hstx].ctrl,
                    CLOCKS_CLK_HSTX_CTRL_AUXSRC_VALUE_CLKSRC_PLL_USB << CLOCKS_CLK_HSTX_CTRL_AUXSRC_LSB,
                    CLOCKS_CLK_HSTX_CTRL_AUXSRC_BITS);
    clocks_hw->clk[clk_hstx].div = 1.0f;  // Full speed, adjust div for ~31.25 MHz if needed (e.g., 48/1.5 approx)

    // Set GPIO functions for HSTX pins
    gpio_set_function(HSTX_DC_PIN, GPIO_FUNC_HSTX);    // HSTX bit 4
    gpio_set_function(HSTX_CS_PIN, GPIO_FUNC_HSTX);    // bit 5
    gpio_set_function(HSTX_SCK_PIN, GPIO_FUNC_HSTX);   // bit 6
    gpio_set_function(HSTX_MOSI_PIN, GPIO_FUNC_HSTX);  // bit 7

    // Bit crossbar: Remap to match example logical bits (0=MOSI,1=SCK,2=CS,3=DC)
    // SCK (bit6): CLK mode
    hstx_ctrl_hw->bit[6] = (1u << HSTX_BIT_CLK_LSB);  // CLK=1, SEL=0 default
    // MOSI (bit7): Logical bit 0 (data)
    hstx_ctrl_hw->bit[7] = (0u << HSTX_BIT_SEL_P_LSB) | (0u << HSTX_BIT_SEL_N_LSB);
    // CS (bit5): Logical bit 2
    hstx_ctrl_hw->bit[5] = (2u << HSTX_BIT_SEL_P_LSB) | (2u << HSTX_BIT_SEL_N_LSB);
    // DC (bit4): Logical bit 3
    hstx_ctrl_hw->bit[4] = (3u << HSTX_BIT_SEL_P_LSB) | (3u << HSTX_BIT_SEL_N_LSB);
    // Unused bits 0-3: Disable/off
    for (int i = 0; i < 4; i++) hstx_ctrl_hw->bit[i] = 0;

    // Enable HSTX (1 bit/cycle for SDR SPI; adjust to 2 for DDR if needed)
    hstx_ctrl_hw->ctrl = HSTX_CTRL_ENABLED_BITS | (1u << HSTX_CTRL_NBITS_LSB);

    return HSTX_DISPLAY_OK;
}

// Write command
static hstx_display_error_t hstx_write_command(uint8_t cmd) {
    if (!hstx_display_initialized) return HSTX_DISPLAY_ERROR_NOT_INITIALIZED;
    hstx_start_cmd(cmd);
    return HSTX_DISPLAY_OK;
}

// Write single data byte
static hstx_display_error_t hstx_write_data(uint8_t data) {
    if (!hstx_display_initialized) return HSTX_DISPLAY_ERROR_NOT_INITIALIZED;
    hstx_put_data(data);
    return HSTX_DISPLAY_OK;
}

// Write data buffer (blocking loop)
static hstx_display_error_t hstx_write_data_buf(const uint8_t *data, size_t len) {
    if (!hstx_display_initialized || !data || len == 0) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    for (size_t i = 0; i < len; i++) {
        hstx_put_data(data[i]);
    }
    return HSTX_DISPLAY_OK;
}

// Set window
static hstx_display_error_t hstx_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    uint8_t buf[4];
    hstx_write_command(0x2A);  // CASET
    buf[0] = x0 >> 8; buf[1] = x0 & 0xFF; buf[2] = x1 >> 8; buf[3] = x1 & 0xFF;
    hstx_write_data_buf(buf, 4);

    hstx_write_command(0x2B);  // RASET
    buf[0] = y0 >> 8; buf[1] = y0 & 0xFF; buf[2] = y1 >> 8; buf[3] = y1 & 0xFF;
    hstx_write_data_buf(buf, 4);

    hstx_write_command(0x2C);  // RAMWR
    return HSTX_DISPLAY_OK;
}

// Public init (ST7789V2 sequence from original)
hstx_display_error_t hstx_display_pack_init(void) {
    if (hstx_display_initialized) return HSTX_DISPLAY_OK;

    // HSTX init
    if (hstx_init() != HSTX_DISPLAY_OK) return HSTX_DISPLAY_ERROR_HSTX_FAILED;

    // GPIO for control pins
    gpio_init(HSTX_CS_PIN); gpio_set_dir(HSTX_CS_PIN, GPIO_OUT); gpio_put(HSTX_CS_PIN, 1);
    gpio_init(HSTX_DC_PIN); gpio_set_dir(HSTX_DC_PIN, GPIO_OUT); gpio_put(HSTX_DC_PIN, 1);
    gpio_init(HSTX_RESET_PIN); gpio_set_dir(HSTX_RESET_PIN, GPIO_OUT);
    gpio_init(HSTX_BL_PIN); gpio_set_dir(HSTX_BL_PIN, GPIO_OUT); gpio_put(HSTX_BL_PIN, 0);

    // Reset sequence
    gpio_put(HSTX_RESET_PIN, 1); sleep_ms(10);
    gpio_put(HSTX_RESET_PIN, 0); sleep_ms(10);
    gpio_put(HSTX_RESET_PIN, 1); sleep_ms(120);

    hstx_display_initialized = true;

    // ST7789V2 init (from original, using HSTX writes)
    hstx_write_command(0x01); sleep_ms(150);  // SWRESET
    hstx_write_command(0x11); sleep_ms(120);  // SLPOUT
    hstx_write_command(0x3A); hstx_write_data(0x55);  // COLMOD 16-bit
    hstx_write_command(0x36); hstx_write_data(0x70);  // MADCTL

    // Full window 320x240
    hstx_write_command(0x2A); hstx_write_data(0x00); hstx_write_data(0x00); hstx_write_data(0x01); hstx_write_data(0x3F);
    hstx_write_command(0x2B); hstx_write_data(0x00); hstx_write_data(0x00); hstx_write_data(0x00); hstx_write_data(0xEF);

    // Additional settings (from original - abbreviated)
    hstx_write_command(0xB2); hstx_write_data_buf((uint8_t[]){0x0C,0x0C,0x00,0x33,0x33}, 5);
    hstx_write_command(0xB7); hstx_write_data(0x35);
    hstx_write_command(0xBB); hstx_write_data(0x19);
    hstx_write_command(0xC0); hstx_write_data(0x2C);
    hstx_write_command(0xC2); hstx_write_data(0x01);
    hstx_write_command(0xC3); hstx_write_data(0x12);
    hstx_write_command(0xC4); hstx_write_data(0x20);
    hstx_write_command(0xC6); hstx_write_data(0x0F);
    hstx_write_command(0xD0); hstx_write_data_buf((uint8_t[]){0xA4,0xA1}, 2);

    // Gamma (abbreviated)
    hstx_write_command(0xE0); hstx_write_data_buf((uint8_t[]){0xD0,0x04,0x0D,0x11,0x13,0x2B,0x3F,0x54,0x4C,0x18,0x0D,0x0B,0x1F,0x23}, 14);
    hstx_write_command(0xE1); hstx_write_data_buf((uint8_t[]){0xD0,0x04,0x0C,0x11,0x13,0x2C,0x3F,0x44,0x51,0x2F,0x1F,0x1F,0x20,0x23}, 14);

    hstx_write_command(0x21);  // INVON
    hstx_write_command(0x13); sleep_ms(10);  // NORON
    hstx_write_command(0x29); sleep_ms(100); // DISPON

    gpio_put(HSTX_BL_PIN, 1);  // Backlight on

    return HSTX_DISPLAY_OK;
}

// Other functions (fill_rect, draw_pixel, etc. - adapted from original, using hstx_set_window and hstx_put_data for pixels)
hstx_display_error_t hstx_display_clear(uint16_t color) {
    return hstx_display_fill_rect(0, 0, HSTX_DISPLAY_WIDTH, HSTX_DISPLAY_HEIGHT, color);
}

hstx_display_error_t hstx_display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color) {
    if (!hstx_display_initialized) return HSTX_DISPLAY_ERROR_NOT_INITIALIZED;
    if (x >= HSTX_DISPLAY_WIDTH || y >= HSTX_DISPLAY_HEIGHT || width == 0 || height == 0) return HSTX_DISPLAY_ERROR_INVALID_PARAM;

    // Clamp
    if (x + width > HSTX_DISPLAY_WIDTH) width = HSTX_DISPLAY_WIDTH - x;
    if (y + height > HSTX_DISPLAY_HEIGHT) height = HSTX_DISPLAY_HEIGHT - y;

    uint32_t pixels = (uint32_t)width * height;
    hstx_display_error_t err = hstx_set_window(x, y, x + width - 1, y + height - 1);
    if (err != HSTX_DISPLAY_OK) return err;

    uint8_t color_high = color >> 8;
    uint8_t color_low = color & 0xFF;
    for (uint32_t i = 0; i < pixels; i++) {
        hstx_put_data(color_high);
        hstx_put_data(color_low);
    }
    return HSTX_DISPLAY_OK;
}

hstx_display_error_t hstx_display_draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    if (x >= HSTX_DISPLAY_WIDTH || y >= HSTX_DISPLAY_HEIGHT) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    return hstx_display_fill_rect(x, y, 1, 1, color);
}

hstx_display_error_t hstx_display_blit_full(const uint16_t *pixels) {
    if (!hstx_display_initialized || !pixels) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    hstx_display_error_t err = hstx_set_window(0, 0, HSTX_DISPLAY_WIDTH - 1, HSTX_DISPLAY_HEIGHT - 1);
    if (err != HSTX_DISPLAY_OK) return err;
    for (uint32_t i = 0; i < (uint32_t)HSTX_DISPLAY_WIDTH * HSTX_DISPLAY_HEIGHT; i++) {
        hstx_put_data(pixels[i] >> 8);
        hstx_put_data(pixels[i] & 0xFF);
    }
    return HSTX_DISPLAY_OK;
}

// draw_char and draw_string (copied from original, using hstx_display_draw_pixel)
hstx_display_error_t hstx_display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color) {
    if (!hstx_display_initialized || x >= HSTX_DISPLAY_WIDTH || y >= HSTX_DISPLAY_HEIGHT) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    if (c < 32 || c > 90) c = 32;
    const uint8_t *char_data = hstx_font5x8[c - 32];
    for (int col = 0; col < 5 && (x + col) < HSTX_DISPLAY_WIDTH; col++) {
        uint8_t line = char_data[4 - col];
        for (int row = 0; row < 8 && (y + row) < HSTX_DISPLAY_HEIGHT; row++) {
            uint16_t pixel_color = (line & (1 << row)) ? color : bg_color;
            hstx_display_draw_pixel(x + col, y + row, pixel_color);
        }
    }
    return HSTX_DISPLAY_OK;
}

hstx_display_error_t hstx_display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color) {
    if (!hstx_display_initialized || !str || x >= HSTX_DISPLAY_WIDTH || y >= HSTX_DISPLAY_HEIGHT) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    int offset_x = 0;
    while (*str && (x + offset_x) < HSTX_DISPLAY_WIDTH) {
        hstx_display_error_t err = hstx_display_draw_char(x + offset_x, y, *str, color, bg_color);
        if (err != HSTX_DISPLAY_OK) return err;
        offset_x += 6;
        str++;
    }
    return HSTX_DISPLAY_OK;
}

hstx_display_error_t hstx_display_set_backlight(bool on) {
    if (!hstx_display_initialized) return HSTX_DISPLAY_ERROR_NOT_INITIALIZED;
    gpio_put(HSTX_BL_PIN, on ? 1 : 0);
    return HSTX_DISPLAY_OK;
}

// Button functions (copied from original)
hstx_display_error_t hstx_buttons_init(void) {
    if (hstx_buttons_initialized) return HSTX_DISPLAY_OK;
    for (int i = 0; i < HSTX_BUTTON_COUNT; i++) {
        gpio_init(hstx_button_pins[i]);
        gpio_set_dir(hstx_button_pins[i], GPIO_IN);
        gpio_pull_up(hstx_button_pins[i]);
        hstx_button_state[i] = true;
        hstx_button_last_state[i] = true;
        hstx_button_callbacks[i] = NULL;
    }
    hstx_buttons_initialized = true;
    return HSTX_DISPLAY_OK;
}

void hstx_buttons_update(void) {
    if (!hstx_buttons_initialized) return;
    uint32_t now = hstx_get_time_ms();
    if (now - hstx_last_button_check < 50) return;
    hstx_last_button_check = now;
    for (int i = 0; i < HSTX_BUTTON_COUNT; i++) {
        hstx_button_last_state[i] = hstx_button_state[i];
        hstx_button_state[i] = gpio_get(hstx_button_pins[i]);
        if (hstx_button_last_state[i] && !hstx_button_state[i] && hstx_button_callbacks[i]) {
            hstx_button_callbacks[i]((hstx_button_t)i);
        }
    }
}

bool hstx_button_pressed(hstx_button_t button) {
    if (!hstx_buttons_initialized || button >= HSTX_BUTTON_COUNT) return false;
    return !hstx_button_state[button];
}

bool hstx_button_just_pressed(hstx_button_t button) {
    if (!hstx_buttons_initialized || button >= HSTX_BUTTON_COUNT) return false;
    return hstx_button_last_state[button] && !hstx_button_state[button];
}

bool hstx_button_just_released(hstx_button_t button) {
    if (!hstx_buttons_initialized || button >= HSTX_BUTTON_COUNT) return false;
    return !hstx_button_last_state[button] && hstx_button_state[button];
}

hstx_display_error_t hstx_button_set_callback(hstx_button_t button, hstx_button_callback_t callback) {
    if (!hstx_buttons_initialized || button >= HSTX_BUTTON_COUNT) return HSTX_DISPLAY_ERROR_INVALID_PARAM;
    uint32_t ints = save_and_disable_interrupts();
    hstx_button_callbacks[button] = callback;
    restore_interrupts(ints);
    return HSTX_DISPLAY_OK;
}

// Utilities (adapted)
bool hstx_display_is_initialized(void) { return hstx_display_initialized; }
bool hstx_display_hstx_busy(void) { return hstx_busy; }  // Stub - HSTX is polled
void hstx_display_wait_for_hstx(void) { tight_loop_contents(); }  // No DMA
const char* hstx_display_error_string(hstx_display_error_t error) {
    if (error < 0 || error >= (sizeof(hstx_error_strings) / sizeof(hstx_error_strings[0]))) return "Unknown error";
    return hstx_error_strings[error];
}

void hstx_display_cleanup(void) {
    hstx_display_wait_for_hstx();
    if (hstx_display_initialized) {
        hstx_ctrl_hw->ctrl = 0;  // Disable HSTX
        gpio_put(HSTX_BL_PIN, 0);
    }
    hstx_display_initialized = false;
    hstx_buttons_initialized = false;
    for (int i = 0; i < HSTX_BUTTON_COUNT; i++) hstx_button_callbacks[i] = NULL;
}
