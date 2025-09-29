#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "display.h"

// Game constants
#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 240
#define PIXEL_SIZE 3  // Each game pixel is 3x3 screen pixels (80x72 game grid)
#define GAME_WIDTH (SCREEN_WIDTH / PIXEL_SIZE)   // 80
#define GAME_HEIGHT (SCREEN_HEIGHT / PIXEL_SIZE) // 80
#define MAX_SHOTS 2  // Max simultaneous shots per plane

// Plane orientations (8 directions, 0-7)
#define DIR_N  0
#define DIR_NE 1
#define DIR_E  2
#define DIR_SE 3
#define DIR_S  4
#define DIR_SW 5
#define DIR_W  6
#define DIR_NW 7

// Plane shapes (3x3 grid, 8 orientations per plane type)
// Type 0 (first plane)
static const uint8_t plane0_shapes[8][9] = {
    {0,1,0, 1,1,1, 0,0,0}, // N
    {1,0,1, 0,1,0, 1,0,0}, // NE
    {0,1,0, 1,1,0, 0,1,0}, // E
    {1,0,0, 0,1,0, 1,0,1}, // SE
    {0,0,0, 1,1,1, 0,1,0}, // S
    {0,0,1, 0,1,0, 1,0,1}, // SW
    {0,1,0, 0,1,1, 0,1,0}, // W
    {1,0,1, 0,1,0, 0,0,1}  // NW
};

// Type 1 (second plane)
static const uint8_t plane1_shapes[8][9] = {
    {0,1,0, 1,1,1, 1,0,1}, // N
    {1,1,1, 1,1,0, 1,0,0}, // NE
    {0,1,1, 1,1,0, 0,1,1}, // E
    {1,0,0, 1,1,0, 1,1,1}, // SE
    {1,0,1, 1,1,1, 0,1,0}, // S
    {0,0,1, 0,1,1, 1,1,1}, // SW
    {1,1,0, 0,1,1, 1,1,0}, // W
    {1,1,1, 0,1,1, 0,0,1}  // NW
};

// Shot structure
typedef struct {
    int8_t x, y;       // Position
    int8_t dir;        // Direction (0-7)
    uint8_t range;     // Remaining range (counts down)
    bool active;       // Is shot active?
} Shot;

// Plane structure
typedef struct {
    int8_t x, y;       // Position
    int8_t dir;        // Direction (0-7)
    uint8_t type;      // Plane type (0 or 1)
    Shot shots[MAX_SHOTS];
} Plane;

// Game state
static Plane planes[2];
static bool game_over = false;
static uint8_t winner = 0; // 0=none, 1=plane0, 2=plane1
static uint32_t frame_counter = 0;

// Framebuffer (1 bit per game pixel, stored as bytes)
static uint8_t framebuffer[GAME_WIDTH * GAME_HEIGHT];

// Previous framebuffer for dirty tracking
static uint8_t prev_framebuffer[GAME_WIDTH * GAME_HEIGHT];

// Direction deltas for movement
static const int8_t dir_dx[8] = {0, 1, 1, 1, 0, -1, -1, -1};
static const int8_t dir_dy[8] = {-1, -1, 0, 1, 1, 1, 0, -1};

// Initialize framebuffer
void clear_framebuffer(void) {
    memset(framebuffer, 0, sizeof(framebuffer));
}

// Set pixel in framebuffer
void set_pixel(int8_t x, int8_t y, uint8_t value) {
    if (x >= 0 && x < GAME_WIDTH && y >= 0 && y < GAME_HEIGHT) {
        framebuffer[y * GAME_WIDTH + x] = value;
    }
}

// Get pixel from framebuffer
uint8_t get_pixel(int8_t x, int8_t y) {
    if (x >= 0 && x < GAME_WIDTH && y >= 0 && y < GAME_HEIGHT) {
        return framebuffer[y * GAME_WIDTH + x];
    }
    return 0;
}

// Draw plane to framebuffer
void draw_plane(Plane *plane) {
    const uint8_t *shape = (plane->type == 0) ? 
        plane0_shapes[plane->dir] : 
        plane1_shapes[plane->dir];
    
    for (int dy = 0; dy < 3; dy++) {
        for (int dx = 0; dx < 3; dx++) {
            if (shape[dy * 3 + dx]) {
                set_pixel(plane->x + dx - 1, plane->y + dy - 1, 1);
            }
        }
    }
}

// Clear plane from framebuffer
void clear_plane(Plane *plane) {
    const uint8_t *shape = (plane->type == 0) ? 
        plane0_shapes[plane->dir] : 
        plane1_shapes[plane->dir];
    
    for (int dy = 0; dy < 3; dy++) {
        for (int dx = 0; dx < 3; dx++) {
            if (shape[dy * 3 + dx]) {
                set_pixel(plane->x + dx - 1, plane->y + dy - 1, 0);
            }
        }
    }
}

// Check if shot hits plane
bool check_hit(Shot *shot, Plane *target) {
    const uint8_t *shape = (target->type == 0) ? 
        plane0_shapes[target->dir] : 
        plane1_shapes[target->dir];
    
    // Check if shot position overlaps with any part of target plane
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

// Initialize game
void init_game(void) {
    clear_framebuffer();
    game_over = false;
    winner = 0;
    frame_counter = 0;
    
    // Initialize plane 0 (bottom right)
    planes[0].x = GAME_WIDTH - 10;
    planes[0].y = GAME_HEIGHT - 10;
    planes[0].dir = DIR_W;
    planes[0].type = 0;
    for (int i = 0; i < MAX_SHOTS; i++) {
        planes[0].shots[i].active = false;
    }
    
    // Initialize plane 1 (top left)
    planes[1].x = 10;
    planes[1].y = 10;
    planes[1].dir = DIR_E;
    planes[1].type = 1;
    for (int i = 0; i < MAX_SHOTS; i++) {
        planes[1].shots[i].active = false;
    }
}

// Fire shot
void fire_shot(Plane *plane) {
    // Find first inactive shot slot
    for (int i = 0; i < MAX_SHOTS; i++) {
        if (!plane->shots[i].active) {
            plane->shots[i].x = plane->x;
            plane->shots[i].y = plane->y;
            plane->shots[i].dir = plane->dir;
            plane->shots[i].range = 15;  // Shot range
            plane->shots[i].active = true;
            break;
        }
    }
}

// Update shot position
void update_shot(Shot *shot) {
    if (!shot->active) return;
    
    // Clear old position
    set_pixel(shot->x, shot->y, 0);
    
    // Move shot
    shot->x += dir_dx[shot->dir] * 3;  // Shots move 3x faster
    shot->y += dir_dy[shot->dir] * 3;
    
    // Wrap around screen
    if (shot->x < 0) shot->x = GAME_WIDTH - 1;
    if (shot->x >= GAME_WIDTH) shot->x = 0;
    if (shot->y < 0) shot->y = GAME_HEIGHT - 1;
    if (shot->y >= GAME_HEIGHT) shot->y = 0;
    
    // Decrement range
    shot->range--;
    if (shot->range == 0) {
        shot->active = false;
        return;
    }
    
    // Draw new position
    set_pixel(shot->x, shot->y, 1);
}

// Update plane position
void update_plane(Plane *plane) {
    // Clear old position
    clear_plane(plane);
    
    // Move plane
    plane->x += dir_dx[plane->dir];
    plane->y += dir_dy[plane->dir];
    
    // Wrap around screen
    if (plane->x < 1) plane->x = GAME_WIDTH - 2;
    if (plane->x >= GAME_WIDTH - 1) plane->x = 1;
    if (plane->y < 1) plane->y = GAME_HEIGHT - 2;
    if (plane->y >= GAME_HEIGHT - 1) plane->y = 1;
    
    // Draw new position
    draw_plane(plane);
}

// Game update
void update_game(void) {
    if (game_over) return;
    
    frame_counter++;
    
    // Get button states for both planes
    bool p0_left = button_pressed(BUTTON_A);   // Plane 0: A=left
    bool p0_right = button_pressed(BUTTON_B);  // Plane 0: B=right
    bool p0_fire = button_pressed(BUTTON_X);   // Plane 0: X=fire
    
    bool p1_left = button_pressed(BUTTON_Y);   // Plane 1: Y=left (placeholder for now)
    bool p1_right = false;  // Would need more buttons
    bool p1_fire = false;   // Would need more buttons
    
    // Update plane 0 rotation
    if (p0_left && !p0_right) {
        planes[0].dir = (planes[0].dir + 7) % 8;  // Rotate left
    } else if (p0_right && !p0_left) {
        planes[0].dir = (planes[0].dir + 1) % 8;  // Rotate right
    }
    
    // Update plane 1 rotation (for testing, will be network-controlled later)
    if (p1_left && !p1_right) {
        planes[1].dir = (planes[1].dir + 7) % 8;
    } else if (p1_right && !p1_left) {
        planes[1].dir = (planes[1].dir + 1) % 8;
    }
    
    // Fire shots
    static uint8_t p0_fire_cooldown = 0;
    static uint8_t p1_fire_cooldown = 0;
    
    if (p0_fire && p0_fire_cooldown == 0) {
        fire_shot(&planes[0]);
        p0_fire_cooldown = 10;  // Cooldown frames
    }
    if (p0_fire_cooldown > 0) p0_fire_cooldown--;
    
    if (p1_fire && p1_fire_cooldown == 0) {
        fire_shot(&planes[1]);
        p1_fire_cooldown = 10;
    }
    if (p1_fire_cooldown > 0) p1_fire_cooldown--;
    
    // Update planes (every frame)
    update_plane(&planes[0]);
    update_plane(&planes[1]);
    
    // Update shots (every frame)
    for (int i = 0; i < MAX_SHOTS; i++) {
        if (planes[0].shots[i].active) {
            update_shot(&planes[0].shots[i]);
            // Check if plane 0's shot hit plane 1
            if (check_hit(&planes[0].shots[i], &planes[1])) {
                game_over = true;
                winner = 1;
                planes[0].shots[i].active = false;
            }
        }
        if (planes[1].shots[i].active) {
            update_shot(&planes[1].shots[i]);
            // Check if plane 1's shot hit plane 0
            if (check_hit(&planes[1].shots[i], &planes[0])) {
                game_over = true;
                winner = 2;
                planes[1].shots[i].active = false;
            }
        }
    }
}

// Render framebuffer to display (only changed pixels)
void render_display(void) {
    for (int y = 0; y < GAME_HEIGHT; y++) {
        for (int x = 0; x < GAME_WIDTH; x++) {
            uint8_t current = framebuffer[y * GAME_WIDTH + x];
            uint8_t previous = prev_framebuffer[y * GAME_WIDTH + x];
            
            // Only update changed pixels
            if (current != previous) {
                uint16_t color = current ? COLOR_WHITE : COLOR_BLACK;
                display_fill_rect(x * PIXEL_SIZE, y * PIXEL_SIZE, 
                                PIXEL_SIZE, PIXEL_SIZE, color);
                prev_framebuffer[y * GAME_WIDTH + x] = current;
            }
        }
    }
    
    // Draw game over message if needed
    if (game_over) {
        char msg[32];
        snprintf(msg, sizeof(msg), "PLANE %d WINS", winner);
        display_draw_string(60, 220, msg, COLOR_YELLOW, COLOR_BLACK);
    }
}

// Main function
int main() {
    stdio_init_all();
    
    // Initialize display and buttons
    display_error_t result = display_pack_init();
    if (result != DISPLAY_OK) {
        printf("Display init failed: %s\n", display_error_string(result));
        return -1;
    }
    
    result = buttons_init();
    if (result != DISPLAY_OK) {
        printf("Button init failed: %s\n", display_error_string(result));
        return -1;
    }
    
    printf("Dogfight game started!\n");
    printf("Plane 0 (right): A=left, B=right, X=fire\n");
    printf("Plane 1 (left): Will be network-controlled\n");
    
    // Clear display
    display_clear(COLOR_BLACK);
    memset(prev_framebuffer, 0, sizeof(prev_framebuffer));
    
    // Initialize game
    init_game();
    
    // Main game loop
    while (true) {
        buttons_update();
        
        // Check for reset (both A and Y pressed)
        if (button_pressed(BUTTON_A) && button_pressed(BUTTON_Y)) {
            init_game();
            display_clear(COLOR_BLACK);
            memset(prev_framebuffer, 0, sizeof(prev_framebuffer));
        }
        
        update_game();
        render_display();
        
        sleep_ms(100);  // ~10 FPS (adjust for desired speed)
    }
    
    return 0;
}
