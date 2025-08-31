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

// Display setup
PicoDisplay2 display;
PicoGraphics_PenRGB565 graphics(display.width, display.height, nullptr);

// Display dimensions
#define WIDTH 320
#define HEIGHT 240
#define SCALE 1.5f

// Colors (RGB565 format)
#define BLACK 0x0000
#define WHITE 0xFFFF
#define GREEN 0x07E0
#define RED 0xF800
#define YELLOW 0xFFE0

// Button pins
#define BUTTON_A 12
#define BUTTON_B 13
#define BUTTON_X 14

// Game constants
#define MAX_BULLETS 10
#define MAX_BOMBS 20
#define MAX_INVADERS 15
#define MAX_BUNKERS 2

// Player structure
typedef struct {
    float x, y;
    int width, height;
    float speed;
} Player;

// Bullet/Bomb structure
typedef struct {
    float x, y;
    bool active;
} Projectile;

// Invader type structure
typedef struct {
    uint8_t pixels[3][6];  // Max 3x6 pixel art
    int pixel_width, pixel_height;
    int width, height;
    uint16_t color;
} InvaderType;

// Invader structure
typedef struct {
    float x, y;
    InvaderType* type;
    int width, height;
    bool alive;
} Invader;

// Bunker structure
typedef struct {
    float x, y;
    uint8_t pixels[3][5];  // 3x5 pixel art
    int width, height;
    uint16_t color;
} Bunker;

// Game state
Player player;
Projectile bullets[MAX_BULLETS];
Projectile bombs[MAX_BOMBS];
Invader invaders[MAX_INVADERS];
Bunker bunkers[MAX_BUNKERS];
InvaderType invader_types[2];

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

// Function prototypes
void init_game(void);
void init_invader_types(void);
void init_invaders(void);
void init_bunkers(void);
void update_game(void);
void draw_game(void);
void draw_invader(Invader* inv);
void draw_bunker(Bunker* bunker);
bool check_collision(float x1, float y1, int w1, int h1, float x2, float y2, int w2, int h2);
bool check_bunker_hit(float proj_x, float proj_y, int proj_w, int proj_h, Bunker* bunker);
void erode_bunker(Bunker* bunker, float hit_x, float hit_y);
void add_bullet(float x, float y);
void add_bomb(float x, float y);

int main() {
    stdio_init_all();
    
    // Init display
    display.init();
    display.set_backlight(200); // 0-255
    
    // Init buttons
    gpio_init(BUTTON_A);
    gpio_set_dir(BUTTON_A, GPIO_IN);
    gpio_pull_up(BUTTON_A);
    
    gpio_init(BUTTON_B);
    gpio_set_dir(BUTTON_B, GPIO_IN);
    gpio_pull_up(BUTTON_B);
    
    gpio_init(BUTTON_X);
    gpio_set_dir(BUTTON_X, GPIO_IN);
    gpio_pull_up(BUTTON_X);
    
    init_game();
    
    uint32_t last_shot_time = 0;
    
    while (true) {
        uint32_t current_time = time_us_32();
        
        if (!game_over && !win) {
            // Input handling
            if (!gpio_get(BUTTON_A) && player.x > 0) {
                player.x -= player.speed;
            }
            if (!gpio_get(BUTTON_B) && player.x < WIDTH - player.width) {
                player.x += player.speed;
            }
            if (!gpio_get(BUTTON_X) && bullet_count < 3 && 
                (current_time - last_shot_time) > 200000) { // 200ms debounce
                add_bullet(player.x + player.width / 2, player.y - 2);
                last_shot_time = current_time;
            }
            
            update_game();
        }
        
        draw_game();
        sleep_ms(20); // ~50 FPS
    }
}

void init_game(void) {
    // Init player
    player.x = WIDTH / 2;
    player.y = HEIGHT * 0.9f;
    player.width = 15;
    player.height = 10;
    player.speed = 4.5f;
    
    // Init arrays
    memset(bullets, 0, sizeof(bullets));
    memset(bombs, 0, sizeof(bombs));
    
    bullet_count = 0;
    bomb_count = 0;
    game_over = false;
    win = false;
    frame_count = 0;
    
    init_invader_types();
    init_invaders();
    init_bunkers();
}

void init_invader_types(void) {
    // Type 0: Small green invader
    invader_types[0].pixel_width = 3;
    invader_types[0].pixel_height = 3;
    invader_types[0].width = 15;
    invader_types[0].height = 15;
    invader_types[0].color = GREEN;
    
    uint8_t type0_pixels[3][3] = {
        {0, 1, 0},
        {1, 1, 1},
        {1, 0, 1}
    };
    memcpy(invader_types[0].pixels, type0_pixels, sizeof(type0_pixels));
    
    // Type 1: Larger red invader
    invader_types[1].pixel_width = 6;
    invader_types[1].pixel_height = 3;
    invader_types[1].width = 22;
    invader_types[1].height = 15;
    invader_types[1].color = RED;
    
    uint8_t type1_pixels[3][6] = {
        {0, 0, 1, 1, 0, 0},
        {1, 1, 1, 1, 1, 1},
        {1, 0, 0, 0, 0, 1}
    };
    memcpy(invader_types[1].pixels, type1_pixels, sizeof(type1_pixels));
}

void init_invaders(void) {
    int rows = 3, cols = 5;
    float spacing_x = 30 * SCALE;
    float spacing_y = 22 * SCALE;
    
    invader_count = 0;
    for (int row = 0; row < rows; row++) {
        for (int col = 0; col < cols; col++) {
            int type_idx = row % 2;
            invaders[invader_count].x = 75 + col * spacing_x;
            invaders[invader_count].y = 30 + row * spacing_y;
            invaders[invader_count].type = &invader_types[type_idx];
            invaders[invader_count].width = invader_types[type_idx].width;
            invaders[invader_count].height = invader_types[type_idx].height;
            invaders[invader_count].alive = true;
            invader_count++;
        }
    }
}

void init_bunkers(void) {
    uint8_t bunker_pixels[3][5] = {
        {1, 1, 1, 1, 1},
        {1, 1, 1, 1, 1},
        {0, 1, 1, 1, 0}
    };
    
    int bunker_spacing = WIDTH / (MAX_BUNKERS + 1);
    for (int i = 0; i < MAX_BUNKERS; i++) {
        bunkers[i].x = (i + 1) * bunker_spacing - 15;
        bunkers[i].y = HEIGHT * 0.75f;
        bunkers[i].width = 30;
        bunkers[i].height = 15;
        bunkers[i].color = GREEN;
        memcpy(bunkers[i].pixels, bunker_pixels, sizeof(bunker_pixels));
    }
}

void add_bullet(float x, float y) {
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) {
            bullets[i].x = x;
            bullets[i].y = y;
            bullets[i].active = true;
            bullet_count++;
            break;
        }
    }
}

void add_bomb(float x, float y) {
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (!bombs[i].active) {
            bombs[i].x = x;
            bombs[i].y = y;
            bombs[i].active = true;
            bomb_count++;
            break;
        }
    }
}

void update_game(void) {
    // Update bullets
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            bullets[i].y -= 7.5f;
            if (bullets[i].y < 0) {
                bullets[i].active = false;
                bullet_count--;
            }
        }
    }
    
    // Update invaders and spawn bombs
    frame_count++;
    if (frame_count % invader_move_interval == 0) {
        bool hit_edge = false;
        
        for (int i = 0; i < invader_count; i++) {
            if (!invaders[i].alive) continue;
            
            invaders[i].x += invader_speed * invader_direction;
            
            if (invaders[i].x <= 0 || invaders[i].x + invaders[i].width >= WIDTH) {
                hit_edge = true;
            }
            
            if (invaders[i].y + invaders[i].height >= player.y) {
                game_over = true;
            }
            
            // Random bomb dropping
            if ((rand() % 1000) < 5) { // 0.5% chance per frame
                add_bomb(invaders[i].x + invaders[i].width / 2, 
                        invaders[i].y + invaders[i].height);
            }
        }
        
        if (hit_edge) {
            invader_direction *= -1;
            for (int i = 0; i < invader_count; i++) {
                invaders[i].y += invader_drop;
            }
        }
    }
    
    // Update bombs
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            bombs[i].y += 6.0f;
            if (bombs[i].y > HEIGHT) {
                bombs[i].active = false;
                bomb_count--;
            }
        }
    }
    
    // Collision detection: bullets vs invaders
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) continue;
        
        for (int j = 0; j < invader_count; j++) {
            if (!invaders[j].alive) continue;
            
            if (check_collision(bullets[i].x, bullets[i].y, 3, 3,
                              invaders[j].x, invaders[j].y, 
                              invaders[j].width, invaders[j].height)) {
                invaders[j].alive = false;
                bullets[i].active = false;
                bullet_count--;
                break;
            }
        }
    }
    
    // Collision detection: bullets vs bunkers
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) continue;
        
        for (int j = 0; j < MAX_BUNKERS; j++) {
            if (check_bunker_hit(bullets[i].x, bullets[i].y, 3, 3, &bunkers[j])) {
                erode_bunker(&bunkers[j], bullets[i].x - bunkers[j].x, 
                           bullets[i].y - bunkers[j].y);
                bullets[i].active = false;
                bullet_count--;
                break;
            }
        }
    }
    
    // Collision detection: bombs vs bunkers
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (!bombs[i].active) continue;
        
        for (int j = 0; j < MAX_BUNKERS; j++) {
            if (check_bunker_hit(bombs[i].x, bombs[i].y, 3, 3, &bunkers[j])) {
                erode_bunker(&bunkers[j], bombs[i].x - bunkers[j].x, 
                           bombs[i].y - bunkers[j].y);
                bombs[i].active = false;
                bomb_count--;
                break;
            }
        }
    }
    
    // Collision detection: bombs vs player
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (!bombs[i].active) continue;
        
        if (check_collision(bombs[i].x, bombs[i].y, 3, 3,
                          player.x, player.y, player.width, player.height)) {
            game_over = true;
            bombs[i].active = false;
            bomb_count--;
        }
    }
    
    // Collision detection: bullets vs bombs
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (!bullets[i].active) continue;
        
        for (int j = 0; j < MAX_BOMBS; j++) {
            if (!bombs[j].active) continue;
            
            if (check_collision(bullets[i].x, bullets[i].y, 3, 3,
                              bombs[j].x, bombs[j].y, 3, 3)) {
                bullets[i].active = false;
                bombs[j].active = false;
                bullet_count--;
                bomb_count--;
                break;
            }
        }
    }
    
    // Check win condition
    bool all_dead = true;
    for (int i = 0; i < invader_count; i++) {
        if (invaders[i].alive) {
            all_dead = false;
            break;
        }
    }
    if (all_dead) {
        win = true;
    }
}

bool check_collision(float x1, float y1, int w1, int h1, 
                    float x2, float y2, int w2, int h2) {
    return !(x1 + w1 < x2 || x1 > x2 + w2 || y1 + h1 < y2 || y1 > y2 + h2);
}

bool check_bunker_hit(float proj_x, float proj_y, int proj_w, int proj_h, Bunker* bunker) {
    if (proj_x + proj_w < bunker->x || proj_x > bunker->x + bunker->width ||
        proj_y + proj_h < bunker->y || proj_y > bunker->y + bunker->height) {
        return false;
    }
    
    float pixel_size_x = bunker->width / 5.0f;
    float pixel_size_y = bunker->height / 3.0f;
    int col = (int)((proj_x - bunker->x + proj_w / 2) / pixel_size_x);
    int row = (int)((proj_y - bunker->y + proj_h / 2) / pixel_size_y);
    
    if (row >= 0 && row < 3 && col >= 0 && col < 5 && bunker->pixels[row][col] == 1) {
        return true;
    }
    return false;
}

void erode_bunker(Bunker* bunker, float hit_x, float hit_y) {
    float pixel_size_x = bunker->width / 5.0f;
    float pixel_size_y = bunker->height / 3.0f;
    int hit_col = (int)(hit_x / pixel_size_x);
    int hit_row = (int)(hit_y / pixel_size_y);
    
    for (int r = -1; r <= 1; r++) {
        for (int c = -1; c <= 1; c++) {
            int row = hit_row + r;
            int col = hit_col + c;
            if (row >= 0 && row < 3 && col >= 0 && col < 5) {
                bunker->pixels[row][col] = 0;
            }
        }
    }
}

void draw_invader(Invader* inv) {
    if (!inv->alive) return;
    
    float pixel_size_x = (float)inv->width / inv->type->pixel_width;
    float pixel_size_y = (float)inv->height / inv->type->pixel_height;
    
    graphics.set_pen(inv->type->color);
    
    for (int y = 0; y < inv->type->pixel_height; y++) {
        for (int x = 0; x < inv->type->pixel_width; x++) {
            if (inv->type->pixels[y][x]) {
                graphics.rectangle(Point(inv->x + x * pixel_size_x, 
                                       inv->y + y * pixel_size_y),
                                 Size(pixel_size_x, pixel_size_y));
            }
        }
    }
}

void draw_bunker(Bunker* bunker) {
    float pixel_size_x = bunker->width / 5.0f;
    float pixel_size_y = bunker->height / 3.0f;
    
    graphics.set_pen(bunker->color);
    
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 5; x++) {
            if (bunker->pixels[y][x]) {
                graphics.rectangle(Point(bunker->x + x * pixel_size_x,
                                       bunker->y + y * pixel_size_y),
                                 Size(pixel_size_x, pixel_size_y));
            }
        }
    }
}

void draw_game(void) {
    graphics.set_pen(BLACK);
    graphics.clear();
    
    // Draw player (triangle)
    graphics.set_pen(WHITE);
    Point triangle_points[3] = {
        Point(player.x, player.y + player.height),
        Point(player.x + player.width / 2, player.y),
        Point(player.x + player.width, player.y + player.height)
    };
    graphics.polygon(triangle_points, 3);
    
    // Draw bullets
    graphics.set_pen(YELLOW);
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            graphics.rectangle(Point(bullets[i].x, bullets[i].y), Size(3, 3));
        }
    }
    
    // Draw bombs
    graphics.set_pen(RED);
    for (int i = 0; i < MAX_BOMBS; i++) {
        if (bombs[i].active) {
            graphics.rectangle(Point(bombs[i].x, bombs[i].y), Size(3, 3));
        }
    }
    
    // Draw invaders
    for (int i = 0; i < invader_count; i++) {
        draw_invader(&invaders[i]);
    }
    
    // Draw bunkers
    for (int i = 0; i < MAX_BUNKERS; i++) {
        draw_bunker(&bunkers[i]);
    }
    
    // Draw game state text
    if (game_over) {
        graphics.set_pen(RED);
        graphics.text("Game Over", Point(WIDTH / 4, HEIGHT / 2), 240, 2);
    } else if (win) {
        graphics.set_pen(GREEN);
        graphics.text("You Win!", Point(WIDTH / 4, HEIGHT / 2), 240, 2);
    }
    
    display.update(&graphics);
}

