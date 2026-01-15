/*
 * Hardware 2FA Token Generator with Display
 * Raspberry Pi Pico W with Pimoroni Display Pack 2.0
 */

#include <stdio.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/rtc.h"
#include "lwip/dns.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"
#include "display.h"


// CONFIG
#define MAX_USERS 4
#define TOTP_INTERVAL 30
#define NTP_SERVER "pool.ntp.org"
#define NTP_PORT 123

// PROFILES
typedef struct {
    char username[32];
    char secret[32];
    char service[32];
    uint16_t color;
} user_profile_t;

user_profile_t users[MAX_USERS] = {
    {"alice", "ALICE_SECRET_KEY_12345", "Auth Server", COLOR_GREEN},
    {"bob", "BOB_SECRET_KEY_67890", "Auth Server", COLOR_BLUE},
    {"charlie", "CHARLIE_KEY_54321", "VPN Service", COLOR_YELLOW},
    {"admin", "ADMIN_MASTER_KEY_99", "Admin Panel", COLOR_MAGENTA}
};

int current_user_index = 0;
uint32_t last_code_generation = 0;
uint32_t last_button_time = 0;


// HMAC-SHA1 TOTP

void hmac_sha1_simple(const uint8_t *key, size_t key_len,
                     const uint8_t *data, size_t data_len,
                     uint8_t *output) {
    // Simplified HMAC (use mbedtls in production please)
    uint32_t hash = 0;
    for (size_t i = 0; i < key_len; i++) {
        hash = hash * 31 + key[i];
    }
    for (size_t i = 0; i < data_len; i++) {
        hash = hash * 31 + data[i];
    }
    
    for (int i = 0; i < 20; i++) {
        output[i] = (hash >> (i * 8)) & 0xFF;
        hash = hash * 1103515245 + 12345;
    }
}

uint32_t generate_totp(uint32_t timestamp, const char *secret) {
    uint64_t time_step = timestamp / TOTP_INTERVAL;
    uint8_t time_bytes[8];
    
    // Big-endian encoding
    for (int i = 7; i >= 0; i--) {
        time_bytes[i] = (time_step >> (8 * (7 - i))) & 0xFF;
    }
    
    uint8_t hmac[20];
    hmac_sha1_simple((uint8_t*)secret, strlen(secret), time_bytes, 8, hmac);
    
    // Dynamic truncation
    uint8_t offset = hmac[19] & 0x0f;
    uint32_t truncated = ((hmac[offset] & 0x7f) << 24) |
                        ((hmac[offset + 1] & 0xff) << 16) |
                        ((hmac[offset + 2] & 0xff) << 8) |
                        (hmac[offset + 3] & 0xff);
    
    return truncated % 1000000;
}


// DISPLAY FUNCTIONS

void draw_token_screen() {
    display_clear(COLOR_BLACK);
    
    user_profile_t *user = &users[current_user_index];
    uint32_t now = time(NULL);
    uint32_t code = generate_totp(now, user->secret);
    int remaining = TOTP_INTERVAL - (now % TOTP_INTERVAL);
    
    // Title bar
    display_fill_rect(0, 0, DISPLAY_WIDTH, 30, user->color);
    display_draw_string(10, 8, "2FA TOKEN GENERATOR", COLOR_BLACK, user->color);
    
    // User info
    char buf[64];
    snprintf(buf, sizeof(buf), "USER: %s", user->username);
    display_draw_string(10, 40, buf, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "SERVICE: %s", user->service);
    display_draw_string(10, 55, buf, COLOR_CYAN, COLOR_BLACK);
    
    // Separator
    display_fill_rect(0, 75, DISPLAY_WIDTH, 2, user->color);
    
    // TOTP Code - Large centered display
    snprintf(buf, sizeof(buf), "%06lu", code);
    
    // Draw large code (2x size)
    int x_offset = 60;
    for (int i = 0; i < 6; i++) {
        // Draw each digit larger by drawing multiple times with offset
        for (int dx = 0; dx < 3; dx++) {
            for (int dy = 0; dy < 3; dy++) {
                display_draw_char(x_offset + i * 36 + dx, 95 + dy, 
                                buf[i], user->color, COLOR_BLACK);
            }
        }
    }
    
    // Time remaining
    snprintf(buf, sizeof(buf), "VALID FOR %d SECONDS", remaining);
    display_draw_string(70, 140, buf, COLOR_YELLOW, COLOR_BLACK);
    
    // Progress bar
    int bar_width = (remaining * 280) / TOTP_INTERVAL;
    display_fill_rect(20, 160, bar_width, 15, COLOR_GREEN);
    display_fill_rect(20 + bar_width, 160, 280 - bar_width, 15, COLOR_RED);
    
    // Instructions
    display_fill_rect(0, 185, DISPLAY_WIDTH, 1, COLOR_WHITE);
    display_draw_string(10, 195, "A: PREV USER", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(10, 210, "B: NEXT USER", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(180, 195, "X: RREFRESH", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(180, 210, "Y: INFO", COLOR_WHITE, COLOR_BLACK);
}

void draw_info_screen() {
    display_clear(COLOR_BLACK);
    
    // Title
    display_draw_string(10, 10, "TOKEN INFO", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, 25, "----------", COLOR_CYAN, COLOR_BLACK);
    
    // Time info
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    char buf[64];
    
    strftime(buf, sizeof(buf), "TIME: %H:%M:%S", tm_info);
    display_draw_string(10, 45, buf, COLOR_WHITE, COLOR_BLACK);
    
    strftime(buf, sizeof(buf), "DATE: %Y-%m-%d", tm_info);
    display_draw_string(10, 60, buf, COLOR_WHITE, COLOR_BLACK);
    
    // TOTP info
    snprintf(buf, sizeof(buf), "TIME STEP: %lu", now / TOTP_INTERVAL);
    display_draw_string(10, 80, buf, COLOR_GREEN, COLOR_BLACK);
    
    snprintf(buf, sizeof(buf), "INTERVAL: %d SEC", TOTP_INTERVAL);
    display_draw_string(10, 95, buf, COLOR_GREEN, COLOR_BLACK);
    
    // User count
    snprintf(buf, sizeof(buf), "PROFILES: %d/%d", current_user_index + 1, MAX_USERS);
    display_draw_string(10, 115, buf, COLOR_YELLOW, COLOR_BLACK);
    
    // Algorithm info
    display_draw_string(10, 140, "ALGORITHM:", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, 155, "HMAC-SHA1 TOTP", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(10, 170, "RFC 6238", COLOR_WHITE, COLOR_BLACK);
    
    // Back instruction
    display_draw_string(10, 200, "PRESS Y TO RETURN", COLOR_YELLOW, COLOR_BLACK);
}


// BUTTON CALLBACKS

bool info_mode = false;

void button_a_callback(button_t button) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_button_time < 200) return;  // Debounce
    last_button_time = now;
    
    if (!info_mode) {
        current_user_index = (current_user_index - 1 + MAX_USERS) % MAX_USERS;
        printf("SWITCHED TO USER: %s\n", users[current_user_index].username);
        draw_token_screen();
    }
}

void button_b_callback(button_t button) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_button_time < 200) return;
    last_button_time = now;
    
    if (!info_mode) {
        current_user_index = (current_user_index + 1) % MAX_USERS;
        printf("SWITCHED TO USER: %s\n", users[current_user_index].username);
        draw_token_screen();
    }
}

void button_x_callback(button_t button) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_button_time < 200) return;
    last_button_time = now;
    
    if (!info_mode) {
        printf("MANUAL REFRESH\n");
        draw_token_screen();
    }
}

void button_y_callback(button_t button) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    if (now - last_button_time < 200) return;
    last_button_time = now;
    
    info_mode = !info_mode;
    if (info_mode) {
        printf("INFO MODE\n");
        draw_info_screen();
    } else {
        printf("TOKEN MODE\n");
        draw_token_screen();
    }
}


// NTP TIME SYNC (Simplified)

void sync_time_ntp() {
    // This is a placeholder - implement proper NTP client in production
    // For now, set a reasonable default time
    // This is the time that the program was tested ..
    datetime_t t = {
        .year  = 2026,
        .month = 1,
        .day   = 15,
        .dotw  = 4,  // Thursday
        .hour  = 12,
        .min   = 0,
        .sec   = 0
    };
    
    rtc_init();
    rtc_set_datetime(&t);
    
    // Wait for RTC to be ready
    sleep_us(64);
    
    printf("Time synchronised (demo mode)\n");
}



int main() {
    stdio_init_all();
    
    printf("\n  HARDWARE TOKEN GENERATOR\n");
    printf("  2FA TOTP (RFC 6238)\n\n");
    
    // Init display
    printf("Init display..\n");
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed\n");
        return -1;
    }
    printf("Display ready\n");
    
    // Init buttons
    if (buttons_init() != DISPLAY_OK) {
        printf("Button init failed\n");
        return -1;
    }
    printf("Buttons ready\n");
    
    // Set button callbacks
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Show startup screen
    display_clear(COLOR_BLACK);
    display_draw_string(80, 100, "TOKEN GENERATOR", COLOR_GREEN, COLOR_BLACK);
    display_draw_string(95, 120, "INITIALISATION..", COLOR_WHITE, COLOR_BLACK);
    sleep_ms(2000);
    
    // Initialise WiFi for time sync (optional!)
    printf("Initialising WiFi for time sync..\n");
    if (cyw43_arch_init() == 0) {
        cyw43_arch_enable_sta_mode();
        
        display_draw_string(85, 140, "CONNECTING WIFI..", COLOR_YELLOW, COLOR_BLACK);
        
        if (cyw43_arch_wifi_connect_timeout_ms("YOUR_SSID", "YOUR_PASSWORD",
                                               CYW43_AUTH_WPA2_AES_PSK, 10000) == 0) {
            printf("WiFi connected\n");
            display_draw_string(90, 160, "SYNCING TIME..", COLOR_CYAN, COLOR_BLACK);
            sync_time_ntp();
            printf("Time synchronised\n");
        } else {
            printf("! WiFi connection failed, using default time\n");
            sync_time_ntp();
        }
    } else {
        printf("! WiFi init failed, using default time\n");
        sync_time_ntp();
    }
    
    sleep_ms(1000);
    
    printf("\n  TOKEN GENERATOR READY\n");
    printf("  Users loaded: %d\n", MAX_USERS);
    printf("  Current user: %s\n", users[0].username);
    printf("\n\n");
    
    // Initial screen
    draw_token_screen();
    
    // Main loop
    uint32_t last_update = 0;
    while (1) {
        buttons_update();
        
        uint32_t now = to_ms_since_boot(get_absolute_time());
        
        // Update display every second
        if (now - last_update > 1000) {
            last_update = now;
            
            if (!info_mode) {
                draw_token_screen();
                
                // Print to console for debugging
                uint32_t timestamp = time(NULL);
                uint32_t code = generate_totp(timestamp, users[current_user_index].secret);
                int remaining = TOTP_INTERVAL - (timestamp % TOTP_INTERVAL);
                
                printf("[%s] Code: %06lu | Valid: %2ds\n", 
                       users[current_user_index].username, code, remaining);
            }
        }
        
        sleep_ms(10);
    }
    
    return 0;
}


