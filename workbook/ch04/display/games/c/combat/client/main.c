#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"
#include "display.h"

// Network configuration
#define SERVER_SSID "DOGFIGHT_SERVER"
#define SERVER_PASSWORD "picopico"
#define SERVER_IP "192.168.4.1"
#define SERVER_PORT 4242

// Packet types (must match server)
#define PKT_JOIN_REQUEST  0x01
#define PKT_JOIN_RESPONSE 0x02
#define PKT_STATE_UPDATE  0x03
#define PKT_GAME_STATE    0x04
#define PKT_GAME_OVER     0x05
#define PKT_PING          0x06
#define PKT_PONG          0x07

// Game constants
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 240
#define PIXEL_SIZE 3
#define GAME_WIDTH 80
#define GAME_HEIGHT 80
#define MAX_SHOTS 2

// Direction constants
#define DIR_N  0
#define DIR_NE 1
#define DIR_E  2
#define DIR_SE 3
#define DIR_S  4
#define DIR_SW 5
#define DIR_W  6
#define DIR_NW 7

// Plane shapes
static const uint8_t plane0_shapes[8][9] = {
    {0,1,0, 1,1,1, 0,0,0}, {1,0,1, 0,1,0, 1,0,0},
    {0,1,0, 1,1,0, 0,1,0}, {1,0,0, 0,1,0, 1,0,1},
    {0,0,0, 1,1,1, 0,1,0}, {0,0,1, 0,1,0, 1,0,1},
    {0,1,0, 0,1,1, 0,1,0}, {1,0,1, 0,1,0, 0,0,1}
};

static const uint8_t plane1_shapes[8][9] = {
    {0,1,0, 1,1,1, 1,0,1}, {1,1,1, 1,1,0, 1,0,0},
    {0,1,1, 1,1,0, 0,1,1}, {1,0,0, 1,1,0, 1,1,1},
    {1,0,1, 1,1,1, 0,1,0}, {0,0,1, 0,1,1, 1,1,1},
    {1,1,0, 0,1,1, 1,1,0}, {1,1,1, 0,1,1, 0,0,1}
};

// Shot structure
typedef struct {
    int8_t x, y;
    int8_t dir;
    uint8_t range;
    uint8_t active;
} Shot;

// Player structure
typedef struct {
    uint8_t player_id;
    int8_t x, y;
    int8_t dir;
    uint8_t type;
    Shot shots[MAX_SHOTS];
} Player;

// Network state
typedef struct {
    bool connected;
    uint8_t my_player_id;
    struct udp_pcb *pcb;
    ip_addr_t server_addr;
    uint32_t last_send;
    uint32_t last_recv;
} NetworkState;

// Game state
typedef struct {
    Player players[2];
    uint8_t num_players;
    bool game_active;
    uint8_t winner;
    uint8_t framebuffer[GAME_WIDTH * GAME_HEIGHT];
    uint8_t prev_framebuffer[GAME_WIDTH * GAME_HEIGHT];
} GameState;

static NetworkState net_state;
static GameState game_state;

// Button state tracking
static bool prev_fire_btn = false;
static uint8_t fire_cooldown = 0;

// Clear framebuffer
void clear_framebuffer(void) {
    memset(game_state.framebuffer, 0, sizeof(game_state.framebuffer));
}

// Set pixel in framebuffer
void set_pixel(int8_t x, int8_t y, uint8_t value) {
    if (x >= 0 && x < GAME_WIDTH && y >= 0 && y < GAME_HEIGHT) {
        game_state.framebuffer[y * GAME_WIDTH + x] = value;
    }
}

// Draw plane to framebuffer
void draw_plane(Player *plane) {
    const uint8_t *shape = (plane->type == 0) ? 
        plane0_shapes[plane->dir] : plane1_shapes[plane->dir];
    
    for (int dy = 0; dy < 3; dy++) {
        for (int dx = 0; dx < 3; dx++) {
            if (shape[dy * 3 + dx]) {
                set_pixel(plane->x + dx - 1, plane->y + dy - 1, 1);
            }
        }
    }
}

// Send packet to server
void send_packet(const uint8_t *data, uint16_t len) {
    if (!net_state.connected) return;
    
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, len, PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, data, len);
        udp_sendto(net_state.pcb, p, &net_state.server_addr, SERVER_PORT);
        pbuf_free(p);
        net_state.last_send = to_ms_since_boot(get_absolute_time());
    }
}

// Send join request
void send_join_request(void) {
    uint8_t packet[1] = {PKT_JOIN_REQUEST};
    send_packet(packet, 1);
    printf("Sent join request\n");
}

// Send state update
void send_state_update(int8_t dir, uint8_t fire) {
    uint8_t packet[4];
    packet[0] = PKT_STATE_UPDATE;
    packet[1] = net_state.my_player_id;
    packet[2] = dir;
    packet[3] = fire;
    send_packet(packet, 4);
}

// Handle incoming packets
void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p,
                       const ip_addr_t *addr, u16_t port) {
    if (p->len < 1) {
        pbuf_free(p);
        return;
    }
    
    uint8_t *data = (uint8_t *)p->payload;
    uint8_t packet_type = data[0];
    
    net_state.last_recv = to_ms_since_boot(get_absolute_time());
    
    switch (packet_type) {
        case PKT_JOIN_RESPONSE: {
            if (p->len >= 3) {
                net_state.my_player_id = data[1];
                bool success = data[2];
                if (success) {
                    net_state.connected = true;
                    printf("Joined as player %d\n", net_state.my_player_id);
                } else {
                    printf("Join failed (server full?)\n");
                }
            }
            break;
        }
        
        case PKT_GAME_STATE: {
            if (p->len >= 4) {
                game_state.num_players = data[1];
                game_state.game_active = data[2];
                game_state.winner = data[3];
                
                uint8_t *ptr = data + 4;
                
                // Parse player states
                for (int i = 0; i < game_state.num_players; i++) {
                    if (ptr + 14 > data + p->len) break;
                    
                    Player *player = &game_state.players[i];
                    player->player_id = *ptr++;
                    player->x = *ptr++;
                    player->y = *ptr++;
                    player->dir = *ptr++;
                    player->type = *ptr++;
                    
                    // Parse shots
                    for (int s = 0; s < MAX_SHOTS; s++) {
                        player->shots[s].x = *ptr++;
                        player->shots[s].y = *ptr++;
                        player->shots[s].dir = *ptr++;
                        player->shots[s].range = *ptr++;
                        player->shots[s].active = *ptr++;
                    }
                }
            }
            break;
        }
        
        case PKT_PONG: {
            // Server is alive
            break;
        }
    }
    
    pbuf_free(p);
}

// Initialize networking
bool init_network(void) {
    if (cyw43_arch_init()) {
        printf("WiFi init failed\n");
        return false;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to '%s'...\n", SERVER_SSID);
    
    if (cyw43_arch_wifi_connect_timeout_ms(SERVER_SSID, SERVER_PASSWORD, 
                                            CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("WiFi connection failed\n");
        return false;
    }
    
    printf("Connected to WiFi\n");
    
    // Parse server IP
    ipaddr_aton(SERVER_IP, &net_state.server_addr);
    
    // Create UDP socket
    net_state.pcb = udp_new();
    udp_bind(net_state.pcb, IP_ADDR_ANY, 0);
    udp_recv(net_state.pcb, udp_recv_callback, NULL);
    
    printf("UDP client initialized\n");
    
    return true;
}

// Render framebuffer to display
void render_display(void) {
    // Clear framebuffer
    clear_framebuffer();
    
    // Draw all players
    for (int i = 0; i < game_state.num_players; i++) {
        draw_plane(&game_state.players[i]);
        
        // Draw shots
        for (int s = 0; s < MAX_SHOTS; s++) {
            if (game_state.players[i].shots[s].active) {
                Shot *shot = &game_state.players[i].shots[s];
                set_pixel(shot->x, shot->y, 1);
            }
        }
    }
    
    // Render to display (only changed pixels)
    for (int y = 0; y < GAME_HEIGHT; y++) {
        for (int x = 0; x < GAME_WIDTH; x++) {
            uint8_t current = game_state.framebuffer[y * GAME_WIDTH + x];
            uint8_t previous = game_state.prev_framebuffer[y * GAME_WIDTH + x];
            
            if (current != previous) {
                uint16_t color = current ? COLOR_WHITE : COLOR_BLACK;
                display_fill_rect(x * PIXEL_SIZE, y * PIXEL_SIZE, 
                                PIXEL_SIZE, PIXEL_SIZE, color);
                game_state.prev_framebuffer[y * GAME_WIDTH + x] = current;
            }
        }
    }
    
    // Draw status text
    char status[64];
    if (!net_state.connected) {
        snprintf(status, sizeof(status), "Connecting...");
        display_draw_string(10, 220, status, COLOR_YELLOW, COLOR_BLACK);
    } else if (game_state.num_players < 2) {
        snprintf(status, sizeof(status), "Waiting for opponent...");
        display_draw_string(10, 220, status, COLOR_CYAN, COLOR_BLACK);
    } else if (!game_state.game_active && game_state.winner > 0) {
        snprintf(status, sizeof(status), "Player %d wins!", game_state.winner);
        display_draw_string(60, 220, status, COLOR_GREEN, COLOR_BLACK);
    }
}

// Main game loop
int main() {
    stdio_init_all();
    
    printf("Dogfight Client Starting...\n");
    
    // Initialize display
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed\n");
        return -1;
    }
    
    if (buttons_init() != DISPLAY_OK) {
        printf("Buttons init failed\n");
        return -1;
    }
    
    display_clear(COLOR_BLACK);
    memset(game_state.prev_framebuffer, 0, sizeof(game_state.prev_framebuffer));
    
    printf("Display initialized\n");
    
    // Initialize networking
    if (!init_network()) {
        display_draw_string(10, 110, "WiFi Failed!", COLOR_RED, COLOR_BLACK);
        while (true) tight_loop_contents();
    }
    
    // Initialize network state
    net_state.connected = false;
    net_state.my_player_id = 0xFF;
    net_state.last_send = 0;
    net_state.last_recv = to_ms_since_boot(get_absolute_time());
    
    // Initialize game state
    memset(&game_state, 0, sizeof(game_state));
    
    // Send join request
    send_join_request();
    
    uint32_t last_input_send = 0;
    uint32_t last_ping = 0;
    
    printf("Client ready. Controls: A=left, B=right, X=fire\n");
    
    // Main loop
    while (true) {
        cyw43_arch_poll();
        buttons_update();
        
        uint32_t now = to_ms_since_boot(get_absolute_time());
        
        // Retry join if not connected
        if (!net_state.connected && now - net_state.last_send > 2000) {
            send_join_request();
        }
        
        // Handle input and send to server
        if (net_state.connected && net_state.my_player_id != 0xFF) {
            bool left = button_pressed(BUTTON_A);
            bool right = button_pressed(BUTTON_B);
            bool fire = button_pressed(BUTTON_X);
            
            // Get current direction from our player
            int8_t current_dir = game_state.players[net_state.my_player_id].dir;
            int8_t new_dir = current_dir;
            
            // Update direction based on input
            if (left && !right) {
                new_dir = (current_dir + 7) % 8;
            } else if (right && !left) {
                new_dir = (current_dir + 1) % 8;
            }
            
            // Handle fire with cooldown
            bool fire_pressed = false;
            if (fire && !prev_fire_btn && fire_cooldown == 0) {
                fire_pressed = true;
                fire_cooldown = 10;
            }
            prev_fire_btn = fire;
            if (fire_cooldown > 0) fire_cooldown--;
            
            // Send input at ~20Hz
            if (now - last_input_send >= 50) {
                send_state_update(new_dir, fire_pressed ? 1 : 0);
                last_input_send = now;
            }
        }
        
        // Send ping to keep connection alive
        if (net_state.connected && now - last_ping > 1000) {
            uint8_t ping[1] = {PKT_PING};
            send_packet(ping, 1);
            last_ping = now;
        }
        
        // Check for connection timeout
        if (net_state.connected && now - net_state.last_recv > 5000) {
            printf("Connection timeout\n");
            net_state.connected = false;
        }
        
        // Render display
        render_display();
        
        sleep_ms(50); // ~20 FPS
    }
    
    return 0;
}
