#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"

// Configuration
#define BUTTON_PIN 14
#define LED_PIN 15
#define UDP_PORT 4242
#define SERVER_IP "192.168.4.1"  // Default AP IP
#define PLAYER_NAME "Player1"    // Change to "Player2" for second controller

// Button state
bool button_pressed = false;
bool button_handled = false;
int player_id = -1;
bool game_active = false;

struct udp_pcb *udp_pcb_handle;
ip_addr_t server_addr;

void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == BUTTON_PIN && (events & GPIO_IRQ_EDGE_FALL)) {
        button_pressed = true;
    }
}

void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    if (p != NULL) {
        char buffer[64];
        memcpy(buffer, p->payload, p->len);
        buffer[p->len] = '\0';
        
        printf("Received: %s\n", buffer);
        
        // Handle JOINED message
        if (strncmp(buffer, "JOINED:", 7) == 0) {
            player_id = atoi(buffer + 7);
            printf("Assigned Player ID: %d\n", player_id);
            
            // Flash LED to confirm
            for(int i = 0; i < player_id; i++) {
                gpio_put(LED_PIN, 1);
                sleep_ms(200);
                gpio_put(LED_PIN, 0);
                sleep_ms(200);
            }
        }
        
        // Handle GO message
        if (strcmp(buffer, "GO!") == 0) {
            game_active = true;
            button_handled = false;
            gpio_put(LED_PIN, 1); // LED on during active round
            printf("Game active! Press button!\n");
        }
        
        // Handle result/timeout messages
        if (strstr(buffer, "ms") != NULL || strcmp(buffer, "GAME_OVER") == 0) {
            game_active = false;
            gpio_put(LED_PIN, 0);
            
            // Check if this player won
            char check[16];
            snprintf(check, sizeof(check), "P%d:", player_id);
            if (strstr(buffer, check) != NULL) {
                // Winner! Flash LED rapidly
                for(int i = 0; i < 6; i++) {
                    gpio_put(LED_PIN, 1);
                    sleep_ms(100);
                    gpio_put(LED_PIN, 0);
                    sleep_ms(100);
                }
            }
        }
        
        pbuf_free(p);
    }
}

void send_button_press() {
    if (player_id < 0) return;
    
    char msg[32];
    snprintf(msg, sizeof(msg), "BUTTON:%d", player_id);
    
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, strlen(msg), PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, msg, strlen(msg));
        udp_sendto(udp_pcb_handle, p, &server_addr, UDP_PORT);
        pbuf_free(p);
        printf("Sent button press\n");
    }
}

void send_join_request() {
    char msg[32];
    snprintf(msg, sizeof(msg), "JOIN:%s", PLAYER_NAME);
    
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, strlen(msg), PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, msg, strlen(msg));
        udp_sendto(udp_pcb_handle, p, &server_addr, UDP_PORT);
        pbuf_free(p);
        printf("Sent join request\n");
    }
}

int main() {
    stdio_init_all();
    
    // Setup button GPIO
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);
    
    // Setup LED GPIO
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);
    
    // Enable interrupt for button
    gpio_set_irq_enabled_with_callback(BUTTON_PIN, GPIO_IRQ_EDGE_FALL, true, &gpio_callback);
    
    // Initialize WiFi
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return -1;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to ButtonBash AP...\n");
    
    if (cyw43_arch_wifi_connect_timeout_ms("ButtonBash", "picopico", CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("Failed to connect\n");
        return -1;
    }
    
    printf("Connected!\n");
    
    // Setup UDP
    udp_pcb_handle = udp_new();
    udp_bind(udp_pcb_handle, IP_ADDR_ANY, 0);  // Bind to any port
    udp_recv(udp_pcb_handle, udp_recv_callback, NULL);
    
    // Set server address
    ipaddr_aton(SERVER_IP, &server_addr);
    
    // Send join request
    sleep_ms(1000);
    send_join_request();
    
    // Flash LED to show ready
    gpio_put(LED_PIN, 1);
    sleep_ms(500);
    gpio_put(LED_PIN, 0);
    
    printf("Ready to play!\n");
    
    while (true) {
        cyw43_arch_poll();
        
        // Handle button press during active game
        if (button_pressed && game_active && !button_handled) {
            send_button_press();
            button_handled = true;
            button_pressed = false;
            
            // Quick LED flash for feedback
            gpio_put(LED_PIN, 0);
            sleep_ms(50);
            gpio_put(LED_PIN, 1);
        }
        
        // Reset button state when game not active
        if (!game_active) {
            button_pressed = false;
        }
        
        sleep_ms(10);
    }
    
    cyw43_arch_deinit();
    return 0;
}