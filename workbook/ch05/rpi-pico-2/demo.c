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
    display_print("=== Math Quiz ===");
    display_print("");
    display_print("Problem 1:");
    double a = 7;
    double b = 8;
    display_print("What is 7 x 8?");
    double answer1 = (a * b);
    display_print("Answer:");
    display_print_number(answer1);
    display_print("");
    display_print("Problem 2:");
    double c = 144;
    double d = 12;
    display_print("What is 144 / 12?");
    double answer2 = (c / d);
    display_print("Answer:");
    display_print_number(answer2);
    display_print("");
    display_print("Fibonacci (10):");
    double n1 = 0;
    double n2 = 1;
    double count = 0;
    display_print_number(n1);
    display_print_number(n2);
    while ((count < 8)) {
        double n3 = (n1 + n2);
        display_print_number(n3);
        n1 = n2;
        n2 = n3;
        count = (count + 1);
    }
    display_print("");
    display_print("Sum 1 to 10:");
    double sum = 0;
    double num = 1;
    while ((num < 11)) {
        sum = (sum + num);
        num = (num + 1);
    }
    display_print_number(sum);
    display_print("");
    display_print("Table of 5:");
    double i = 1;
    while ((i < 11)) {
        double product = (i * 5);
        display_print_number(product);
        i = (i + 1);
    }
    display_print("");
    display_print("=== Quiz End ===");

    // Program complete - infinite loop
    while (1) {
        tight_loop_contents();
    }

    return 0;
}