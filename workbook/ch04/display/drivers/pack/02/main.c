#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "engine.h"

// Game state using handles (safer than direct references)
typedef struct {
    sprite_handle_t player;
    sprite_handle_t enemies[4];
    sprite_handle_t bullets[8];
    particle_system_handle_t explosion_particles;
    
    texture_handle_t player_texture;
    texture_handle_t enemy_texture;
    texture_handle_t bullet_texture;
    
    float player_x, player_y;
    uint16_t score;
    uint32_t last_bullet_time;
    uint32_t enemy_spawn_timer;
    uint32_t last_input_time;  // For input debouncing
    bool game_running;
    bool game_over;
    
    // Error recovery
    uint32_t error_count;
    uint32_t last_error_time;
    
} game_state_t;

static game_state_t game = {0};

// Function prototypes
bool init_textures(void);
bool init_game_objects(void);
void update_game_logic(void);
void handle_input(void);
void spawn_enemy(void);
void fire_bullet(void);
void draw_ui(void);
void on_collision(sprite_handle_t sprite1, sprite_handle_t sprite2);
void cleanup_game(void);
bool validate_game_state(void);
void reset_game_state(void);

// Button callbacks
void button_a_callback(button_t button);
void button_b_callback(button_t button);
void button_x_callback(button_t button);
void button_y_callback(button_t button);

// Error handling
#define MAX_ERRORS_PER_MINUTE 10
static void report_error(const char* context) {
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    game.error_count++;
    printf("ERROR in %s (total: %lu)\n", context, game.error_count);
    
    // If too many errors in short time, trigger shutdown
    if (game.error_count > MAX_ERRORS_PER_MINUTE && 
        (now - game.last_error_time) < 60000) {
        printf("Too many errors detected, shutting down\n");
        game.game_running = false;
    }
    
    game.last_error_time = now;
}

int main() {
    stdio_init_all();
    printf("Robust Graphics Engine Demo Starting...\n");
    
    // Initialize random seed
    srand(to_ms_since_boot(get_absolute_time()));
    
    // Initialize engine
    engine_error_t result = engine_init();
    if (result != ENGINE_OK) {
        printf("Engine init failed: %s\n", engine_error_string(result));
        return 1;
    }
    
    // Initialize display controls
    display_error_t display_result = buttons_init();
    if (display_result != DISPLAY_OK) {
        printf("Button init failed: %s\n", display_error_string(display_result));
        engine_shutdown();
        return 1;
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, button_a_callback);
    button_set_callback(BUTTON_B, button_b_callback);
    button_set_callback(BUTTON_X, button_x_callback);
    button_set_callback(BUTTON_Y, button_y_callback);
    
    // Initialize game
    if (!init_textures()) {
        printf("Failed to initialize textures\n");
        cleanup_game();
        engine_shutdown();
        return 1;
    }
    
    if (!init_game_objects()) {
        printf("Failed to initialize game objects\n");
        cleanup_game();
        engine_shutdown();
        return 1;
    }
    
    // Set collision callback
    sprite_set_collision_callback(on_collision);
    
    printf("Game initialized successfully!\n");
    printf("Controls: A=Fire, B=Particles, X=Left, Y=Right\n");
    
    uint32_t frame_count = 0;
    uint32_t last_stats_time = 0;
    uint32_t last_validation_time = 0;
    
    // Clear initial framebuffer
    engine_render();
    engine_present();
    
    // Main game loop
    while (game.game_running) {
        uint32_t frame_start = to_ms_since_boot(get_absolute_time());
        
        // Periodic game state validation
        if (frame_start - last_validation_time > 5000) { // Every 5 seconds
            if (!validate_game_state()) {
                report_error("game state validation");
                reset_game_state();
            }
            last_validation_time = frame_start;
        }
        
        // Handle input with error protection
        buttons_update();
        handle_input();
        
        // Update game logic with error protection
        update_game_logic();
        
        // Update engine with error protection
        engine_update();
        
        // Check engine stats for anomalies
        const engine_stats_t* stats = engine_get_stats();
        if (stats->frame_time_ms > 100) { // Frame taking too long
            printf("Warning: Long frame time: %lu ms\n", stats->frame_time_ms);
        }
        
        // Render frame
        engine_render();
        
        // Draw UI overlay (with error protection)
        draw_ui();
        
        // Present frame
        engine_present();
        
        frame_count++;
        
        // Print stats every 2 seconds
        if (frame_start - last_stats_time >= 2000) {
            printf("Frame %lu: FPS=%d, Sprites=%d, Particles=%d, Score=%d, Errors=%lu\n",
                   frame_count, stats->fps, stats->sprite_count, 
                   stats->particle_count, game.score, game.error_count);
            last_stats_time = frame_start;
        }
        
        // Frame rate limiting (30 FPS target)
        uint32_t frame_end = to_ms_since_boot(get_absolute_time());
        uint32_t frame_time = frame_end - frame_start;
        
        // Safety check on frame time
        if (frame_time < 1000) { // Only sleep if frame time is reasonable
            if (frame_time < 33) {
                sleep_ms(33 - frame_time);
            }
        }
        
        // Exit conditions
        if (frame_count > 3600) {  // 2 minutes at 30fps
            printf("Demo time limit reached\n");
            game.game_running = false;
        }
        
        if (game.game_over) {
            printf("Game over condition reached\n");
            break;
        }
    }
    
    printf("Game ended. Final score: %d, Total frames: %lu\n", game.score, frame_count);
    
    // Cleanup
    cleanup_game();
    engine_shutdown();
    display_cleanup();
    
    return 0;
}

bool init_textures(void) {
    // Create player texture (8x8 blue square with white border)
    uint16_t* player_pixels = malloc(64 * sizeof(uint16_t));
    if (!player_pixels) {
        report_error("player texture allocation");
        return false;
    }
    
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            if (x == 0 || x == 7 || y == 0 || y == 7) {
                player_pixels[y * 8 + x] = ENGINE_COLOR_WHITE;
            } else {
                player_pixels[y * 8 + x] = ENGINE_COLOR_BLUE;
            }
        }
    }
    game.player_texture = texture_create(player_pixels, 8, 8, true);
    free(player_pixels); // Free temporary buffer
    
    if (game.player_texture == INVALID_HANDLE) {
        report_error("player texture creation");
        return false;
    }
    
    // Create enemy texture (6x6 red diamond)
    uint16_t* enemy_pixels = malloc(36 * sizeof(uint16_t));
    if (!enemy_pixels) {
        report_error("enemy texture allocation");
        return false;
    }
    
    for (int y = 0; y < 6; y++) {
        for (int x = 0; x < 6; x++) {
            int center_dist = abs(x - 3) + abs(y - 3);
            if (center_dist <= 2) {
                enemy_pixels[y * 6 + x] = ENGINE_COLOR_RED;
            } else {
                enemy_pixels[y * 6 + x] = 0x0000; // Transparent
            }
        }
    }
    game.enemy_texture = texture_create(enemy_pixels, 6, 6, true);
    free(enemy_pixels); // Free temporary buffer
    
    if (game.enemy_texture == INVALID_HANDLE) {
        report_error("enemy texture creation");
        return false;
    }
    
    // Create bullet texture (2x4 yellow rectangle)
    game.bullet_texture = texture_create_solid(ENGINE_COLOR_YELLOW, 2, 4);
    if (game.bullet_texture == INVALID_HANDLE) {
        report_error("bullet texture creation");
        return false;
    }
    
    printf("Textures created: Player=%d, Enemy=%d, Bullet=%d\n",
           game.player_texture, game.enemy_texture, game.bullet_texture);
    return true;
}

bool init_game_objects(void) {
    // Initialize game state safely
    game.player_x = DISPLAY_WIDTH / 2 - 4;
    game.player_y = DISPLAY_HEIGHT - 20;
    game.score = 0;
    game.game_running = true;
    game.game_over = false;
    game.last_bullet_time = 0;
    game.enemy_spawn_timer = 0;
    game.last_input_time = 0;
    game.error_count = 0;
    game.last_error_time = 0;
    
    // Create player sprite
    game.player = sprite_create(game.player_x, game.player_y, game.player_texture);
    if (game.player == INVALID_HANDLE) {
        report_error("player sprite creation");
        return false;
    }
    
    sprite_set_layer(game.player, 2);
    sprite_enable_collision(game.player, true);
    
    // Initialize enemy handles
    for (int i = 0; i < 4; i++) {
        game.enemies[i] = INVALID_HANDLE;
    }
    
    // Initialize bullet handles
    for (int i = 0; i < 8; i++) {
        game.bullets[i] = INVALID_HANDLE;
    }
    
    // Create particle system for explosions
    game.explosion_particles = particles_create(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2, ENGINE_COLOR_YELLOW);
    if (game.explosion_particles == INVALID_HANDLE) {
        report_error("particle system creation");
        return false;
    }
    
    particles_set_spawn_rate(game.explosion_particles, 0); // Manual emission only
    particles_set_lifetime(game.explosion_particles, 1500);
    particles_set_spawn_radius(game.explosion_particles, 10.0f);
    
    printf("Game objects initialized\n");
    return true;
}

void update_game_logic(void) {
    if (game.game_over) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    const engine_stats_t* stats = engine_get_stats();
    
    // Validate player sprite
    if (!sprite_is_valid(game.player)) {
        report_error("invalid player sprite");
        game.game_over = true;
        return;
    }
    
    // Update player position
    sprite_set_position(game.player, game.player_x, game.player_y);
    
    // Spawn enemies periodically
    game.enemy_spawn_timer += stats->frame_time_ms;
    if (game.enemy_spawn_timer > 1500) {  // Every 1.5 seconds
        spawn_enemy();
        game.enemy_spawn_timer = 0;
    }
    
    // Update enemies - move them down
    for (int i = 0; i < 4; i++) {
        if (game.enemies[i] != INVALID_HANDLE) {
            if (!sprite_is_valid(game.enemies[i])) {
                // Handle corrupted sprite
                game.enemies[i] = INVALID_HANDLE;
                continue;
            }
            
            sprite_set_velocity(game.enemies[i], 0, 1.0f);
            
            // Remove enemies that go off screen
            float x, y;
            sprite_get_position(game.enemies[i], &x, &y);
            if (y > DISPLAY_HEIGHT + 10) {
                sprite_destroy(game.enemies[i]);
                game.enemies[i] = INVALID_HANDLE;
            }
        }
    }
    
    // Update bullets - move them up
    for (int i = 0; i < 8; i++) {
        if (game.bullets[i] != INVALID_HANDLE) {
            if (!sprite_is_valid(game.bullets[i])) {
                // Handle corrupted sprite
                game.bullets[i] = INVALID_HANDLE;
                continue;
            }
            
            sprite_set_velocity(game.bullets[i], 0, -4.0f);
            
            // Remove bullets that go off screen
            float x, y;
            sprite_get_position(game.bullets[i], &x, &y);
            if (y < -10) {
                sprite_destroy(game.bullets[i]);
                game.bullets[i] = INVALID_HANDLE;
            }
        }
    }
    
    // Simple camera follow (with bounds)
    float cam_target_x = game.player_x - (DISPLAY_WIDTH / 2);
    float cam_target_y = game.player_y - (DISPLAY_HEIGHT / 2);
    
    // Clamp camera to reasonable bounds
    if (cam_target_x < -50) cam_target_x = -50;
    if (cam_target_x > 50) cam_target_x = 50;
    if (cam_target_y < -50) cam_target_y = -50;
    if (cam_target_y > 50) cam_target_y = 50;
    
    camera_set_position(cam_target_x, cam_target_y);
}

void handle_input(void) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Input rate limiting
    if (current_time - game.last_input_time < 16) return; // ~60Hz max
    
    // Continuous movement with bounds checking
    if (button_pressed(BUTTON_X) && game.player_x > 8) {
        game.player_x -= 2.0f;
        if (game.player_x < 0) game.player_x = 0;
    }
    if (button_pressed(BUTTON_Y) && game.player_x < DISPLAY_WIDTH - 16) {
        game.player_x += 2.0f;
        if (game.player_x > DISPLAY_WIDTH - 8) game.player_x = DISPLAY_WIDTH - 8;
    }
    
    game.last_input_time = current_time;
}

void spawn_enemy(void) {
    // Find empty slot
    for (int i = 0; i < 4; i++) {
        if (game.enemies[i] == INVALID_HANDLE) {
            float x = (float)(rand() % (DISPLAY_WIDTH - 20)) + 10;
            game.enemies[i] = sprite_create(x, -10, game.enemy_texture);
            
            if (game.enemies[i] == INVALID_HANDLE) {
                report_error("enemy sprite creation");
                return;
            }
            
            sprite_set_layer(game.enemies[i], 1);
            sprite_enable_collision(game.enemies[i], true);
            printf("Enemy spawned at x=%.1f\n", x);
            break;
        }
    }
}

void fire_bullet(void) {
    if (game.game_over) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Rate limiting
    if (current_time - game.last_bullet_time < 250) return;
    
    // Find empty slot
    for (int i = 0; i < 8; i++) {
        if (game.bullets[i] == INVALID_HANDLE) {
            game.bullets[i] = sprite_create(game.player_x + 3, game.player_y - 5, game.bullet_texture);
            
            if (game.bullets[i] == INVALID_HANDLE) {
                report_error("bullet sprite creation");
                return;
            }
            
            sprite_set_layer(game.bullets[i], 1);
            sprite_enable_collision(game.bullets[i], true);
            game.last_bullet_time = current_time;
            printf("Bullet fired\n");
            break;
        }
    }
}

void draw_ui(void) {
    // Draw score and stats directly to display (bypassing engine)
    char text[64];
    
    // Bounds check for score
    if (game.score > 999999) game.score = 999999;
    
    snprintf(text, sizeof(text), "Score: %d", game.score);
    display_error_t result = display_draw_string(5, 5, text, COLOR_WHITE, COLOR_BLACK);
    if (result != DISPLAY_OK) {
        // Don't report this as critical error, just skip UI updates
        return;
    }
    
    const engine_stats_t* stats = engine_get_stats();
    snprintf(text, sizeof(text), "FPS: %d", stats ? stats->fps : 0);
    display_draw_string(5, 20, text, COLOR_YELLOW, COLOR_BLACK);
    
    // Controls
    display_draw_string(5, DISPLAY_HEIGHT - 35, "X/Y: Move", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(5, DISPLAY_HEIGHT - 20, "A: Fire  B: Boom", COLOR_CYAN, COLOR_BLACK);
    
    // Game over message
    if (game.game_over) {
        display_draw_string(DISPLAY_WIDTH/2 - 30, DISPLAY_HEIGHT/2, "GAME OVER", COLOR_RED, COLOR_BLACK);
    }
    
    // Simple HUD elements using engine primitives
    graphics_draw_rect(2, 2, DISPLAY_WIDTH - 4, DISPLAY_HEIGHT - 4, ENGINE_COLOR_WHITE);
}

void on_collision(sprite_handle_t sprite1, sprite_handle_t sprite2) {
    // Validate sprite handles
    if (!sprite_is_valid(sprite1) || !sprite_is_valid(sprite2)) {
        return;
    }
    
    // Check player-enemy collision
    if (sprite1 == game.player || sprite2 == game.player) {
        printf("Player hit! Game Over. Final Score: %d\n", game.score);
        
        // Create explosion at player position
        particles_set_position(game.explosion_particles, game.player_x, game.player_y);
        particles_emit_burst(game.explosion_particles, 30);
        
        game.game_over = true;
        return;
    }
    
    // Check bullet-enemy collisions
    for (int b = 0; b < 8; b++) {
        if (game.bullets[b] == INVALID_HANDLE) continue;
        
        if (game.bullets[b] == sprite1 || game.bullets[b] == sprite2) {
            // This is a bullet collision
            for (int e = 0; e < 4; e++) {
                if (game.enemies[e] == INVALID_HANDLE) continue;
                
                if (game.enemies[e] == sprite1 || game.enemies[e] == sprite2) {
                    // Bullet hit enemy!
                    float enemy_x, enemy_y;
                    sprite_get_position(game.enemies[e], &enemy_x, &enemy_y);
                    
                    // Create explosion at enemy position
                    particles_set_position(game.explosion_particles, enemy_x + 3, enemy_y + 3);
                    particles_emit_burst(game.explosion_particles, 15);
                    
                    // Destroy both sprites
                    sprite_destroy(game.bullets[b]);
                    sprite_destroy(game.enemies[e]);
                    
                    // Clear handles
                    game.bullets[b] = INVALID_HANDLE;
                    game.enemies[e] = INVALID_HANDLE;
                    
                    // Update score safely
                    if (game.score < 999900) {  // Prevent overflow
                        game.score += 100;
                    }
                    printf("Enemy destroyed! Score: %d\n", game.score);
                    return;
                }
            }
        }
    }
}

bool validate_game_state(void) {
    // Check player sprite
    if (game.player != INVALID_HANDLE && !sprite_is_valid(game.player)) {
        printf("Invalid player sprite detected\n");
        return false;
    }
    
    // Check position bounds
    if (game.player_x < -100 || game.player_x > DISPLAY_WIDTH + 100 ||
        game.player_y < -100 || game.player_y > DISPLAY_HEIGHT + 100) {
        printf("Player position out of bounds: %.1f, %.1f\n", game.player_x, game.player_y);
        return false;
    }
    
    // Check score bounds
    if (game.score > 1000000) {
        printf("Score overflow detected: %d\n", game.score);
        return false;
    }
    
    // Count active enemies and bullets
    int active_enemies = 0, active_bullets = 0;
    for (int i = 0; i < 4; i++) {
        if (game.enemies[i] != INVALID_HANDLE) {
            if (sprite_is_valid(game.enemies[i])) {
                active_enemies++;
            } else {
                game.enemies[i] = INVALID_HANDLE; // Clean up
            }
        }
    }
    
    for (int i = 0; i < 8; i++) {
        if (game.bullets[i] != INVALID_HANDLE) {
            if (sprite_is_valid(game.bullets[i])) {
                active_bullets++;
            } else {
                game.bullets[i] = INVALID_HANDLE; // Clean up
            }
        }
    }
    
    return true;
}

void reset_game_state(void) {
    printf("Resetting game state\n");
    
    // Clear all sprites safely
    for (int i = 0; i < 4; i++) {
        if (game.enemies[i] != INVALID_HANDLE) {
            sprite_destroy(game.enemies[i]);
            game.enemies[i] = INVALID_HANDLE;
        }
    }
    
    for (int i = 0; i < 8; i++) {
        if (game.bullets[i] != INVALID_HANDLE) {
            sprite_destroy(game.bullets[i]);
            game.bullets[i] = INVALID_HANDLE;
        }
    }
    
    // Reset player position
    game.player_x = DISPLAY_WIDTH / 2 - 4;
    game.player_y = DISPLAY_HEIGHT - 20;
    
    if (sprite_is_valid(game.player)) {
        sprite_set_position(game.player, game.player_x, game.player_y);
    }
    
    // Reset timers
    game.enemy_spawn_timer = 0;
    game.last_bullet_time = 0;
}

void cleanup_game(void) {
    printf("Cleaning up game resources\n");
    
    // Destroy all sprites
    if (game.player != INVALID_HANDLE) {
        sprite_destroy(game.player);
    }
    
    for (int i = 0; i < 4; i++) {
        if (game.enemies[i] != INVALID_HANDLE) {
            sprite_destroy(game.enemies[i]);
        }
    }
    
    for (int i = 0; i < 8; i++) {
        if (game.bullets[i] != INVALID_HANDLE) {
            sprite_destroy(game.bullets[i]);
        }
    }
    
    // Destroy particle system
    if (game.explosion_particles != INVALID_HANDLE) {
        particles_destroy(game.explosion_particles);
    }
    
    // Destroy textures
    if (game.player_texture != INVALID_HANDLE) {
        texture_destroy(game.player_texture);
    }
    if (game.enemy_texture != INVALID_HANDLE) {
        texture_destroy(game.enemy_texture);
    }
    if (game.bullet_texture != INVALID_HANDLE) {
        texture_destroy(game.bullet_texture);
    }
}

// Button callback implementations
void button_a_callback(button_t button) {
    fire_bullet();
}

void button_b_callback(button_t button) {
    if (game.game_over) return;
    
    // Create particle explosion at player position
    particles_set_position(game.explosion_particles, game.player_x + 4, game.player_y + 4);
    particles_emit_burst(game.explosion_particles, 25);
    printf("Particle explosion!\n");
}

void button_x_callback(button_t button) {
    // Movement handled in continuous input
}

void button_y_callback(button_t button) {
    // Movement handled in continuous input
}
