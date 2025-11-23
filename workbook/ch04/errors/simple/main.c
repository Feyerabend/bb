#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>

// Button callback — this will be called with the correct button
void btn_callback(button_t button)
{
    const char* names[] = {"A", "B", "X", "Y"};
    printf("Button %s pressed!\n", names[button]);
}

int main()
{
    stdio_init_all();
    sleep_ms(1500);          // give serial monitor time to connect

    disp_error_t err = disp_init(NULL);
    if (err != DISP_OK) {
        printf("Display init failed: %s\n", disp_error_string(err));
        while (1) tight_loop_contents();
    }
    printf("Display initialized\n");

    // ---- Buttons ----
    buttons_init();

    // Register ONE callback for ALL buttons — the function receives the button number
    button_set_callback(BUTTON_A, btn_callback);
    button_set_callback(BUTTON_B, btn_callback);
    button_set_callback(BUTTON_X, btn_callback);
    button_set_callback(BUTTON_Y, btn_callback);

    // ---- Demo graphics ----
    disp_clear(COLOR_BLACK);
    disp_fill_rect(40, 40, 240, 160, COLOR_RED);

    disp_draw_text(50, 60,  "Pimoroni Display Pack 2.0", COLOR_WHITE, COLOR_BLACK);
    disp_draw_text(80, 90,  "Press any button!",       COLOR_CYAN,  COLOR_BLACK);
    disp_draw_text(70, 130, "Lowercase works too!",    COLOR_YELLOW,COLOR_BLACK);
    disp_draw_text(100, 160,"A B X Y all fixed",       COLOR_GREEN, COLOR_BLACK);

    printf("Ready - press A, B, X or Y\n");

    while (1)
    {
        buttons_update();   // <-- this must be called frequently
        sleep_ms(10);
    }

    return 0;
}
