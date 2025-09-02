/*
- Spatial grid system for efficient collision detection
- Dirty region tracking to minimize redraws
- Bit masks for tracking active objects
- Pre-computed pixel data for invaders
- Batch update system
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "libraries/pico_display_2/pico_display_2.hpp"

using namespace pimoroni;

PicoDisplay2 display;
PicoGraphics_PenRGB565 graphics(display.width, display.height, nullptr);

#define WIDTH 320
#define HEIGHT 240
#define SCALE 1.5f

// Colours (RGB565 format)
#define BLACK 0x0000
#define WHITE 0xFFFF
#define GREEN 0x07E0
#define RED 0xF800
#define YELLOW 0xFFE0

#define BUTTON_A 12
#define BUTTON_B 13
#define BUTTON_X 14

#define MAX_BULLETS 10
#define MAX_BOMBS 20
#define MAX_INVADERS 15
#define MAX_BUNKERS 2
#define SPATIAL_GRID_SIZE 8  // 8x8 spatial grid

// Performance optimisation flags
#define DIRTY_REGIONS 1
#define USE_SPATIAL_GRID 1
#define BATCH_UPDATES 1

// Player structure
typedef struct {
    float x, y;
    int width, height;
    float speed;
    bool needs_redraw;
} Player;

// Bullet/Bomb structure with spatial optimisation
typedef struct {
    float x, y;
    float prev_x, prev_y;  // For dirty region tracking
    bool active;
    uint8_t grid_x, grid_y;  // Spatial grid position
} Projectile;

// Invader type structure - optimised with pre-computed data
typedef struct {
    uint8_t pixels[3][6];
    int pixel_width, pixel_height;
    int width, height;
    uint16_t color;
    // Pre-computed pixel positions for faster rendering
    struct {
        uint8_t x, y;
    } solid_pixels[18];  // Max pixels for largest invader
    uint8_t solid_pixel_count;
} InvaderType;

// Invader structure with spatial optimisation
typedef struct {
    float x, y;
    float prev_x, prev_y;  // For dirty region tracking
    InvaderType* type;
    int width, height;
    bool alive;
    bool needs_redraw;
    uint8_t grid_x, grid_y;  // Spatial grid position
} Invader;

// Bunker structure with damage tracking optimisation
typedef struct {
    float x, y;
    uint8_t pixels[3][5];
    int width, height;
    uint16_t color;
    bool needs_redraw;
    uint32_t damage_hash;  // Hash of damage state for quick comparison
} Bunker;

// Spatial grid for collision optimisation
typedef struct {
    uint16_t invader_mask;    // Bit mask for invaders in this cell
    uint16_t bullet_mask;     // Bit mask for bullets in this cell
    uint16_t bomb_mask;       // Bit mask for bombs in this cell
} SpatialCell;

// Game state with optimisation data
Player player;
Projectile bullets[MAX_BULLETS];
Projectile bombs[MAX_BOMBS];
Invader invaders[MAX_INVADERS];
Bunker bunkers[MAX_BUNKERS];
InvaderType invader_types[2];

// Spatial optimisation
SpatialCell spatial_grid[SPATIAL_GRID_SIZE][SPATIAL_GRID_SIZE];
float grid_cell_width, grid_cell_height;

// Performance tracking
uint32_t active_bullets_mask = 0;  // Bit mask for active bullets
uint32_t active_bombs_mask = 0;    // Bit mask for active bombs
uint32_t alive_invaders_mask = 0;  // Bit mask for alive invaders

// Game variables
int bullet_count = 0;
int bomb_count = 0;
int invader_count = 0;
float invader_speed = 1.5f;
int invader_direction = 1;
float invader_drop = 7.5f;
int frame_count = 0;
int invader_move_interval = 20;
bool game_over = false;
bool win = false;

// Batch update system
typedef struct {
    enum { UPDATE_INVADER, UPDATE_BULLET, UPDATE_BOMB, UPDATE_PLAYER } type;
    uint8_t index;
} UpdateBatch;

UpdateBatch update_queue[MAX_INVADERS + MAX_BULLETS + MAX_BOMBS + 1];
uint8_t update_queue_size = 0;

// Function prototypes
void init_game(void);
void init_invader_types(void);
void init_invaders(void);
void init_bunkers(void);
void init_spatial_grid(void);
void update_spatial_position(uint8_t type, uint8_t index, float x, float y);
void batch_update_game(void);
void optimized_collision_detection(void);
void draw_game_optimized(void);
void draw_invader_optimized(Invader* inv);
void draw_bunker_optimized(Bunker* bunker);
void draw_player_optimized(Player* p);
void fire_bullet(void);
void fire_bomb(int invader_index);
void update_projectiles(void);
void update_invaders(void);
void handle_input(void);
bool check_collision(float x1, float y1, int w1, int h1, float x2, float y2, int w2, int h2);
uint32_t calculate_damage_hash(uint8_t pixels[3][5]);

// Init invader types with pre-computed pixel data
void init_invader_types(void) {
    // Type 0 - Small invader
    invader_types[0].pixel_width = 3;
    invader_types[0].pixel_height = 3;
    invader_types[0].width = 9;
    invader_types[0].height = 9;
    invader_types[0].color = GREEN;
    
    // Define pixel pattern (1 = solid, 0 = empty)
    uint8_t type0_pattern[3][3] = {
        {1, 0, 1},
        {0, 1, 0},
        {1, 0, 1}
    };
    
    // Pre-compute solid pixel positions
    invader_types[0].solid_pixel_count = 0;
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 3; x++) {
            if (type0_pattern[y][x]) {
                invader_types[0].solid_pixels[invader_types[0].solid_pixel_count].x = x;
                invader_types[0].solid_pixels[invader_types[0].solid_pixel_count].y = y;
                invader_types[0].solid_pixel_count++;
            }
        }
    }
    
    // Type 1 - Large invader
    invader_types[1].pixel_width = 4;
    invader_types[1].pixel_height = 3;
    invader_types[1].width = 12;
    invader_types[1].height = 9;
    invader_types[1].color = RED;
    
    uint8_t type1_pattern[3][4] = {
        {0, 1, 1, 0},
        {1, 1, 1, 1},
        {1, 0, 0, 1}
    };
    
    invader_types[1].solid_pixel_count = 0;
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 4; x++) {
            if (type1_pattern[y][x]) {
                invader_types[1].solid_pixels[invader_types[1].solid_pixel_count].x = x;
                invader_types[1].solid_pixels[invader_types[1].solid_pixel_count].y = y;
                invader_types[1].solid_pixel_count++;
            }
        }
    }
}

// Init spatial grid
void init_spatial_grid(void) {
    grid_cell_width = (float)WIDTH / SPATIAL_GRID_SIZE;
    grid_cell_height = (float)HEIGHT / SPATIAL_GRID_SIZE;
    
    // Clear spatial grid
    memset(spatial_grid, 0, sizeof(spatial_grid));
}

// Update spatial position for an object
void update_spatial_position(uint8_t type, uint8_t index, float x, float y) {
    uint8_t grid_x = (uint8_t)(x / grid_cell_width);
    uint8_t grid_y = (uint8_t)(y / grid_cell_height);
    
    // Clamp to grid bounds
    if (grid_x >= SPATIAL_GRID_SIZE) grid_x = SPATIAL_GRID_SIZE - 1;
    if (grid_y >= SPATIAL_GRID_SIZE) grid_y = SPATIAL_GRID_SIZE - 1;
    
    switch (type) {
        case 0: // Invader
            invaders[index].grid_x = grid_x;
            invaders[index].grid_y = grid_y;
            spatial_grid[grid_y][grid_x].invader_mask |= (1 << index);
            break;
        case 1: // Bullet
            bullets[index].grid_x = grid_x;
            bullets[index].grid_y = grid_y;
            spatial_grid[grid_y][grid_x].bullet_mask |= (1 << index);
            break;
        case 2: // Bomb
            bombs[index].grid_x = grid_x;
            bombs[index].grid_y = grid_y;
            spatial_grid[grid_y][grid_x].bomb_mask |= (1 << index);
            break;
    }
}

// Init invaders
void init_invaders(void) {
    invader_count = 0;
    alive_invaders_mask = 0;
    
    for (int row = 0; row < 3; row++) {
        for (int col = 0; col < 5; col++) {
            if (invader_count >= MAX_INVADERS) break;
            
            invaders[invader_count].x = 50 + col * 30;
            invaders[invader_count].y = 50 + row * 25;
            invaders[invader_count].type = (row < 2) ? &invader_types[0] : &invader_types[1];
            invaders[invader_count].width = invaders[invader_count].type->width;
            invaders[invader_count].height = invaders[invader_count].type->height;
            invaders[invader_count].alive = true;
            invaders[invader_count].needs_redraw = true;
            
            alive_invaders_mask |= (1 << invader_count);
            update_spatial_position(0, invader_count, invaders[invader_count].x, invaders[invader_count].y);
            
            invader_count++;
        }
    }
}

// Init bunkers
void init_bunkers(void) {
    for (int i = 0; i < MAX_BUNKERS; i++) {
        bunkers[i].x = 80 + i * 160;
        bunkers[i].y = 180;
        bunkers[i].width = 15;
        bunkers[i].height = 9;
        bunkers[i].color = GREEN;
        bunkers[i].needs_redraw = true;
        
        // Init bunker pixels (simple rectangle pattern)
        for (int y = 0; y < 3; y++) {
            for (int x = 0; x < 5; x++) {
                bunkers[i].pixels[y][x] = 1;
            }
        }
        
        bunkers[i].damage_hash = calculate_damage_hash(bunkers[i].pixels);
    }
}

// Calculate damage hash for bunker
uint32_t calculate_damage_hash(uint8_t pixels[3][5]) {
    uint32_t hash = 0;
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 5; x++) {
            hash = (hash << 1) | pixels[y][x];
        }
    }
    return hash;
}

// Init game
void init_game(void) {
    // Init player
    player.x = WIDTH / 2 - 10;
    player.y = HEIGHT - 20;
    player.width = 20;
    player.height = 10;
    player.speed = 3.0f;
    player.needs_redraw = true;
    
    // Init projectiles
    bullet_count = 0;
    bomb_count = 0;
    active_bullets_mask = 0;
    active_bombs_mask = 0;
    
    for (int i = 0; i < MAX_BULLETS; i++) {
        bullets[i].active = false;
    }
    
    for (int i = 0; i < MAX_BOMBS; i++) {
        bombs[i].active = false;
    }
    
    // Init game components
    init_invader_types();
    init_spatial_grid();
    init_invaders();
    init_bunkers();
    
    game_over = false;
    win = false;
    frame_count = 0;
}

// Fire bullet
void fire_bullet(void) {
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) {
            bullets[i].x = player.x + player.width / 2;
            bullets[i].y = player.y;
            bullets[i].active = true;
            active_bullets_mask |= (1 << i);
            update_spatial_position(1, i, bullets[i].x, bullets[i].y);
            bullet_count++;
            break;
        }
    }
}

// Fire bomb from invader
void fire_bomb(int invader_index) {
    if (!invaders[invader_index].alive) return;
    
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (!bombs[i].active) {
            bombs[i].x = invaders[invader_index].x + invaders[invader_index].width / 2;
            bombs[i].y = invaders[invader_index].y + invaders[invader_index].height;
            bombs[i].active = true;
            active_bombs_mask |= (1 << i);
            update_spatial_position(2, i, bombs[i].x, bombs[i].y);
            bomb_count++;
            break;
        }
    }
}

// Check collision between two rectangles
bool check_collision(float x1, float y1, int w1, int h1, float x2, float y2, int w2, int h2) {
    return (x1 < x2 + w2 && x1 + w1 > x2 && y1 < y2 + h2 && y1 + h1 > y2);
}

// Update projectiles
void update_projectiles(void) {
    // Update bullets
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            bullets[i].prev_y = bullets[i].y;
            bullets[i].y -= 5.0f;
            
            if (bullets[i].y < -5) {
                bullets[i].active = false;
                active_bullets_mask &= ~(1 << i);
                bullet_count--;
            } else {
                update_spatial_position(1, i, bullets[i].x, bullets[i].y);
            }
        }
    }
    
    // Update bombs
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            bombs[i].prev_y = bombs[i].y;
            bombs[i].y += 3.0f;
            
            if (bombs[i].y > HEIGHT + 5) {
                bombs[i].active = false;
                active_bombs_mask &= ~(1 << i);
                bomb_count--;
            } else {
                update_spatial_position(2, i, bombs[i].x, bombs[i].y);
            }
        }
    }
}

// Update invaders
void update_invaders(void) {
    if (frame_count % invader_move_interval == 0) {
        bool should_drop = false;
        
        // Check if any invader hits screen edge
        for (int i = 0; i < invader_count; i++) {
            if (invaders[i].alive) {
                if ((invader_direction > 0 && invaders[i].x + invaders[i].width >= WIDTH) ||
                    (invader_direction < 0 && invaders[i].x <= 0)) {
                    should_drop = true;
                    break;
                }
            }
        }
        
        if (should_drop) {
            invader_direction *= -1;
            for (int i = 0; i < invader_count; i++) {
                if (invaders[i].alive) {
                    invaders[i].prev_y = invaders[i].y;
                    invaders[i].y += invader_drop;
                    invaders[i].needs_redraw = true;
                    update_spatial_position(0, i, invaders[i].x, invaders[i].y);
                    
                    // Check if invaders reached player level
                    if (invaders[i].y + invaders[i].height >= player.y) {
                        game_over = true;
                    }
                }
            }
        } else {
            // Move horizontally
            for (int i = 0; i < invader_count; i++) {
                if (invaders[i].alive) {
                    invaders[i].prev_x = invaders[i].x;
                    invaders[i].x += invader_speed * invader_direction;
                    invaders[i].needs_redraw = true;
                    update_spatial_position(0, i, invaders[i].x, invaders[i].y);
                }
            }
        }
        
        // Random bomb firing
        if (rand() % 100 < 5) { // 5% chance per update
            int alive_invaders[MAX_INVADERS];
            int alive_count = 0;
            
            for (int i = 0; i < invader_count; i++) {
                if (invaders[i].alive) {
                    alive_invaders[alive_count++] = i;
                }
            }
            
            if (alive_count > 0) {
                fire_bomb(alive_invaders[rand() % alive_count]);
            }
        }
    }
}

// optimised collision detection using spatial grid
void optimized_collision_detection(void) {
    // Clear spatial grid
    memset(spatial_grid, 0, sizeof(spatial_grid));
    
    // Populate spatial grid
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            update_spatial_position(1, i, bullets[i].x, bullets[i].y);
        }
    }
    
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            update_spatial_position(2, i, bombs[i].x, bombs[i].y);
        }
    }
    
    for (int i = 0; i < invader_count; i++) {
        if (invaders[i].alive) {
            update_spatial_position(0, i, invaders[i].x, invaders[i].y);
        }
    }
    
    // Check bullet-invader collisions
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) continue;
        
        uint8_t gx = bullets[i].grid_x;
        uint8_t gy = bullets[i].grid_y;
        
        // Check current cell and adjacent cells
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                int cx = gx + dx;
                int cy = gy + dy;
                
                if (cx < 0 || cx >= SPATIAL_GRID_SIZE || cy < 0 || cy >= SPATIAL_GRID_SIZE) continue;
                
                uint16_t invader_mask = spatial_grid[cy][cx].invader_mask;
                
                for (int j = 0; j < invader_count && invader_mask; j++) {
                    if ((invader_mask & (1 << j)) && invaders[j].alive) {
                        if (check_collision(bullets[i].x, bullets[i].y, 2, 4,
                                          invaders[j].x, invaders[j].y, 
                                          invaders[j].width, invaders[j].height)) {
                            // Hit!
                            bullets[i].active = false;
                            active_bullets_mask &= ~(1 << i);
                            bullet_count--;
                            
                            invaders[j].alive = false;
                            invaders[j].needs_redraw = true;
                            alive_invaders_mask &= ~(1 << j);
                            
                            // Check win condition
                            bool any_alive = false;
                            for (int k = 0; k < invader_count; k++) {
                                if (invaders[k].alive) {
                                    any_alive = true;
                                    break;
                                }
                            }
                            if (!any_alive) {
                                win = true;
                            }
                            
                            invader_mask &= ~(1 << j);
                        }
                    }
                }
            }
        }
    }
    
    // Check bomb-player collisions
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            if (check_collision(bombs[i].x, bombs[i].y, 2, 4,
                              player.x, player.y, player.width, player.height)) {
                game_over = true;
            }
        }
    }
    
    // Check bomb-bunker and bullet-bunker collisions
    for (int b = 0; b < MAX_BUNKERS; b++) {
        // Bullets hitting bunkers
        for (int i = 0; i < MAX_BULLETS; i++) {
            if (bullets[i].active) {
                if (check_collision(bullets[i].x, bullets[i].y, 2, 4,
                                  bunkers[b].x, bunkers[b].y, bunkers[b].width, bunkers[b].height)) {
                    bullets[i].active = false;
                    active_bullets_mask &= ~(1 << i);
                    bullet_count--;
                    
                    // Damage bunker
                    int px = (int)((bullets[i].x - bunkers[b].x) * 5 / bunkers[b].width);
                    int py = (int)((bullets[i].y - bunkers[b].y) * 3 / bunkers[b].height);
                    if (px >= 0 && px < 5 && py >= 0 && py < 3) {
                        bunkers[b].pixels[py][px] = 0;
                        bunkers[b].needs_redraw = true;
                        bunkers[b].damage_hash = calculate_damage_hash(bunkers[b].pixels);
                    }
                }
            }
        }
        
        // Bombs hitting bunkers
        for (int i = 0; i < MAX_BOMBS; i++) {
            if (bombs[i].active) {
                if (check_collision(bombs[i].x, bombs[i].y, 2, 4,
                                  bunkers[b].x, bunkers[b].y, bunkers[b].width, bunkers[b].height)) {
                    bombs[i].active = false;
                    active_bombs_mask &= ~(1 << i);
                    bomb_count--;
                    
                    // Damage bunker
                    int px = (int)((bombs[i].x - bunkers[b].x) * 5 / bunkers[b].width);
                    int py = (int)((bombs[i].y - bunkers[b].y) * 3 / bunkers[b].height);
                    if (px >= 0 && px < 5 && py >= 0 && py < 3) {
                        bunkers[b].pixels[py][px] = 0;
                        bunkers[b].needs_redraw = true;
                        bunkers[b].damage_hash = calculate_damage_hash(bunkers[b].pixels);
                    }
                }
            }
        }
    }
}

// Handle input
void handle_input(void) {
    if (!gpio_get(BUTTON_A)) {  // Move left
        if (player.x > 0) {
            player.x -= player.speed;
            player.needs_redraw = true;
        }
    }
    
    if (!gpio_get(BUTTON_B)) {  // Move right
        if (player.x < WIDTH - player.width) {
            player.x += player.speed;
            player.needs_redraw = true;
        }
    }
    
    static bool x_pressed = false;
    if (!gpio_get(BUTTON_X)) {  // Fire
        if (!x_pressed) {
            fire_bullet();
            x_pressed = true;
        }
    } else {
        x_pressed = false;
    }
}

// Draw player optimised
void draw_player_optimised(Player* p) {
    if (!p->needs_redraw) return;
    
    graphics.set_pen(WHITE);
    graphics.rectangle(p->x, p->y, p->width, p->height);
    p->needs_redraw = false;
}

// Draw invader optimised
void draw_invader_optimised(Invader* inv) {
    if (!inv->alive) return;
    
    graphics.set_pen(inv->type->color);
    
    // Use pre-computed pixel positions for faster rendering
    int pixel_size = 3;
    for (uint8_t i = 0; i < inv->type->solid_pixel_count; i++) {
        int px = inv->x + inv->type->solid_pixels[i].x * pixel_size;
        int py = inv->y + inv->type->solid_pixels[i].y * pixel_size;
        graphics.rectangle(px, py, pixel_size, pixel_size);
    }
    
    inv->needs_redraw = false;
}

// Draw bunker optimised
void draw_bunker_optimised(Bunker* bunker) {
    if (!bunker->needs_redraw) return;
    
    graphics.set_pen(bunker->color);
    int pixel_size = 3;
    
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 5; x++) {
            if (bunker->pixels[y][x]) {
                int px = bunker->x + x * pixel_size;
                int py = bunker->y + y * pixel_size;
                graphics.rectangle(px, py, pixel_size, pixel_size);
            }
        }
    }
    
    bunker->needs_redraw = false;
}

// optimised game drawing
void draw_game_optimised(void) {
    // Clear screen
    graphics.set_pen(BLACK);
    graphics.clear();
    
    // Draw player
    draw_player_optimised(&player);
    
    // Draw invaders
    for (int i = 0; i < invader_count; i++) {
        draw_invader_optimised(&invaders[i]);
    }
    
    // Draw bunkers
    for (int i = 0; i < MAX_BUNKERS; i++) {
        draw_bunker_optimised(&bunkers[i]);
    }
    
    // Draw bullets
    graphics.set_pen(YELLOW);
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            graphics.rectangle(bullets[i].x, bullets[i].y, 2, 4);
        }
    }
    
    // Draw bombs
    graphics.set_pen(RED);
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            graphics.rectangle(bombs[i].x, bombs[i].y, 2, 4);
        }
    }
    
    // Draw game over/win messages
    if (game_over) {
        graphics.set_pen(RED);
        graphics.text("GAME OVER", Point(WIDTH/2 - 40, HEIGHT/2), 240);
    } else if (win) {
        graphics.set_pen(GREEN);
        graphics.text("YOU WIN!", Point(WIDTH/2 - 35, HEIGHT/2), 240);
    }
}

// Batch update game (optimisation placeholder)
void batch_update_game(void) {
    update_queue_size = 0;
    
    if (!game_over && !win) {
        handle_input();
        update_projectiles();
        update_invaders();
        optimized_collision_detection();
    }
    
    frame_count++;
}

// Main function
int main() {
    stdio_init_all();
    
    // Init display
    display.init();
    graphics.set_pen(BLACK);
    graphics.clear();
    display.update(&graphics);
    
    // Init GPIO buttons
    gpio_init(BUTTON_A);
    gpio_set_dir(BUTTON_A, GPIO_IN);
    gpio_pull_up(BUTTON_A);
    
    gpio_init(BUTTON_B);
    gpio_set_dir(BUTTON_B, GPIO_IN);
    gpio_pull_up(BUTTON_B);
    
    gpio_init(BUTTON_X);
    gpio_set_dir(BUTTON_X, GPIO_IN);
    gpio_pull_up(BUTTON_X);
    
    // Init game
    init_game();
    
    // Main game loop
    while (true) {
        batch_update_game();
        draw_game_optimised();
        display.update(&graphics);
        sleep_ms(33); // ~30 FPS
        
        // Reset game on game over or win
        if ((game_over || win) && !gpio_get(BUTTON_X)) {
            sleep_ms(500); // Debounce
            init_game();
        }
    }
    
    return 0;
}
