#ifndef DISPLAY_PACK_H
#define DISPLAY_PACK_H

#include <stdint.h>
#include <stdbool.h>
#include "pico/stdlib.h"

// Display dimensions - Updated for full 320x240 display
#define DISPLAY_WIDTH 320
#define DISPLAY_HEIGHT 240

// Colors (RGB565 format)
#define COLOR_BLACK     0x0000
#define COLOR_WHITE     0xFFFF
#define COLOR_RED       0xF800
#define COLOR_GREEN     0x07E0
#define COLOR_BLUE      0x001F
#define COLOR_YELLOW    0xFFE0
#define COLOR_CYAN      0x07FF
#define COLOR_MAGENTA   0xF81F

// Button definitions
typedef enum {
    BUTTON_A = 0,
    BUTTON_B = 1,
    BUTTON_X = 2,
    BUTTON_Y = 3
} button_t;

// Button callback function type
typedef void (*button_callback_t)(button_t button);

// Display functions
bool display_pack_init(void);
void display_clear(uint16_t color);
void display_fill_rect(uint16_t x, uint16_t y, uint16_t width, uint16_t height, uint16_t color);
void display_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
void display_draw_char(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg_color);
void display_draw_string(uint16_t x, uint16_t y, const char* str, uint16_t color, uint16_t bg_color);
void display_set_backlight(bool on);

// Button functions
void buttons_init(void);
void buttons_update(void);
bool button_pressed(button_t button);
bool button_just_pressed(button_t button);
bool button_just_released(button_t button);
void button_set_callback(button_t button, button_callback_t callback);

#endif // DISPLAY_PACK_H