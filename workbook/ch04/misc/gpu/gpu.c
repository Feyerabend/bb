#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "pico/multicore.h"
#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "lwip/udp.h"
#include "lwip/ip_addr.h"

// Configuration
#define DISPLAY_WIDTH 240
#define DISPLAY_HEIGHT 135
#define MAX_SPRITES 20
#define COMMAND_QUEUE_SIZE 64
#define SPRITE_CACHE_SIZE 32
#define UDP_PORT 8080
#define UDP_RESPONSE_PORT 8081

// Network credentials (replace with your values)
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// VM Bytecode Instructions
typedef enum {
    VM_NOP = 0,
    VM_LOAD_SPRITE,
    VM_DRAW_SPRITE,
    VM_MOVE_SPRITE,
    VM_CLEAR_SCREEN,
    VM_SET_PALETTE,
    VM_CHECK_COLLISION,
    VM_ANIMATE,
    VM_HALT
} vm_opcode_t;

// Network Command Types
typedef enum {
    NET_MOVE_OBJECT = 0,
    NET_DRAW_SPRITE,
    NET_UPDATE_TILEMAP,
    NET_CLEAR_SCREEN,
    NET_SET_PALETTE
} net_command_t;

// Network Response Types
typedef enum {
    NET_COLLISION_DETECTED = 0,
    NET_OBJECT_OUT_OF_BOUNDS,
    NET_RENDER_COMPLETE,
    NET_HEARTBEAT,
    NET_ERROR
} net_response_t;

// Inter-core Command Structure
typedef struct {
    uint8_t opcode;
    uint8_t sprite_id;
    int16_t x, y;
    uint8_t frame;
    uint8_t flags;
} graphics_command_t;

// Inter-core Response Structure
typedef struct {
    uint8_t type;
    uint8_t object_id;
    uint8_t collision_detected;
    uint8_t collision_object_id;
    uint16_t render_time_ms;
} graphics_response_t;

// Sprite Structure
typedef struct {
    uint8_t id;
    int16_t x, y;
    uint8_t width, height;
    uint8_t current_frame;
    uint8_t frame_count;
    uint8_t* data; // Simplified - would point to actual sprite data
    bool active;
} sprite_t;

// Global state
static sprite_t sprites[MAX_SPRITES];
static uint16_t framebuffer[DISPLAY_WIDTH * DISPLAY_HEIGHT];
static graphics_command_t command_queue[COMMAND_QUEUE_SIZE];
static volatile uint8_t queue_head = 0;
static volatile uint8_t queue_tail = 0;
static struct udp_pcb *udp_server_pcb;
static ip_addr_t server_addr;

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

// prototypes
void core1_main(void);
void init_graphics_system(void);
void process_vm_command(graphics_command_t* cmd);
bool check_sprite_collision(sprite_t* s1, sprite_t* s2);
void render_sprite(sprite_t* sprite);
void clear_framebuffer(void);
void update_display(void);
void send_graphics_command(graphics_command_t* cmd);
graphics_response_t* get_graphics_response(void);
void udp_recv_callback(void* arg, struct udp_pcb* pcb, struct pbuf* p, const ip_addr_t* addr, u16_t port);
void send_network_response(net_response_t type, uint8_t obj1, uint8_t obj2, int16_t x, int16_t y);
void init_network(void);
void process_network_command(network_packet_t* packet);


// Core 1 Entry Point (Graphics Engine)
void core1_main(void) {
    printf("Core 1 starting - Graphics Engine\n");
    
    init_graphics_system();
    clear_framebuffer();
    
    graphics_command_t current_cmd;
    uint32_t frame_count = 0;
    
    while (true) {
        // Check for commands from Core 0
        if (multicore_fifo_rvalid()) {
            uint32_t raw_cmd = multicore_fifo_pop_blocking();
            memcpy(&current_cmd, &raw_cmd, sizeof(uint32_t));
            
            // Process the graphics command
            process_vm_command(&current_cmd);
        }
        
        // Perform collision detection for all active sprites
        for (int i = 0; i < MAX_SPRITES; i++) {
            if (!sprites[i].active) continue;
            
            for (int j = i + 1; j < MAX_SPRITES; j++) {
                if (!sprites[j].active) continue;
                
                if (check_sprite_collision(&sprites[i], &sprites[j])) {
                    // Send collision result back to Core 0
                    graphics_response_t response = {
                        .type = 0, // COLLISION_RESULT
                        .object_id = sprites[i].id,
                        .collision_detected = 1,
                        .collision_object_id = sprites[j].id,
                        .render_time_ms = 16 // Approximate frame time
                    };
                    
                    multicore_fifo_push_blocking(*(uint32_t*)&response);
                }
            }
        }
        
        // Update display at ~30 FPS
        if (frame_count++ % 4 == 0) {
            update_display();
        }
        
        sleep_ms(8); // ~120 Hz processing loop
    }
}

// Init graphics system
void init_graphics_system(void) {
    // Init sprite array
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprites[i].active = false;
        sprites[i].id = i;
        sprites[i].width = 16;
        sprites[i].height = 16;
        sprites[i].data = NULL; // Would allocate sprite data in real implementation
    }
    
    printf("Graphics system initialised\n");
}

// Process VM commands
void process_vm_command(graphics_command_t* cmd) {
    switch (cmd->opcode) {
        case VM_LOAD_SPRITE:
            if (cmd->sprite_id < MAX_SPRITES) {
                sprites[cmd->sprite_id].active = true;
                sprites[cmd->sprite_id].x = cmd->x;
                sprites[cmd->sprite_id].y = cmd->y;
                sprites[cmd->sprite_id].current_frame = cmd->frame;
            }
            break;
            
        case VM_DRAW_SPRITE:
            if (cmd->sprite_id < MAX_SPRITES && sprites[cmd->sprite_id].active) {
                sprites[cmd->sprite_id].x = cmd->x;
                sprites[cmd->sprite_id].y = cmd->y;
                sprites[cmd->sprite_id].current_frame = cmd->frame;
                render_sprite(&sprites[cmd->sprite_id]);
            }
            break;
            
        case VM_MOVE_SPRITE:
            if (cmd->sprite_id < MAX_SPRITES && sprites[cmd->sprite_id].active) {
                sprites[cmd->sprite_id].x += cmd->x; // Use x,y as delta values
                sprites[cmd->sprite_id].y += cmd->y;
                render_sprite(&sprites[cmd->sprite_id]);
            }
            break;
            
        case VM_CLEAR_SCREEN:
            clear_framebuffer();
            break;
            
        case VM_SET_PALETTE:
            // Palette setting could be implemented here
            break;
            
        default:
            break;
    }
}

// Simple AABB collision detection
bool check_sprite_collision(sprite_t* s1, sprite_t* s2) {
    return (s1->x < s2->x + s2->width &&
            s1->x + s1->width > s2->x &&
            s1->y < s2->y + s2->height &&
            s1->y + s1->height > s2->y);
}

// Render a sprite to framebuffer (simplified)
void render_sprite(sprite_t* sprite) {
    // Simple colored rectangle for demonstration
    uint16_t color = 0xF800; // Red in RGB565
    
    for (int y = 0; y < sprite->height && (sprite->y + y) < DISPLAY_HEIGHT; y++) {
        for (int x = 0; x < sprite->width && (sprite->x + x) < DISPLAY_WIDTH; x++) {
            if (sprite->x + x >= 0 && sprite->y + y >= 0) {
                framebuffer[(sprite->y + y) * DISPLAY_WIDTH + (sprite->x + x)] = color + sprite->id;
            }
        }
    }
}

// Clear framebuffer
void clear_framebuffer(void) {
    memset(framebuffer, 0, sizeof(framebuffer));
}

// Update physical display (placeholder)
void update_display(void) {
    // In real implementation, this would send framebuffer to SPI display
    // For now, we'll just indicate a display update occurred
    static uint32_t update_count = 0;
    if (++update_count % 30 == 0) {
        printf("Display updated (frame %lu)\n", update_count);
    }
}

// Send command to graphics core
void send_graphics_command(graphics_command_t* cmd) {
    multicore_fifo_push_blocking(*(uint32_t*)cmd);
}

// Get response from graphics core (non-blocking)
graphics_response_t* get_graphics_response(void) {
    static graphics_response_t response;
    
    if (multicore_fifo_rvalid()) {
        uint32_t raw_response = multicore_fifo_pop_blocking();
        memcpy(&response, &raw_response, sizeof(uint32_t));
        return &response;
    }
    return NULL;
}

// UDP receive callback
void udp_recv_callback(void* arg, struct udp_pcb* pcb, struct pbuf* p, const ip_addr_t* addr, u16_t port) {
    if (p != NULL) {
        network_packet_t packet;
        if (p->len >= sizeof(network_packet_t)) {
            memcpy(&packet, p->payload, sizeof(network_packet_t));
            process_network_command(&packet);
        }
        pbuf_free(p);
    }
}

// Process incoming network commands
void process_network_command(network_packet_t* packet) {
    graphics_command_t gfx_cmd = {0};
    
    switch (packet->command) {
        case NET_MOVE_OBJECT:
            gfx_cmd.opcode = VM_DRAW_SPRITE;
            gfx_cmd.sprite_id = packet->object_id;
            gfx_cmd.x = packet->x;
            gfx_cmd.y = packet->y;
            gfx_cmd.frame = packet->frame;
            send_graphics_command(&gfx_cmd);
            break;
            
        case NET_DRAW_SPRITE:
            gfx_cmd.opcode = VM_LOAD_SPRITE;
            gfx_cmd.sprite_id = packet->object_id;
            gfx_cmd.x = packet->x;
            gfx_cmd.y = packet->y;
            gfx_cmd.frame = packet->frame;
            send_graphics_command(&gfx_cmd);
            break;
            
        case NET_CLEAR_SCREEN:
            gfx_cmd.opcode = VM_CLEAR_SCREEN;
            send_graphics_command(&gfx_cmd);
            break;
            
        default:
            break;
    }
}

// Send network response
void send_network_response(net_response_t type, uint8_t obj1, uint8_t obj2, int16_t x, int16_t y) {
    network_response_packet_t response = {
        .response = type,
        .object1_id = obj1,
        .object2_id = obj2,
        .x = x,
        .y = y,
        .timestamp = to_ms_since_boot(get_absolute_time())
    };
    
    struct pbuf* p = pbuf_alloc(PBUF_TRANSPORT, sizeof(response), PBUF_RAM);
    if (p != NULL) {
        memcpy(p->payload, &response, sizeof(response));
        udp_sendto(udp_server_pcb, p, &server_addr, UDP_RESPONSE_PORT);
        pbuf_free(p);
    }
}

// Init network system
void init_network(void) {
    if (cyw43_arch_init_with_country(CYW43_COUNTRY_USA)) {
        printf("Failed to initialise WiFi\n");
        return;
    }
    
    cyw43_arch_enable_sta_mode();
    
    printf("Connecting to WiFi..\n");
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 30000)) {
        printf("Failed to connect to WiFi\n");
        return;
    }
    
    printf("WiFi connected\n");
    
    // Set up UDP server
    udp_server_pcb = udp_new();
    if (udp_server_pcb != NULL) {
        err_t err = udp_bind(udp_server_pcb, IP_ADDR_ANY, UDP_PORT);
        if (err == ERR_OK) {
            udp_recv(udp_server_pcb, udp_recv_callback, NULL);
            printf("UDP server listening on port %d\n", UDP_PORT);
        }
    }
    
    // Set server address to access point (gateway IP)
    ipaddr_aton("192.168.4.1", &server_addr);
}

// Main function (Core 0)
int main(void) {
    stdio_init_all();
    printf("Pico W GPU Starting..\n");
    
    // Init network
    init_network();
    
    // Launch Core 1 (Graphics Engine)
    multicore_launch_core1(core1_main);
    printf("Core 1 launched\n");
    
    // Core 0 main loop - Network and coordination
    uint32_t heartbeat_timer = 0;
    
    while (true) {
        // Process network stack
        cyw43_arch_poll();
        
        // Check for responses from graphics core
        graphics_response_t* response = get_graphics_response();
        if (response != NULL) {
            if (response->collision_detected) {
                send_network_response(NET_COLLISION_DETECTED, 
                                    response->object_id, 
                                    response->collision_object_id,
                                    0, 0);
            }
        }
        
        // Send periodic heartbeat
        if (++heartbeat_timer > 1000) { // Every ~10 seconds at 100Hz
            send_network_response(NET_HEARTBEAT, 0, 0, 0, 0);
            heartbeat_timer = 0;
        }
        
        sleep_ms(10); // 100Hz main loop
    }
    
    return 0;
}


