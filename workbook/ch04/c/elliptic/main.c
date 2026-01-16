#include <stdio.h>
#include "pico/stdlib.h"
#include "display.h"

// Modular exponentiation
long long mod_exp(long long base, long long exp, long long mod) {
    long long result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

// Draw a progress bar
void draw_progress_bar(uint16_t x, uint16_t y, uint16_t width, uint16_t height, 
                       float progress, uint16_t color) {
    // Border
    display_fill_rect(x, y, width, 2, COLOR_WHITE);
    display_fill_rect(x, y + height - 2, width, 2, COLOR_WHITE);
    display_fill_rect(x, y, 2, height, COLOR_WHITE);
    display_fill_rect(x + width - 2, y, 2, height, COLOR_WHITE);
    
    // Fill
    uint16_t fill_width = (uint16_t)((width - 4) * progress);
    if (fill_width > 0) {
        display_fill_rect(x + 2, y + 2, fill_width, height - 4, color);
    }
}

// Animated number display with color transition
void animate_number(uint16_t x, uint16_t y, long long value, uint16_t color) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%lld", value);
    display_draw_string(x, y, buf, color, COLOR_BLACK);
}

// Draw a key visualization
void draw_key(uint16_t x, uint16_t y, const char* label, long long val1, long long val2, uint16_t color) {
    char buf[64];
    display_draw_string(x, y, label, COLOR_WHITE, COLOR_BLACK);
    snprintf(buf, sizeof(buf), "(%lld, %lld)", val1, val2);
    display_draw_string(x, y + 10, buf, color, COLOR_BLACK);
}

// Visualization stages
typedef enum {
    STAGE_INTRO,
    STAGE_KEYS,
    STAGE_ENCRYPT,
    STAGE_DECRYPT,
    STAGE_COMPLETE
} stage_t;

int main() {
    stdio_init_all();
    
    // Initialize display
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed!\n");
        return 1;
    }
    
    if (buttons_init() != DISPLAY_OK) {
        printf("Buttons init failed!\n");
        return 1;
    }
    
    // RSA parameters
    long long p = 61, q = 53;
    long long n = p * q;
    long long phi = (p - 1) * (q - 1);
    long long e = 17;
    long long d = 2753;
    long long message = 65;
    long long ciphertext = 0;
    long long decrypted = 0;
    
    stage_t stage = STAGE_INTRO;
    stage_t last_stage = STAGE_COMPLETE; // Force initial draw
    uint32_t last_update = 0;
    float animation_progress = 0.0f;
    
    while (true) {
        buttons_update();
        uint32_t now = to_ms_since_boot(get_absolute_time());
        
        // Advance on button press
        if (button_just_pressed(BUTTON_A) || button_just_pressed(BUTTON_B)) {
            stage = (stage + 1) % 5;
            animation_progress = 0.0f;
            last_stage = STAGE_COMPLETE; // Force redraw
        }
        
        // Update animation
        if (now - last_update > 50) {
            last_update = now;
            animation_progress += 0.05f;
            if (animation_progress > 1.0f) animation_progress = 1.0f;
        }
        
        // Redraw screen when stage changes
        if (stage != last_stage) {
            display_clear(COLOR_BLACK);
            last_stage = stage;
        }
        
        // Render based on stage - ALWAYS RENDER EVERY FRAME
        switch (stage) {
            case STAGE_INTRO:
                display_draw_string(60, 20, "RSA ENCRYPTION", COLOR_CYAN, COLOR_BLACK);
                display_draw_string(50, 40, "DEMONSTRATION", COLOR_CYAN, COLOR_BLACK);
                display_fill_rect(40, 60, 240, 2, COLOR_CYAN);
                
                display_draw_string(20, 80, "MESSAGE: 65 ('A')", COLOR_GREEN, COLOR_BLACK);
                display_draw_string(20, 100, "PRIMES: P=61, Q=53", COLOR_YELLOW, COLOR_BLACK);
                display_draw_string(20, 120, "MODULUS: N=3233", COLOR_YELLOW, COLOR_BLACK);
                
                display_draw_string(30, 160, "PRESS A/B TO", COLOR_WHITE, COLOR_BLACK);
                display_draw_string(30, 172, "ADVANCE STAGES", COLOR_WHITE, COLOR_BLACK);
                break;
                
            case STAGE_KEYS:
                display_draw_string(80, 10, "KEY GENERATION", COLOR_MAGENTA, COLOR_BLACK);
                display_fill_rect(20, 30, 280, 2, COLOR_MAGENTA);
                
                draw_key(20, 50, "PUBLIC KEY:", e, n, COLOR_GREEN);
                draw_progress_bar(20, 75, 280, 20, animation_progress, COLOR_GREEN);
                
                draw_key(20, 110, "PRIVATE KEY:", d, n, COLOR_RED);
                draw_progress_bar(20, 135, 280, 20, animation_progress, COLOR_RED);
                
                display_draw_string(20, 170, "PUBLIC: ENCRYPT", COLOR_GREEN, COLOR_BLACK);
                display_draw_string(20, 185, "PRIVATE: DECRYPT", COLOR_RED, COLOR_BLACK);
                break;
                
            case STAGE_ENCRYPT:
                display_draw_string(70, 10, "ENCRYPTION", COLOR_YELLOW, COLOR_BLACK);
                display_fill_rect(20, 30, 280, 2, COLOR_YELLOW);
                
                display_draw_string(20, 50, "MESSAGE M:", COLOR_WHITE, COLOR_BLACK);
                animate_number(130, 50, message, COLOR_GREEN);
                
                display_draw_string(20, 75, "COMPUTING:", COLOR_WHITE, COLOR_BLACK);
                display_draw_string(20, 90, "C = M^E MOD N", COLOR_CYAN, COLOR_BLACK);
                
                draw_progress_bar(20, 110, 280, 25, animation_progress, COLOR_YELLOW);
                
                if (animation_progress > 0.5f) {
                    ciphertext = mod_exp(message, e, n);
                    display_draw_string(20, 150, "CIPHERTEXT C:", COLOR_WHITE, COLOR_BLACK);
                    animate_number(165, 150, ciphertext, COLOR_YELLOW);
                    
                    display_draw_string(20, 175, "ENCRYPTED!", COLOR_GREEN, COLOR_BLACK);
                }
                break;
                
            case STAGE_DECRYPT:
                display_draw_string(70, 10, "DECRYPTION", COLOR_CYAN, COLOR_BLACK);
                display_fill_rect(20, 30, 280, 2, COLOR_CYAN);
                
                display_draw_string(20, 50, "CIPHERTEXT C:", COLOR_WHITE, COLOR_BLACK);
                animate_number(165, 50, ciphertext, COLOR_YELLOW);
                
                display_draw_string(20, 75, "COMPUTING:", COLOR_WHITE, COLOR_BLACK);
                display_draw_string(20, 90, "M = C^D MOD N", COLOR_MAGENTA, COLOR_BLACK);
                
                draw_progress_bar(20, 110, 280, 25, animation_progress, COLOR_CYAN);
                
                if (animation_progress > 0.5f) {
                    decrypted = mod_exp(ciphertext, d, n);
                    display_draw_string(20, 150, "DECRYPTED M:", COLOR_WHITE, COLOR_BLACK);
                    animate_number(155, 150, decrypted, COLOR_GREEN);
                    
                    display_draw_string(20, 175, "SUCCESS!", COLOR_GREEN, COLOR_BLACK);
                }
                break;
                
            case STAGE_COMPLETE:
                display_draw_string(90, 20, "COMPLETE!", COLOR_GREEN, COLOR_BLACK);
                display_fill_rect(20, 45, 280, 3, COLOR_GREEN);
                
                display_draw_string(20, 65, "ORIGINAL:", COLOR_WHITE, COLOR_BLACK);
                animate_number(120, 65, message, COLOR_CYAN);
                
                display_draw_string(20, 85, "ENCRYPTED:", COLOR_WHITE, COLOR_BLACK);
                animate_number(135, 85, ciphertext, COLOR_YELLOW);
                
                display_draw_string(20, 105, "DECRYPTED:", COLOR_WHITE, COLOR_BLACK);
                animate_number(135, 105, decrypted, COLOR_GREEN);
                
                if (message == decrypted) {
                    display_draw_string(40, 140, "MATCH: RSA WORKS!", COLOR_GREEN, COLOR_BLACK);
                    
                    // Draw checkmark animation
                    uint16_t check_y = 165 + (uint16_t)(animation_progress * 10);
                    display_fill_rect(140, check_y, 6, 15, COLOR_GREEN);
                    display_fill_rect(146, check_y + 10, 15, 6, COLOR_GREEN);
                }
                
                display_draw_string(30, 200, "PRESS A/B TO", COLOR_WHITE, COLOR_BLACK);
                display_draw_string(30, 212, "RESTART", COLOR_WHITE, COLOR_BLACK);
                break;
        }
        
        sleep_ms(10);
    }
    
    return 0;
}

