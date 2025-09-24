#ifndef DISPLAY_H
#define DISPLAY_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Display dimensions
#define DISPLAY_WIDTH  240
#define DISPLAY_HEIGHT 135

// Display offset calibration for ST7789V2
#define COLUMN_OFFSET 40
#define ROW_OFFSET    53

// Button definitions
typedef enum {
    BUTTON_A = 0,
    BUTTON_B = 1,
    BUTTON_X = 2,
    BUTTON_Y = 3,
    BUTTON_COUNT = 4
} button_t;

// Error codes
typedef enum {
    DISPLAY_OK = 0,
    DISPLAY_ERROR_INIT_FAILED = -1,
    DISPLAY_ERROR_DMA_FAILED = -2,
    DISPLAY_ERROR_INVALID_PARAM = -3,
    DISPLAY_ERROR_NOT_INITIALIZED = -4
} display_error_t;

// Button callback type
typedef void (*button_callback_t)(button_t button);

// Display functions
display_error_t display_pack_init(void);
display_error_t display_clear(uint16_t color);
display_error_t display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color);
display_error_t display_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
display_error_t display_blit_full(const uint16_t *pixels);
display_error_t display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color);
display_error_t display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color);
display_error_t display_set_backlight(bool on);

// Button functions
display_error_t buttons_init(void);
void buttons_update(void);
bool button_pressed(button_t button);
bool button_just_pressed(button_t button);
bool button_just_released(button_t button);
display_error_t button_set_callback(button_t button, button_callback_t callback);

// Utility functions
bool display_is_initialized(void);
bool display_dma_busy(void);
void display_wait_for_dma(void);
const char* display_error_string(display_error_t error);
void display_cleanup(void);

// Common RGB565 color definitions
#define RGB565(r, g, b) ((((r) & 0xF8) << 8) | (((g) & 0xFC) << 3) | ((b) >> 3))

// Predefined colors
#define COLOR_BLACK   0x0000
#define COLOR_WHITE   0xFFFF
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_YELLOW  0xFFE0
#define COLOR_MAGENTA 0xF81F
#define COLOR_CYAN    0x07FF
#define COLOR_ORANGE  0xFC00
#define COLOR_PINK    0xF81F
#define COLOR_PURPLE  0x8010
#define COLOR_BROWN   0x8A22
#define COLOR_GRAY    0x8410
#define COLOR_DARK_GRAY 0x4208
#define COLOR_LIGHT_GRAY 0xC618

#endif // DISPLAY_H
