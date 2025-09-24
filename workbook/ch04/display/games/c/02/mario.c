#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/timer.h"
#include "mario.h"

// Game constants matching JavaScript version
#define LEVEL_COLS 211
#define LEVEL_ROWS 14
#define TILE_SIZE 16
#define MARIO_WIDTH 16
#define MARIO_HEIGHT 16

// Physics constants (using fixed-point math - multiply by 256 for precision)
#define MIN_WALK_SPEED_FP (int)(256 * (1.0f/16.0f + 3.0f/256.0f))
#define WALK_ACCEL_FP (int)(256 * (9.0f/256.0f + 8.0f/(16*16*16)))
#define MAX_WALK_SPEED_FP (int)(256 * (1 + 9.0f/16.0f))
#define RELEASE_DECEL_FP (int)(256 * (13.0f/256.0f))
#define SKID_DECEL_FP (int)(256 * (1.0f/16.0f + 10.0f/256.0f))
#define TURN_SPEED_FP (int)(256 * (9.0f/16.0f))
#define MAX_RUN_SPEED_FP (int)(256 * (2 + 9.0f/16.0f))
#define RUN_ACCEL_FP (int)(256 * (14.0f/256.0f + 4.0f/(16*16*16)))

#define AIRSPEED_CUTOFF_FP (int)(256 * (1 + 13.0f/16.0f))
#define AIR_SLOW_GAIN_FP (int)(256 * (9.0f/256.0f + 8.0f/(16*16*16)))
#define AIR_FAST_GAIN_FP (int)(256 * (14.0f/256.0f + 4.0f/(16*16*16)))
#define AIR_FAST_DRAG_FP (int)(256 * (13.0f/256.0f))
#define AIR_SLOW_DRAG_FP (int)(256 * (9.0f/256.0f + 8.0f/(16*16*16)))

#define JUMP_SPEED_FP (int)(256 * 4)
#define BIG_JUMP_SPEED_FP (int)(256 * 5)
#define SMALL_UP_DRAG_FP (int)(256 * (2.0f/16.0f))
#define MEDIUM_UP_DRAG_FP (int)(256 * (1.0f/16.0f + 14.0f/256.0f))
#define BIG_UP_DRAG_FP (int)(256 * (2.0f/16.0f + 8.0f/256.0f))
#define SMALL_GRAVITY_FP (int)(256 * (7.0f/16.0f))
#define MED_GRAVITY_FP (int)(256 * (6.0f/16.0f))
#define BIG_GRAVITY_FP (int)(256 * (9.0f/16.0f))
#define JUMP_CUTOFF1_FP (int)(256 * 1)
#define JUMP_CUTOFF2_FP (int)(256 * (2 + 5.0f/16.0f))
#define MAX_VSPEED_FP (int)(256 * 4)

// Colors (RGB565)
#define COLOR_BLACK 0x0000
#define COLOR_WHITE 0xFFFF
#define COLOR_BLUE 0x001F
#define COLOR_GREEN 0x07E0
#define COLOR_RED 0xF800
#define COLOR_BROWN 0x8A22
#define COLOR_YELLOW 0xFFE0
#define COLOR_SKY_BLUE 0x87CEEB

// Game state
typedef struct {
    int x_fp, y_fp;           // Position in fixed point (256 = 1 pixel)
    int xspeed_fp, yspeed_fp; // Velocity in fixed point
    bool skidding;
    bool fast_jump;
    bool faster_jump;
    bool fast_vjump;
    bool faster_vjump;
    bool facing_left;
    int run_count;
} mario_t;

typedef struct {
    int x, y;
    int type;
    int anim_frame;
} object_t;

// Global game state
static mario_t mario;
static int scroll_fp = 0; // Scroll position in fixed point
static int frame = 0;
static int background_frame = 0;
static object_t objects[256]; // Max objects
static int object_count = 0;
static bool prev_keys[4] = {false, false, false, false}; // A, B, X, Y
static bool keys[4] = {false, false, false, false};

// Block animation frames
static const int block_anim[] = {-1,0,1,2,3,4,5,6,6,5,4,3,2,1};
#define BLOCK_ANIM_LEN 14

// Level data (from JavaScript)
static const uint8_t level_data[] = {
    0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,26,27,1,0,0,0,0,0,0,0,0,0,0,24,27,32,1,0,0,0,0,0,0,0,0,0,0,0,28,33,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,2,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,24,27,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,9,13,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,3,0,0,0,1,0,0,11,15,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,2,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0,0,0,2,0,0,34,1,0,0,0,0,0,0,0,0,0,3,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,9,13,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,5,7,1,0,0,0,10,14,0,0,0,0,0,0,6,8,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,11,15,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,9,13,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,5,7,7,1,0,0,11,15,0,0,0,0,0,0,6,8,8,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,5,7,7,7,1,0,0,0,0,0,0,0,0,0,6,8,8,8,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,26,27,1,0,0,0,0,0,0,0,0,0,0,24,27,32,1,0,0,0,0,0,0,0,0,0,0,0,28,33,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,9,13,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,5,7,7,7,1,0,0,0,11,15,0,0,0,0,6,8,8,8,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,24,27,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,9,13,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,0,0,0,1,0,0,11,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,9,13,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,3,0,0,0,1,0,0,0,10,14,0,0,0,0,2,0,0,0,1,0,0,0,11,15,0,0,0,0,3,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,9,13,0,3,0,0,0,0,0,0,0,1,0,0,10,14,0,3,0,0,0,0,0,0,0,1,0,0,10,14,0,3,0,0,0,0,0,0,0,0,0,0,11,15,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,3,0,0,0,0,0,0,35,1,0,0,0,0,0,3,0,0,0,0,0,0,36,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,26,27,1,0,0,0,0,0,0,0,0,0,0,24,27,32,1,0,0,0,0,0,0,0,0,0,0,0,28,33,1,0,0,0,0,0,0,0,0,0,3,0,0,28,1,0,0,0,0,0,0,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,9,13,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,11,15,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,2,0,0,0,2,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,37,1,0,0,0,0,0,0,0,0,0,2,0,29,38,1,0,0,0,0,0,0,0,0,0,0,0,30,39,1,0,0,0,0,0,0,0,0,0,0,0,0,40,1,0,0,9,13,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,0,0,0,1,0,0,11,15,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,3,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,3,0,0,0,0,0,0,36,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,9,13,3,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,11,15,0,0,0,0,0,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,3,0,0,0,1,0,0,0,0,0,2,0,0,0,3,0,0,0,1,0,0,0,0,0,3,0,0,0,0,0,0,0,1,0,0,9,13,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,0,0,0,1,0,0,10,14,0,0,0,0,0,0,0,0,4,1,0,0,11,15,0,0,0,0,0,0,0,4,4,1,0,0,0,0,0,0,0,0,0,0,4,4,4,1,0,0,0,0,0,0,0,0,0,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,0,0,0,35,1,0,0,0,0,0,0,0,0,0,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0,4,4,1,0,0,0,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,26,27,1,0,0,0,0,0,0,0,0,0,0,24,27,32,1,0,0,0,0,0,0,0,0,0,0,0,28,33,1,0,0,0,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,0,4,4,1,0,0,0,0,0,0,0,0,0,0,4,4,4,1,0,0,0,0,0,0,0,0,0,4,4,4,4,1,0,0,0,9,13,0,0,0,0,4,4,4,4,1,0,0,0,10,14,0,0,0,0,0,0,0,0,0,0,0,0,11,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0,4,4,1,0,0,0,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,24,27,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,9,13,0,0,0,0,0,0,0,5,7,1,0,0,10,14,0,0,0,0,0,0,0,6,8,1,0,0,11,15,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,34,1,0,0,0,0,0,0,0,0,0,3,0,0,35,1,0,0,0,0,0,0,0,0,0,3,0,0,36,1,0,0,0,0,0,0,0,0,0,2,0,0,0,1,0,0,0,9,13,0,0,0,0,3,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,11,15,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,5,7,1,0,0,9,13,0,0,0,0,0,0,0,6,8,1,0,0,10,14,0,0,0,0,0,0,0,0,4,1,0,0,10,14,0,0,0,0,0,0,0,4,4,1,0,0,11,15,0,0,0,0,0,0,4,4,4,1,0,0,0,0,0,0,0,0,0,4,4,4,4,1,0,0,0,0,0,0,0,0,4,4,4,4,4,1,0,0,0,0,0,0,0,4,4,4,4,4,4,1,0,0,0,0,0,4,4,4,4,4,4,4,1,0,0,0,0,0,4,4,4,4,4,4,4,4,1,0,0,0,0,0,4,4,4,4,4,4,4,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,26,27,1,0,0,0,0,0,0,0,0,0,0,24,27,32,1,0,0,0,0,0,0,0,0,0,0,0,28,33,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1,0,0,0,16,0,0,0,0,0,0,0,0,0,1,0,0,12,17,18,19,19,19,19,19,19,19,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,9,13,0,0,0,0,0,0,0,0,1,0,0,0,10,14,0,0,0,0,0,0,0,0,1,0,0,0,11,15,0,0,0,0,0,20,22,22,1,0,0,0,0,0,0,0,0,20,21,25,22,22,1,0,0,0,0,0,0,0,0,20,22,25,31,41,1,0,0,0,0,0,0,0,0,20,23,25,22,22,1,0,0,0,0,0,0,0,0,0,0,20,22,22,1,0,0,0,0,0,0,0,0,0,0,0,0,36,1,0,0,0,0,0,0,0,0,0,0,0,0,26,1,0,0,0,0,0,0,0,0,0,0,0,24,27,1,0,0,0,0,0,0,0,0,0,0,0,0,28,1
};

// Tile colors (simplified - in real implementation you'd load actual sprites)
static uint16_t get_tile_color(uint8_t tile) {
    switch (tile) {
        case 0: return COLOR_SKY_BLUE;  // Sky
        case 1: return COLOR_BROWN;     // Ground
        case 2: 
        case 3: return COLOR_YELLOW;    // Blocks
        case 4: return COLOR_GREEN;     // Pipe
        default: return COLOR_BROWN;
    }
}

// Check if a tile is solid
static bool is_solid(int x, int y) {
    int tile_x = (scroll_fp / 256 + x) / TILE_SIZE;
    int tile_y = y / TILE_SIZE;
    
    if (tile_x < 0 || tile_x >= LEVEL_COLS || tile_y < 0 || tile_y >= LEVEL_ROWS) {
        return false;
    }
    
    uint8_t tile = level_data[tile_x * LEVEL_ROWS + tile_y];
    return (tile && tile < 9);
}

// Check if a tile is an object (coin/block)
static bool is_object(uint8_t tile) {
    return (tile == 2 || tile == 3);
}

// Init game objects from level data
static void init_objects() {
    object_count = 0;
    for (int j = 0; j < LEVEL_ROWS && object_count < 255; j++) {
        for (int i = 0; i < LEVEL_COLS && object_count < 255; i++) {
            uint8_t tile = level_data[j + LEVEL_ROWS * i];
            if (is_object(tile)) {
                objects[object_count].x = i;
                objects[object_count].y = j;
                objects[object_count].type = tile;
                objects[object_count].anim_frame = 0;
                object_count++;
            }
        }
    }
}

// Init Mario
static void init_mario() {
    mario.x_fp = 50 * 256;
    mario.y_fp = 128 * 256;
    mario.xspeed_fp = 0;
    mario.yspeed_fp = 0;
    mario.skidding = false;
    mario.fast_jump = false;
    mario.faster_jump = false;
    mario.fast_vjump = false;
    mario.faster_vjump = false;
    mario.facing_left = false;
    mario.run_count = 0;
}

// Update input
static void update_input() {
    // Copy previous state
    memcpy(prev_keys, keys, sizeof(keys));
    
    // Read current state (mapping display pack buttons to game controls)
    keys[0] = button_pressed(BUTTON_A);  // Run button (A in JS)
    keys[1] = button_pressed(BUTTON_B);  // Jump button (S in JS) 
    keys[2] = button_pressed(BUTTON_X);  // Left arrow
    keys[3] = button_pressed(BUTTON_Y);  // Right arrow
}

// Absolute value for fixed point
static int abs_fp(int val) {
    return val < 0 ? -val : val;
}

// Update Mario physics
static void update_mario() {
    // Check if standing on ground
    bool standing_on = is_solid(mario.x_fp / 256, (mario.y_fp / 256) + 8) ||
                      (is_solid((mario.x_fp / 256) + 4, (mario.y_fp / 256) + 8) && 
                       (((mario.y_fp / 256) + 8) % 16) < 1 + (mario.yspeed_fp / 256)) ||
                      (is_solid((mario.x_fp / 256) - 4, (mario.y_fp / 256) + 8) && 
                       (((mario.y_fp / 256) + 8) % 16) < 1 + (mario.yspeed_fp / 256));
    
    if (standing_on) {
        // Snap to ground
        mario.y_fp = (((mario.y_fp / 256 + 8) / 16) * 16 - 8) * 256;
        mario.yspeed_fp = 0;
        
        // Ground movement
        int accel = keys[0] ? RUN_ACCEL_FP : WALK_ACCEL_FP; // A button for run
        
        if (keys[0]) {
            mario.run_count = 10;
        } else if (mario.run_count > 0) {
            mario.run_count--;
        }
        
        if (keys[3]) { // Right (Y button)
            if (mario.xspeed_fp < 0) { // Skidding
                mario.skidding = true;
                if (mario.xspeed_fp > -TURN_SPEED_FP) {
                    mario.xspeed_fp = 0;
                } else {
                    mario.xspeed_fp += SKID_DECEL_FP;
                }
            } else {
                mario.skidding = false;
                mario.facing_left = false;
                
                if (mario.xspeed_fp == 0) {
                    mario.xspeed_fp = MIN_WALK_SPEED_FP;
                } else {
                    mario.xspeed_fp += accel;
                }
                
                if (mario.xspeed_fp > MAX_RUN_SPEED_FP) {
                    mario.xspeed_fp = MAX_RUN_SPEED_FP;
                }
                if (mario.xspeed_fp > MAX_WALK_SPEED_FP && mario.run_count == 0) {
                    mario.xspeed_fp = MAX_WALK_SPEED_FP;
                }
            }
        } else if (keys[2]) { // Left (X button)
            if (mario.xspeed_fp > 0) { // Skidding
                mario.skidding = true;
                if (mario.xspeed_fp < TURN_SPEED_FP) {
                    mario.xspeed_fp = 0;
                } else {
                    mario.xspeed_fp -= SKID_DECEL_FP;
                }
            } else {
                mario.skidding = false;
                mario.facing_left = true;
                
                if (mario.xspeed_fp == 0) {
                    mario.xspeed_fp = -MIN_WALK_SPEED_FP;
                } else {
                    mario.xspeed_fp -= accel;
                }
                
                if (mario.xspeed_fp < -MAX_RUN_SPEED_FP) {
                    mario.xspeed_fp = -MAX_RUN_SPEED_FP;
                }
                if (mario.xspeed_fp < -MAX_WALK_SPEED_FP && mario.run_count == 0) {
                    mario.xspeed_fp = -MAX_WALK_SPEED_FP;
                }
            }
        } else { // No direction pressed
            int decel = mario.skidding ? SKID_DECEL_FP : RELEASE_DECEL_FP;
            
            if (mario.xspeed_fp > decel) {
                mario.xspeed_fp -= decel;
            } else if (mario.xspeed_fp < -decel) {
                mario.xspeed_fp += decel;
            } else {
                mario.xspeed_fp = 0;
                mario.skidding = false;
            }
        }
        
        // Set jump flags based on speed
        int abs_xspeed = abs_fp(mario.xspeed_fp);
        
        mario.faster_vjump = (abs_xspeed > JUMP_CUTOFF2_FP);
        mario.fast_vjump = (abs_xspeed > JUMP_CUTOFF1_FP);
        mario.fast_jump = (abs_xspeed > MAX_WALK_SPEED_FP);
        mario.faster_jump = (abs_xspeed > AIRSPEED_CUTOFF_FP);
        
        // Jump
        if (keys[1] && !prev_keys[1]) { // B button pressed (jump)
            mario.yspeed_fp = mario.faster_vjump ? -BIG_JUMP_SPEED_FP : -JUMP_SPEED_FP;
        }
        
    } else { // In air
        // Air movement
        if (keys[3]) { // Right
            if (abs_fp(mario.xspeed_fp) >= MAX_WALK_SPEED_FP) {
                mario.xspeed_fp += AIR_FAST_GAIN_FP;
            } else {
                if (mario.xspeed_fp > 0) {
                    mario.xspeed_fp += AIR_SLOW_GAIN_FP;
                } else {
                    mario.xspeed_fp += mario.faster_jump ? AIR_FAST_DRAG_FP : AIR_SLOW_DRAG_FP;
                }
            }
        } else if (keys[2]) { // Left
            if (abs_fp(mario.xspeed_fp) >= MAX_WALK_SPEED_FP) {
                mario.xspeed_fp -= AIR_FAST_GAIN_FP;
            } else {
                if (mario.xspeed_fp < 0) {
                    mario.xspeed_fp -= AIR_SLOW_GAIN_FP;
                } else {
                    mario.xspeed_fp -= mario.faster_jump ? AIR_FAST_DRAG_FP : AIR_SLOW_DRAG_FP;
                }
            }
        }
        
        // Air speed limits
        if (mario.fast_jump) {
            if (mario.xspeed_fp < -MAX_RUN_SPEED_FP) mario.xspeed_fp = -MAX_RUN_SPEED_FP;
            if (mario.xspeed_fp > MAX_RUN_SPEED_FP) mario.xspeed_fp = MAX_RUN_SPEED_FP;
        } else {
            if (mario.xspeed_fp < -MAX_WALK_SPEED_FP) mario.xspeed_fp = -MAX_WALK_SPEED_FP;
            if (mario.xspeed_fp > MAX_WALK_SPEED_FP) mario.xspeed_fp = MAX_WALK_SPEED_FP;
        }
        
        // Gravity and jump control
        if (mario.yspeed_fp < 0 && keys[1]) { // Holding jump while going up
            if (mario.faster_vjump) {
                mario.yspeed_fp += BIG_UP_DRAG_FP;
            } else if (mario.fast_vjump) {
                mario.yspeed_fp += MEDIUM_UP_DRAG_FP;
            } else {
                mario.yspeed_fp += SMALL_UP_DRAG_FP;
            }
        } else { // Not holding jump or falling
            if (mario.faster_vjump) {
                mario.yspeed_fp += BIG_GRAVITY_FP;
            } else if (mario.fast_vjump) {
                mario.yspeed_fp += MED_GRAVITY_FP;
            } else {
                mario.yspeed_fp += SMALL_GRAVITY_FP;
            }
        }
        
        if (mario.yspeed_fp > MAX_VSPEED_FP) {
            mario.yspeed_fp = MAX_VSPEED_FP;
        }
    }
    
    // Apply velocity
    mario.x_fp += mario.xspeed_fp;
    mario.y_fp += mario.yspeed_fp;
    
    // Wall collisions
    bool solid_left = is_solid((mario.x_fp / 256) - 7, mario.y_fp / 256);
    bool solid_right = is_solid((mario.x_fp / 256) + 7, mario.y_fp / 256);
    
    if (solid_left && !solid_right) {
        if (mario.facing_left) {
            mario.xspeed_fp = 0;
        }
        mario.x_fp += 256; // Push right
    }
    
    if (solid_right && !solid_left) {
        if (!mario.facing_left) {
            mario.xspeed_fp = 0;
        }
        mario.x_fp -= 256; // Push left
    }
    
    // Head collision
    if (is_solid(mario.x_fp / 256, (mario.y_fp / 256) - 4)) {
        mario.yspeed_fp = 0;
        mario.y_fp = (((mario.y_fp / 256 - 4) / 16 + 1) * 16 + 4) * 256;
        
        // Hit block animation (simplified)
        int tile_x = (scroll_fp / 256 + mario.x_fp / 256) / 16;
        int tile_y = (mario.y_fp / 256 - 4) / 16;
        
        for (int k = 0; k < object_count; k++) {
            if (objects[k].x == tile_x && objects[k].y == tile_y) {
                if (objects[k].type == 2 || objects[k].type == 3) {
                    objects[k].anim_frame = BLOCK_ANIM_LEN;
                }
                break;
            }
        }
    }
    
    // Screen boundaries
    if (mario.x_fp / 256 < 8) {
        mario.x_fp = 8 * 256;
        mario.xspeed_fp = 0;
    }
    
    if (mario.x_fp / 256 > 90) {
        int scroll_amount = ((mario.x_fp / 256) - 90) / 2;
        scroll_fp += scroll_amount * 256;
        mario.x_fp -= scroll_amount * 256;
    }
}

// Update animations and objects
static void update_animations() {
    // Update Mario animation frame
    if (mario.xspeed_fp || keys[2] || keys[3]) {
        frame = (frame + 1 + abs_fp(mario.xspeed_fp * 2) / 256) % 48;
    } else {
        frame = 0;
    }
    
    background_frame = (background_frame + 1) % 80;
    
    // Update object animations
    for (int i = 0; i < object_count; i++) {
        if (objects[i].anim_frame > 0) {
            objects[i].anim_frame--;
        }
    }
}

// Draw a tile at screen position
static void draw_tile(int screen_x, int screen_y, uint8_t tile) {
    if (screen_x < -16 || screen_x >= DISPLAY_WIDTH || screen_y < -16 || screen_y >= DISPLAY_HEIGHT) {
        return;
    }
    
    uint16_t color = get_tile_color(tile);
    
    // Draw 16x16 tile (simplified - single color)
    for (int y = 0; y < 16 && screen_y + y < DISPLAY_HEIGHT; y++) {
        for (int x = 0; x < 16 && screen_x + x < DISPLAY_WIDTH; x++) {
            if (screen_x + x >= 0 && screen_y + y >= 0) {
                display_draw_pixel(screen_x + x, screen_y + y, color);
            }
        }
    }
}

// Draw Mario sprite (simplified)
static void draw_mario(int screen_x, int screen_y) {
    if (screen_x < -16 || screen_x >= DISPLAY_WIDTH || screen_y < -16 || screen_y >= DISPLAY_HEIGHT) {
        return;
    }
    
    uint16_t mario_color = COLOR_RED; // Simple red rectangle for Mario
    
    // Draw 16x16 Mario sprite (simplified)
    for (int y = 0; y < 16 && screen_y + y < DISPLAY_HEIGHT; y++) {
        for (int x = 0; x < 16 && screen_x + x < DISPLAY_WIDTH; x++) {
            if (screen_x + x >= 0 && screen_y + y >= 0) {
                // Simple Mario shape
                if ((x >= 2 && x <= 13) && (y >= 2 && y <= 13)) {
                    display_draw_pixel(screen_x + x, screen_y + y, mario_color);
                }
            }
        }
    }
}

// Render the game
static void render() {
    // Clear screen
    display_clear(COLOR_SKY_BLUE);
    
    // Draw level tiles
    int scroll_pixels = scroll_fp / 256;
    int start_tile_x = scroll_pixels / 16;
    int end_tile_x = start_tile_x + (DISPLAY_WIDTH / 16) + 2;
    
    for (int j = 0; j < LEVEL_ROWS; j++) {
        for (int i = start_tile_x; i <= end_tile_x && i < LEVEL_COLS; i++) {
            if (i >= 0) {
                uint8_t tile = level_data[j + LEVEL_ROWS * i];
                if (!is_object(tile)) {
                    int screen_x = i * 16 - scroll_pixels;
                    int screen_y = j * 16;
                    draw_tile(screen_x, screen_y, tile);
                }
            }
        }
    }
    
    // Draw objects (coins, blocks, etc.)
    for (int i = 0; i < object_count; i++) {
        int screen_x = objects[i].x * 16 - scroll_pixels;
        int screen_y = objects[i].y * 16;
        
        if (screen_x > -16 && screen_x < DISPLAY_WIDTH + 16) {
            // Animate blocks when hit
            int offset_y = 0;
            if (objects[i].anim_frame > 0) {
                offset_y = block_anim[BLOCK_ANIM_LEN - objects[i].anim_frame];
            }
            
            draw_tile(screen_x, screen_y - offset_y, objects[i].type);
        }
    }
    
    // Draw Mario
    int mario_screen_x = (mario.x_fp / 256) - 8;
    int mario_screen_y = (mario.y_fp / 256) - 7;
    draw_mario(mario_screen_x, mario_screen_y);
}

// Button callback handlers
static void button_a_callback(button_t button) {
    // Run button - handled in update_input
}

static void button_b_callback(button_t button) {
    // Jump button - handled in update_input
}

static void button_x_callback(button_t button) {
    // Left button - handled in update_input
}

static void button_y_callback(button_t button) {
    // Right button - handled in update_input
}

// Game init
static void game_init() {
    init_mario();
    init_objects();
    scroll_fp = 0;
    frame = 0;
    background_frame = 0;
    
    // Set up button callbacks (optional - we're using polling)
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
}

// Main game loop
static void game_loop() {
    while (true) {
        update_input();
        buttons_update();
        update_mario();
        update_animations();
        render();
        
        // Simple frame rate control (approximately 60 FPS)
        sleep_ms(16);
    }
}

// Main function
int main() {
    stdio_init_all();
    
    // Init display
    if (display_pack_init() != DISPLAY_OK) {
        printf("Failed to initialise display\n");
        return 1;
    }
    
    // Init buttons
    if (buttons_init() != DISPLAY_OK) {
        printf("Failed to initialise buttons\n");
        return 1;
    }
    
    printf("Mario game starting..\n");
    
    // Init game
    game_init();
    
    // Start game loop
    game_loop();
    
    return 0;
}

