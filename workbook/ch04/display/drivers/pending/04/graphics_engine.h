#ifndef GRAPHICS_ENGINE_H
#define GRAPHICS_ENGINE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "pico/stdlib.h"
#include "pico_display_2.hpp"

// config (display pack 2.0)
#define DISPLAY_WIDTH  320
#define DISPLAY_HEIGHT 240

// mem pool (try Pico 2 instead)
#define TEXTURE_POOL_SIZE    (128 * 1024)  // 128KB for textures
#define ANIMATION_POOL_SIZE  (32 * 1024)   // 32KB for animations

// resource limits (all static allocation)
#define MAX_SPRITES          64
#define MAX_ANIMATIONS       32
#define MAX_TEXTURES         MAX_SPRITES
#define MAX_TEXTURE_SLOTS    32
#define MAX_TILESETS         8
#define MAX_LAYERS           4
#define MAX_PARTICLES        256
#define MAX_PARTICLE_SYSTEMS 4

// sprite cleanup configuration
#define SPRITE_CLEANUP_MARGIN 64  // pixels outside screen before cleanup
#define SPRITE_CLEANUP_ENABLED_BY_DEFAULT true

// Enumerations
typedef enum {
    SPRITE_STATIC,
    SPRITE_ANIMATED,
    SPRITE_PHYSICS,
    SPRITE_PARTICLE
} sprite_type_t;

typedef enum {
    BLEND_NONE,
    BLEND_ALPHA,
    BLEND_ADDITIVE,
    BLEND_MULTIPLY
} blend_mode_t;

typedef enum {
    SPRITE_CLEANUP_NONE,           // Never auto-cleanup
    SPRITE_CLEANUP_OFF_SCREEN,     // Cleanup when off screen
    SPRITE_CLEANUP_FAR_OFF_SCREEN, // Cleanup when far off screen
    SPRITE_CLEANUP_TIMEOUT,        // Cleanup after timeout
    SPRITE_CLEANUP_INACTIVE        // Cleanup when inactive
} sprite_cleanup_mode_t;

// pool structure
typedef struct {
    uint8_t* data;
    size_t size;
    size_t used;
    bool initialized;
} memory_pool_t;

// texture structure (allocated from pool)
typedef struct {
    uint16_t* data;      // Points into texture pool
    uint16_t width;
    uint16_t height;
    uint8_t frame_count;
    size_t size;         // Total size in bytes
} texture_t;

// texture slot for memory management
typedef struct {
    texture_t texture;
    bool allocated;
    uint32_t last_used;  // Timestamp for LRU cleanup
    size_t size;
} texture_slot_t;

// animation slot for memory management
typedef struct {
    uint8_t* frame_sequence;
    uint16_t* frame_durations;
    uint8_t frame_count;
    bool allocated;
    size_t size;
} animation_slot_t;

// sprite structure
typedef struct {
    uint8_t id;
    sprite_type_t type;
    
    // Position and physics
    int16_t x, y;
    int16_t velocity_x, velocity_y;
    
    // Visual properties
    uint8_t texture_id;      // Index into texture slots
    uint8_t animation_id;    // Index into animation slots
    uint8_t current_frame;
    uint8_t layer;
    uint8_t alpha;
    blend_mode_t blend_mode;
    bool visible;
    bool collision_enabled;
    bool active;
    
    // Bounding box (for collision)
    uint8_t width, height;
    
    // Animation state
    uint32_t last_frame_time;
    uint16_t frame_duration;
    
    // Cleanup configuration
    sprite_cleanup_mode_t cleanup_mode;
    uint32_t creation_time;
    uint32_t timeout_ms;     // For SPRITE_CLEANUP_TIMEOUT mode
    bool auto_cleanup_enabled;
} sprite_t;

typedef struct {
    uint8_t id;
    uint8_t frame_count;
    uint8_t* frame_sequence;   // Points into animation pool
    uint16_t* frame_durations; // Points into animation pool
    uint8_t slot_id;           // Which animation slot this uses
    bool loop;
    bool active;
} animation_t;

typedef struct {
    texture_t* texture;      // Points to texture in pool
    uint8_t tile_width, tile_height;
    uint8_t tiles_per_row;
    bool active;
} tileset_t;

typedef struct {
    uint8_t* tile_map;       
    uint8_t tileset_id;
    uint16_t width, height;  
    int16_t scroll_x, scroll_y; 
    uint8_t layer;
    bool active;
    bool visible;
} tile_layer_t;

typedef struct {
    uint8_t id1, id2;
    uint32_t timestamp;
} collision_event_t;

// particle system (using static allocation)
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
    particle_t particles[MAX_PARTICLES / MAX_PARTICLE_SYSTEMS]; // divide particles among systems
    uint8_t max_particles;
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
    texture_t textures[MAX_SPRITES]; 
    tileset_t tilesets[MAX_TILESETS];
    tile_layer_t tile_layers[MAX_LAYERS];
    particle_system_t particle_systems[MAX_PARTICLE_SYSTEMS];
    
    // Memory pools
    memory_pool_t texture_pool;
    memory_pool_t animation_pool;
    texture_slot_t texture_slots[MAX_TEXTURE_SLOTS];
    animation_slot_t animation_slots[MAX_ANIMATIONS];
    
    // Static framebuffers (no dynamic allocation)
    uint16_t framebuffer[DISPLAY_WIDTH * DISPLAY_HEIGHT];
    uint16_t back_buffer[DISPLAY_WIDTH * DISPLAY_HEIGHT];
    
    // Camera
    int16_t camera_x, camera_y;
    
    // Collision detection
    collision_event_t collision_events[16];
    uint8_t collision_count;
    
    // Performance stats
    uint32_t frame_time_ms;
    uint32_t last_frame_time;
    uint16_t fps;
    uint32_t sprites_cleaned_up;
    uint32_t memory_allocations;
    uint32_t memory_allocation_failures;
    
    // Engine state
    bool double_buffering;
    bool collision_detection_enabled;
    bool vsync_enabled;
    bool auto_cleanup_enabled;
    
} graphics_engine_t;

// Core Engine
bool graphics_engine_init(void);
void graphics_engine_shutdown(void);
void graphics_engine_update(void);
void graphics_engine_render(void);
void graphics_engine_present(void);

// Memory Pool Management
bool memory_pool_init(memory_pool_t* pool, size_t size);
void memory_pool_shutdown(memory_pool_t* pool);
void* memory_pool_alloc(memory_pool_t* pool, size_t size, size_t alignment);
void memory_pool_free(memory_pool_t* pool, void* ptr, size_t size);
size_t memory_pool_get_used(memory_pool_t* pool);
size_t memory_pool_get_free(memory_pool_t* pool);
void memory_pool_defrag(memory_pool_t* pool); // Compact fragmented memory

// Texture Management with Static Pools
uint8_t texture_load_from_data(uint16_t* data, uint16_t width, uint16_t height, uint8_t frames);
bool texture_destroy(uint8_t texture_id);
uint16_t* texture_get_frame_data(uint8_t texture_id, uint8_t frame);
void texture_cleanup_unused(uint32_t max_age_ms); // Clean up old unused textures

// Animation Management with Static Pools  
uint8_t animation_create(uint8_t frame_count, uint8_t* frames, uint16_t* durations, bool loop);
bool animation_destroy(uint8_t animation_id);
void animation_start(uint8_t sprite_id);
void animation_stop(uint8_t sprite_id);
void animation_pause(uint8_t sprite_id);
void animation_set_frame(uint8_t sprite_id, uint8_t frame);

// Sprite Management with Auto-Cleanup
uint8_t sprite_create(int16_t x, int16_t y, uint8_t width, uint8_t height);
uint8_t sprite_create_with_cleanup(int16_t x, int16_t y, uint8_t width, uint8_t height, 
                                  sprite_cleanup_mode_t cleanup_mode, uint32_t timeout_ms);
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

// Sprite Cleanup Functions
void sprite_set_cleanup_mode(uint8_t sprite_id, sprite_cleanup_mode_t mode, uint32_t timeout_ms);
void sprite_enable_auto_cleanup(uint8_t sprite_id, bool enabled);
uint32_t sprite_cleanup_off_screen(void); // Returns number of sprites cleaned up
uint32_t sprite_cleanup_timed_out(void);  // Clean up sprites that have timed out
void sprite_cleanup_all_inactive(void);   // Clean up all inactive sprites

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

// Particle Systems (Static Allocation)
uint8_t particle_system_create(float x, float y, uint16_t color, uint16_t spawn_rate);
void particle_system_destroy(uint8_t system_id);
void particle_system_emit(uint8_t system_id, uint8_t count);
void particle_system_set_position(uint8_t system_id, float x, float y);

// Rendering Primitives 
void graphics_draw_line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t color);
void graphics_draw_circle(int16_t x, int16_t y, uint8_t radius, uint16_t color);
void graphics_draw_circle_filled(int16_t x, int16_t y, uint8_t radius, uint16_t color);
void graphics_draw_triangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color);
void graphics_draw_triangle_filled(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color);

// Utility Functions
void graphics_enable_double_buffering(bool enabled);
void graphics_enable_vsync(bool enabled);
void graphics_enable_collision_detection(bool enabled);
void graphics_enable_auto_cleanup(bool enabled);
uint16_t graphics_get_fps(void);
uint32_t graphics_get_frame_time(void);

// Memory and Performance Statistics
typedef struct {
    uint32_t sprites_active;
    uint32_t sprites_cleaned_up_total;
    uint32_t texture_pool_used;
    uint32_t texture_pool_free;
    uint32_t animation_pool_used;
    uint32_t animation_pool_free;
    uint32_t memory_allocations;
    uint32_t memory_allocation_failures;
    uint16_t fps;
    uint32_t frame_time_ms;
} graphics_stats_t;

void graphics_get_stats(graphics_stats_t* stats);
void graphics_print_stats(void);

// Color utilities
uint16_t rgb_to_rgb565(uint8_t r, uint8_t g, uint8_t b);
void rgb565_to_rgb(uint16_t color, uint8_t* r, uint8_t* g, uint8_t* b);
uint16_t blend_colors(uint16_t color1, uint16_t color2, uint8_t alpha);

#endif // GRAPHICS_ENGINE_H
