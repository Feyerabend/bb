/*
 * Side-Channel Attack Demonstration for Raspberry Pi Pico 2
 * With Pimoroni Display Pack 2.0
 * 
 * This demonstrates timing and power analysis side-channels in cryptographic
 * operations, showing both vulnerable and hardened implementations.
 * 
 * Educational Features:
 * - Timing attack on password comparison (visual on display)
 * - Timing attack on AES key scheduling  
 * - Power analysis simulation via LED patterns
 * - Constant-time implementations as countermeasures
 * - Interactive demo selection via buttons
 * 
 * Hardware Setup:
 * - Pimoroni Display Pack 2.0 (320x240 display + 4 buttons)
 * - Button A: Next demo
 * - Button B: Previous demo  
 * - Button X: Run current demo
 * - Button Y: Toggle auto-run
 * - LED patterns show "power consumption"
 * 
 * Display shows:
 * - Current demo title and explanation
 * - Real-time timing measurements
 * - Visual comparison graphs
 * - Security status indicators
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"
#include "pico/time.h"
#include "display.h"

// Power simulation LED pins (external LEDs for power trace)
#define POWER_LED_1 6
#define POWER_LED_2 7
#define POWER_LED_3 8
#define POWER_LED_4 9

// Demo modes
typedef enum {
    DEMO_TIMING_PASSWORD,
    DEMO_TIMING_AES,
    DEMO_POWER_ANALYSIS,
    DEMO_COUNTERMEASURES,
    DEMO_COUNT
} demo_mode_t;

static demo_mode_t current_demo = DEMO_TIMING_PASSWORD;
static bool auto_run = false;
static bool demo_running = false;

// Display layout constants
#define TITLE_Y 10
#define STATUS_Y 30
#define GRAPH_Y 80
#define GRAPH_HEIGHT 120
#define INFO_Y 210

/*
 * DISPLAY HELPER FUNCTIONS
 */

void draw_title(const char *title, uint16_t color) {
    display_fill_rect(0, 0, DISPLAY_WIDTH, 25, COLOR_BLACK);
    display_draw_string(10, 8, title, color, COLOR_BLACK);
}

void draw_status(const char *status, uint16_t color) {
    display_fill_rect(0, STATUS_Y, DISPLAY_WIDTH, 40, COLOR_BLACK);
    display_draw_string(10, STATUS_Y + 10, status, color, COLOR_BLACK);
}

void draw_info(const char *info) {
    display_fill_rect(0, INFO_Y, DISPLAY_WIDTH, 30, COLOR_BLACK);
    display_draw_string(5, INFO_Y + 5, info, COLOR_CYAN, COLOR_BLACK);
}

void draw_timing_bar(uint16_t x, uint16_t y, uint16_t width, uint16_t height, 
                     uint64_t time_us, uint64_t max_time, uint16_t color, const char *label) {
    // Draw label
    display_draw_string(x, y - 12, label, COLOR_WHITE, COLOR_BLACK);
    
    // Draw bar background
    display_fill_rect(x, y, width, height, COLOR_BLACK);
    display_fill_rect(x, y, width, height, 0x2104); // Dark gray border
    
    // Draw filled portion based on timing
    uint16_t fill_width = (uint32_t)width * time_us / max_time;
    if (fill_width > width) fill_width = width;
    display_fill_rect(x + 2, y + 2, fill_width - 4, height - 4, color);
    
    // Draw time value
    char time_str[16];
    snprintf(time_str, sizeof(time_str), "%llu us", time_us);
    display_draw_string(x + width + 5, y + 3, time_str, color, COLOR_BLACK);
}

void draw_power_bar(uint16_t x, uint16_t y, uint16_t width, uint16_t height,
                    int power_level, int max_power, const char *label) {
    // Draw label
    display_draw_string(x, y - 12, label, COLOR_WHITE, COLOR_BLACK);
    
    // Draw bar
    display_fill_rect(x, y, width, height, COLOR_BLACK);
    
    uint16_t fill_width = (uint32_t)width * power_level / max_power;
    if (fill_width > width) fill_width = width;
    
    // Color gradient based on power
    uint16_t color = COLOR_GREEN;
    if (power_level > max_power * 2 / 3) color = COLOR_RED;
    else if (power_level > max_power / 3) color = COLOR_YELLOW;
    
    display_fill_rect(x, y, fill_width, height, color);
}

void show_power_leds(int hamming_weight) {
    // Use external LEDs to show "power consumption"
    gpio_put(POWER_LED_1, hamming_weight >= 2);
    gpio_put(POWER_LED_2, hamming_weight >= 4);
    gpio_put(POWER_LED_3, hamming_weight >= 6);
    gpio_put(POWER_LED_4, hamming_weight >= 7);
}

/*
 * VULNERABLE PASSWORD COMPARISON (Early Exit)
 */

bool check_password_vulnerable(const char *input, const char *correct) {
    size_t len = strlen(correct);
    if (strlen(input) != len) return false;
    
    for (size_t i = 0; i < len; i++) {
        if (input[i] != correct[i]) {
            return false;  // Early exit - timing leak!
        }
        busy_wait_us(100);
    }
    return true;
}

/*
 * SECURE PASSWORD COMPARISON (Constant Time)
 */

bool check_password_secure(const char *input, const char *correct) {
    size_t len = strlen(correct);
    if (strlen(input) != len) {
        len = strlen(input);
    }
    
    uint8_t diff = 0;
    
    for (size_t i = 0; i < len; i++) {
        diff |= (input[i] ^ correct[i]);
        busy_wait_us(100);
    }
    
    return (diff == 0);
}

/*
 * TIMING ATTACK DEMONSTRATION - PASSWORD
 */

void demo_timing_attack_password(void) {
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    draw_status("TESTING VULNERABLE IMPLEMENTAION..", COLOR_YELLOW);
    
    const char *correct_password = "SECRET123";
    const char *test_passwords[] = {
        "XXXXXXXXX",  // 0 chars correct
        "SXXXXXXXX",  // 1 char correct
        "SECXXXXX",   // 3 chars correct
        "SECRXXXX",   // 4 chars correct
        "SECRET123"   // All correct
    };
    const int num_tests = 5;
    
    uint64_t timings_vuln[5];
    uint64_t timings_secure[5];
    uint64_t max_time = 0;
    
    // Test vulnerable version
    for (int i = 0; i < num_tests; i++) {
        uint64_t start = time_us_64();
        check_password_vulnerable(test_passwords[i], correct_password);
        timings_vuln[i] = time_us_64() - start;
        if (timings_vuln[i] > max_time) max_time = timings_vuln[i];
    }
    
    // Test secure version  
    for (int i = 0; i < num_tests; i++) {
        uint64_t start = time_us_64();
        check_password_secure(test_passwords[i], correct_password);
        timings_secure[i] = time_us_64() - start;
        if (timings_secure[i] > max_time) max_time = timings_secure[i];
    }
    
    max_time += 100; // Add margin
    
    // Draw comparison
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (EARLY EXIT):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < num_tests; i++) {
        char label[16];
        snprintf(label, sizeof(label), "%d chars", i * 2);
        draw_timing_bar(10, 55 + i * 22, 200, 18, 
                       timings_vuln[i], max_time, COLOR_RED, label);
    }
    
    display_draw_string(10, 180, "SECURE (CONSTANT TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < 3; i++) {
        char label[16];
        snprintf(label, sizeof(label), "%d CHARS", i * 2);
        draw_timing_bar(10, 200 + i * 22, 200, 18,
                       timings_secure[i], max_time, COLOR_GREEN, label);
    }
    
    draw_info("NOTICE: Vulnerable times increase with more correct chars!");
    
    sleep_ms(5000);
}

/*
 * SIMPLE AES S-BOX (for demonstration)
 */

static const uint8_t sbox[16] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76
};

uint8_t aes_sbox_lookup_vulnerable(uint8_t input) {
    uint8_t index = input & 0x0F;
    
    // Simulate cache timing variation
    if ((input & 0x10) == 0) {
        busy_wait_us(50);  // "Cache miss"
    } else {
        busy_wait_us(10);  // "Cache hit"
    }
    
    return sbox[index];
}

uint8_t aes_sbox_lookup_secure(uint8_t input) {
    uint8_t index = input & 0x0F;
    busy_wait_us(50);  // Always same time
    return sbox[index];
}

/*
 * TIMING ATTACK DEMONSTRATION - AES
 */

void demo_timing_attack_aes(void) {
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    draw_status("TESTING CACHE-TIMING VULNERABILITY..", COLOR_YELLOW);
    
    uint8_t test_inputs[] = {0x00, 0x10, 0x05, 0x15, 0x0A, 0x1A, 0x0F, 0x1F};
    const int num_tests = 8;
    
    uint64_t timings_vuln[8];
    uint64_t timings_secure[8];
    uint64_t max_time = 0;
    
    // Test vulnerable version
    for (int i = 0; i < num_tests; i++) {
        uint64_t start = time_us_64();
        aes_sbox_lookup_vulnerable(test_inputs[i]);
        timings_vuln[i] = time_us_64() - start;
        if (timings_vuln[i] > max_time) max_time = timings_vuln[i];
    }
    
    // Test secure version
    for (int i = 0; i < num_tests; i++) {
        uint64_t start = time_us_64();
        aes_sbox_lookup_secure(test_inputs[i]);
        timings_secure[i] = time_us_64() - start;
        if (timings_secure[i] > max_time) max_time = timings_secure[i];
    }
    
    max_time += 10;
    
    // Draw comparison
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (CACHE-TIMING):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < 4; i++) {
        char label[16];
        snprintf(label, sizeof(label), "0x%02X", test_inputs[i]);
        draw_timing_bar(10, 55 + i * 22, 200, 18,
                       timings_vuln[i], max_time, COLOR_RED, label);
    }
    
    display_draw_string(10, 160, "SECURE (CONSTANT TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < 3; i++) {
        char label[16];
        snprintf(label, sizeof(label), "0x%02X", test_inputs[i]);
        draw_timing_bar(10, 180 + i * 22, 200, 18,
                       timings_secure[i], max_time, COLOR_GREEN, label);
    }
    
    draw_info("CACHE HITS/MISES LEAK KEY INFORMATION!");
    
    sleep_ms(5000);
}

/*
 * POWER ANALYSIS DEMONSTRATION
 */

int hamming_weight(uint8_t byte) {
    int weight = 0;
    for (int i = 0; i < 8; i++) {
        if (byte & (1 << i)) weight++;
    }
    return weight;
}

void demo_power_analysis(void) {
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    draw_status("SIMULATING POWER CONSUMPTION TRACES..", COLOR_YELLOW);
    
    uint8_t secret_key = 0b10101010;
    
    display_clear(COLOR_BLACK);
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    
    char key_str[32];
    snprintf(key_str, sizeof(key_str), "SECRET KEY: 0x%02X", secret_key);
    display_draw_string(10, 35, key_str, COLOR_YELLOW, COLOR_BLACK);
    
    display_draw_string(10, 50, "POWER TRACES REVEAL HAMMING WEIGHT:", COLOR_WHITE, COLOR_BLACK);
    
    // Show power traces for different plaintexts
    for (uint8_t plaintext = 0; plaintext < 8; plaintext++) {
        uint8_t result = secret_key ^ plaintext;
        int hw = hamming_weight(result);
        
        char label[32];
        snprintf(label, sizeof(label), "PT:0x%02X HW:%d", plaintext, hw);
        
        draw_power_bar(10, 75 + plaintext * 18, 250, 14, hw, 8, label);
        
        // Show on external LEDs
        show_power_leds(hw);
        
        sleep_ms(400);
    }
    
    draw_info("POWER = F(HAMMING WEIGHT) LEAKS SECRETS!");
    
    sleep_ms(3000);
    
    // Clear LEDs
    show_power_leds(0);
}

/*
 * COUNTERMEASURES DEMONSTRATION
 */

void demo_countermeasures(void) {
    display_clear(COLOR_BLACK);
    draw_title("COUNTERMEASURES", COLOR_GREEN);
    
    const char *countermeasures[] = {
        "1. CONSTANT-TIME OPERATIONS",
        "  - No data-dependent branches",
        "  - Same execution path always",
        "",
        "2. MASKING",
        "  - Add random values",
        "  - Remove mask at end",
        "",
        "3. BLINDING",
        "  - Randomize intermediates",
        "  - Decorrelate from secrets",
        "",
        "4. NOISE INJECTION", 
        "  - Add dummy operations",
        "  - Randomize timing",
        "",
        "5. HARDWARE DEFENSES",
        "  - Power filtering",
        "  - EMI shielding",
        "  - Secure enclaves"
    };
    
    int y = 30;
    for (int i = 0; i < 19; i++) {
        uint16_t color = COLOR_WHITE;
        if (countermeasures[i][0] >= '1' && countermeasures[i][0] <= '5') {
            color = COLOR_CYAN;
        }
        display_draw_string(10, y, countermeasures[i], color, COLOR_BLACK);
        y += 11;
    }
    
    draw_info("DEFENCE-IN-DEPTH ESSENTIAL!");
    
    sleep_ms(8000);
}

/*
 * BUTTON CALLBACKS
 */

void button_a_callback(button_t button) {
    if (!demo_running) {
        current_demo = (current_demo + 1) % DEMO_COUNT;
        display_clear(COLOR_BLACK);
        draw_title("DEMO CHANGED", COLOR_CYAN);
    }
}

void button_b_callback(button_t button) {
    if (!demo_running) {
        current_demo = (current_demo + DEMO_COUNT - 1) % DEMO_COUNT;
        display_clear(COLOR_BLACK);
        draw_title("DEMO CHANGED", COLOR_CYAN);
    }
}

void button_x_callback(button_t button) {
    demo_running = true;
}

void button_y_callback(button_t button) {
    auto_run = !auto_run;
    draw_status(auto_run ? "AUTO-RUN: ON" : "AUTO-RUN: OFF", COLOR_CYAN);
    sleep_ms(1000);
}

/*
 * MAIN PROGRAM
 */

int main() {
    stdio_init_all();
    
    // Init display
    if (display_pack_init() != DISPLAY_OK) {
        // Fallback: blink onboard LED as error indicator
        gpio_init(PICO_DEFAULT_LED_PIN);
        gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
        while (1) {
            gpio_put(PICO_DEFAULT_LED_PIN, 1);
            sleep_ms(100);
            gpio_put(PICO_DEFAULT_LED_PIN, 0);
            sleep_ms(100);
        }
    }
    
    // Init buttons
    buttons_init();
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Init power LEDs
    gpio_init(POWER_LED_1);
    gpio_init(POWER_LED_2);
    gpio_init(POWER_LED_3);
    gpio_init(POWER_LED_4);
    gpio_set_dir(POWER_LED_1, GPIO_OUT);
    gpio_set_dir(POWER_LED_2, GPIO_OUT);
    gpio_set_dir(POWER_LED_3, GPIO_OUT);
    gpio_set_dir(POWER_LED_4, GPIO_OUT);
    
    // Splash screen
    display_clear(COLOR_BLACK);
    display_draw_string(20, 60, "SIDE-CHANNEL ATTACK", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(60, 80, "DEMONSTRATION", COLOR_CYAN, COLOR_BLACK);
    //display_draw_string(40, 110, "Raspberry Pi Pico 2", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(20, 140, "A: NEXT  B: PREV", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(20, 155, "X: RUN   Y: AUTO", COLOR_GREEN, COLOR_BLACK);
    sleep_ms(3000);
    
    const char *demo_names[] = {
        "PASSWORD TIMING ATTACK",
        "AES CACHE-TIMING ATTACK",
        "POWER ANALYSIS ATTACK",
        "COUNTERMEASURES"
    };
    
    while (true) {
        buttons_update();
        
        if (!demo_running) {
            // Show menu
            display_clear(COLOR_BLACK);
            draw_title("SELECT DEMONSTRATION", COLOR_CYAN);
            
            for (int i = 0; i < DEMO_COUNT; i++) {
                uint16_t color = (i == current_demo) ? COLOR_GREEN : COLOR_WHITE;
                char line[32];
                snprintf(line, sizeof(line), "%s %d. %s",
                        (i == current_demo) ? ">" : " ", i + 1, demo_names[i]);
                display_draw_string(10, 60 + i * 20, line, color, COLOR_BLACK);
            }
            
            draw_info("A/B: SELECT  X: RUN  Y: TOGGLE AUTO");
            sleep_ms(100);
            continue;
        }
        
        // Run selected demo
        switch (current_demo) {
            case DEMO_TIMING_PASSWORD:
                demo_timing_attack_password();
                break;
                
            case DEMO_TIMING_AES:
                demo_timing_attack_aes();
                break;
                
            case DEMO_POWER_ANALYSIS:
                demo_power_analysis();
                break;
                
            case DEMO_COUNTERMEASURES:
                demo_countermeasures();
                break;
                
            default:
                break;
        }
        
        demo_running = false;
        
        if (auto_run) {
            current_demo = (current_demo + 1) % DEMO_COUNT;
            sleep_ms(1000);
            demo_running = true;
        }
    }
    
    return 0;
}
