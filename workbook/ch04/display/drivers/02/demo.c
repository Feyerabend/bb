#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "pico/stdlib.h"
#include "engine.h"

// Demo sprites and textures
static uint16_t player_texture[16*16];
static uint16_t enemy_texture[16*16];
static uint16_t bullet_texture[4*4];
static uint16_t tileset_texture[128*128]; // 8x8 tiles, 16x16 grid

// Game state
typedef struct {
    uint8_t player_sprite;
    uint8_t enemies[8];
    uint8_t bullets[16];
    uint8_t particle_system;
    uint8_t tilemap;
    
    int16_t player_x, player_y;
    uint32_t last_bullet_time;
    uint32_t enemy_spawn_timer;
    
    uint16_t score;
    bool game_running;
} game_state_t;

static game_state_t game = {0};

// Function prototypes
void create_textures(void);
void init_game(void);
void update_game(void);
void handle_input(void);
void spawn_enemy(void);
void fire_bullet(void);
void draw_ui(void);
void button_a_callback(button_t button);
void button_b_callback(button_t button);
void button_x_callback(button_t button);
void button_y_callback(button_t button);

int main() {
    stdio_init_all();
    printf("Graphics Engine Demo Starting...\n");
    
    // Initialize display and graphics engine
    if (!graphics_engine_init()) {
        printf("Failed to initialize graphics engine!\n");
        return 1;
    }
    
    // Initialize buttons
    buttons_init();
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Create textures and initialize game
    create_textures();
    init_game();
    
    printf("Graphics Engine Demo Started!\n");
    printf("Controls: A=Fire, B=Particles, X=Move Left, Y=Move Right\n");
    
    uint32_t frame_count = 0;
    
    // Main game loop
    while (game.game_running) {
        uint32_t frame_start = to_ms_since_boot(get_absolute_time());
        
        // Update button states
        buttons_update();
        
        // Handle input
        handle_input();
        
        // Update game logic
        update_game();
        
        // Update graphics engine
        graphics_engine_update();
        
        // Render frame
        graphics_engine_render();
        
        // Draw UI elements
        draw_ui();
        
        // Present frame
        graphics_engine_present();
        
        frame_count++;
        
        // Print performance stats every 60 frames
        if (frame_count % 60 == 0) {
            printf("FPS: %d, Frame Time: %lu ms\n", 
                   graphics_get_fps(), graphics_get_frame_time());
        }
        
        // Target 30 FPS
        uint32_t frame_end = to_ms_since_boot(get_absolute_time());
        uint32_t frame_time = frame_end - frame_start;
        if (frame_time < 33) {
            sleep_ms(33 - frame_time);
        }
    }
    
    printf("Game ended. Final score: %d\n", game.score);
    graphics_engine_shutdown();
    return 0;
}

void create_textures(void) {
    // Create player texture (blue square with white outline)
    for (int y = 0; y < 16; y++) {
        for (int x = 0; x < 16; x++) {
            if (x == 0 || x == 15 || y == 0 || y == 15) {
                player_texture[y * 16 + x] = COLOR_WHITE;
            } else {
                player_texture[y * 16 + x] = COLOR_BLUE;
            }
        }
    }
    
    // Create enemy texture (red triangle-ish shape)
    for (int y = 0; y < 16; y++) {
        for (int x = 0; x < 16; x++) {
            if ((x >= y/2 && x <= 16 - y/2) && y < 12) {
                enemy_texture[y * 16 + x] = COLOR_RED;
            } else {
                enemy_texture[y * 16 + x] = 0x0000; // Transparent
            }
        }
    }
    
    // Create bullet texture (small yellow square)
    for (int y = 0; y < 4; y++) {
        for (int x = 0; x < 4; x++) {
            bullet_texture[y * 4 + x] = COLOR_YELLOW;
        }
    }
    
    // Create a simple tileset (grass, stone, water)
    for (int ty = 0; ty < 16; ty++) {
        for (int tx = 0; tx < 16; tx++) {
            for (int py = 0; py < 8; py++) {
                for (int px = 0; px < 8; px++) {
                    int idx = (ty * 8 + py) * 128 + (tx * 8 + px);
                    
                    if (tx == 0 && ty == 0) {
                        // Grass tile
                        tileset_texture[idx] = COLOR_GREEN;
                    } else if (tx == 1 && ty == 0) {
                        // Stone tile
                        tileset_texture[idx] = rgb_to_rgb565(128, 128, 128);
                    } else if (tx == 2 && ty == 0) {
                        // Water tile
                        tileset_texture[idx] = rgb_to_rgb565(0, 100, 200);
                    } else {
                        // Empty/transparent
                        tileset_texture[idx] = 0x0000;
                    }
                }
            }
        }
    }
}

void init_game(void) {
    // Create player sprite
    game.player_sprite = sprite_create(112, 100, 16, 16);
    sprite_set_texture(game.player_sprite, player_texture, 16, 16);
    sprite_set_layer(game.player_sprite, 2); // Front layer
    sprite_enable_collision(game.player_sprite, true);
    
    game.player_x = 112;
    game.player_y = 100;
    
    // Initialize enemy array
    for (int i = 0; i < 8; i++) {
        game.enemies[i] = 255; // Invalid ID = not active
    }
    
    // Initialize bullet array
    for (int i = 0; i < 16; i++) {
        game.bullets[i] = 255; // Invalid ID = not active
    }
    
    // Create particle system
    game.particle_system = particle_system_create(120, 67, COLOR_CYAN, 10);
    
    // Create a simple background tilemap
    game.tilemap = tilemap_create(0, 30, 17, 0); // Background layer
    if (game.tilemap != 255) {
        // Fill with a pattern
        for (int y = 0; y < 17; y++) {
            for (int x = 0; x < 30; x++) {
                uint8_t tile = 1; // Grass by default
                if (y == 0 || y == 16) tile = 2; // Stone borders
                if (x == 0 || x == 29) tile = 2;
                if ((x + y) % 7 == 0) tile = 3; // Water spots
                
                tilemap_set_tile(game.tilemap, x, y, tile);
            }
        }
    }
    
    game.score = 0;
    game.game_running = true;
    game.enemy_spawn_timer = 0;
    
    printf("Game initialized\n");
}

void update_game(void) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Update player position
    sprite_set_position(game.player_sprite, game.player_x, game.player_y);
    
    // Spawn enemies periodically
    game.enemy_spawn_timer += graphics_get_frame_time();
    if (game.enemy_spawn_timer > 2000) { // Every 2 seconds
        spawn_enemy();
        game.enemy_spawn_timer = 0;
    }
    
    // Update enemy positions
    for (int i = 0; i < 8; i++) {
        if (game.enemies[i] != 255) {
            // Move enemies down
            sprite_set_velocity(game.enemies[i], 0, 1);
            
            // Remove enemies that go off screen
            // Note: In a real implementation, you'd check sprite position
        }
    }
    
    // Update bullet positions
    for (int i = 0; i < 16; i++) {
        if (game.bullets[i] != 255) {
            sprite_set_velocity(game.bullets[i], 0, -3); // Move up
            
            // Remove bullets that go off screen
            // Note: In a real implementation, you'd check sprite position
        }
    }
    
    // Check collisions
    uint8_t collision_count;
    collision_event_t* collisions = get_collision_events(&collision_count);
    
    for (int i = 0; i < collision_count; i++) {
        uint8_t id1 = collisions[i].id1;
        uint8_t id2 = collisions[i].id2;
        
        // Check if player hit enemy
        if (id1 == game.player_sprite || id2 == game.player_sprite) {
            printf("Player hit! Game Over. Score: %d\n", game.score);
            game.game_running = false;
        }
        
        // Check bullet-enemy collisions
        bool bullet_hit = false;
        for (int b = 0; b < 16; b++) {
            if (game.bullets[b] == id1 || game.bullets[b] == id2) {
                for (int e = 0; e < 8; e++) {
                    if (game.enemies[e] == id1 || game.enemies[e] == id2) {
                        // Bullet hit enemy
                        sprite_destroy(game.bullets[b]);
                        sprite_destroy(game.enemies[e]);
                        game.bullets[b] = 255;
                        game.enemies[e] = 255;
                        game.score += 10;
                        bullet_hit = true;
                        
                        // Create particle explosion
                        particle_system_set_position(game.particle_system, 
                                                    game.player_x + 8, game.player_y);
                        printf("Enemy destroyed! Score: %d\n", game.score);
                        break;
                    }
                }
                if (bullet_hit) break;
            }
        }
    }
    
    // Update camera to follow player (with some offset)
    camera_set_position(game.player_x - 120, game.player_y - 67);
}

void handle_input(void) {
    // Continuous movement based on button state
    if (button_pressed(BUTTON_X) && game.player_x > 8) {
        game.player_x -= 2;
    }
    if (button_pressed(BUTTON_Y) && game.player_x < DISPLAY_WIDTH - 24) {
        game.player_x += 2;
    }
    
    // Firing is handled in button callbacks for single-press events
}

void spawn_enemy(void) {
    // Find empty enemy slot
    for (int i = 0; i < 8; i++) {
        if (game.enemies[i] == 255) {
            int16_t x = rand() % (DISPLAY_WIDTH - 16);
            game.enemies[i] = sprite_create(x, -16, 16, 16);
            sprite_set_texture(game.enemies[i], enemy_texture, 16, 16);
            sprite_set_layer(game.enemies[i], 1);
            sprite_enable_collision(game.enemies[i], true);
            printf("Enemy spawned at x=%d\n", x);
            break;
        }
    }
}

void fire_bullet(void) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Rate limiting
    if (current_time - game.last_bullet_time < 200) return;
    
    // Find empty bullet slot
    for (int i = 0; i < 16; i++) {
        if (game.bullets[i] == 255) {
            game.bullets[i] = sprite_create(game.player_x + 6, game.player_y - 4, 4, 4);
            sprite_set_texture(game.bullets[i], bullet_texture, 4, 4);
            sprite_set_layer(game.bullets[i], 1);
            sprite_enable_collision(game.bullets[i], true);
            game.last_bullet_time = current_time;
            printf("Bullet fired\n");
            break;
        }
    }
}

void draw_ui(void) {
    // Draw score
    char score_text[32];
    snprintf(score_text, sizeof(score_text), "Score: %d", game.score);
    display_draw_string(10, 10, score_text, COLOR_WHITE, COLOR_BLACK);
    
    // Draw FPS
    char fps_text[16];
    snprintf(fps_text, sizeof(fps_text), "FPS: %d", graphics_get_fps());
    display_draw_string(10, 25, fps_text, COLOR_YELLOW, COLOR_BLACK);
    
    // Draw instructions
    display_draw_string(10, DISPLAY_HEIGHT - 40, "X/Y: Move", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(10, DISPLAY_HEIGHT - 25, "A: Fire  B: Particles", COLOR_CYAN, COLOR_BLACK);
    
    // Draw simple crosshair at center
    graphics_draw_line(DISPLAY_WIDTH/2 - 5, DISPLAY_HEIGHT/2, 
                      DISPLAY_WIDTH/2 + 5, DISPLAY_HEIGHT/2, COLOR_WHITE);
    graphics_draw_line(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2 - 5, 
                      DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2 + 5, COLOR_WHITE);
}

// Button callbacks
void button_a_callback(button_t button) {
    fire_bullet();
}

void button_b_callback(button_t button) {
    // Trigger particle effect at player position
    particle_system_set_position(game.particle_system, game.player_x + 8, game.player_y + 8);
    printf("Particle effect triggered\n");
}

void button_x_callback(button_t button) {
    // Movement is handled in continuous input check
    printf("Moving left\n");
}

void button_y_callback(button_t button) {
    // Movement is handled in continuous input check  
    printf("Moving right\n");
}