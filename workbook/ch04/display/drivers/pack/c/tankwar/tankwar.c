#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pico/stdlib.h"
#include "pico/time.h"
#include "display.h"

// Game constants - vertical mode (135x240)
// Player cannon at bottom, enemy at top, projectiles move vertically
#define GAME_WIDTH 135
#define GAME_HEIGHT 240
#define CANNON_WIDTH 16   // Made smaller
#define CANNON_HEIGHT 6   // Made smaller
#define CANNON_Y (GAME_HEIGHT - CANNON_HEIGHT)  // Use every pixel - right at bottom edge
#define PROJECTILE_WIDTH 3
#define PROJECTILE_HEIGHT 6
#define ENEMY_WIDTH 18
#define ENEMY_HEIGHT 7
#define ENEMY_Y 30   // Move enemy well into visible screen area
#define MAX_PROJECTILES 8
#define MAX_ENEMY_PROJECTILES 5
#define PROJECTILE_SPEED 5
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

// Button state tracking for simultaneous press detection
static bool button_x_pressed = false;
static bool button_y_pressed = false;

// Initialize game state
void game_init(void) {
    // Initialize cannon at bottom center (with proper bounds)
    cannon.x = GAME_WIDTH / 2 - CANNON_WIDTH / 2;
    cannon.lives = 3;
    cannon.score = 0;
    cannon.last_shot_time = 0;
    
    // Initialize enemy at top center (with proper bounds)
    enemy.x = GAME_WIDTH / 2 - ENEMY_WIDTH / 2;
    enemy.y = ENEMY_Y;
    enemy.direction = 1;
    enemy.health = 3;
    enemy.last_shot_time = 0;
    enemy.last_move_time = 0;
    enemy.moving_to_avoid = false;
    enemy.target_x = enemy.x;
    
    // Initialize projectiles
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        projectiles[i].active = false;
    }
    for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
        enemy_projectiles[i].active = false;
    }
    
    game_running = true;
    game_over = false;
    button_x_pressed = false;
    button_y_pressed = false;
}

// Shoot function for simultaneous button press
void shoot_projectile(void) {
    if (!game_running) return;
    
    uint32_t now = to_ms_since_boot(get_absolute_time());
    
    // Shoot projectile upward (with cooldown)
    if (now - cannon.last_shot_time > 150) {
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

// Button callbacks
void on_button_a(button_t button) {
    // A button - not used for movement anymore
}

void on_button_b(button_t button) {
    // B button - not used for movement anymore  
}

void on_button_x(button_t button) {
    if (!game_running) return;
    
    button_x_pressed = true;
    
    // Check if both X and Y are pressed for shooting
    if (button_y_pressed) {
        shoot_projectile();
        return;
    }
    
    // Move cannon right
    cannon.x += 6;
    if (cannon.x > GAME_WIDTH - CANNON_WIDTH) {
        cannon.x = GAME_WIDTH - CANNON_WIDTH;
    }
}

void on_button_y(button_t button) {
    if (game_over) {
        // Restart game
        game_init();
        return;
    }
    
    if (!game_running) return;
    
    button_y_pressed = true;
    
    // Check if both X and Y are pressed for shooting
    if (button_x_pressed) {
        shoot_projectile();
        return;
    }
    
    // Move cannon left
    cannon.x -= 6;
    if (cannon.x < 0) cannon.x = 0;
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
            projectiles[i].y < enemy.y + 80 && // Within danger zone
            abs(projectiles[i].x - (enemy.x + ENEMY_WIDTH/2)) < 25) {
            should_avoid = true;
            closest_projectile_x = projectiles[i].x;
            break;
        }
    }
    
    // Movement logic
    if (current_time - enemy.last_move_time > 200) {
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
            if (rand() % 100 < 25) { // 25% chance to change direction
                enemy.direction = -enemy.direction;
            }
        } else {
            // Occasionally stop avoiding
            if (rand() % 100 < 40) {
                enemy.moving_to_avoid = false;
            }
        }
        
        enemy.last_move_time = current_time;
    }
    
    // Move enemy horizontally
    enemy.x += enemy.direction * ENEMY_SPEED;
    
    // Bounce off walls (with proper bounds checking)
    if (enemy.x <= 0) {
        enemy.x = 0;
        enemy.direction = 1;
    } else if (enemy.x >= GAME_WIDTH - ENEMY_WIDTH) {
        enemy.x = GAME_WIDTH - ENEMY_WIDTH;
        enemy.direction = -1;
    }
    
    // Enemy shooting downward
    if (current_time - enemy.last_shot_time > 1200 + (rand() % 800)) {
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

// Update button states for simultaneous press detection
void update_button_states(void) {
    // Reset button press states each frame
    // They get set to true in the callback functions when buttons are pressed
    // We need to check actual button states to detect simultaneous presses
    static bool last_x_state = false;
    static bool last_y_state = false;
    
    bool current_x = button_pressed(BUTTON_X);
    bool current_y = button_pressed(BUTTON_Y);
    
    // Reset flags when buttons are released
    if (!current_x) button_x_pressed = false;
    if (!current_y) button_y_pressed = false;
    
    last_x_state = current_x;
    last_y_state = current_y;
}

// Draw game objects
void draw_cannon(void) {
    // Draw cannon at absolute bottom - using every pixel
    display_fill_rect(cannon.x, CANNON_Y, CANNON_WIDTH, CANNON_HEIGHT, COLOR_GREEN);
    // Draw barrel pointing up (positioned above the tank body)
    display_fill_rect(cannon.x + CANNON_WIDTH/2 - 1, CANNON_Y - 6, 3, 6, COLOR_GREEN);
}

void draw_enemy(void) {
    // Draw enemy with different colors based on health
    uint16_t color = COLOR_RED;
    if (enemy.health > 2) color = COLOR_YELLOW;
    else if (enemy.health > 1) color = COLOR_MAGENTA;
    
    display_fill_rect(enemy.x, enemy.y, ENEMY_WIDTH, ENEMY_HEIGHT, color);
    // Draw barrel pointing down (smaller)
    display_fill_rect(enemy.x + ENEMY_WIDTH/2 - 1, enemy.y + ENEMY_HEIGHT, 3, 4, color);
}

void draw_projectiles(void) {
    // Draw player projectiles (moving up)
    for (int i = 0; i < MAX_PROJECTILES; i++) {
        if (projectiles[i].active) {
            display_fill_rect(projectiles[i].x, projectiles[i].y, 
                            PROJECTILE_WIDTH, PROJECTILE_HEIGHT, COLOR_CYAN);
        }
    }
    
    // Draw enemy projectiles (moving down)
    for (int i = 0; i < MAX_ENEMY_PROJECTILES; i++) {
        if (enemy_projectiles[i].active) {
            display_fill_rect(enemy_projectiles[i].x, enemy_projectiles[i].y,
                            PROJECTILE_WIDTH, PROJECTILE_HEIGHT, COLOR_RED);
        }
    }
}

void draw_ui(void) {
    // Draw score and lives in compact format for narrow screen
    snprintf(score_text, sizeof(score_text), "S:%d", cannon.score);
    display_draw_string(2, 2, score_text, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(score_text, sizeof(score_text), "L:%d", cannon.lives);
    display_draw_string(50, 2, score_text, COLOR_WHITE, COLOR_BLACK);
    
    snprintf(score_text, sizeof(score_text), "E:%d", enemy.health);
    display_draw_string(90, 2, score_text, COLOR_WHITE, COLOR_BLACK);
    
    // Draw reference lines to show we're using full screen
    display_fill_rect(0, 0, GAME_WIDTH, 1, COLOR_WHITE);  // Top border (y=0)
    display_fill_rect(0, 15, GAME_WIDTH, 1, COLOR_WHITE); // Below UI (y=15)
    display_fill_rect(0, GAME_HEIGHT-1, GAME_WIDTH, 1, COLOR_WHITE); // Bottom border (y=239)
    
    // Show enemy area clearly
    display_fill_rect(0, 25, GAME_WIDTH, 1, COLOR_CYAN); // Enemy zone marker
    
    if (game_over) {
        // Center the game over text
        display_draw_string(30, GAME_HEIGHT/2 - 10, "GAME OVER!", COLOR_RED, COLOR_BLACK);
        display_draw_string(15, GAME_HEIGHT/2 + 5, "Y to restart", COLOR_WHITE, COLOR_BLACK);
    }
}

// Main game loop
void game_update(void) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Limit frame rate to ~40 FPS for smooth movement
    if (current_time - last_frame_time < 25) {
        return;
    }
    last_frame_time = current_time;
    
    if (game_running) {
        update_button_states();
        update_enemy(current_time);
        update_projectiles();
    }
    
    // Clear screen
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
    
    // Initialize display and buttons
    if (display_pack_init() != DISPLAY_OK) {
        printf("Display initialization failed!\n");
        return 1;
    }
    
    if (buttons_init() != DISPLAY_OK) {
        printf("Button initialization failed!\n");
        return 1;
    }
    
    // Set up button callbacks
    button_set_callback(BUTTON_A, on_button_a);  // Not used
    button_set_callback(BUTTON_B, on_button_b);  // Not used
    button_set_callback(BUTTON_X, on_button_x);  // Move right
    button_set_callback(BUTTON_Y, on_button_y);  // Move left
    
    // Initialize game
    game_init();
    
    printf("Vertical Tank War Game Started! (135x240)\n");
    printf("Controls:\n");
    printf("Y: Move tank left\n");
    printf("X: Move tank right\n");
    printf("X+Y: Shoot upward (press both buttons together)\n");
    printf("Y: Restart (when game over)\n");
    printf("Player at bottom, enemy at top!\n");
    
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
