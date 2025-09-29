#include "pico/stdlib.h"
#include "hstx_display.h"

uint16_t current_color = HSTX_COLOR_BLACK;

void button_callback(hstx_button_t button) {
    switch (button) {
        case HSTX_BUTTON_A: current_color = HSTX_COLOR_RED; break;
        case HSTX_BUTTON_B: current_color = HSTX_COLOR_GREEN; break;
        case HSTX_BUTTON_X: current_color = HSTX_COLOR_BLUE; break;
        case HSTX_BUTTON_Y: current_color = HSTX_COLOR_WHITE; break;
        default: break;
    }
    hstx_display_clear(current_color);
    hstx_display_draw_string(10, 10, "Hello HSTX! Press buttons to change color.", HSTX_COLOR_BLACK, current_color);
}

int main() {
    stdio_init_all();
    sleep_ms(2000);  // Let serial connect

    printf("Starting Demo..\n");

    hstx_display_error_t err = hstx_display_pack_init();
    if (err != HSTX_DISPLAY_OK) {
        printf("Display init failed: %s\n", hstx_display_error_string(err));
        while (true) tight_loop_contents();
    }

    err = hstx_buttons_init();
    if (err != HSTX_DISPLAY_OK) {
        printf("Buttons init failed: %s\n", hstx_display_error_string(err));
    }

    // Set callbacks
    for (int i = 0; i < HSTX_BUTTON_COUNT; i++) {
        hstx_button_set_callback((hstx_button_t)i, button_callback);
    }

    // Initial draw
    hstx_display_clear(HSTX_COLOR_BLACK);
    hstx_display_draw_string(10, 10, "Hello HSTX! Press buttons to change color.", HSTX_COLOR_WHITE, HSTX_COLOR_BLACK);
    hstx_display_set_backlight(true);

    while (true) {
        hstx_buttons_update();
        sleep_ms(10);
    }

    return 0;
}
