/*
 * Side-Channel Attack Demonstration for Raspberry Pi Pico 2
 * With Pimoroni Display Pack 2.0
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <boards/pico.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "hardware/timer.h"
#include "hardware/sync.h"
#include "pico/time.h"
#include "display.h"

#define LED_R_PIN  6
#define LED_G_PIN  7
#define LED_B_PIN  8
#define PWM_WRAP   4095

// System state with proper synchronization
typedef struct {
    demo_mode_t current_demo;
    volatile bool auto_run;
    volatile bool demo_running;
    volatile bool demo_change_requested;
    volatile int8_t demo_direction; // -1, 0, or +1
} system_state_t;

static system_state_t g_state = {
    .current_demo = DEMO_TIMING_PASSWORD,
    .auto_run = false,
    .demo_running = false,
    .demo_change_requested = false,
    .demo_direction = 0
};

typedef enum {
    DEMO_TIMING_PASSWORD = 0,
    DEMO_TIMING_AES = 1,
    DEMO_POWER_ANALYSIS = 2,
    DEMO_COUNTERMEASURES = 3,
    DEMO_COUNT = 4
} demo_mode_t;

// Display layout constants
#define TITLE_Y     10
#define STATUS_Y    30
#define GRAPH_Y     80
#define GRAPH_HEIGHT 120
#define INFO_Y      210

// Maximum string buffer sizes
#define MAX_LABEL_LEN 32
#define MAX_STATUS_LEN 64
#define MAX_INFO_LEN 80


static bool rgb_led_init(void) {
    // Verify pins are valid
    if (LED_R_PIN >= NUM_BANK0_GPIOS || LED_G_PIN >= NUM_BANK0_GPIOS || 
        LED_B_PIN >= NUM_BANK0_GPIOS) {
        return false;
    }
    
    gpio_set_function(LED_R_PIN, GPIO_FUNC_PWM);
    gpio_set_function(LED_G_PIN, GPIO_FUNC_PWM);
    gpio_set_function(LED_B_PIN, GPIO_FUNC_PWM);

    uint slice_r = pwm_gpio_to_slice_num(LED_R_PIN);
    uint chan_r  = pwm_gpio_to_channel(LED_R_PIN);
    uint slice_g = pwm_gpio_to_slice_num(LED_G_PIN);
    uint chan_g  = pwm_gpio_to_channel(LED_G_PIN);
    uint slice_b = pwm_gpio_to_slice_num(LED_B_PIN);
    uint chan_b  = pwm_gpio_to_channel(LED_B_PIN);

    pwm_set_wrap(slice_r, PWM_WRAP);
    pwm_set_wrap(slice_g, PWM_WRAP);
    pwm_set_wrap(slice_b, PWM_WRAP);

    pwm_set_enabled(slice_r, true);
    pwm_set_enabled(slice_g, true);
    pwm_set_enabled(slice_b, true);

    // Start with LED off (active low)
    pwm_set_chan_level(slice_r, chan_r, PWM_WRAP);
    pwm_set_chan_level(slice_g, chan_g, PWM_WRAP);
    pwm_set_chan_level(slice_b, chan_b, PWM_WRAP);
    
    return true;
}

static void rgb_led_set(uint8_t r, uint8_t g, uint8_t b) {
    uint slice_r = pwm_gpio_to_slice_num(LED_R_PIN);
    uint chan_r  = pwm_gpio_to_channel(LED_R_PIN);
    uint slice_g = pwm_gpio_to_slice_num(LED_G_PIN);
    uint chan_g  = pwm_gpio_to_channel(LED_G_PIN);
    uint slice_b = pwm_gpio_to_slice_num(LED_B_PIN);
    uint chan_b  = pwm_gpio_to_channel(LED_B_PIN);

    // Clamp values and convert (active low)
    uint16_t level_r = PWM_WRAP - ((uint32_t)(r & 0xFF) * PWM_WRAP / 255);
    uint16_t level_g = PWM_WRAP - ((uint32_t)(g & 0xFF) * PWM_WRAP / 255);
    uint16_t level_b = PWM_WRAP - ((uint32_t)(b & 0xFF) * PWM_WRAP / 255);

    pwm_set_chan_level(slice_r, chan_r, level_r);
    pwm_set_chan_level(slice_g, chan_g, level_g);
    pwm_set_chan_level(slice_b, chan_b, level_b);
}

static void rgb_led_off(void) {
    rgb_led_set(0, 0, 0);
}



static display_error_t draw_title(const char *title, uint16_t color) {
    if (!title) return DISPLAY_ERROR_INVALID_PARAM;
    
    display_error_t err = display_fill_rect(0, 0, DISPLAY_WIDTH, 25, COLOR_BLACK);
    if (err != DISPLAY_OK) return err;
    
    return display_draw_string(10, 8, title, color, COLOR_BLACK);
}

static display_error_t draw_status(const char *status, uint16_t color) {
    if (!status) return DISPLAY_ERROR_INVALID_PARAM;
    
    display_error_t err = display_fill_rect(0, STATUS_Y, DISPLAY_WIDTH, 40, COLOR_BLACK);
    if (err != DISPLAY_OK) return err;
    
    return display_draw_string(10, STATUS_Y + 10, status, color, COLOR_BLACK);
}

static display_error_t draw_info(const char *info) {
    if (!info) return DISPLAY_ERROR_INVALID_PARAM;
    
    display_error_t err = display_fill_rect(0, INFO_Y, DISPLAY_WIDTH, 30, COLOR_BLACK);
    if (err != DISPLAY_OK) return err;
    
    return display_draw_string(5, INFO_Y + 5, info, COLOR_CYAN, COLOR_BLACK);
}

static display_error_t draw_timing_bar(uint16_t x, uint16_t y, uint16_t width, 
                                       uint16_t height, uint64_t time_us, 
                                       uint64_t max_time, uint16_t color, 
                                       const char *label) {
    if (!label) return DISPLAY_ERROR_INVALID_PARAM;
    if (max_time == 0) max_time = 1; // Prevent division by zero
    
    display_error_t err;
    
    // Draw label
    err = display_draw_string(x, y - 12, label, COLOR_WHITE, COLOR_BLACK);
    if (err != DISPLAY_OK) return err;
    
    // Draw background
    err = display_fill_rect(x, y, width, height, COLOR_BLACK);
    if (err != DISPLAY_OK) return err;
    
    // Draw border
    err = display_fill_rect(x, y, width, height, 0x2104);
    if (err != DISPLAY_OK) return err;
    
    // Calculate and clamp fill width
    uint32_t fill_width = (uint32_t)((uint64_t)width * time_us / max_time);
    if (fill_width > width) fill_width = width;
    if (fill_width < 4) fill_width = 4; // Minimum visible bar
    
    // Draw filled portion
    err = display_fill_rect(x + 2, y + 2, fill_width - 4, height - 4, color);
    if (err != DISPLAY_OK) return err;
    
    // Draw timing value
    char buf[MAX_LABEL_LEN];
    int written = snprintf(buf, sizeof(buf), "%llu us", time_us);
    if (written < 0 || written >= (int)sizeof(buf)) {
        return DISPLAY_ERROR_INVALID_PARAM;
    }
    
    return display_draw_string(x + width + 5, y + 3, buf, color, COLOR_BLACK);
}


// Cryptographic Helper Functions

static int hamming_weight(uint8_t byte) {
    int count = 0;
    for (int i = 0; i < 8; i++) {
        if (byte & (1 << i)) count++;
    }
    return count;
}

static void show_power_rgb(int hw) {
    // Clamp hamming weight to valid range
    if (hw < 0) hw = 0;
    if (hw > 8) hw = 8;
    
    float norm = hw / 8.0f;
    
    // Green (low power) -> Red (high power)
    uint8_t r = (uint8_t)(255.0f * norm * 0.85f);
    uint8_t g = (uint8_t)(255.0f * (1.0f - norm) * 0.85f);
    uint8_t b = 0;
    
    rgb_led_set(r, g, b);
}


// Password Comparison Functions

static bool check_password_vulnerable(const char *input, const char *correct) {
    if (!input || !correct) return false;
    
    size_t correct_len = strlen(correct);
    size_t input_len = strlen(input);
    
    if (input_len != correct_len) return false;
    
    for (size_t i = 0; i < correct_len; i++) {
        if (input[i] != correct[i]) return false;
        busy_wait_us(100); // Timing leak
    }
    return true;
}

static bool check_password_secure(const char *input, const char *correct) {
    if (!input || !correct) return false;
    
    size_t correct_len = strlen(correct);
    size_t input_len = strlen(input);
    size_t max_len = (input_len > correct_len) ? input_len : correct_len;
    
    uint8_t diff = 0;
    
    // Always compare all characters, constant time
    for (size_t i = 0; i < max_len; i++) {
        char c1 = (i < input_len) ? input[i] : 0;
        char c2 = (i < correct_len) ? correct[i] : 0;
        diff |= c1 ^ c2;
        busy_wait_us(100);
    }
    
    // Check length mismatch in constant time
    diff |= (input_len != correct_len) ? 1 : 0;
    
    return diff == 0;
}


// AES S-Box Functions

static const uint8_t sbox[16] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76
};

static uint8_t aes_sbox_vuln(uint8_t x) {
    uint8_t idx = x & 0x0F;
    // Simulate cache timing variation
    busy_wait_us(((x & 0x10) == 0) ? 50 : 10);
    return sbox[idx];
}

static uint8_t aes_sbox_secure(uint8_t x) {
    uint8_t idx = x & 0x0F;
    busy_wait_us(50); // Constant time
    return sbox[idx];
}


// Demos
static void demo_timing_attack_password(void) {
    const char *correct = "SECRET123";
    const char *tests[] = {
        "XXXXXXXXX",
        "SXXXXXXXX",
        "SECXXXXXX",
        "SECRXXXXX",
        "SECRET123"
    };
    const int num_tests = 5;
    
    uint64_t vuln_times[5] = {0};
    uint64_t secure_times[5] = {0};
    uint64_t max_time = 0;
    
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    draw_status("TESTING VULNERABLE IMPLEMENTATION..", COLOR_YELLOW);
    
    // Run vulnerable tests
    for (int i = 0; i < num_tests; i++) {
        uint64_t t0 = time_us_64();
        check_password_vulnerable(tests[i], correct);
        uint64_t t1 = time_us_64();
        
        // Handle timer overflow gracefully
        vuln_times[i] = (t1 >= t0) ? (t1 - t0) : 0;
        if (vuln_times[i] > max_time) max_time = vuln_times[i];
    }
    
    // Run secure tests
    for (int i = 0; i < num_tests; i++) {
        uint64_t t0 = time_us_64();
        check_password_secure(tests[i], correct);
        uint64_t t1 = time_us_64();
        
        secure_times[i] = (t1 >= t0) ? (t1 - t0) : 0;
        if (secure_times[i] > max_time) max_time = secure_times[i];
    }
    
    max_time += 100; // Add margin
    if (max_time == 0) max_time = 1; // Prevent division by zero
    
    // Display results
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (EARLY EXIT):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < num_tests; i++) {
        char label[MAX_LABEL_LEN];
        int chars_match = (i == 0) ? 0 : (i * 2 - 1);
        snprintf(label, sizeof(label), "%d chars", chars_match);
        
        draw_timing_bar(10, 60 + i * 24, 220, 18, vuln_times[i], 
                       max_time, COLOR_RED, label);
    }
    
    display_draw_string(10, 175, "SECURE (CONSTANT-TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < num_tests; i++) {
        char label[MAX_LABEL_LEN];
        int chars_match = (i == 0) ? 0 : (i * 2 - 1);
        snprintf(label, sizeof(label), "%d chars", chars_match);
        
        draw_timing_bar(10, 200 + i * 24, 220, 18, secure_times[i], 
                       max_time, COLOR_GREEN, label);
    }
    
    draw_info("VULNERABLE LEAKS PREFIX LENGTH VIA TIMING!");
    sleep_ms(6000);
}

static void demo_timing_attack_aes(void) {
    const uint8_t inputs[] = {0x00, 0x10, 0x05, 0x15, 0x0A, 0x1A, 0x0F, 0x1F};
    const int num_inputs = 8;
    
    uint64_t t_vuln[8] = {0};
    uint64_t t_secure[8] = {0};
    uint64_t max_time = 0;
    
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    draw_status("TESTING CACHE-TIMING VULNERABILITY..", COLOR_YELLOW);
    
    // Run vulnerable tests
    for (int i = 0; i < num_inputs; i++) {
        uint64_t t0 = time_us_64();
        aes_sbox_vuln(inputs[i]);
        uint64_t t1 = time_us_64();
        
        t_vuln[i] = (t1 >= t0) ? (t1 - t0) : 0;
        if (t_vuln[i] > max_time) max_time = t_vuln[i];
    }
    
    // Run secure tests
    for (int i = 0; i < num_inputs; i++) {
        uint64_t t0 = time_us_64();
        aes_sbox_secure(inputs[i]);
        uint64_t t1 = time_us_64();
        
        t_secure[i] = (t1 >= t0) ? (t1 - t0) : 0;
        if (t_secure[i] > max_time) max_time = t_secure[i];
    }
    
    max_time += 10;
    if (max_time == 0) max_time = 1;
    
    // Display results
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (CACHE TIMING):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < 5 && i < num_inputs; i++) {
        char label[MAX_LABEL_LEN];
        snprintf(label, sizeof(label), "0x%02X", inputs[i]);
        
        draw_timing_bar(10, 60 + i * 22, 220, 18, t_vuln[i], 
                       max_time, COLOR_RED, label);
    }
    
    display_draw_string(10, 170, "SECURE (CONSTANT TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < 3 && i < num_inputs; i++) {
        char label[MAX_LABEL_LEN];
        snprintf(label, sizeof(label), "0x%02X", inputs[i]);
        
        draw_timing_bar(10, 190 + i * 22, 220, 18, t_secure[i], 
                       max_time, COLOR_GREEN, label);
    }
    
    draw_info("CACHE TIMING LEAKS KEY INFORMATION!");
    sleep_ms(5500);
}

static void demo_power_analysis(void) {
    const uint8_t secret = 0b10101010;
    
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    draw_status("SIMULATING POWER CONSUMPTION..", COLOR_YELLOW);
    sleep_ms(500);
    
    display_clear(COLOR_BLACK);
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    
    char buf[MAX_STATUS_LEN];
    snprintf(buf, sizeof(buf), "SECRET KEY: 0x%02X", secret);
    display_draw_string(10, 35, buf, COLOR_YELLOW, COLOR_BLACK);
    
    display_draw_string(10, 55, "HAMMING WEIGHT -> COLOR:", COLOR_WHITE, COLOR_BLACK);
    
    // Demonstrate power consumption for different plaintexts
    for (uint8_t pt = 0; pt < 8; pt++) {
        uint8_t result = secret ^ pt;
        int hw = hamming_weight(result);
        
        char label[MAX_LABEL_LEN];
        snprintf(label, sizeof(label), "PT 0x%02X  HW:%d", pt, hw);
        display_draw_string(10, 80 + pt * 22, label, COLOR_WHITE, COLOR_BLACK);
        
        show_power_rgb(hw);
        sleep_ms(650);
    }
    
    draw_info("HIGHER HW = BRIGHTER RED = MORE POWER!");
    sleep_ms(2200);
    
    // Fade out LED
    for (int i = 40; i >= 0; i -= 4) {
        rgb_led_set(i * 2, i * 2, i * 3);
        sleep_ms(40);
    }
    rgb_led_off();
}

static void demo_countermeasures(void) {
    display_clear(COLOR_BLACK);
    draw_title("COUNTERMEASURES", COLOR_GREEN);
    
    const char *lines[] = {
        "1. CONSTANT-TIME OPERATIONS",
        "   NO SECRET-DEPENDENT BRANCHES",
        "2. MASKING",
        "   RANDOMIZE INTERMEDIATES",
        "3. BLINDING",
        "   RANDOMIZE COMPUTATION",
        "4. NOISE INJECTION",
        "   DUMMY OPS / JITTER",
        "5. HARDWARE PROTECTION",
        "   POWER/EM FILTERING"
    };
    
    int y = 45;
    const size_t num_lines = sizeof(lines) / sizeof(lines[0]);
    
    for (size_t i = 0; i < num_lines; i++) {
        display_draw_string(12, y, lines[i], COLOR_WHITE, COLOR_BLACK);
        y += 18;
    }
    
    draw_info("DEFENSE IN DEPTH ESSENTIAL!");
    sleep_ms(8500);
}

// Button Callbacks
static void button_a_callback(button_t b) {
    (void)b; // Unused parameter
    
    uint32_t save = save_and_disable_interrupts();
    if (!g_state.demo_running) {
        g_state.demo_change_requested = true;
        g_state.demo_direction = 1;
    }
    restore_interrupts(save);
}

static void button_b_callback(button_t b) {
    (void)b;
    
    uint32_t save = save_and_disable_interrupts();
    if (!g_state.demo_running) {
        g_state.demo_change_requested = true;
        g_state.demo_direction = -1;
    }
    restore_interrupts(save);
}

static void button_x_callback(button_t b) {
    (void)b;
    
    uint32_t save = save_and_disable_interrupts();
    g_state.demo_running = true;
    restore_interrupts(save);
}

static void button_y_callback(button_t b) {
    (void)b;
    
    uint32_t save = save_and_disable_interrupts();
    g_state.auto_run = !g_state.auto_run;
    restore_interrupts(save);
    
    // Show status briefly
    draw_status(g_state.auto_run ? "AUTO-RUN: ON" : "AUTO-RUN: OFF", COLOR_CYAN);
    sleep_ms(700);
}


// Error Handling and Fallback
static void error_blink_loop(void) {
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
    
    while (true) {
        gpio_put(PICO_DEFAULT_LED_PIN, 1);
        sleep_ms(100);
        gpio_put(PICO_DEFAULT_LED_PIN, 0);
        sleep_ms(100);
    }
}



int main() {
    stdio_init_all();
    
    // Initialize display with error handling
    display_error_t disp_err = display_pack_init();
    if (disp_err != DISPLAY_OK) {
        error_blink_loop(); // Never returns
    }
    
    // Initialize buttons with error handling
    display_error_t btn_err = buttons_init();
    if (btn_err != DISPLAY_OK) {
        draw_title("ERROR: BUTTONS INIT FAILED", COLOR_RED);
        sleep_ms(3000);
        error_blink_loop();
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Initialize RGB LED
    if (!rgb_led_init()) {
        draw_title("WARNING: RGB LED INIT FAILED", COLOR_YELLOW);
        sleep_ms(2000);
        // Continue without LED - not critical
    } else {
        rgb_led_set(5, 10, 30); // Gentle startup glow
    }
    
    // Splash screen
    display_clear(COLOR_BLACK);
    display_draw_string(25, 55, "SIDE-CHANNEL", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(45, 80, "ATTACK DEMO", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(25, 135, "A: NEXT   B: PREV", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(25, 155, "X: RUN    Y: AUTO", COLOR_GREEN, COLOR_BLACK);
    sleep_ms(2800);
    
    const char *demo_titles[] = {
        "PASSWORD TIMING ATTACK",
        "AES CACHE TIMING ATTACK",
        "POWER ANALYSIS (RGB LED)",
        "COUNTERMEASURES"
    };
    
    // Main loop
    while (true) {
        buttons_update();
        
        // Handle demo selection changes (thread-safe)
        uint32_t save = save_and_disable_interrupts();
        bool change_req = g_state.demo_change_requested;
        int8_t direction = g_state.demo_direction;
        g_state.demo_change_requested = false;
        restore_interrupts(save);
        
        if (change_req) {
            int new_demo = (int)g_state.current_demo + direction;
            if (new_demo < 0) new_demo = DEMO_COUNT - 1;
            if (new_demo >= DEMO_COUNT) new_demo = 0;
            g_state.current_demo = (demo_mode_t)new_demo;
        }
        
        // Display demo selection menu
        if (!g_state.demo_running) {
            display_clear(COLOR_BLACK);
            draw_title("SELECT DEMONSTRATION", COLOR_CYAN);
            
            for (int i = 0; i < DEMO_COUNT; i++) {
                uint16_t color = (i == g_state.current_demo) ? COLOR_GREEN : COLOR_WHITE;
                char line[MAX_STATUS_LEN];
                
                int written = snprintf(line, sizeof(line), "%s %d. %s",
                                      (i == g_state.current_demo) ? ">" : " ",
                                      i + 1, demo_titles[i]);
                
                if (written > 0 && written < (int)sizeof(line)) {
                    display_draw_string(10, 65 + i * 24, line, color, COLOR_BLACK);
                }
            }
            
            draw_info("A/B SELECT   X RUN   Y AUTO");
            sleep_ms(90);
            continue;
        }
        
        // Run selected demo
        switch (g_state.current_demo) {
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
                // Should never happen, but handle gracefully
                g_state.current_demo = DEMO_TIMING_PASSWORD;
                break;
        }
        
        // Demo finished
        g_state.demo_running = false;
        rgb_led_off();
        
        // Auto-advance if enabled
        if (g_state.auto_run) {
            int next = ((int)g_state.current_demo + 1) % DEMO_COUNT;
            g_state.current_demo = (demo_mode_t)next;
            sleep_ms(1200);
            g_state.demo_running = true;
        }
    }
    
    // Cleanup (unreachable but good practice)
    display_cleanup();
    return 0;
}