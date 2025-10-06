#include <stdio.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/rtc.h"

// Hardware connections
#define BUTTON_PIN 15
#define LED_PIN 25

// Generate TOTP code (must match server implementation)
uint32_t generate_totp(uint32_t timestamp, const char *secret) {
    uint32_t time_step = timestamp / 30; // 30-second intervals
    uint32_t hash = 0;
    for (int i = 0; secret[i]; i++) {
        hash = hash * 31 + secret[i] + time_step;
    }
    return (hash % 900000) + 100000; // 6-digit code
}

// Display 2FA code on console (could use LCD/OLED display) .. drop USB
void display_totp_code(uint32_t code) {
    printf("\n");
    printf("--> 2FA TOKEN\n");
    printf("--> %06u \n", code);
    printf("--> Valid for 30 seconds\n");
    printf("\n");
}

// Blink LED to indicate code generation
void blink_led(int times) {
    for (int i = 0; i < times; i++) {
        gpio_put(LED_PIN, 1);
        sleep_ms(150);
        gpio_put(LED_PIN, 0);
        sleep_ms(150);
    }
}

int main() {
    stdio_init_all();
    
    // Initialize GPIO
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);
    
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    // Initialize WiFi for time sync (optional)
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return -1;
    }
    
    printf("==> 2FA TOKEN GENERATOR\n");
    printf("==> Press button to generate code\n");
    
    bool last_button_state = true;
    uint32_t last_code_time = 0;
    
    // User database - in practice, this would be securely provisioned
    typedef struct {
        char username[32];
        char secret[32];
        int user_id;
    } token_user_t;
    
    token_user_t current_user = {"alice", "SECRET_KEY_ALICE", 0};
    
    while (1) {
        bool button_state = gpio_get(BUTTON_PIN);
        
        // Button pressed (falling edge)
        if (last_button_state && !button_state) {
            printf("Button pressed! Generating 2FA code ..\n");
            
            // Get current time (in real implementation, sync with NTP)
            uint32_t current_time = time(NULL);
            if (current_time == 0) {
                current_time = 1704067200; // Fallback: Jan 1, 2024
            }
            
            // Generate TOTP code
            uint32_t totp_code = generate_totp(current_time, current_user.secret);
            
            // Display the code
            printf("User: %s\n", current_user.username);
            display_totp_code(totp_code);
            
            // Indicate code generation with LED
            blink_led(3);
            
            // Show countdown
            printf("Code expires in: ");
            int remaining = 30 - (current_time % 30);
            for (int i = remaining; i > 0; i--) {
                printf("\rCode expires in: %2d seconds", i);
                fflush(stdout);
                sleep_ms(1000);
            }
            printf("\rCode expired!\n");
            
            last_code_time = current_time;
        }
        
        last_button_state = button_state;
        sleep_ms(50);
    }
    
    return 0;
}

