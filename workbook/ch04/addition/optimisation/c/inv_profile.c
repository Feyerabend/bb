/*
 * Space Invaders - Visual Performance Profiler
 * 
 * Shows real-time performance metrics ON SCREEN:
 * - FPS counter with min/max/avg
 * - Frame time breakdown (logic, render, total)
 * - Visual bar graph of frame timing
 * - Memory usage stats
 * 
 * Press Y to toggle profiler display
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "display.h"

// Profiler configuration
#define PROFILE_ENABLED 1
#define PROFILE_HISTORY_SIZE 60  // 1 second at 60 FPS

// Performance data
typedef struct {
    uint32_t frame_start_us;
    uint32_t logic_start_us;
    uint32_t render_start_us;
    
    uint32_t frame_time_us;
    uint32_t logic_time_us;
    uint32_t render_time_us;
    
    uint32_t frame_history[PROFILE_HISTORY_SIZE];
    uint8_t history_index;
    
    uint32_t frame_count;
    uint32_t fps;
    uint32_t min_fps;
    uint32_t max_fps;
    uint32_t avg_frame_us;
    
    uint32_t last_fps_calc;
    uint32_t fps_frame_count;
    
    bool show_profiler;
} profiler_t;

static profiler_t prof = {0};

// Profiler macros
#define PROF_FRAME_START() \
    do { if (PROFILE_ENABLED) prof.frame_start_us = time_us_32(); } while(0)

#define PROF_LOGIC_START() \
    do { if (PROFILE_ENABLED) prof.logic_start_us = time_us_32(); } while(0)

#define PROF_LOGIC_END() \
    do { if (PROFILE_ENABLED) prof.logic_time_us = time_us_32() - prof.logic_start_us; } while(0)

#define PROF_RENDER_START() \
    do { if (PROFILE_ENABLED) prof.render_start_us = time_us_32(); } while(0)

#define PROF_RENDER_END() \
    do { if (PROFILE_ENABLED) prof.render_time_us = time_us_32() - prof.render_start_us; } while(0)

#define PROF_FRAME_END() \
    do { if (PROFILE_ENABLED) profiler_frame_end(); } while(0)

// Game objects (simplified for example)
typedef struct {
    float x, y;
    int width, height;
} player_t;

typedef struct {
    float x, y;
    int width, height;
    bool alive;
} invader_t;

typedef struct {
    float x, y;
    bool active;
} projectile_t;

#define MAX_INVADERS 15
#define MAX_BULLETS 5
#define MAX_BOMBS 15

static player_t player;
static invader_t invaders[MAX_INVADERS];
static projectile_t bullets[MAX_BULLETS];
static projectile_t bombs[MAX_BOMBS];
static int invader_count = 0;
static bool game_over = false;
static bool win = false;

// Init profiler
void profiler_init(void) {
    memset(&prof, 0, sizeof(profiler_t));
    prof.show_profiler = true;  // Start visible
    prof.min_fps = 999;
    prof.max_fps = 0;
    prof.last_fps_calc = time_us_32();
}

// Update profiler at end of frame
void profiler_frame_end(void) {
    prof.frame_time_us = time_us_32() - prof.frame_start_us;
    
    // Store in history
    prof.frame_history[prof.history_index] = prof.frame_time_us;
    prof.history_index = (prof.history_index + 1) % PROFILE_HISTORY_SIZE;
    
    // Calculate FPS every second
    prof.fps_frame_count++;
    uint32_t now = time_us_32();
    uint32_t elapsed = now - prof.last_fps_calc;
    
    if (elapsed >= 1000000) {  // 1 second
        prof.fps = prof.fps_frame_count;
        prof.fps_frame_count = 0;
        prof.last_fps_calc = now;
        
        // Update min/max
        if (prof.fps > 0 && prof.fps < prof.min_fps) prof.min_fps = prof.fps;
        if (prof.fps > prof.max_fps) prof.max_fps = prof.fps;
        
        // Calculate average frame time
        uint32_t sum = 0;
        for (int i = 0; i < PROFILE_HISTORY_SIZE; i++) {
            sum += prof.frame_history[i];
        }
        prof.avg_frame_us = sum / PROFILE_HISTORY_SIZE;
    }
    
    prof.frame_count++;
}

// Draw profiler overlay
void profiler_draw(void) {
    if (!prof.show_profiler) return;
    
    int x = 5;
    int y = 5;
    int line_height = 10;
    char buf[64];
    
    // Semi-transparent background (draw black rectangles for text background)
    disp_framebuffer_fill_rect(0, 0, 150, 120, COLOR_BLACK);
    
    // FPS stats
    snprintf(buf, sizeof(buf), "FPS: %lu", prof.fps);
    disp_framebuffer_draw_text(x, y, buf, COLOR_GREEN, COLOR_BLACK);
    y += line_height;
    
    snprintf(buf, sizeof(buf), "Min: %lu Max: %lu", prof.min_fps, prof.max_fps);
    disp_framebuffer_draw_text(x, y, buf, COLOR_CYAN, COLOR_BLACK);
    y += line_height;
    
    // Frame time breakdown
    y += 2;
    snprintf(buf, sizeof(buf), "Frame: %lu us", prof.frame_time_us);
    disp_framebuffer_draw_text(x, y, buf, COLOR_WHITE, COLOR_BLACK);
    y += line_height;
    
    snprintf(buf, sizeof(buf), "Logic: %lu us", prof.logic_time_us);
    disp_framebuffer_draw_text(x, y, buf, COLOR_YELLOW, COLOR_BLACK);
    y += line_height;
    
    snprintf(buf, sizeof(buf), "Render: %lu us", prof.render_time_us);
    disp_framebuffer_draw_text(x, y, buf, COLOR_YELLOW, COLOR_BLACK);
    y += line_height;
    
    // Frame time percentage breakdown
    if (prof.frame_time_us > 0) {
        uint32_t logic_pct = (prof.logic_time_us * 100) / prof.frame_time_us;
        uint32_t render_pct = (prof.render_time_us * 100) / prof.frame_time_us;
        
        snprintf(buf, sizeof(buf), "L:%lu%% R:%lu%%", logic_pct, render_pct);
        disp_framebuffer_draw_text(x, y, buf, COLOR_CYAN, COLOR_BLACK);
        y += line_height;
    }
    
    // Visual frame time graph
    y += 5;
    int graph_width = 140;
    int graph_height = 30;
    
    // Background
    disp_framebuffer_fill_rect(x, y, graph_width, graph_height, COLOR_BLACK);
    
    // Draw 16ms and 33ms reference lines (60 FPS and 30 FPS)
    int ref_60fps = (16666 * graph_height) / 40000;  // 16.6ms scaled to graph
    int ref_30fps = (33333 * graph_height) / 40000;  // 33.3ms scaled to graph
    
    // 60 FPS line (green)
    for (int i = 0; i < graph_width; i += 2) {
        disp_framebuffer_set_pixel(x + i, y + graph_height - ref_60fps, COLOR_GREEN);
    }
    
    // 30 FPS line (yellow)
    for (int i = 0; i < graph_width; i += 2) {
        disp_framebuffer_set_pixel(x + i, y + graph_height - ref_30fps, COLOR_YELLOW);
    }
    
    // Draw frame time history
    for (int i = 0; i < PROFILE_HISTORY_SIZE && i < graph_width; i++) {
        int idx = (prof.history_index + i) % PROFILE_HISTORY_SIZE;
        uint32_t frame_us = prof.frame_history[idx];
        
        // Scale to graph (max 40ms = 25 FPS)
        int bar_height = (frame_us * graph_height) / 40000;
        if (bar_height > graph_height) bar_height = graph_height;
        
        // Color code: green=good, yellow=ok, red=bad
        uint16_t color;
        if (frame_us < 16666) color = COLOR_GREEN;       // >60 FPS
        else if (frame_us < 33333) color = COLOR_YELLOW; // 30-60 FPS
        else color = COLOR_RED;                          // <30 FPS
        
        // Draw vertical bar
        int px = x + (i * graph_width) / PROFILE_HISTORY_SIZE;
        for (int j = 0; j < bar_height; j++) {
            disp_framebuffer_set_pixel(px, y + graph_height - j, color);
        }
    }
    
    // Labels
    disp_framebuffer_draw_text(x, y + graph_height + 2, "Frame Time (1s history)", 
                               COLOR_CYAN, COLOR_BLACK);
}

// Simple game functions (minimal for demo)
void init_game(void) {
    player.x = DISPLAY_WIDTH / 2 - 10;
    player.y = DISPLAY_HEIGHT - 30;
    player.width = 20;
    player.height = 10;
    
    invader_count = 15;
    for (int i = 0; i < invader_count; i++) {
        invaders[i].x = 60 + (i % 5) * 40;
        invaders[i].y = 40 + (i / 5) * 30;
        invaders[i].width = 20;
        invaders[i].height = 15;
        invaders[i].alive = true;
    }
    
    memset(bullets, 0, sizeof(bullets));
    memset(bombs, 0, sizeof(bombs));
    game_over = false;
    win = false;
}

void update_game(void) {
    // Simplified update logic
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            bullets[i].y -= 5;
            if (bullets[i].y < 0) bullets[i].active = false;
        }
    }
}

void render_game(void) {
    // Clear
    disp_framebuffer_clear(COLOR_BLACK);
    
    // Player
    disp_framebuffer_fill_rect(player.x, player.y, player.width, player.height, COLOR_WHITE);
    
    // Invaders
    for (int i = 0; i < invader_count; i++) {
        if (invaders[i].alive) {
            disp_framebuffer_fill_rect(invaders[i].x, invaders[i].y, 
                                      invaders[i].width, invaders[i].height, COLOR_GREEN);
        }
    }
    
    // Bullets
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (bullets[i].active) {
            disp_framebuffer_fill_rect(bullets[i].x, bullets[i].y, 2, 4, COLOR_YELLOW);
        }
    }
    
    // Draw profiler overlay LAST
    profiler_draw();
    
    // Flush to display
    disp_framebuffer_flush();
}

void handle_input(void) {
    buttons_update();
    
    if (button_pressed(BUTTON_A) && player.x > 0) {
        player.x -= 3;
    }
    if (button_pressed(BUTTON_B) && player.x < DISPLAY_WIDTH - player.width) {
        player.x += 3;
    }
    if (button_just_pressed(BUTTON_X)) {
        for (int i = 0; i < MAX_BULLETS; i++) {
            if (!bullets[i].active) {
                bullets[i].x = player.x + player.width / 2;
                bullets[i].y = player.y;
                bullets[i].active = true;
                break;
            }
        }
    }
    
    // Toggle profiler with Y button
    if (button_just_pressed(BUTTON_Y)) {
        prof.show_profiler = !prof.show_profiler;
        printf("Profiler %s\n", prof.show_profiler ? "ON" : "OFF");
    }
}

int main() {
    stdio_init_all();
    
    printf("Space Invaders - Visual Profiler Demo\n\n");
    printf("Press Y to toggle profiler overlay\n\n");
    
    // Initialize display
    disp_config_t config = disp_get_default_config();
    if (disp_init(&config) != DISP_OK) {
        printf("Display init failed!\n");
        return 1;
    }
    
    // Init buttons
    buttons_init();
    
    // Allocate framebuffer
    if (disp_framebuffer_alloc() != DISP_OK) {
        printf("Framebuffer allocation failed!\n");
        return 1;
    }
    
    // Init game and profiler
    init_game();
    profiler_init();
    
    // Main loop
    while (true) {
        PROF_FRAME_START();
        
        // Game logic
        PROF_LOGIC_START();
        handle_input();
        if (!game_over && !win) {
            update_game();
        }
        PROF_LOGIC_END();
        
        // Rendering
        PROF_RENDER_START();
        render_game();
        PROF_RENDER_END();
        
        PROF_FRAME_END();
        
        // Frame pacing
        sleep_ms(16);  // ~60 FPS target
    }
    
    return 0;
}
