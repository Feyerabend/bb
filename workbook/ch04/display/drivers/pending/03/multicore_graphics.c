#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/multicore.h"
#include "pico/cyw43_arch.h"
#include "lwip/udp.h"
#include "lwip/ip_addr.h"
#include "hardware/sync.h"
#include "engine.h"
#include "multicore_graphics.h"

// Network configuration
#define UDP_PORT 8080
#define UDP_RESPONSE_PORT 8081
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Command queue configuration
#define COMMAND_QUEUE_SIZE 32

// Network packet structures
typedef struct {
    uint8_t command;
    uint8_t object_id;
    int16_t x, y;
    int16_t velocity_x, velocity_y;
    uint8_t frame;
} __attribute__((packed)) network_packet_t;

typedef struct {
    uint8_t response;
    uint8_t object1_id;
    uint8_t object2_id;
    int16_t x, y;
    uint32_t timestamp;
} __attribute__((packed)) network_response_packet_t;

// Network command/response enums
typedef enum {
    NET_MOVE_OBJECT = 0,
    NET_DRAW_SPRITE,
    NET_CLEAR_SCREEN,
    NET_FIRE_BULLET
} net_command_t;

typedef enum {
    NET_COLLISION_DETECTED = 0,
    NET_OBJECT_OUT_OF_BOUNDS,
    NET_RENDER_COMPLETE,
    NET_HEARTBEAT,
    NET_ERROR
} net_response_t;

// Graphics command structure
typedef struct {
    uint8_t opcode;
    uint8_t sprite_id;
    int16_t x, y;
    uint8_t frame;
    uint8_t flags;
} graphics_command_t;

// Command queue
static graphics_command_t command_queue[COMMAND_QUEUE_SIZE];
static volatile uint8_t queue_head = 0;
static volatile uint8_t queue_tail = 0;
static spin_lock_t *queue_lock;

// Network state
static struct udp_pcb *udp_pcb;
static ip_addr_t remote_addr;
static u16_t remote_port;
static bool remote_connected = false;

// External game state (from demo.c)
extern game_state_t game;

// Command opcodes
typedef enum {
    CMD_LOAD_SPRITE = 0,
    CMD_MOVE_SPRITE,
    CMD_CLEAR_SCREEN,
    CMD_FIRE_BULLET
} cmd_opcode_t;

// Init network
void init_network(void) {
    if (cyw43_arch_init_with_country(CYW43_COUNTRY_WORLDWIDE)) {
        printf("Failed to init WiFi\n");
        return;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to WiFi: %s\n", WIFI_SSID);
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("Failed to connect to WiFi\n");
        return;
    }
    
    printf("WiFi connected. IP: %s\n", ip4addr_ntoa(&cyw43_state.netif[0].ip_addr));
    
    udp_pcb = udp_new();
    if (udp_pcb != NULL) {
        err_t err = udp_bind(udp_pcb, IP_ADDR_ANY, UDP_PORT);
        if (err == ERR_OK) {
            udp_recv(udp_pcb, udp_recv_callback, NULL);
            printf("UDP listening on port %d\n", UDP_PORT);
        } else {
            printf("Failed to bind UDP: %d\n", err);
        }
    }
}

// UDP receive callback
void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    if (p != NULL) {
        network_packet_t packet;
        if (p->len >= sizeof(network_packet_t)) {
            memcpy(&packet, p->payload, sizeof(packet));
            remote_addr = *addr;
            remote_port = port;
            remote_connected = true;
            process_network_command(&packet);
        }
        pbuf_free(p);
    }
}

// Process network commands
void process_network_command(network_packet_t *packet) {
    graphics_command_t cmd = {0};
    uint32_t save = spin_lock_blocking(queue_lock);
    
    switch (packet->command) {
        case NET_MOVE_OBJECT:
            cmd.opcode = CMD_MOVE_SPRITE;
            cmd.sprite_id = packet->object_id;
            cmd.x = packet->x;
            cmd.y = packet->y;
            send_graphics_command(&cmd);
            printf("Network: Move sprite %d to (%d, %d)\n", packet->object_id, packet->x, packet->y);
            break;
        
        case NET_DRAW_SPRITE:
            cmd.opcode = CMD_LOAD_SPRITE;
            cmd.sprite_id = packet->object_id;
            cmd.x = packet->x;
            cmd.y = packet->y;
            cmd.frame = packet->frame;
            send_graphics_command(&cmd);
            printf("Network: Draw sprite %d at (%d, %d)\n", packet->object_id, packet->x, packet->y);
            break;
        
        case NET_CLEAR_SCREEN:
            cmd.opcode = CMD_CLEAR_SCREEN;
            send_graphics_command(&cmd);
            printf("Network: Clear screen\n");
            break;
        
        case NET_FIRE_BULLET:
            cmd.opcode = CMD_FIRE_BULLET;
            send_graphics_command(&cmd);
            printf("Network: Fire bullet\n");
            break;
        
        default:
            printf("Unknown network command: %d\n", packet->command);
            break;
    }
    
    spin_lock_unsafe_unblock(queue_lock, save);
}

// Send network response
void send_network_response(net_response_t type, uint8_t obj1, uint8_t obj2, int16_t x, int16_t y) {
    if (!remote_connected) return;
    
    network_response_packet_t response = {
        .response = type,
        .object1_id = obj1,
        .object2_id = obj2,
        .x = x,
        .y = y,
        .timestamp = to_ms_since_boot(get_absolute_time())
    };
    
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, sizeof(response), PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, &response, sizeof(response));
        udp_sendto(udp_pcb, p, &remote_addr, UDP_RESPONSE_PORT);
        pbuf_free(p);
    }
}

// Send graphics command to queue
void send_graphics_command(graphics_command_t *cmd) {
    uint32_t save = spin_lock_blocking(queue_lock);
    if ((queue_head + 1) % COMMAND_QUEUE_SIZE != queue_tail) {
        command_queue[queue_head] = *cmd;
        queue_head = (queue_head + 1) % COMMAND_QUEUE_SIZE;
    } else {
        printf("Command queue full\n");
    }
    spin_lock_unsafe_unblock(queue_lock, save);
}

// Process a graphics command on Core 1
static void process_graphics_command(graphics_command_t *cmd) {
    switch (cmd->opcode) {
        case CMD_LOAD_SPRITE:
            if (cmd->sprite_id < MAX_SPRITES) {
                sprite_set_position(cmd->sprite_id, cmd->x, cmd->y);
                sprite_set_animation(cmd->sprite_id, cmd->frame);
            }
            break;
        
        case CMD_MOVE_SPRITE:
            if (cmd->sprite_id < MAX_SPRITES) {
                sprite_set_position(cmd->sprite_id, cmd->x, cmd->y);
            }
            break;
        
        case CMD_CLEAR_SCREEN:
            for (int i = 0; i < 8; i++) {
                if (game.enemies[i] != 255) {
                    sprite_destroy(game.enemies[i]);
                    game.enemies[i] = 255;
                }
            }
            for (int i = 0; i < 16; i++) {
                if (game.bullets[i] != 255) {
                    sprite_destroy(game.bullets[i]);
                    game.bullets[i] = 255;
                }
            }
            break;
        
        case CMD_FIRE_BULLET:
            for (int i = 0; i < 16; i++) {
                if (game.bullets[i] == 255) {
                    game.bullets[i] = sprite_create(game.player_x + 6, game.player_y - 4, 4, 4);
                    sprite_set_texture(game.bullets[i], bullet_texture, 4, 4);
                    sprite_set_layer(game.bullets[i], 1);
                    sprite_enable_collision(game.bullets[i], true);
                    game.last_bullet_time = to_ms_since_boot(get_absolute_time());
                    printf("Bullet fired\n");
                    break;
                }
            }
            break;
        
        default:
            break;
    }
}

// Core 1 graphics loop
static void core1_graphics_loop(void) {
    printf("Core 1 starting - Graphics Engine\n");
    
    while (game.game_running) {
        // Process command queue
        uint32_t save = spin_lock_blocking(queue_lock);
        while (queue_tail != queue_head) {
            process_graphics_command(&command_queue[queue_tail]);
            queue_tail = (queue_tail + 1) % COMMAND_QUEUE_SIZE;
        }
        spin_lock_unsafe_unblock(queue_lock, save);
        
        // Wait for Core 0 signal to render
        multicore_fifo_pop_blocking();
        
        // Perform graphics tasks
        graphics_engine_update();
        graphics_engine_render();
        draw_ui();
        graphics_engine_present();
        
        // Check collisions and send responses
        uint8_t collision_count;
        collision_event_t *collisions = get_collision_events(&collision_count);
        for (int i = 0; i < collision_count; i++) {
            if (collisions[i].id1 == game.player_sprite || collisions[i].id2 == game.player_sprite) {
                send_network_response(NET_ERROR, collisions[i].id1, collisions[i].id2, game.player_x, game.player_y);
                game.game_running = false;
            } else {
                bool bullet_hit = false;
                for (int b = 0; b < 16; b++) {
                    if (game.bullets[b] == collisions[i].id1 || game.bullets[b] == collisions[i].id2) {
                        for (int e = 0; e < 8; e++) {
                            if (game.enemies[e] == collisions[i].id1 || game.enemies[e] == collisions[i].id2) {
                                send_network_response(NET_COLLISION_DETECTED, game.bullets[b], game.enemies[e], game.player_x, game.player_y);
                                bullet_hit = true;
                                break;
                            }
                        }
                        if (bullet_hit) break;
                    }
                }
            }
        }
    }
    
    printf("Core 1 graphics loop exiting\n");
}

// Launch graphics core
void launch_graphics_core(void) {
    // Initialize spin lock
    uint32_t lock_num = spin_lock_claim_unused(true);
    queue_lock = spin_lock_init(lock_num);
    
    // Initialize network
    init_network();
    
    // Launch Core 1
    multicore_launch_core1(core1_graphics_loop);
}
