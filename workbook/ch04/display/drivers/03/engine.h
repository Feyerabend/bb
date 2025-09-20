#ifndef GRAPHICS_ENGINE_H
#define GRAPHICS_ENGINE_H

#include <stdint.h>
#include <stdbool.h>
#include "display.h"

// Engine Configuration
#define MAX_SPRITES 32
#define MAX_ANIMATIONS 16
#define MAX_TILESETS 8
#define MAX_LAYERS 4
#define TILE_SIZE 16
#define ANIMATION_FRAME_BUFFER 64

// Graphics Engine Types
typedef enum {
    BLEND_NONE = 0,
    BLEND_ALPHA,
    BLEND_ADD,
    BLEND_MULTIPLY,
    BLEND_SUBTRACT
} blend_mode_t;

typedef enum {
    SPRITE_STATIC = 0,
    SPRITE_ANIMATED,
    SPRITE_PARTICLE
} sprite_type_t;

typedef struct {
    uint16_t* data;          // Pixel data (RGB565)
    uint16_t width, height;
    uint8_t frames;          // Number of animation frames
    uint8_t frame_width;     // Width of single frame (for sprite sheets)
} texture_t;

typedef struct {
    uint8_t id;
    int16_t x, y;            // Position (can be negative for off-screen)
    int16_t velocity_x, velocity_y; // Movement per frame
    uint8_t texture_id;
    uint8_t current_frame;
    uint8_t animation_id;
    uint8_t layer;           // Render layer (0 = back, higher = front)
    sprite_type_t type;
    blend_mode_t blend_mode;
    uint8_t alpha;           // 0-255 transparency
    bool active;
    bool visible;
    bool collision_enabled;
    
    // Bounding box (for collision)
    uint8_t width, height;
    
    // Animation state
    uint32_t last_frame_time;
    uint16_t frame_duration;  // ms per frame
} sprite_t;

typedef struct {
    uint8_t id;
    uint8_t frame_count;
    uint8_t* frame_sequence;  // Array of frame indices
    uint16_t* frame_durations; // Duration for each frame (ms)
    bool loop;
    bool active;
} animation_t;

typedef struct {
    texture_t* texture;
    uint8_t tile_width, tile_height;
    uint8_t tiles_per_row;
    bool active;
} tileset_t;

typedef struct {
    uint8_t* tile_map;       // Grid of tile indices
    uint8_t tileset_id;
    uint16_t width, height;  // Map dimensions in tiles
    int16_t scroll_x, scroll_y; // Scroll offset
    uint8_t layer;
    bool active;
    bool visible;
} tile_layer_t;

typedef struct {
    uint8_t id1, id2;
    uint32_t timestamp;
} collision_event_t;

// Particle system
typedef struct {
    float x, y;
    float velocity_x, velocity_y;
    float acceleration_x, acceleration_y;
    uint16_t color;
    uint8_t alpha;
    uint16_t life_time;
    uint16_t max_life;
    bool active;
} particle_t;

typedef struct {
    particle_t particles[64];
    uint8_t active_count;
    float spawn_x, spawn_y;
    float spawn_velocity_range;
    uint16_t spawn_rate;
    uint32_t last_spawn;
    uint16_t particle_life;
    uint16_t color;
    bool active;
} particle_system_t;

// Graphics Engine State
typedef struct {
    sprite_t sprites[MAX_SPRITES];
    animation_t animations[MAX_ANIMATIONS];
    texture_t textures[MAX_SPRITES]; // One texture per sprite for simplicity
    tileset_t tilesets[MAX_TILESETS];
    tile_layer_t tile_layers[MAX_LAYERS];
    particle_system_t particle_systems[4];
    
    // Framebuffer for double buffering
    uint16_t* framebuffer;
    uint16_t* back_buffer;
    
    // Camera
    int16_t camera_x, camera_y;
    
    // Collision detection
    collision_event_t collision_events[16];
    uint8_t collision_count;
    
    // Performance stats
    uint32_t frame_time_ms;
    uint32_t last_frame_time;
    uint16_t fps;
    
    // Engine state
    bool double_buffering;
    bool collision_detection_enabled;
    bool vsync_enabled;
    
} graphics_engine_t;

// Core Engine Functions
bool graphics_engine_init(void);
void graphics_engine_shutdown(void);
void graphics_engine_update(void);
void graphics_engine_render(void);
void graphics_engine_present(void);

// Sprite Management
uint8_t sprite_create(int16_t x, int16_t y, uint8_t width, uint8_t height);
void sprite_destroy(uint8_t sprite_id);
void sprite_set_position(uint8_t sprite_id, int16_t x, int16_t y);
void sprite_set_velocity(uint8_t sprite_id, int16_t vx, int16_t vy);
void sprite_set_texture(uint8_t sprite_id, uint16_t* texture_data, uint8_t width, uint8_t height);
void sprite_set_animation(uint8_t sprite_id, uint8_t animation_id);
void sprite_set_layer(uint8_t sprite_id, uint8_t layer);
void sprite_set_blend_mode(uint8_t sprite_id, blend_mode_t mode);
void sprite_set_alpha(uint8_t sprite_id, uint8_t alpha);
void sprite_set_visibility(uint8_t sprite_id, bool visible);
void sprite_enable_collision(uint8_t sprite_id, bool enabled);

// Animation System
uint8_t animation_create(uint8_t frame_count, uint8_t* frames, uint16_t* durations, bool loop);
void animation_destroy(uint8_t animation_id);
void animation_start(uint8_t sprite_id);
void animation_stop(uint8_t sprite_id);
void animation_pause(uint8_t sprite_id);
void animation_set_frame(uint8_t sprite_id, uint8_t frame);

// Texture Management
uint8_t texture_load_from_data(uint16_t* data, uint16_t width, uint16_t height, uint8_t frames);
void texture_destroy(uint8_t texture_id);
uint16_t* texture_get_frame_data(uint8_t texture_id, uint8_t frame);

// Tilemap System
uint8_t tileset_create(uint16_t* texture_data, uint8_t tile_width, uint8_t tile_height, uint8_t tiles_per_row);
void tileset_destroy(uint8_t tileset_id);
uint8_t tilemap_create(uint8_t tileset_id, uint16_t width, uint16_t height, uint8_t layer);
void tilemap_destroy(uint8_t tilemap_id);
void tilemap_set_tile(uint8_t tilemap_id, uint16_t x, uint16_t y, uint8_t tile_index);
void tilemap_set_scroll(uint8_t tilemap_id, int16_t scroll_x, int16_t scroll_y);

// Camera System
void camera_set_position(int16_t x, int16_t y);
void camera_move(int16_t dx, int16_t dy);
void camera_follow_sprite(uint8_t sprite_id);

// Collision Detection
bool sprite_check_collision(uint8_t sprite1_id, uint8_t sprite2_id);
collision_event_t* get_collision_events(uint8_t* count);
void clear_collision_events(void);

// Particle Systems
uint8_t particle_system_create(float x, float y, uint16_t color, uint16_t spawn_rate);
void particle_system_destroy(uint8_t system_id);
void particle_system_emit(uint8_t system_id, uint8_t count);
void particle_system_set_position(uint8_t system_id, float x, float y);

// Rendering Primitives (extended from base display)
void graphics_draw_line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t color);
void graphics_draw_circle(int16_t x, int16_t y, uint8_t radius, uint16_t color);
void graphics_draw_circle_filled(int16_t x, int16_t y, uint8_t radius, uint16_t color);
void graphics_draw_triangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color);
void graphics_draw_triangle_filled(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color);

// Utility Functions
void graphics_enable_double_buffering(bool enabled);
void graphics_enable_vsync(bool enabled);
void graphics_enable_collision_detection(bool enabled);
uint16_t graphics_get_fps(void);
uint32_t graphics_get_frame_time(void);

// Color utilities
uint16_t rgb_to_rgb565(uint8_t r, uint8_t g, uint8_t b);
void rgb565_to_rgb(uint16_t color, uint8_t* r, uint8_t* g, uint8_t* b);
uint16_t blend_colors(uint16_t color1, uint16_t color2, uint8_t alpha);

#endif // GRAPHICS_ENGINE_H