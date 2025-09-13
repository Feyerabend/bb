#include <stdio.h>
#include "pico/stdlib.h"
#include "display_pack.h"

// Callback functions
void on_button_a(button_t button) {
    printf("Button A pressed!\n");
    display_clear(COLOR_RED);
    display_draw_string(10, 60, "BUTTON A PRESSED", COLOR_WHITE, COLOR_RED);
}

void on_button_b(button_t button) {
    printf("Button B pressed!\n");
    display_clear(COLOR_GREEN);
    display_draw_string(10, 60, "BUTTON B PRESSED", COLOR_WHITE, COLOR_GREEN);
}

void on_button_x(button_t button) {
    printf("Button X pressed!\n");
    display_clear(COLOR_BLUE);
    display_draw_string(10, 60, "BUTTON X PRESSED", COLOR_WHITE, COLOR_BLUE);
}

void on_button_y(button_t button) {
    printf("Button Y pressed!\n");
    display_clear(COLOR_YELLOW);
    display_draw_string(10, 60, "BUTTON Y PRESSED", COLOR_BLACK, COLOR_YELLOW);
}

int main() {
    stdio_init_all();
    
    // Init display pack
    if (!display_pack_init()) {
        printf("Failed to initialize display!\n");
        return 1;
    }
    
    // Init buttons
    buttons_init();
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, on_button_a);
    button_set_callback(BUTTON_B, on_button_b);
    button_set_callback(BUTTON_X, on_button_x);
    button_set_callback(BUTTON_Y, on_button_y);
    
    // Clear screen and check
    display_clear(COLOR_BLACK);
    display_draw_string(10, 10, "Display Pack Library", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(10, 25, "Text should not be mirrored?", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, 45, "Press any button to test", COLOR_YELLOW, COLOR_BLACK);
    display_draw_string(10, 70, "A=Red B=Green X=Blue Y=Yellow", COLOR_WHITE, COLOR_BLACK);
    
    // Draw some graphics
    display_fill_rect(10, 90, 50, 20, COLOR_MAGENTA);
    display_draw_string(15, 95, "RECT", COLOR_WHITE, COLOR_MAGENTA);
    
    // Draw individual pixels
    for (int i = 0; i < 20; i++) {
        display_draw_pixel(70 + i, 90 + i/2, COLOR_RED);
        display_draw_pixel(90 + i, 90 + i/2, COLOR_GREEN);
        display_draw_pixel(110 + i, 90 + i/2, COLOR_BLUE);
    }
    
    printf("Display Pack Library Example Started!\n");
    printf("Press buttons A, B, X, or Y to test functionality\n");
    
    // Main loop
    while (true) {
        // Update button states (debouncing and callbacks)
        buttons_update();
        
        // You can also check button states manually
        if (button_pressed(BUTTON_A) && button_pressed(BUTTON_B)) {
            // Both A and B pressed - special action
            static bool backlight_on = true;
            backlight_on = !backlight_on;
            display_set_backlight(backlight_on);
            printf("Toggled backlight: %s\n", backlight_on ? "ON" : "OFF");
            sleep_ms(500); // Prevent rapid toggling
        }
        
        sleep_ms(10);
    }
    
    return 0;
}

