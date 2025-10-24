#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "display.h"
#include "test_pattern.h"

typedef enum {
    MODE_TEST_PATTERN,
    MODE_COLOR_DEMO,
    MODE_RGB_BREAKDOWN
} display_mode_t;

static display_mode_t current_mode = MODE_TEST_PATTERN;
static int current_color_index = 0;
static bool need_redraw = true;


void draw_test_pattern(void) {
    // Simple 5x pixel scaling to fill 320x240 from 64x48 (should work)
    for (int y = 0; y < TEST_PATTERN_HEIGHT; y++) {
        for (int x = 0; x < TEST_PATTERN_WIDTH; x++) {
            uint16_t color = test_pattern[y][x];
            // Draw 5x5 pixel block
            display_fill_rect(x * 5, y * 5, 5, 5, color);
        }
    }
    
    display_fill_rect(0, 0, 320, 20, COLOR_BLACK);
    display_draw_string(10, 6, "TV TEST PATTERN - Press B", COLOR_WHITE, COLOR_BLACK);
}


void draw_color_demo(void) {
    display_clear(COLOR_BLACK);
    
    const color_info_t *info = &color_palette[current_color_index];
    
    // Large colour swatch in center
    display_fill_rect(60, 60, 200, 120, info->color);
    
    // Draw border around swatch
    display_fill_rect(58, 58, 204, 2, COLOR_WHITE);   // Top
    display_fill_rect(58, 180, 204, 2, COLOR_WHITE);  // Bottom
    display_fill_rect(58, 58, 2, 124, COLOR_WHITE);   // Left
    display_fill_rect(260, 58, 2, 124, COLOR_WHITE);  // Right
    
    // Title bar
    display_fill_rect(0, 0, 320, 25, 0x2104);
    display_draw_string(10, 8, "COLOR PALETTE DEMO", COLOR_WHITE, 0x2104);
    
    // Colour name
    char name_buf[32];
    snprintf(name_buf, sizeof(name_buf), "Colour: %s", info->name);
    display_draw_string(10, 35, name_buf, COLOR_WHITE, COLOR_BLACK);
    
    // RGB565 value
    char hex_buf[32];
    snprintf(hex_buf, sizeof(hex_buf), "RGB565: 0x%04X", info->color);
    display_draw_string(10, 190, hex_buf, COLOR_CYAN, COLOR_BLACK);
    
    // Component breakdown
    char comp_buf[32];
    snprintf(comp_buf, sizeof(comp_buf), "R:%02d G:%02d B:%02d (5:6:5 bit)", 
             info->r_bits, info->g_bits, info->b_bits);
    display_draw_string(10, 202, comp_buf, COLOR_YELLOW, COLOR_BLACK);
    
    // Instructions
    display_draw_string(10, 220, "A:Prev X:Next Y:RGB Mode", COLOR_WHITE, COLOR_BLACK);
}


void draw_rgb_breakdown(void) {
    display_clear(COLOR_BLACK);
    
    const color_info_t *info = &color_palette[current_color_index];
    
    // Title
    display_fill_rect(0, 0, 320, 25, 0x2104);
    display_draw_string(10, 8, "RGB565 BREAKDOWN", COLOR_WHITE, 0x2104);
    
    char name_buf[32];
    snprintf(name_buf, sizeof(name_buf), "%s (0x%04X)", info->name, info->color);
    display_draw_string(10, 35, name_buf, COLOR_WHITE, COLOR_BLACK);
    
    // Draw RGB component bars
    int bar_y = 60;
    int bar_height = 35;
    int bar_spacing = 45;
    
    // Red component (5 bits: 0-31)
    display_draw_string(10, bar_y - 12, "RED (5-bit):", COLOR_RED, COLOR_BLACK);
    int red_width = (info->r_bits * 280) / 31;  // Scale to 280 pixels
    display_fill_rect(20, bar_y, 280, bar_height, 0x2104);  // Background
    display_fill_rect(20, bar_y, red_width, bar_height, COLOR_RED);
    char val_buf[16];
    snprintf(val_buf, sizeof(val_buf), "%d/31", info->r_bits);
    display_draw_string(310 - strlen(val_buf) * 6, bar_y + 13, val_buf, COLOR_WHITE, COLOR_BLACK);
    
    // Green component (6 bits: 0-63)
    bar_y += bar_spacing;
    display_draw_string(10, bar_y - 12, "GREEN (6-bit):", COLOR_GREEN, COLOR_BLACK);
    int green_width = (info->g_bits * 280) / 63;  // Scale to 280 pixels
    display_fill_rect(20, bar_y, 280, bar_height, 0x2104);  // Background
    display_fill_rect(20, bar_y, green_width, bar_height, COLOR_GREEN);
    snprintf(val_buf, sizeof(val_buf), "%d/63", info->g_bits);
    display_draw_string(310 - strlen(val_buf) * 6, bar_y + 13, val_buf, COLOR_WHITE, COLOR_BLACK);
    
    // Blue component (5 bits: 0-31)
    bar_y += bar_spacing;
    display_draw_string(10, bar_y - 12, "BLUE (5-bit):", COLOR_BLUE, COLOR_BLACK);
    int blue_width = (info->b_bits * 280) / 31;  // Scale to 280 pixels
    display_fill_rect(20, bar_y, 280, bar_height, 0x2104);  // Background
    display_fill_rect(20, bar_y, blue_width, bar_height, COLOR_BLUE);
    snprintf(val_buf, sizeof(val_buf), "%d/31", info->b_bits);
    display_draw_string(310 - strlen(val_buf) * 6, bar_y + 13, val_buf, COLOR_WHITE, COLOR_BLACK);
    
    // Instructions
    display_draw_string(10, 220, "A:Prev X:Next B:Pattern", COLOR_WHITE, COLOR_BLACK);
}


void redraw_display(void) {
    switch (current_mode) {
        case MODE_TEST_PATTERN:
            draw_test_pattern();
            break;
        case MODE_COLOR_DEMO:
            draw_color_demo();
            break;
        case MODE_RGB_BREAKDOWN:
            draw_rgb_breakdown();
            break;
    }
    need_redraw = false;
}


void on_button_a(button_t button) {
    (void)button;
    if (current_mode != MODE_TEST_PATTERN) {
        current_color_index--;
        if (current_color_index < 0) {
            current_color_index = NUM_COLORS - 1;
        }
        need_redraw = true;
    }
}

void on_button_b(button_t button) {
    (void)button;
    // Cycle through modes
    current_mode = (current_mode + 1) % 3;
    need_redraw = true;
}

void on_button_x(button_t button) {
    (void)button;
    if (current_mode != MODE_TEST_PATTERN) {
        current_color_index = (current_color_index + 1) % NUM_COLORS;
        need_redraw = true;
    }
}

void on_button_y(button_t button) {
    (void)button;
    // Switch to RGB breakdown mode
    current_mode = MODE_RGB_BREAKDOWN;
    need_redraw = true;
}

int main() {
    // Init stdio
    stdio_init_all();
    sleep_ms(1000);  // Give USB time to enumerate
    
    printf("Display Pack Test Pattern Demo\n");
    printf("Init display ..\n");
    
    // Init display
    display_error_t result = display_pack_init();
    if (result != DISPLAY_OK) {
        printf("Display init failed: %s\n", display_error_string(result));
        return 1;
    }
    printf("Display initialised successfully\n");
    
    // Init buttons
    result = buttons_init();
    if (result != DISPLAY_OK) {
        printf("Button init failed: %s\n", display_error_string(result));
        return 1;
    }
    printf("Buttons initialised\n");
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, on_button_a);
    button_set_callback(BUTTON_B, on_button_b);
    button_set_callback(BUTTON_X, on_button_x);
    button_set_callback(BUTTON_Y, on_button_y);
    
    printf("Starting main loop ..\n");
    
    // Initial draw
    draw_test_pattern();
    
    // Main loop
    while (1) {
        buttons_update();
        
        if (need_redraw) {
            redraw_display();
        }
        
        sleep_ms(10);
    }
    
    // Cleanup (never reached in this example)
    display_cleanup();
    return 0;
}

