// Auto-generated code for Raspberry Pi Pico 2
// Compiled from custom language

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "display.h"

// Display configuration
#define TEXT_LINE_HEIGHT 10
#define TEXT_START_X 5
#define TEXT_START_Y 5

// Global variables
static uint16_t display_y = TEXT_START_Y;
static char print_buffer[256];

// Helper function to print to display
void display_print(const char *str) {
    if (display_y >= DISPLAY_HEIGHT - TEXT_LINE_HEIGHT) {
        // Screen full, clear and restart
        disp_clear(COLOR_BLACK);
        display_y = TEXT_START_Y;
    }
    disp_draw_text(TEXT_START_X, display_y, str, COLOR_WHITE, COLOR_BLACK);
    display_y += TEXT_LINE_HEIGHT;
}

void display_print_number(double num) {
    if (num == (int)num) {
        snprintf(print_buffer, sizeof(print_buffer), "%d", (int)num);
    } else {
        snprintf(print_buffer, sizeof(print_buffer), "%.2f", num);
    }
    display_print(print_buffer);
}

int main() {
    // Initialize stdio and display
    stdio_init_all();

    disp_config_t config = disp_get_default_config();
    if (disp_init(&config) != DISP_OK) {
        return -1;
    }

    disp_clear(COLOR_BLACK);
    disp_set_backlight(true);

    // User program variables
    char message[256];
    strcpy(message, "Pico Display Test");
    display_print(message);
    double x = 10;
    double y = 20;
    display_print("x = ");
    display_print_number(x);
    display_print("y = ");
    display_print_number(y);
    if ((x < y)) {
        display_print("x is less than y");
        double sum = (x + y);
        display_print("Sum: ");
        display_print_number(sum);
    } else {
        display_print("x is greater or equal to y");
    }
    display_print("Counting to 10:");
    double i = 0;
    while ((i < 10)) {
        display_print_number(i);
        i = (i + 1);
    }
    double result = (x * y);
    display_print("x * y = ");
    display_print_number(result);
    display_print("Program complete!");

    // Program complete - infinite loop
    while (1) {
        tight_loop_contents();
    }

    return 0;
}