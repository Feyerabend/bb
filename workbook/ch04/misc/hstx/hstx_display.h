#ifndef HSTX_DISPLAY_H
#define HSTX_DISPLAY_H

#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"

// Display Pack 2.0 specifications: 320x240 pixels
#define HSTX_DISPLAY_WIDTH 320
#define HSTX_DISPLAY_HEIGHT 240

// Colors (RGB565 format)
#define HSTX_COLOR_BLACK     0x0000
#define HSTX_COLOR_WHITE     0xFFFF
#define HSTX_COLOR_RED       0xF800
#define HSTX_COLOR_GREEN     0x07E0
#define HSTX_COLOR_BLUE      0x001F
#define HSTX_COLOR_YELLOW    0xFFE0
#define HSTX_COLOR_CYAN      0x07FF
#define HSTX_COLOR_MAGENTA   0xF81F

// Button definitions
typedef enum {
    HSTX_BUTTON_A = 0,
    HSTX_BUTTON_B = 1,
    HSTX_BUTTON_X = 2,
    HSTX_BUTTON_Y = 3,
    HSTX_BUTTON_COUNT = 4  // Added for bounds checking
} hstx_button_t;

// Button callback function type
typedef void (*hstx_button_callback_t)(hstx_button_t button);

// Error codes
typedef enum {
    HSTX_DISPLAY_OK = 0,
    HSTX_DISPLAY_ERROR_INIT_FAILED,
    HSTX_DISPLAY_ERROR_HSTX_FAILED,
    HSTX_DISPLAY_ERROR_INVALID_PARAM,
    HSTX_DISPLAY_ERROR_NOT_INITIALIZED
} hstx_display_error_t;

// Display functions
hstx_display_error_t hstx_display_pack_init(void);
hstx_display_error_t hstx_display_clear(uint16_t color);
hstx_display_error_t hstx_display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color);
hstx_display_error_t hstx_display_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
hstx_display_error_t hstx_display_blit_full(const uint16_t *pixels);
hstx_display_error_t hstx_display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color);
hstx_display_error_t hstx_display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color);
hstx_display_error_t hstx_display_set_backlight(bool on);

// Button functions
hstx_display_error_t hstx_buttons_init(void);
void hstx_buttons_update(void);
bool hstx_button_pressed(hstx_button_t button);
bool hstx_button_just_pressed(hstx_button_t button);
bool hstx_button_just_released(hstx_button_t button);
hstx_display_error_t hstx_button_set_callback(hstx_button_t button, hstx_button_callback_t callback);

// Utility functions
bool hstx_display_is_initialized(void);
bool hstx_display_hstx_busy(void);
void hstx_display_wait_for_hstx(void);
void hstx_display_cleanup(void);
const char* hstx_display_error_string(hstx_display_error_t error);

#endif // HSTX_DISPLAY_H
