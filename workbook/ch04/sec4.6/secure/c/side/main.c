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

 * Display shows:
 * - Current demo title and explanation
 * - Real-time timing measurements
 * - Visual comparison graphs
 * - Security status indicators

 * Hardware Setup:
 * - Pimoroni Display Pack 2.0 (320x240 display + 4 buttons + RGB LED)
 *   RGB LED pins: 6=Red, 7=Green, 8=Blue (active low)
 * - Button A: Next demo
 * - Button B: Previous demo  
 * - Button X: Run current demo
 * - Button Y: Toggle auto-run
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "hardware/timer.h"
#include "pico/time.h"
#include "display.h"


#define LED_R_PIN  6
#define LED_G_PIN  7
#define LED_B_PIN  8

#define PWM_WRAP   4095     // 12-bit res

static void rgb_led_init(void) {
    gpio_set_function(LED_R_PIN, GPIO_FUNC_PWM);
    gpio_set_function(LED_G_PIN, GPIO_FUNC_PWM);
    gpio_set_function(LED_B_PIN, GPIO_FUNC_PWM);

    uint slice_r = pwm_gpio_to_slice_num(LED_R_PIN);
    uint chan_r  = pwm_gpio_to_channel(LED_R_PIN);
    uint slice_g = pwm_gpio_to_slice_num(LED_G_PIN);
    uint chan_g  = pwm_gpio_to_channel(LED_G_PIN);
    uint slice_b = pwm_gpio_to_slice_num(LED_B_PIN);
    uint chan_b  = pwm_gpio_to_channel(LED_B_PIN);

    // Configure same wrap value and enable all channels
    pwm_set_wrap(slice_r, PWM_WRAP);
    pwm_set_wrap(slice_g, PWM_WRAP);
    pwm_set_wrap(slice_b, PWM_WRAP);

    pwm_set_enabled(slice_r, true);
    pwm_set_enabled(slice_g, true);
    pwm_set_enabled(slice_b, true);

    // Start with LED off (active low -> full PWM value = off)
    pwm_set_chan_level(slice_r, chan_r, PWM_WRAP);
    pwm_set_chan_level(slice_g, chan_g, PWM_WRAP);
    pwm_set_chan_level(slice_b, chan_b, PWM_WRAP);
}

// Set RGB values 0-255 (0=off, 255=full brightness)
// Internally inverted because LED is active low
static void rgb_led_set(uint8_t r, uint8_t g, uint8_t b) {
    uint slice_r = pwm_gpio_to_slice_num(LED_R_PIN);
    uint chan_r  = pwm_gpio_to_channel(LED_R_PIN);
    uint slice_g = pwm_gpio_to_slice_num(LED_G_PIN);
    uint chan_g  = pwm_gpio_to_channel(LED_G_PIN);
    uint slice_b = pwm_gpio_to_slice_num(LED_B_PIN);
    uint chan_b  = pwm_gpio_to_channel(LED_B_PIN);

    uint16_t level_r = PWM_WRAP - ((uint32_t)r * PWM_WRAP / 255);
    uint16_t level_g = PWM_WRAP - ((uint32_t)g * PWM_WRAP / 255);
    uint16_t level_b = PWM_WRAP - ((uint32_t)b * PWM_WRAP / 255);

    pwm_set_chan_level(slice_r, chan_r, level_r);
    pwm_set_chan_level(slice_g, chan_g, level_g);
    pwm_set_chan_level(slice_b, chan_b, level_b);
}

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
#define TITLE_Y     10
#define STATUS_Y    30
#define GRAPH_Y     80
#define GRAPH_HEIGHT 120
#define INFO_Y      210

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
    display_draw_string(x, y - 12, label, COLOR_WHITE, COLOR_BLACK);
    display_fill_rect(x, y, width, height, COLOR_BLACK);
    display_fill_rect(x, y, width, height, 0x2104); // border
    
    uint16_t fill_width = (uint32_t)width * time_us / max_time;
    if (fill_width > width) fill_width = width;
    display_fill_rect(x + 2, y + 2, fill_width - 4, height - 4, color);
    
    char buf[16];
    snprintf(buf, sizeof(buf), "%llu us", time_us);
    display_draw_string(x + width + 5, y + 3, buf, color, COLOR_BLACK);
}


int hamming_weight(uint8_t byte) {
    int count = 0;
    for (int i = 0; i < 8; i++) {
        if (byte & (1 << i)) count++;
    }
    return count;
}

void show_power_rgb(int hw) {  // hw = 0..8
    float norm = hw / 8.0f;
    
    // Green (low) -> Yellow -> Red (high)
    uint8_t r = (uint8_t)(255.0f * norm);
    uint8_t g = (uint8_t)(255.0f * (1.0f - norm));
    uint8_t b = 0;
    
    // Optional: slightly warmer / less aggressive green
    // g = (uint8_t)(200.0f * (1.0f - norm) + 55.0f * norm);
    
    // Reduce max brightness a bit (too bright can be uncomfortable)
    r = r * 85 / 100;
    g = g * 85 / 100;
    b = b * 85 / 100;
    
    rgb_led_set(r, g, b);
}


bool check_password_vulnerable(const char *input, const char *correct) {
    size_t len = strlen(correct);
    if (strlen(input) != len) return false;
    
    for (size_t i = 0; i < len; i++) {
        if (input[i] != correct[i]) return false;
        busy_wait_us(100);
    }
    return true;
}

bool check_password_secure(const char *input, const char *correct) {
    size_t len = strlen(correct);
    if (strlen(input) != len) len = strlen(input);
    
    uint8_t diff = 0;
    for (size_t i = 0; i < len; i++) {
        diff |= input[i] ^ correct[i];
        busy_wait_us(100);
    }
    return diff == 0;
}


void demo_timing_attack_password(void) {
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    draw_status("TESTING VULNERABLE IMPLEMENTATION..", COLOR_YELLOW);
    
    const char *correct = "SECRET123";
    const char *tests[] = {"XXXXXXXXX","SXXXXXXXX","SECXXXXXX","SECRXXXXX","SECRET123"};
    const int n = 5;
    
    uint64_t vuln_times[5] = {0};
    uint64_t secure_times[5] = {0};
    uint64_t max_t = 0;
    
    for (int i = 0; i < n; i++) {
        uint64_t t0 = time_us_64();
        check_password_vulnerable(tests[i], correct);
        vuln_times[i] = time_us_64() - t0;
        if (vuln_times[i] > max_t) max_t = vuln_times[i];
    }
    
    for (int i = 0; i < n; i++) {
        uint64_t t0 = time_us_64();
        check_password_secure(tests[i], correct);
        secure_times[i] = time_us_64() - t0;
        if (secure_times[i] > max_t) max_t = secure_times[i];
    }
    
    max_t += 100;
    
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: PASSWORD", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (EARLY EXIT):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < n; i++) {
        char lbl[16];
        snprintf(lbl, sizeof(lbl), "%d chars", i * 2 + (i>0));
        draw_timing_bar(10, 60 + i*24, 220, 18, vuln_times[i], max_t, COLOR_RED, lbl);
    }
    
    display_draw_string(10, 175, "SECURE (CONSTANT-TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < n; i++) {
        char lbl[16];
        snprintf(lbl, sizeof(lbl), "%d chars", i * 2 + (i>0));
        draw_timing_bar(10, 200 + i*24, 220, 18, secure_times[i], max_t, COLOR_GREEN, lbl);
    }
    
    draw_info("VULNERABLE VERSION LEAKS PREFIX LENGTH THROUGH TIMING!");
    sleep_ms(6000);
}


static const uint8_t sbox[16] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76
};

uint8_t aes_sbox_vuln(uint8_t x) {
    uint8_t idx = x & 0x0F;
    busy_wait_us( ((x & 0x10)==0) ? 50 : 10 ); // simulate cache timing
    return sbox[idx];
}

uint8_t aes_sbox_secure(uint8_t x) {
    uint8_t idx = x & 0x0F;
    busy_wait_us(50); // constant time
    return sbox[idx];
}

void demo_timing_attack_aes(void) {
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    draw_status("TESTING CACHE-TIMING VULNERABILITY..", COLOR_YELLOW);
    
    uint8_t inputs[] = {0x00,0x10,0x05,0x15,0x0A,0x1A,0x0F,0x1F};
    const int n = 8;
    
    uint64_t t_vuln[8]={0}, t_secure[8]={0};
    uint64_t maxt = 0;
    
    for (int i = 0; i < n; i++) {
        uint64_t t0 = time_us_64();
        aes_sbox_vuln(inputs[i]);
        t_vuln[i] = time_us_64() - t0;
        if (t_vuln[i] > maxt) maxt = t_vuln[i];
    }
    
    for (int i = 0; i < n; i++) {
        uint64_t t0 = time_us_64();
        aes_sbox_secure(inputs[i]);
        t_secure[i] = time_us_64() - t0;
        if (t_secure[i] > maxt) maxt = t_secure[i];
    }
    
    maxt += 10;
    
    display_clear(COLOR_BLACK);
    draw_title("TIMING ATTACK: AES S-BOX", COLOR_RED);
    
    display_draw_string(10, 35, "VULNERABLE (CACHE TIMING):", COLOR_RED, COLOR_BLACK);
    for (int i = 0; i < 5; i++) {
        char lbl[16];
        snprintf(lbl, sizeof(lbl), "0x%02X", inputs[i]);
        draw_timing_bar(10, 60 + i*22, 220, 18, t_vuln[i], maxt, COLOR_RED, lbl);
    }
    
    display_draw_string(10, 170, "SECURE (CONSTANT TIME):", COLOR_GREEN, COLOR_BLACK);
    for (int i = 0; i < 3; i++) {
        char lbl[16];
        snprintf(lbl, sizeof(lbl), "0x%02X", inputs[i]);
        draw_timing_bar(10, 190 + i*22, 220, 18, t_secure[i], maxt, COLOR_GREEN, lbl);
    }
    
    draw_info("CACHE TIMING DIFFERENCES CAN LEAK KEY INFORMATION!");
    sleep_ms(5500);
}


void demo_power_analysis(void) {
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    draw_status("SIMULATING POWER CONSUMPTION..", COLOR_YELLOW);
    
    uint8_t secret = 0b10101010;
    
    display_clear(COLOR_BLACK);
    draw_title("POWER ANALYSIS ATTACK", COLOR_RED);
    
    char buf[32];
    snprintf(buf, sizeof(buf), "SECRET KEY: 0x%02X", secret);
    display_draw_string(10, 35, buf, COLOR_YELLOW, COLOR_BLACK);
    
    display_draw_string(10, 55, "HAMMING WEIGHT -> COLOR:", COLOR_WHITE, COLOR_BLACK);
    
    for (uint8_t pt = 0; pt < 8; pt++) {
        uint8_t result = secret ^ pt;
        int hw = hamming_weight(result);
        
        char lbl[24];
        snprintf(lbl, sizeof(lbl), "PT 0x%02X  HW:%d", pt, hw);
        display_draw_string(10, 80 + pt*22, lbl, COLOR_WHITE, COLOR_BLACK);
        
        show_power_rgb(hw);
        sleep_ms(650);
    }
    
    draw_info("HIGHER HW -> BRIGHTER RED = MORE POWER LEAKAGE!");
    sleep_ms(2200);
    
    // Nice fade out
    for (int i = 40; i >= 0; i -= 4) {
        rgb_led_set(i*2, i*2, i*3);
        sleep_ms(40);
    }
    rgb_led_set(0,0,0);
}


void demo_countermeasures(void) {
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
"   DUMMY OPERATIONS / JITTER",
"5. HARDWARE PROTECTION",
"   POWER/EM FILTERING AND SHIELDING"
    };
    
    int y = 45;
    for (size_t i = 0; i < sizeof(lines)/sizeof(lines[0]); i++) {
        display_draw_string(12, y, lines[i], COLOR_WHITE, COLOR_BLACK);
        y += 18;
    }
    
    draw_info("DEFENSE IN DEPTH ESSENTIAL!");
    sleep_ms(8500);
}


void button_a_callback(button_t b) {
    if (!demo_running) {
        current_demo = (current_demo + 1) % DEMO_COUNT;
        display_clear(COLOR_BLACK);
        draw_title("DEMO CHANGED", COLOR_CYAN);
    }
}

void button_b_callback(button_t b) {
    if (!demo_running) {
        current_demo = (current_demo + DEMO_COUNT - 1) % DEMO_COUNT;
        display_clear(COLOR_BLACK);
        draw_title("DEMO CHANGED", COLOR_CYAN);
    }
}

void button_x_callback(button_t b) {
    demo_running = true;
}

void button_y_callback(button_t b) {
    auto_run = !auto_run;
    draw_status(auto_run ? "AUTO-RUN: ON" : "AUTO-RUN: OFF", COLOR_CYAN);
    sleep_ms(700);
}


int main() {
    stdio_init_all();
    
    // Init display
    if (display_pack_init() != DISPLAY_OK) {
        gpio_init(PICO_DEFAULT_LED_PIN);
        gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
        while (true) {
            gpio_put(PICO_DEFAULT_LED_PIN, 1);
            sleep_ms(80);
            gpio_put(PICO_DEFAULT_LED_PIN, 0);
            sleep_ms(80);
        }
    }
    
    // Init buttons
    buttons_init();
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Init RGB LED with PWM
    rgb_led_init();
    rgb_led_set(5, 10, 30);  // gentle cyan startup glow
    
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
    
    while (true) {
        buttons_update();
        
        if (!demo_running) {
            display_clear(COLOR_BLACK);
            draw_title("SELECT DEMONSTRATION", COLOR_CYAN);
            
            for (int i = 0; i < DEMO_COUNT; i++) {
                uint16_t col = (i == current_demo) ? COLOR_GREEN : COLOR_WHITE;
                char line[48];
                snprintf(line, sizeof(line), "%s %d. %s",
                         (i == current_demo) ? ">" : " ", i+1, demo_titles[i]);
                display_draw_string(10, 65 + i*24, line, col, COLOR_BLACK);
            }
            
            draw_info("A/B SELECT   X RUN   Y AUTO");
            sleep_ms(90);
            continue;
        }
        
        // Run selected demo
        switch (current_demo) {
            case DEMO_TIMING_PASSWORD:    demo_timing_attack_password();    break;
            case DEMO_TIMING_AES:         demo_timing_attack_aes();         break;
            case DEMO_POWER_ANALYSIS:     demo_power_analysis();            break;
            case DEMO_COUNTERMEASURES:    demo_countermeasures();           break;
        }
        
        demo_running = false;
        rgb_led_set(0,0,0);  // LED off between demos
        
        if (auto_run) {
            current_demo = (current_demo + 1) % DEMO_COUNT;
            sleep_ms(1200);
            demo_running = true;
        }
    }
    
    return 0;
}
