#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"
#include "dhcpserver.h"

// Network configuration
#define WIFI_SSID "DOGFIGHT_SERVER"
#define WIFI_PASSWORD "picopico"
#define UDP_PORT 4242

// Game constants
#define MAX_CLIENTS 2
#define GAME_WIDTH 80
#define GAME_HEIGHT 80
#define MAX_SHOTS 2

// Packet types
#define PKT_JOIN_REQUEST  0x01
#define PKT_JOIN_RESPONSE 0x02
#define PKT_STATE_UPDATE  0x03
#define PKT_GAME_STATE    0x04
#define PKT_GAME_OVER     0x05
#define PKT_PING          0x06
#define PKT_PONG          0x07

// Direction constants
#define DIR_N  0
#define DIR_NE 1
#define DIR_E  2
#define DIR_SE 3
#define DIR_S  4
#define DIR_SW 5
#define DIR_W  6
#define DIR_NW 7

// Shot structure
typedef struct {
    int8_t x, y;
    int8_t dir;
    uint8_t range;
    uint8_t active;
} Shot;

// Player state
typedef struct {
    uint8_t player_id;
    int8_t x, y;
    int8_t dir;
    uint8_t type;
    Shot shots[MAX_SHOTS];
    ip_addr_t client_ip;
    uint16_t client_port;
    bool connected;
    uint32_t last_update;
} Player;

// Game server state
typedef struct {
    Player players[MAX_CLIENTS];
    uint8_t num_players;
    bool game_active;
    uint8_t winner;
    uint32_t frame_count;
} GameServer;

static GameServer server;
static struct udp_pcb *server_pcb;
static dhcp_server_t dhcp_server;

// Direction deltas
static const int8_t dir_dx[8] = {0, 1, 1, 1, 0, -1, -1, -1};
static const int8_t dir_dy[8] = {-1, -1, 0, 1, 1, 1, 0, -1};

// Plane shapes for collision detection
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

// Initialize game server
void init_server(void) {
    memset(&server, 0, sizeof(server));
    server.num_players = 0;
    server.game_active = false;
    server.winner = 0;
    server.frame_count = 0;
}

// Initialize player
void init_player(Player *player, uint8_t id) {
    player->player_id = id;
    player->type = id;
    
    if (id == 0) {
        player->x = GAME_WIDTH - 10;
        player->y = GAME_HEIGHT - 10;
        player->dir = DIR_W;
    } else {
        player->x = 10;
        player->y = 10;
        player->dir = DIR_E;
    }
    
    for (int i = 0; i < MAX_SHOTS; i++) {
        player->shots[i].active = 0;
    }
    
    player->connected = false;
    player->last_update = 0;
}

// Check if shot hits plane
bool check_hit(Shot *shot, Player *target) {
    const uint8_t *shape = (target->type == 0) ? 
        plane0_shapes[target->dir] : plane1_shapes[target->dir];
    
    for (int dy = 0; dy < 3; dy++) {
        for (int dx = 0; dx < 3; dx++) {
            if (shape[dy * 3 + dx]) {
                int8_t px = target->x + dx - 1;
                int8_t py = target->y + dy - 1;
                if (shot->x == px && shot->y == py) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Update shot
void update_shot(Shot *shot) {
    if (!shot->active) return;
    
    shot->x += dir_dx[shot->dir] * 3;
    shot->y += dir_dy[shot->dir] * 3;
    
    // Wrap around
    if (shot->x < 0) shot->x = GAME_WIDTH - 1;
    if (shot->x >= GAME_WIDTH) shot->x = 0;
    if (shot->y < 0) shot->y = GAME_HEIGHT - 1;
    if (shot->y >= GAME_HEIGHT) shot->y = 0;
    
    shot->range--;
    if (shot->range == 0) {
        shot->active = 0;
    }
}

// Update player movement
void update_player_movement(Player *player) {
    player->x += dir_dx[player->dir];
    player->y += dir_dy[player->dir];
    
    // Wrap around
    if (player->x < 1) player->x = GAME_WIDTH - 2;
    if (player->x >= GAME_WIDTH - 1) player->x = 1;
    if (player->y < 1) player->y = GAME_HEIGHT - 2;
    if (player->y >= GAME_HEIGHT - 1) player->y = 1;
}

// Game update logic
void update_game(void) {
    if (!server.game_active || server.num_players < 2) return;
    
    server.frame_count++;
    
    // Update all players
    for (int i = 0; i < server.num_players; i++) {
        update_player_movement(&server.players[i]);
        
        // Update shots
        for (int s = 0; s < MAX_SHOTS; s++) {
            if (server.players[i].shots[s].active) {
                update_shot(&server.players[i].shots[s]);
            }
        }
    }
    
    // Check collisions
    for (int i = 0; i < server.num_players; i++) {
        for (int s = 0; s < MAX_SHOTS; s++) {
            if (server.players[i].shots[s].active) {
                // Check against other players
                for (int j = 0; j < server.num_players; j++) {
                    if (i != j && check_hit(&server.players[i].shots[s], &server.players[j])) {
                        server.game_active = false;
                        server.winner = i + 1;
                        server.players[i].shots[s].active = 0;
                        printf("Player %d wins!\n", server.winner);
                        return;
                    }
                }
            }
        }
    }
}

// Send packet to client
void send_packet(const ip_addr_t *addr, uint16_t port, const uint8_t *data, uint16_t len) {
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, len, PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, data, len);
        udp_sendto(server_pcb, p, addr, port);
        pbuf_free(p);
    }
}

// Broadcast game state to all clients
void broadcast_game_state(void) {
    uint8_t packet[256];
    uint8_t *ptr = packet;
    
    *ptr++ = PKT_GAME_STATE;
    *ptr++ = server.num_players;
    *ptr++ = server.game_active ? 1 : 0;
    *ptr++ = server.winner;
    
    // Send all player states
    for (int i = 0; i < server.num_players; i++) {
        Player *p = &server.players[i];
        *ptr++ = p->player_id;
        *ptr++ = p->x;
        *ptr++ = p->y;
        *ptr++ = p->dir;
        *ptr++ = p->type;
        
        // Send shots
        for (int s = 0; s < MAX_SHOTS; s++) {
            *ptr++ = p->shots[s].x;
            *ptr++ = p->shots[s].y;
            *ptr++ = p->shots[s].dir;
            *ptr++ = p->shots[s].range;
            *ptr++ = p->shots[s].active;
        }
    }
    
    uint16_t packet_len = ptr - packet;
    
    // Send to all connected clients
    for (int i = 0; i < server.num_players; i++) {
        if (server.players[i].connected) {
            send_packet(&server.players[i].client_ip, 
                       server.players[i].client_port,
                       packet, packet_len);
        }
    }
}

// Handle incoming UDP packets
void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p,
                       const ip_addr_t *addr, u16_t port) {
    if (p->len < 1) {
        pbuf_free(p);
        return;
    }
    
    uint8_t *data = (uint8_t *)p->payload;
    uint8_t packet_type = data[0];
    
    switch (packet_type) {
        case PKT_JOIN_REQUEST: {
            if (server.num_players < MAX_CLIENTS) {
                uint8_t player_id = server.num_players;
                Player *player = &server.players[player_id];
                
                init_player(player, player_id);
                player->client_ip = *addr;
                player->client_port = port;
                player->connected = true;
                player->last_update = to_ms_since_boot(get_absolute_time());
                
                server.num_players++;
                
                printf("Player %d joined from %s:%d\n", player_id, 
                       ipaddr_ntoa(addr), port);
                
                // Send join response
                uint8_t response[3];
                response[0] = PKT_JOIN_RESPONSE;
                response[1] = player_id;
                response[2] = 1; // Success
                send_packet(addr, port, response, 3);
                
                // Start game when we have 2 players
                if (server.num_players == 2) {
                    server.game_active = true;
                    printf("Game started!\n");
                }
            } else {
                // Server full
                uint8_t response[3];
                response[0] = PKT_JOIN_RESPONSE;
                response[1] = 0xFF;
                response[2] = 0; // Failure
                send_packet(addr, port, response, 3);
            }
            break;
        }
        
        case PKT_STATE_UPDATE: {
            if (p->len >= 5) {
                uint8_t player_id = data[1];
                if (player_id < server.num_players) {
                    Player *player = &server.players[player_id];
                    player->dir = data[2];
                    uint8_t fire = data[3];
                    player->last_update = to_ms_since_boot(get_absolute_time());
                    
                    // Handle fire button
                    if (fire && server.game_active) {
                        // Find empty shot slot
                        for (int i = 0; i < MAX_SHOTS; i++) {
                            if (!player->shots[i].active) {
                                player->shots[i].x = player->x;
                                player->shots[i].y = player->y;
                                player->shots[i].dir = player->dir;
                                player->shots[i].range = 15;
                                player->shots[i].active = 1;
                                break;
                            }
                        }
                    }
                }
            }
            break;
        }
        
        case PKT_PING: {
            uint8_t response[1] = {PKT_PONG};
            send_packet(addr, port, response, 1);
            break;
        }
    }
    
    pbuf_free(p);
}

// Main server loop
int main() {
    stdio_init_all();
    
    printf("Dogfight Server Starting...\n");
    
    // Initialize WiFi
    if (cyw43_arch_init()) {
        printf("Failed to initialize WiFi\n");
        return 1;
    }
    
    // Enable AP mode
    cyw43_arch_enable_ap_mode(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK);
    
    // Configure IP
    ip4_addr_t gw, mask;
    IP4_ADDR(&gw, 192, 168, 4, 1);
    IP4_ADDR(&mask, 255, 255, 255, 0);
    
    dhcp_server_init(&dhcp_server, &gw, &mask);
    
    printf("Access Point '%s' started\n", WIFI_SSID);
    printf("Server IP: 192.168.4.1\n");
    
    // Initialize UDP server
    server_pcb = udp_new();
    udp_bind(server_pcb, IP_ADDR_ANY, UDP_PORT);
    udp_recv(server_pcb, udp_recv_callback, NULL);
    
    printf("UDP server listening on port %d\n", UDP_PORT);
    
    // Initialize game
    init_server();
    
    uint32_t last_update = 0;
    uint32_t last_broadcast = 0;
    
    // Main loop
    while (true) {
        cyw43_arch_poll();
        
        uint32_t now = to_ms_since_boot(get_absolute_time());
        
        // Update game at ~10Hz
        if (now - last_update >= 100) {
            update_game();
            last_update = now;
        }
        
        // Broadcast state at ~20Hz
        if (now - last_broadcast >= 50) {
            if (server.num_players > 0) {
                broadcast_game_state();
            }
            last_broadcast = now;
        }
        
        // Check for disconnected players
        for (int i = 0; i < server.num_players; i++) {
            if (server.players[i].connected) {
                if (now - server.players[i].last_update > 5000) {
                    printf("Player %d timed out\n", i);
                    server.players[i].connected = false;
                    server.game_active = false;
                }
            }
        }
        
        sleep_ms(10);
    }
    
    return 0;
}
