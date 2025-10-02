#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/irq.h"
#include <stdio.h>

// Pin definitions
#define LED_PIN 15    // External LED on GPIO 15, Physical pin 16
#define BUTTON_PIN 12 // Button on GPIO 12, Physical pin 20

// Global variables
volatile uint32_t led_on_time = 0; // Timestamp when LED turns on
volatile bool waiting_for_press = false; // State flag
struct repeating_timer timer;

// Timer callback to turn on LED
bool timer_callback(struct repeating_timer *t) {
    led_on_time = to_ms_since_boot(get_absolute_time());
    gpio_put(LED_PIN, 1); // Turn on LED
    waiting_for_press = true;
    cancel_repeating_timer(t); // Stop timer until next round
    return false; // One-shot behavior
}

// GPIO interrupt handler for button
void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == BUTTON_PIN && (events & GPIO_IRQ_EDGE_FALL) && waiting_for_press) {
        uint32_t reaction_time = to_ms_since_boot(get_absolute_time()) - led_on_time;
        printf("Reaction time: %lu ms\n", reaction_time);
        gpio_put(LED_PIN, 0); // Turn off LED
        waiting_for_press = false;
        // Restart timer with random delay (1-5s)
        uint32_t delay_ms = (rand() % 4000) + 1000; // Random 1000-5000ms
        add_repeating_timer_ms(delay_ms, timer_callback, NULL, &timer);
    }
}

int main() {
    stdio_init_all();

    // Initialize LED pin
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);

    // Initialize button pin with pull-up
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);

    // Set up GPIO interrupt for button (falling edge)
    gpio_set_irq_enabled_with_callback(BUTTON_PIN, GPIO_IRQ_EDGE_FALL, true, &gpio_callback);

    // Seed random number generator
    srand(to_ms_since_boot(get_absolute_time()));

    // Start timer with random delay (1-5s)
    uint32_t initial_delay = (rand() % 4000) + 1000;
    add_repeating_timer_ms(initial_delay, timer_callback, NULL, &timer);

    while (true) {
        tight_loop_contents();
    }
}