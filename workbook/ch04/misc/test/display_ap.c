#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"

// DisplayPack 2.0 ST7789 Configuration 
// Change to def driver?
#define LCD_WIDTH 320
#define LCD_HEIGHT 240
#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS   17
#define PIN_SCK  18
#define PIN_MOSI 19
#define PIN_DC   20
#define PIN_RST  21
#define PIN_BL   22

// UDP Configuration
#define UDP_PORT 4242
#define MAX_PLAYERS 2

// Game States
typedef enum {
    WAITING_FOR_PLAYERS,
    COUNTDOWN,
    SHOWING_PROMPT,
    WAITING_FOR_RESPONSE,
    SHOWING_RESULTS,
    GAME_OVER
} GameState;

// Player data
typedef struct {
    ip_addr_t addr;
    uint16_t port;
    bool connected;
    uint32_t reaction_time;
    int score;
    char name[16];
} Player;

Player players[MAX_PLAYERS];
int player_count = 0;
GameState game_state = WAITING_FOR_PLAYERS;
uint32_t prompt_start_time = 0;
int winner = -1;
int round_num = 0;
const int MAX_ROUNDS = 5;

// LCD Functions (simplified for ST7789)
void lcd_write_cmd(uint8_t cmd) {
    gpio_put(PIN_DC, 0);
    gpio_put(PIN_CS, 0);
    spi_write_blocking(SPI_PORT, &cmd, 1);
    gpio_put(PIN_CS, 1);
}

void lcd_write_data(uint8_t data) {
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    spi_write_blocking(SPI_PORT, &data, 1);
    gpio_put(PIN_CS, 1);
}

void lcd_init() {
    // Initialize SPI
    spi_init(SPI_PORT, 62500000); // 62.5MHz
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    
    gpio_init(PIN_CS);
    gpio_init(PIN_DC);
    gpio_init(PIN_RST);
    gpio_init(PIN_BL);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_set_dir(PIN_DC, GPIO_OUT);
    gpio_set_dir(PIN_RST, GPIO_OUT);
    gpio_set_dir(PIN_BL, GPIO_OUT);
    
    // Reset LCD
    gpio_put(PIN_RST, 1);
    sleep_ms(5);
    gpio_put(PIN_RST, 0);
    sleep_ms(20);
    gpio_put(PIN_RST, 1);
    sleep_ms(150);
    
    // Initialize ST7789
    lcd_write_cmd(0x01); // Software reset
    sleep_ms(150);
    
    lcd_write_cmd(0x11); // Sleep out
    sleep_ms(500);
    
    lcd_write_cmd(0x3A); // Color mode
    lcd_write_data(0x55); // 16-bit color
    
    lcd_write_cmd(0x36); // Memory access control
    lcd_write_data(0x00);
    
    lcd_write_cmd(0x29); // Display on
    sleep_ms(100);
    
    gpio_put(PIN_BL, 1); // Backlight on
}

void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    lcd_write_cmd(0x2A); // Column address set
    lcd_write_data(x0 >> 8);
    lcd_write_data(x0 & 0xFF);
    lcd_write_data(x1 >> 8);
    lcd_write_data(x1 & 0xFF);
    
    lcd_write_cmd(0x2B); // Row address set
    lcd_write_data(y0 >> 8);
    lcd_write_data(y0 & 0xFF);
    lcd_write_data(y1 >> 8);
    lcd_write_data(y1 & 0xFF);
    
    lcd_write_cmd(0x2C); // Write to RAM
}

void lcd_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
    lcd_set_window(x, y, x + w - 1, y + h - 1);
    
    gpio_put(PIN_DC, 1);
    gpio_put(PIN_CS, 0);
    
    uint8_t hi = color >> 8;
    uint8_t lo = color & 0xFF;
    
    for(uint32_t i = 0; i < w * h; i++) {
        spi_write_blocking(SPI_PORT, &hi, 1);
        spi_write_blocking(SPI_PORT, &lo, 1);
    }
    
    gpio_put(PIN_CS, 1);
}

void lcd_clear(uint16_t color) {
    lcd_fill_rect(0, 0, LCD_WIDTH, LCD_HEIGHT, color);
}

void lcd_draw_text(const char* text, uint16_t x, uint16_t y, uint16_t color, uint16_t bg, uint8_t size) {
    // Simple large text rendering - draw as rectangles for visibility
    int text_len = strlen(text);
    int char_width = 16 * size;
    int char_height = 20 * size;
    
    // Clear background
    lcd_fill_rect(x, y, char_width * text_len, char_height, bg);
    
    // Draw simple block letters (very basic representation)
    for(int i = 0; i < text_len; i++) {
        lcd_fill_rect(x + i * char_width, y, char_width - 4, char_height, color);
    }
}

// UDP Receive callback
void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    if (p != NULL) {
        char buffer[64];
        memcpy(buffer, p->payload, p->len);
        buffer[p->len] = '\0';
        
        printf("Received: %s from %s:%d\n", buffer, ipaddr_ntoa(addr), port);
        
        // Handle JOIN message
        if (strncmp(buffer, "JOIN:", 5) == 0 && player_count < MAX_PLAYERS) {
            players[player_count].addr = *addr;
            players[player_count].port = port;
            players[player_count].connected = true;
            players[player_count].score = 0;
            strncpy(players[player_count].name, buffer + 5, 15);
            players[player_count].name[15] = '\0';
            
            // Send acknowledgment
            char ack[32];
            snprintf(ack, sizeof(ack), "JOINED:%d", player_count + 1);
            struct pbuf *p_ack = pbuf_alloc(PBUF_TRANSPORT, strlen(ack), PBUF_RAM);
            memcpy(p_ack->payload, ack, strlen(ack));
            udp_sendto(pcb, p_ack, addr, port);
            pbuf_free(p_ack);
            
            player_count++;
            printf("Player %d joined: %s\n", player_count, players[player_count-1].name);
            
            if (player_count == MAX_PLAYERS) {
                game_state = COUNTDOWN;
            }
        }
        
        // Handle BUTTON message
        if (strncmp(buffer, "BUTTON:", 7) == 0 && game_state == WAITING_FOR_RESPONSE) {
            int player_id = atoi(buffer + 7);
            if (player_id > 0 && player_id <= player_count && winner == -1) {
                winner = player_id - 1;
                players[winner].reaction_time = time_us_32() - prompt_start_time;
                players[winner].score++;
                game_state = SHOWING_RESULTS;
            }
        }
        
        pbuf_free(p);
    }
}

void broadcast_message(struct udp_pcb *pcb, const char* msg) {
    for(int i = 0; i < player_count; i++) {
        if(players[i].connected) {
            struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, strlen(msg), PBUF_RAM);
            memcpy(p->payload, msg, strlen(msg));
            udp_sendto(pcb, p, &players[i].addr, players[i].port);
            pbuf_free(p);
        }
    }
}

int main() {
    stdio_init_all();
    
    // Init LCD
    lcd_init();
    lcd_clear(0x0000); // Black
    
    // Init WiFi
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return -1;
    }
    
    cyw43_arch_enable_ap_mode("ButtonBash", "picopico", CYW43_AUTH_WPA2_AES_PSK);
    printf("AP Started: ButtonBash\n");
    
    // Setup UDP
    struct udp_pcb *pcb = udp_new();
    udp_bind(pcb, IP_ADDR_ANY, UDP_PORT);
    udp_recv(pcb, udp_recv_callback, NULL);
    
    lcd_draw_text("WAITING", 80, 100, 0xFFFF, 0x0000, 2);
    
    uint32_t last_update = 0;
    int countdown = 3;
    
    while (true) {
        cyw43_arch_poll();
        
        uint32_t now = time_us_32() / 1000; // Convert to ms
        
        switch(game_state) {
            case WAITING_FOR_PLAYERS:
                if (now - last_update > 1000) {
                    char msg[32];
                    snprintf(msg, sizeof(msg), "Players: %d/%d", player_count, MAX_PLAYERS);
                    lcd_clear(0x0000);
                    lcd_draw_text(msg, 60, 100, 0xFFFF, 0x0000, 2);
                    last_update = now;
                }
                break;
                
            case COUNTDOWN:
                if (now - last_update > 1000) {
                    lcd_clear(0x001F); // Blue
                    char count[16];
                    snprintf(count, sizeof(count), "%d", countdown);
                    lcd_draw_text(count, 140, 100, 0xFFFF, 0x001F, 3);
                    countdown--;
                    last_update = now;
                    
                    if (countdown < 0) {
                        game_state = SHOWING_PROMPT;
                        round_num++;
                    }
                }
                break;
                
            case SHOWING_PROMPT:
                lcd_clear(0xF800); // Red - PRESS NOW!
                lcd_draw_text("PRESS!", 80, 100, 0xFFFF, 0xF800, 2);
                broadcast_message(pcb, "GO!");
                prompt_start_time = time_us_32();
                game_state = WAITING_FOR_RESPONSE;
                break;
                
            case WAITING_FOR_RESPONSE:
                // Waiting for button press...
                if (now - (prompt_start_time / 1000) > 5000) {
                    lcd_clear(0x0000);
                    lcd_draw_text("TIMEOUT", 80, 100, 0xFFFF, 0x0000, 2);
                    sleep_ms(2000);
                    
                    if (round_num >= MAX_ROUNDS) {
                        game_state = GAME_OVER;
                    } else {
                        countdown = 3;
                        game_state = COUNTDOWN;
                    }
                }
                break;
                
            case SHOWING_RESULTS:
                lcd_clear(0x07E0); // Green
                char result[32];
                snprintf(result, sizeof(result), "P%d: %dms", winner + 1, 
                        players[winner].reaction_time / 1000);
                lcd_draw_text(result, 60, 100, 0x0000, 0x07E0, 2);
                
                broadcast_message(pcb, result);
                sleep_ms(3000);
                
                winner = -1;
                
                if (round_num >= MAX_ROUNDS) {
                    game_state = GAME_OVER;
                } else {
                    countdown = 3;
                    game_state = COUNTDOWN;
                }
                break;
                
            case GAME_OVER:
                lcd_clear(0xFFE0); // Yellow
                int max_score = 0;
                int game_winner = 0;
                for(int i = 0; i < player_count; i++) {
                    if(players[i].score > max_score) {
                        max_score = players[i].score;
                        game_winner = i;
                    }
                }
                
                char final[32];
                snprintf(final, sizeof(final), "WINNER P%d", game_winner + 1);
                lcd_draw_text(final, 60, 100, 0x0000, 0xFFE0, 2);
                
                broadcast_message(pcb, "GAME_OVER");
                sleep_ms(10000);
                
                // Reset for new game
                player_count = 0;
                round_num = 0;
                game_state = WAITING_FOR_PLAYERS;
                break;
        }
        
        sleep_ms(10);
    }
    
    cyw43_arch_deinit();
    return 0;
}


