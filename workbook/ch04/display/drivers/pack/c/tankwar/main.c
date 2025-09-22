#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "pico/time.h"
#include "display.h"

// Game constants - landscape mode (240x135) ~ failed with portrait (135x240)
#define GAME_WIDTH DISPLAY_WIDTH    // 240
#define GAME_HEIGHT DISPLAY_HEIGHT  // 135
#define CANNON_WIDTH 16
#define CANNON_HEIGHT 8
#define CANNON_Y (GAME_HEIGHT - CANNON_HEIGHT - 2)  // Near bottom but not at edge
#define PROJECTILE_WIDTH 3
#define PROJECTILE_HEIGHT 6
#define ENEMY_WIDTH 18
#define ENEMY_HEIGHT 10
#define ENEMY_Y 20   // Adjusted for shorter height
#define MAX_PROJECTILES 8
#define MAX_ENEMY_PROJECTILES 5
#define PROJECTILE_SPEED 4
#define ENEMY_PROJECTILE_SPEED 3
#define ENEMY_SPEED 1

// Game structures
typedef struct {
    float x, y;
    bool active;
    bool is_enemy;
} Projectile;

typedef struct {
    float x, y;
    int direction;  // -1 left, 1 right
    int health;
    uint32_t last_shot_time;
    uint32_t last_move_time;
    bool moving_to_avoid;
    float target_x;
} Enemy;

typedef struct {
    float x;
    int lives;
    int score;
    uint32_t last_shot_time;
} Cannon;

// Game state
static Cannon cannon;
static Enemy enemy;
static Projectile projectiles[MAX_PROJECTILES];
static Projectile enemy_projectiles[MAX_ENEMY_PROJECTILES];
static bool game_running = true;
static bool game_over = false;
static uint32_t last_frame_time = 0;
static char score_text[32];

// Init game state
void game_init(void) {
    // Init cannon at bottom center
    cannon.x = GAME_WIDTH / 2 - CANNON_WIDTH / 2;
    cannon.lives = 3;
    cannon.score = 0;
    cannon.last_shot_time = 0;
    
    // Init enemy at top
    enemy.x = GAME_WIDTH / 2 - ENEMY_WIDTH / 2;
    enemy.y = ENEMY_Y;
    enemy.direction = 1;
    enemy.health = 3;
    enemy.last_shot_time = 0;
    enemy.last_move_time = 0;
    enemy.moving_to_avoid = false;
    enemy.target_x = enemy.x;
    
    // Init projectiles
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        projectiles[i].active = false;
    }
    for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
        enemy_projectiles[i].active = false;
    }
    
    game_running = true;
    game_over = false;
}

// Shoot function
void shoot_projectile(void) {
    if (!game_running) return;
    
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    // Shoot projectile upward (with cooldown)
    if (now - cannon.last_shot_time > 200) {
        for (int i = 0; i < MAX_PROJECTILES; i++) {
            if (!projectiles[i].active) {
                projectiles[i].x = cannon.x + CANNON_WIDTH / 2 - PROJECTILE_WIDTH / 2;
                projectiles[i].y = CANNON_Y - PROJECTILE_HEIGHT;
                projectiles[i].active = true;
                projectiles[i].is_enemy = false;
                cannon.last_shot_time = now;
                break;
            }
        }
    }
}

// Handle movement and shooting with combo detection
void handle_game_controls(void) {
    if (game_over) return;
    if (!game_running) return;
    
    // Check if both B and Y are pressed for shooting
    bool b_pressed = button_pressed(BUTTON_B);
    bool y_pressed = button_pressed(BUTTON_Y);
    
    if (b_pressed && y_pressed) {
        // Both buttons pressed = SHOOT
        shoot_projectile();
        return; // Don't process movement when shooting
    }
    
    // Single button presses for movement
    if (button_just_pressed(BUTTON_B) && !y_pressed) {
        // B alone = Move LEFT
        cannon.x -= 8;
        if (cannon.x < 0) cannon.x = 0;
    }
    
    if (button_just_pressed(BUTTON_Y) && !b_pressed) {
        // Y alone = Move RIGHT
        cannon.x += 8;
        if (cannon.x > GAME_WIDTH - CANNON_WIDTH) {
            cannon.x = GAME_WIDTH - CANNON_WIDTH;
        }
    }
}

// Button callbacks - Handle game reset only
void on_button_a(button_t button) {
    if (game_over) {
        game_init();
    }
}

void on_button_b(button_t button) {
    if (game_over) {
        game_init();
    }
    // Movement handled in handle_game_controls()
}

void on_button_x(button_t button) {
    if (game_over) {
        game_init();
    }
}

void on_button_y(button_t button) {
    if (game_over) {
        game_init();
    }
    // Movement handled in handle_game_controls()
}

// Check collision between two rectangles
bool check_collision(float x1, float y1, float w1, float h1,
                    float x2, float y2, float w2, float h2) {
    return (x1 < x2 + w2 && x1 + w1 > x2 &&
            y1 < y2 + h2 && y1 + h1 > y2);
}

// Update enemy AI
void update_enemy(uint32_t current_time) {
    // AI: move horizontally and try to avoid player projectiles
    
    // Check if there are incoming projectiles to avoid
    bool should_avoid = false;
    float closest_projectile_x = -1;
    
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        if (projectiles[i].active && 
            projectiles[i].y < enemy.y + 40 && // Adjusted for shorter height
            fabs(projectiles[i].x - (enemy.x + ENEMY_WIDTH/2)) < 30) {
            should_avoid = true;
            closest_projectile_x = projectiles[i].x;
            break;
        }
    }
    
    // Movement logic
    if (current_time - enemy.last_move_time > 300) {
        if (should_avoid) {
            // Move away from incoming projectile
            if (closest_projectile_x < enemy.x + ENEMY_WIDTH/2) {
                enemy.direction = 1; // Move right
            } else {
                enemy.direction = -1; // Move left
            }
            enemy.moving_to_avoid = true;
        } else if (!enemy.moving_to_avoid) {
            // Random movement when not avoiding
            if (rand() % 100 < 30) { // 30% chance to change direction
                enemy.direction = -enemy.direction;
            }
        } else {
            // Occasionally stop avoiding
            if (rand() % 100 < 50) {
                enemy.moving_to_avoid = false;
            }
        }
        
        enemy.last_move_time = current_time;
    }
    
    // Move enemy horizontally
    enemy.x += enemy.direction * ENEMY_SPEED;
    
    // Bounce off walls
    if (enemy.x <= 0) {
        enemy.x = 0;
        enemy.direction = 1;
    } else if (enemy.x >= GAME_WIDTH - ENEMY_WIDTH) {
        enemy.x = GAME_WIDTH - ENEMY_WIDTH;
        enemy.direction = -1;
    }
    
    // Enemy shooting downward
    if (current_time - enemy.last_shot_time > 1500 + (rand() % 1000)) {
        for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
            if (!enemy_projectiles[i].active) {
                enemy_projectiles[i].x = enemy.x + ENEMY_WIDTH / 2 - PROJECTILE_WIDTH / 2;
                enemy_projectiles[i].y = enemy.y + ENEMY_HEIGHT;
                enemy_projectiles[i].active = true;
                enemy_projectiles[i].is_enemy = true;
                enemy.last_shot_time = current_time;
                break;
            }
        }
    }
}

// Update projectiles
void update_projectiles(void) {
    // Update player projectiles (moving upward)
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        if (projectiles[i].active) {
            projectiles[i].y -= PROJECTILE_SPEED; // Move up
            
            // Remove if off screen (top)
            if (projectiles[i].y < -PROJECTILE_HEIGHT) {
                projectiles[i].active = false;
                continue;
            }
            
            // Check collision with enemy
            if (check_collision(projectiles[i].x, projectiles[i].y, 
                              PROJECTILE_WIDTH, PROJECTILE_HEIGHT,
                              enemy.x, enemy.y, ENEMY_WIDTH, ENEMY_HEIGHT)) {
                projectiles[i].active = false;
                enemy.health--;
                cannon.score += 10;
                
                if (enemy.health <= 0) {
                    // Enemy defeated, respawn with more health
                    cannon.score += 50;
                    enemy.health = 3 + (cannon.score / 200); // Increase health over time
                    enemy.x = rand() % (GAME_WIDTH - ENEMY_WIDTH);
                    // Add some visual feedback time
                    enemy.last_shot_time = to_ms_since_boot(get_absolute_time()) + 500;
                }
            }
        }
    }
    
    // Update enemy projectiles (moving downward)
    for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
        if (enemy_projectiles[i].active) {
            enemy_projectiles[i].y += ENEMY_PROJECTILE_SPEED; // Move down
            
            // Remove if off screen (bottom)
            if (enemy_projectiles[i].y > GAME_HEIGHT) {
                enemy_projectiles[i].active = false;
                continue;
            }
            
            // Check collision with cannon
            if (check_collision(enemy_projectiles[i].x, enemy_projectiles[i].y,
                              PROJECTILE_WIDTH, PROJECTILE_HEIGHT,
                              cannon.x, CANNON_Y, CANNON_WIDTH, CANNON_HEIGHT)) {
                enemy_projectiles[i].active = false;
                cannon.lives--;
                
                if (cannon.lives <= 0) {
                    game_over = true;
                    game_running = false;
                }
            }
        }
    }
}

// Draw game objects
void draw_cannon(void) {
    // Draw cannon body
    display_fill_rect(cannon.x, CANNON_Y, CANNON_WIDTH, CANNON_HEIGHT, COLOR_GREEN);
    
    // Draw barrel pointing up
    display_fill_rect(cannon.x + CANNON_WIDTH/2 - 2, CANNON_Y - 8, 4, 8, COLOR_GREEN);
    
    // Draw tank treads
    display_fill_rect(cannon.x, CANNON_Y + CANNON_HEIGHT - 2, CANNON_WIDTH, 2, COLOR_YELLOW);
}

void draw_enemy(void) {
    // Draw enemy with different colors based on health
    uint16_t color = COLOR_RED;
    if (enemy.health > 3) color = COLOR_MAGENTA;
    else if (enemy.health > 2) color = COLOR_YELLOW;
    else if (enemy.health > 1) color = COLOR_CYAN;
    
    // Draw enemy body
    display_fill_rect(enemy.x, enemy.y, ENEMY_WIDTH, ENEMY_HEIGHT, color);
    
    // Draw barrel pointing down
    display_fill_rect(enemy.x + ENEMY_WIDTH/2 - 2, enemy.y + ENEMY_HEIGHT, 4, 6, color);
    
    // Draw enemy details
    display_fill_rect(enemy.x + 2, enemy.y + 2, ENEMY_WIDTH - 4, 2, COLOR_WHITE);
}

void draw_projectiles(void) {
    // Draw player projectiles (moving up) - bright cyan
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        if (projectiles[i].active) {
            display_fill_rect(projectiles[i].x, projectiles[i].y, 
                            PROJECTILE_WIDTH, PROJECTILE_HEIGHT, COLOR_CYAN);
            // Add a trail effect
            display_fill_rect(projectiles[i].x, projectiles[i].y + PROJECTILE_HEIGHT, 
                            PROJECTILE_WIDTH, 2, COLOR_BLUE);
        }
    }
    
    // Draw enemy projectiles (moving down) - bright red
    for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
        if (enemy_projectiles[i].active) {
            display_fill_rect(enemy_projectiles[i].x, enemy_projectiles[i].y,
                            PROJECTILE_WIDTH, PROJECTILE_HEIGHT, COLOR_RED);
            // Add a trail effect
            display_fill_rect(enemy_projectiles[i].x, enemy_projectiles[i].y - 2, 
                            PROJECTILE_WIDTH, 2, COLOR_MAGENTA);
        }
    }
}

void draw_ui(void) {
    // Draw score and status information
    snprintf(score_text, sizeof(score_text), "Score:%d", cannon.score);
    display_draw_string(2, 2, score_text, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(score_text, sizeof(score_text), "Lives:%d", cannon.lives);
    display_draw_string(2, 12, score_text, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(score_text, sizeof(score_text), "Enemy:%d", enemy.health);
    display_draw_string(2, 22, score_text, COLOR_WHITE, COLOR_BLACK);
    
    // Draw game borders for visual reference
    display_fill_rect(0, 0, GAME_WIDTH, 1, COLOR_WHITE);  // Top border
    display_fill_rect(0, GAME_HEIGHT-1, GAME_WIDTH, 1, COLOR_WHITE); // Bottom border
    display_fill_rect(0, 0, 1, GAME_HEIGHT, COLOR_WHITE);  // Left border
    display_fill_rect(GAME_WIDTH-1, 0, 1, GAME_HEIGHT, COLOR_WHITE); // Right border
    
    // Draw separation line between UI and game area
    display_fill_rect(0, 32, GAME_WIDTH, 1, COLOR_CYAN);
    
    if (game_over) {
        // Center the game over text
        display_fill_rect(10, GAME_HEIGHT/2 - 20, GAME_WIDTH - 20, 40, COLOR_BLACK);
        display_fill_rect(8, GAME_HEIGHT/2 - 22, GAME_WIDTH - 16, 44, COLOR_RED);
        
        display_draw_string(20, GAME_HEIGHT/2 - 15, "GAME OVER!", COLOR_WHITE, COLOR_RED);
        display_draw_string(15, GAME_HEIGHT/2 - 5, "Press any btn", COLOR_WHITE, COLOR_RED);
        display_draw_string(20, GAME_HEIGHT/2 + 5, "to restart", COLOR_WHITE, COLOR_RED);
    }
}

// Main game loop
void game_update(void) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Limit frame rate to ~30 FPS for smooth gameplay
    if (current_time - last_frame_time < 33) {
        return;
    }
    last_frame_time = current_time;
    
    // Handle combo controls
    handle_game_controls();
    
    if (game_running) {
        update_enemy(current_time);
        update_projectiles();
    }
    
    // Clear screen with black background
    display_clear(COLOR_BLACK);
    
    // Draw everything
    if (game_running) {
        draw_cannon();
        draw_enemy();
        draw_projectiles();
    }
    draw_ui();
}

int main() {
    stdio_init_all();
    
    printf("Starting Tank War Game..\n");
    
    // Initialize display and buttons
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display init failed!\n");
        return 1;
    }
    
    if (buttons_init() != DISPLAY_OK) {
        printf("Button init failed!\n");
        return 1;
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, on_button_a);  // Reset when game over
    button_set_callback(BUTTON_B, on_button_b);  // Move LEFT + Reset
    button_set_callback(BUTTON_X, on_button_x);  // Reset when game over
    button_set_callback(BUTTON_Y, on_button_y);  // Move RIGHT + Reset
    
    // Initialize game
    game_init();
    
    printf("Tank War Game Started! (240x135)\n");
    printf("FIXED COMBO CONTROLS:\n");
    printf("B: Move tank LEFT\n");
    printf("Y: Move tank RIGHT\n");
    printf("B+Y together: SHOOT upward\n");
    printf("Any button: Restart (when game over)\n");
    printf("Player tank at bottom, enemy tank at top!\n");
    
    // Test display with a simple pattern first
    printf("Testing display with colored rectangles..\n");
    display_clear(COLOR_BLACK);
    
    // Test pattern to verify display is working correctly
    display_fill_rect(0, 0, GAME_WIDTH/3, 20, COLOR_RED);
    display_fill_rect(GAME_WIDTH/3, 0, GAME_WIDTH/3, 20, COLOR_GREEN);
    display_fill_rect(2*GAME_WIDTH/3, 0, GAME_WIDTH/3, 20, COLOR_BLUE);
    
    display_draw_string(5, 25, "Display Driver Fixed", COLOR_WHITE, COLOR_BLACK);
    display_draw_string(5, 35, "240x135 Landscape", COLOR_CYAN, COLOR_BLACK);
    display_draw_string(5, 45, "No more stripes!?", COLOR_YELLOW, COLOR_BLACK);
    
    sleep_ms(3000); // Show test pattern for 3 seconds
    
    printf("Starting main game loop..\n");
    
    // Main game loop
    while (true) {
        buttons_update();
        game_update();
        
        // Small delay to prevent overwhelming the system
        sleep_ms(1);
    }
    
    // Cleanup (never reached in this case)
    display_cleanup();
    return 0;
}