#include "display.h"
#include "pico/stdlib.h"
#include <stdio.h>  // For sprintf

volatile uint32_t counter = 0;
volatile bool update_display_flag = false;

// Timer callback (called in interrupt context every 1s)
bool timer_callback(struct repeating_timer *t) {
    counter++;
    update_display_flag = true;
    return true;  // Continue repeating
}

// GPIO interrupt handler for Button A
void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == BUTTON_A_PIN && (events & GPIO_IRQ_EDGE_FALL)) {
        counter = 0;
        update_display_flag = true;
    }
}

int main() {
    stdio_init_all();

    // Initialize display and button pins (sets pull-ups)
    display_pack_init();
    buttons_init();

    // Set up GPIO interrupt for Button A (falling edge)
    gpio_set_irq_enabled_with_callback(BUTTON_A_PIN, GPIO_IRQ_EDGE_FALL, true, &gpio_callback);

    // Set up repeating timer for 1s intervals
    struct repeating_timer timer;
    add_repeating_timer_ms(1000, timer_callback, NULL, &timer);

    // Clear display and turn on backlight
    display_clear(COLOR_BLACK);
    display_set_backlight(true);

    char buf[32];

    // Initial display update
    sprintf(buf, "Counter: %lu", counter);
    display_draw_string(10, 10, buf, COLOR_WHITE, COLOR_BLACK);
    update_display_flag = false;

    while (true) {
        if (update_display_flag) {
            update_display_flag = false;

            // Clear area and draw new counter
            display_fill_rect(0, 0, DISPLAY_WIDTH, 20, COLOR_BLACK);
            sprintf(buf, "Counter: %lu", counter);
            display_draw_string(10, 10, buf, COLOR_WHITE, COLOR_BLACK);
        }

        tight_loop_contents();
    }
}