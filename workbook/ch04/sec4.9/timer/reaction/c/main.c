#include "pico/stdlib.h"
#include "display.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Game states
typedef enum {
    STATE_WAITING,      // Waiting for random delay
    STATE_READY,        // Green shown - press now!
    STATE_RESULT,       // Showing result
    STATE_TOO_EARLY     // Pressed before green
} game_state_t;

// Game variables
static game_state_t state = STATE_WAITING;
static uint32_t led_on_time = 0;
static uint32_t next_ready_time = 0;
static uint32_t wait_start_time = 0;
static uint32_t actual_wait_duration = 0;
static uint32_t fake_wait_duration = 0;  // Slightly different for display
static uint32_t last_reaction_time = 0;
static uint32_t best_time = 999999;
static int round_count = 0;
static uint32_t result_show_time = 0;

// History tracking
#define MAX_HISTORY 8
static uint32_t reaction_history[MAX_HISTORY];
static int history_count = 0;

// Visual elements
static uint16_t circle_x = DISPLAY_WIDTH / 2;
static uint16_t circle_y = 100;
static uint16_t circle_radius = 50;

// Helper: Draw filled circle
static void draw_filled_circle(uint16_t cx, uint16_t cy, uint16_t r, uint16_t color) {
    for (int16_t y = -r; y <= r; y++) {
        for (int16_t x = -r; x <= r; x++) {
            if (x*x + y*y <= r*r) {
                int16_t px = cx + x;
                int16_t py = cy + y;
                if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                    display_draw_pixel(px, py, color);
                }
            }
        }
    }
}

// Helper: Draw number centered
static void draw_number_centered(uint16_t y, uint32_t num, uint16_t color) {
    char buf[16];
    snprintf(buf, sizeof(buf), "%lu", num);
    int len = 0;
    while (buf[len]) len++;
    uint16_t x = (DISPLAY_WIDTH - len * 6) / 2;
    display_draw_string(x, y, buf, color, COLOR_BLACK);
}

// Helper: Draw shrinking progress bar
static void draw_progress_bar(uint32_t now) {
    uint32_t elapsed = now - wait_start_time;
    
    // Calculate progress (with fake duration that's slightly off)
    float progress = (float)elapsed / (float)fake_wait_duration;
    if (progress > 1.0f) progress = 1.0f;
    
    // Bar dimensions
    uint16_t bar_width = 200;
    uint16_t bar_height = 30;
    uint16_t bar_x = (DISPLAY_WIDTH - bar_width) / 2;
    uint16_t bar_y = circle_y - circle_radius - 50;
    
    // Draw border
    display_fill_rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4, COLOR_WHITE);
    display_fill_rect(bar_x, bar_y, bar_width, bar_height, COLOR_BLACK);
    
    // Draw filled portion (shrinking from right)
    uint16_t fill_width = (uint16_t)(bar_width * (1.0f - progress));
    if (fill_width > 0) {
        // Color transitions from blue to yellow to red as it empties
        uint16_t bar_color;
        if (progress < 0.5f) {
            bar_color = COLOR_BLUE;
        } else if (progress < 0.8f) {
            bar_color = COLOR_YELLOW;
        } else {
            bar_color = COLOR_RED;
        }
        
        display_fill_rect(bar_x + bar_width - fill_width, bar_y, fill_width, bar_height, bar_color);
    }
}

// Helper: Draw reaction time history
static void draw_history(void) {
    uint16_t list_x = 10;
    uint16_t list_y = 165;
    
    display_draw_string(list_x, list_y, "Recent times:", COLOR_CYAN, COLOR_BLACK);
    
    for (int i = 0; i < history_count && i < MAX_HISTORY; i++) {
        char buf[20];
        snprintf(buf, sizeof(buf), "%d. %lums", i + 1, reaction_history[i]);
        
        // Color code based on time
        uint16_t color;
        if (reaction_history[i] < 200) {
            color = COLOR_GREEN;
        } else if (reaction_history[i] < 300) {
            color = COLOR_CYAN;
        } else if (reaction_history[i] < 400) {
            color = COLOR_YELLOW;
        } else {
            color = COLOR_RED;
        }
        
        display_draw_string(list_x, list_y + 15 + i * 12, buf, color, COLOR_BLACK);
    }
}

// Draw the main UI
static void draw_ui(uint32_t now) {
    display_clear(COLOR_BLACK);
    
    // Draw title
    display_draw_string(90, 10, "REACTION TIMER", COLOR_WHITE, COLOR_BLACK);
    
    // Draw stats at top
    char buf[32];
    if (best_time < 999999) {
        snprintf(buf, sizeof(buf), "Best: %lums", best_time);
        display_draw_string(10, 30, buf, COLOR_YELLOW, COLOR_BLACK);
    }
    
    snprintf(buf, sizeof(buf), "Round: %d", round_count);
    display_draw_string(220, 30, buf, COLOR_CYAN, COLOR_BLACK);
    
    // Draw main circle based on state
    switch (state) {
        case STATE_WAITING:
            // Draw shrinking progress bar
            draw_progress_bar(now);
            
            // Draw waiting circle
            draw_filled_circle(circle_x, circle_y, circle_radius, COLOR_RED);
            display_draw_string(110, circle_y - 5, "WAIT...", COLOR_WHITE, COLOR_BLACK);
            break;
            
        case STATE_READY:
            // Large green circle - GO!
            draw_filled_circle(circle_x, circle_y, circle_radius + 10, COLOR_GREEN);
            display_draw_string(100, circle_y + 70, "PRESS NOW!", COLOR_GREEN, COLOR_BLACK);
            break;
            
        case STATE_RESULT:
            // Show result with color-coded feedback
            uint16_t result_color;
            const char* message;
            
            if (last_reaction_time < 200) {
                result_color = COLOR_GREEN;
                message = "EXCELLENT!";
            } else if (last_reaction_time < 300) {
                result_color = COLOR_CYAN;
                message = "GREAT!";
            } else if (last_reaction_time < 400) {
                result_color = COLOR_YELLOW;
                message = "GOOD";
            } else {
                result_color = COLOR_RED;
                message = "TRY AGAIN";
            }
            
            draw_filled_circle(circle_x, circle_y, circle_radius, result_color);
            
            // Draw reaction time
            draw_number_centered(circle_y + 70, last_reaction_time, COLOR_WHITE);
            display_draw_string(140, circle_y + 85, "ms", COLOR_WHITE, COLOR_BLACK);
            
            // Draw message
            uint16_t msg_x = (DISPLAY_WIDTH - strlen(message) * 6) / 2;
            display_draw_string(msg_x, circle_y + 105, message, result_color, COLOR_BLACK);
            break;
            
        case STATE_TOO_EARLY:
            // Red X
            draw_filled_circle(circle_x, circle_y, circle_radius, COLOR_RED);
            display_draw_string(80, circle_y + 70, "TOO EARLY!", COLOR_RED, COLOR_BLACK);
            display_draw_string(90, circle_y + 85, "Wait for green!", COLOR_WHITE, COLOR_BLACK);
            break;
    }
    
    // Draw history list
    draw_history();
}

// Button callback
static void button_a_pressed(button_t button) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    if (state == STATE_READY) {
        // Calculate reaction time
        last_reaction_time = now - led_on_time;
        
        // Add to history
        if (history_count < MAX_HISTORY) {
            reaction_history[history_count++] = last_reaction_time;
        } else {
            // Shift history and add new one
            for (int i = 0; i < MAX_HISTORY - 1; i++) {
                reaction_history[i] = reaction_history[i + 1];
            }
            reaction_history[MAX_HISTORY - 1] = last_reaction_time;
        }
        
        // Update best time
        if (last_reaction_time < best_time) {
            best_time = last_reaction_time;
        }
        
        state = STATE_RESULT;
        result_show_time = now;
        draw_ui(now);
        
    } else if (state == STATE_WAITING) {
        // Pressed too early!
        state = STATE_TOO_EARLY;
        result_show_time = now;
        draw_ui(now);
    }
}

int main() {
    stdio_init_all();
    
    // Initialize display
    display_error_t result = display_pack_init();
    if (result != DISPLAY_OK) {
        printf("Display init failed: %s\n", display_error_string(result));
        return 1;
    }
    
    // Initialize buttons
    result = buttons_init();
    if (result != DISPLAY_OK) {
        printf("Button init failed: %s\n", display_error_string(result));
        return 1;
    }
    
    // Set up button callback
    button_set_callback(BUTTON_A, button_a_pressed);
    
    // Seed random
    srand(to_ms_since_boot(get_absolute_time()));
    
    // Set initial random delay (2-5 seconds)
    uint32_t now = to_ms_since_boot(get_absolute_time());
    actual_wait_duration = (rand() % 3000) + 2000;
    // Fake duration is slightly off (±20%) to keep players guessing
    int offset_percent = (rand() % 40) - 20;  // -20% to +20%
    fake_wait_duration = actual_wait_duration + (actual_wait_duration * offset_percent / 100);
    next_ready_time = now + actual_wait_duration;
    wait_start_time = now;
    
    // Draw initial UI
    draw_ui(now);
    
    uint32_t last_update = 0;
    
    while (true) {
        uint32_t now = to_ms_since_boot(get_absolute_time());
        
        // Update buttons
        buttons_update();
        
        // Update every 50ms for smooth animation
        if (now - last_update >= 50) {
            last_update = now;
            
            switch (state) {
                case STATE_WAITING:
                    // Check if it's time to turn green
                    if (now >= next_ready_time) {
                        state = STATE_READY;
                        led_on_time = now;
                        round_count++;
                        draw_ui(now);
                    } else {
                        // Redraw for progress bar animation
                        draw_ui(now);
                    }
                    break;
                    
                case STATE_READY:
                    // Just wait for button press (handled by callback)
                    break;
                    
                case STATE_RESULT:
                case STATE_TOO_EARLY:
                    // Show result for 2 seconds, then restart
                    if (now - result_show_time >= 2000) {
                        state = STATE_WAITING;
                        // New random delay (2-5 seconds)
                        actual_wait_duration = (rand() % 3000) + 2000;
                        // Fake duration is slightly off to keep it unpredictable
                        int offset_percent = (rand() % 40) - 20;
                        fake_wait_duration = actual_wait_duration + (actual_wait_duration * offset_percent / 100);
                        next_ready_time = now + actual_wait_duration;
                        wait_start_time = now;
                        draw_ui(now);
                    }
                    break;
            }
        }
        
        tight_loop_contents();
    }
    
    display_cleanup();
    return 0;
}