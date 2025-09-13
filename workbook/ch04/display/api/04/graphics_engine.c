#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// THE IDEA: NOT using dynamic memory allocation (malloc/free) for core engine structures
// PICO_PLATFORM=rp2350, RPI Pico 2, Pimironi Display Pack 2.0, C17 standard

#include "graphics_engine.h"
#include "pico/stdlib.h"
#include "pico/time.h"
#include "pico_display_2.hpp" // Assume? display_pack_init, display_pack_update, etc.

// Global engine state (now with static allocation)
static graphics_engine_t g_engine = {0};
static bool g_initialized = false;

// Static memory pools (no malloc/free!)
static uint8_t texture_pool_memory[TEXTURE_POOL_SIZE];
static uint8_t animation_pool_memory[ANIMATION_POOL_SIZE];

// Internal helper functions
static void update_sprite_animation(sprite_t* sprite);
static void render_sprite(sprite_t* sprite);
static void render_tilemap(tile_layer_t* layer);
static void update_particles(particle_system_t* system);
static void render_particles(particle_system_t* system);
static bool is_sprite_off_screen(sprite_t* sprite, int16_t margin);
static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y);
static void cleanup_sprites_automatic(void);
static uint16_t* get_render_target(void);

// Memory Pool Implementation
bool memory_pool_init(memory_pool_t* pool, size_t size) {
    if (!pool) return false;
    
    pool->data = (pool == &g_engine.texture_pool) ? texture_pool_memory : animation_pool_memory;
    pool->size = size;
    pool->used = 0;
    pool->initialized = true;
    
    // Clear the memory
    memset(pool->data, 0, size);
    
    return true;
}

void memory_pool_shutdown(memory_pool_t* pool) {
    if (!pool) return;
    pool->initialized = false;
    pool->used = 0;
}

void* memory_pool_alloc(memory_pool_t* pool, size_t size, size_t alignment) {
    if (!pool || !pool->initialized || size == 0) return NULL;
    
    // Align the current position
    size_t aligned_used = (pool->used + alignment - 1) & ~(alignment - 1);
    
    // Check if we have enough space
    if (aligned_used + size > pool->size) {
        printf("Memory pool allocation failed: requested %zu bytes, available %zu\n", 
               size, pool->size - aligned_used);
        g_engine.memory_allocation_failures++;
        return NULL;
    }
    
    void* ptr = pool->data + aligned_used;
    pool->used = aligned_used + size;
    g_engine.memory_allocations++;
    
    return ptr;
}

void memory_pool_free(memory_pool_t* pool, void* ptr, size_t size) {
    // Simple pool allocator doesn't support individual free operations
    // Memory is reclaimed when the pool is reset or defragmented
    // The idea at least
    (void)pool;
    (void)ptr;
    (void)size;
}

size_t memory_pool_get_used(memory_pool_t* pool) {
    return pool ? pool->used : 0;
}

size_t memory_pool_get_free(memory_pool_t* pool) {
    return pool ? (pool->size - pool->used) : 0;
}

void memory_pool_defrag(memory_pool_t* pool) {
    if (!pool || !pool->initialized) return;
    
    // For this simple implementation, we'll just reset and rebuild
    // In a more sophisticated version, we'd compact and move allocations
    
    if (pool == &g_engine.texture_pool) {
        // Rebuild texture allocations
        size_t new_used = 0;
        for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
            if (g_engine.texture_slots[i].allocated) {
                // Move texture data to new position
                void* new_pos = pool->data + new_used;
                if (g_engine.texture_slots[i].texture.data != new_pos) {
                    memmove(new_pos, g_engine.texture_slots[i].texture.data, g_engine.texture_slots[i].size);
                    g_engine.texture_slots[i].texture.data = (uint16_t*)new_pos;
                }
                new_used += g_engine.texture_slots[i].size;
            }
        }
        pool->used = new_used;
        printf("Texture pool defragmented: %zu bytes used\n", new_used);
    }
}

// Core Engine Functions
bool graphics_engine_init(void) {
    if (g_initialized) return true;
    
    printf("Init Graphics Engine V2 (Static Memory)...\n");
    
    // Initialize base display system
    if (!display_pack_init()) {
        printf("Failed to init display pack\n");
        return false;
    }
    
    // Initialize engine state (all static now!)
    memset(&g_engine, 0, sizeof(graphics_engine_t));
    
    // Initialize memory pools
    if (!memory_pool_init(&g_engine.texture_pool, TEXTURE_POOL_SIZE)) {
        printf("Failed to init texture pool\n");
        return false;
    }
    
    if (!memory_pool_init(&g_engine.animation_pool, ANIMATION_POOL_SIZE)) {
        printf("Failed to init animation pool\n");
        return false;
    }
    
    // Set defaults
    g_engine.double_buffering = true;
    g_engine.collision_detection_enabled = true;
    g_engine.vsync_enabled = true;
    g_engine.auto_cleanup_enabled = SPRITE_CLEANUP_ENABLED_BY_DEFAULT;
    g_engine.camera_x = 0;
    g_engine.camera_y = 0;
    
    // Initialize sprite pool
    for (int i = 0; i < MAX_SPRITES; i++) {
        g_engine.sprites[i].id = i;
        g_engine.sprites[i].active = false;
        g_engine.sprites[i].auto_cleanup_enabled = true;
        g_engine.sprites[i].cleanup_mode = SPRITE_CLEANUP_OFF_SCREEN;
        g_engine.sprites[i].timeout_ms = 5000; // 5 second default timeout
    }
    
    // Initialize animation pool
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        g_engine.animations[i].id = i;
        g_engine.animations[i].active = false;
    }
    
    // Initialize texture slots
    for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
        g_engine.texture_slots[i].allocated = false;
    }
    
    // Initialize particle systems with divided particle allocation
    uint8_t particles_per_system = MAX_PARTICLES / MAX_PARTICLE_SYSTEMS;
    for (int i = 0; i < MAX_PARTICLE_SYSTEMS; i++) {
        g_engine.particle_systems[i].max_particles = particles_per_system;
        g_engine.particle_systems[i].active = false;
    }
    
    // Clear framebuffers (static allocation)
    memset(g_engine.framebuffer, 0, sizeof(g_engine.framebuffer));
    memset(g_engine.back_buffer, 0, sizeof(g_engine.back_buffer));
    
    g_initialized = true;
    printf("Graphics Engine init successfully\n");
    printf("Memory pools: Texture=%dKB, Animation=%dKB\n", 
           TEXTURE_POOL_SIZE/1024, ANIMATION_POOL_SIZE/1024);
    return true;
}

void graphics_engine_shutdown(void) {
    if (!g_initialized) return;
    
    // Clean up all sprites
    for (int i = 0; i < MAX_SPRITES; i++) {
        if (g_engine.sprites[i].active) {
            sprite_destroy(i);
        }
    }
    
    // Clean up all animations
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (g_engine.animations[i].active) {
            animation_destroy(i);
        }
    }
    
    // Shutdown memory pools
    memory_pool_shutdown(&g_engine.texture_pool);
    memory_pool_shutdown(&g_engine.animation_pool);
    
    g_initialized = false;
    printf("Graphics Engine shutdown\n");
}

void graphics_engine_update(void) {
    if (!g_initialized) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    g_engine.frame_time_ms = current_time - g_engine.last_frame_time;
    g_engine.last_frame_time = current_time;
    
    // Update FPS counter
    static uint32_t fps_timer = 0;
    static uint16_t frame_count = 0;
    fps_timer += g_engine.frame_time_ms;
    frame_count++;
    if (fps_timer >= 1000) {
        g_engine.fps = frame_count;
        frame_count = 0;
        fps_timer = 0;
    }
    
    // Clear collision events from last frame
    g_engine.collision_count = 0;
    
    // Automatic sprite cleanup
    if (g_engine.auto_cleanup_enabled) {
        cleanup_sprites_automatic();
    }
    
    // Update sprites
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprite_t* sprite = &g_engine.sprites[i];
        if (!sprite->active) continue;
        
        // Update position with velocity
        if (sprite->velocity_x != 0 || sprite->velocity_y != 0) {
            sprite->x += sprite->velocity_x;
            sprite->y += sprite->velocity_y;
        }
        
        // Update animation
        if (sprite->animation_id < MAX_ANIMATIONS && 
            g_engine.animations[sprite->animation_id].active) {
            update_sprite_animation(sprite);
        }
        
        // Update texture usage timestamp
        if (sprite->texture_id < MAX_TEXTURE_SLOTS) {
            g_engine.texture_slots[sprite->texture_id].last_used = current_time;
        }
    }
    
    // Update particle systems
    for (int i = 0; i < MAX_PARTICLE_SYSTEMS; i++) {
        if (g_engine.particle_systems[i].active) {
            update_particles(&g_engine.particle_systems[i]);
        }
    }
    
    // Collision detection
    if (g_engine.collision_detection_enabled) {
        for (int i = 0; i < MAX_SPRITES; i++) {
            sprite_t* sprite1 = &g_engine.sprites[i];
            if (!sprite1->active || !sprite1->collision_enabled) continue;
            
            for (int j = i + 1; j < MAX_SPRITES; j++) {
                sprite_t* sprite2 = &g_engine.sprites[j];
                if (!sprite2->active || !sprite2->collision_enabled) continue;
                
                if (sprite_check_collision(i, j)) {
                    if (g_engine.collision_count < 16) {
                        g_engine.collision_events[g_engine.collision_count].id1 = i;
                        g_engine.collision_events[g_engine.collision_count].id2 = j;
                        g_engine.collision_events[g_engine.collision_count].timestamp = current_time;
                        g_engine.collision_count++;
                    }
                }
            }
        }
    }
}

void graphics_engine_render(void) {
    if (!g_initialized) return;
    
    uint16_t* target = get_render_target();
    memset(target, 0, DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t)); // Clear to black
    
    // Render layers in order
    for (uint8_t l = 0; l < MAX_LAYERS; l++) {
        // Render tilemaps on this layer
        for (int i = 0; i < MAX_LAYERS; i++) {
            tile_layer_t* tl = &g_engine.tile_layers[i];
            if (tl->active && tl->visible && tl->layer == l) {
                render_tilemap(tl);
            }
        }
        
        // Render sprites on this layer
        for (int i = 0; i < MAX_SPRITES; i++) {
            sprite_t* sprite = &g_engine.sprites[i];
            if (sprite->active && sprite->visible && sprite->layer == l) {
                render_sprite(sprite);
            }
        }
    }
    
    // Render particles (assume on top)
    for (int i = 0; i < MAX_PARTICLE_SYSTEMS; i++) {
        if (g_engine.particle_systems[i].active) {
            render_particles(&g_engine.particle_systems[i]);
        }
    }
}

void graphics_engine_present(void) {
    if (!g_initialized) return;
    
    if (g_engine.double_buffering) {
        // Swap buffers
        uint16_t* temp = g_engine.framebuffer;
        g_engine.framebuffer = g_engine.back_buffer;
        g_engine.back_buffer = temp;
    }
    
    // Assume display_pack_update is defined in pico_display_2.hpp
    display_pack_update(g_engine.framebuffer);
    
    if (g_engine.vsync_enabled) {
        // Assume display_pack_wait_vsync();
        display_pack_wait_vsync();
    }
}

// Texture Management with Static Pools
uint8_t texture_load_from_data(uint16_t* data, uint16_t width, uint16_t height, uint8_t frames) {
    size_t frame_size = width * height * sizeof(uint16_t);
    size_t total_size = frame_size * frames;
    
    int slot_id = -1;
    for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
        if (!g_engine.texture_slots[i].allocated) {
            slot_id = i;
            break;
        }
    }
    if (slot_id == -1) return 255;
    
    uint16_t* dest = (uint16_t*)memory_pool_alloc(&g_engine.texture_pool, total_size, 2);
    if (!dest) return 255;
    
    memcpy(dest, data, total_size);
    
    texture_slot_t* slot = &g_engine.texture_slots[slot_id];
    slot->texture.data = dest;
    slot->texture.width = width;
    slot->texture.height = height;
    slot->texture.frame_count = frames;
    slot->texture.size = total_size;
    slot->size = total_size;
    slot->allocated = true;
    slot->last_used = to_ms_since_boot(get_absolute_time());
    
    return slot_id;
}

bool texture_destroy(uint8_t texture_id) {
    if (texture_id >= MAX_TEXTURE_SLOTS || !g_engine.texture_slots[texture_id].allocated) return false;
    g_engine.texture_slots[texture_id].allocated = false;
    return true;
}

uint16_t* texture_get_frame_data(uint8_t texture_id, uint8_t frame) {
    if (texture_id >= MAX_TEXTURE_SLOTS || !g_engine.texture_slots[texture_id].allocated) return NULL;
    texture_t* tex = &g_engine.texture_slots[texture_id].texture;
    if (frame >= tex->frame_count) return NULL;
    return tex->data + (tex->width * tex->height * frame);
}

void texture_cleanup_unused(uint32_t max_age_ms) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
        texture_slot_t* slot = &g_engine.texture_slots[i];
        if (slot->allocated && (current_time - slot->last_used > max_age_ms)) {
            texture_destroy(i);
        }
    }
}

// Animation Management with Static Pools  
uint8_t animation_create(uint8_t frame_count, uint8_t* frames, uint16_t* durations, bool loop) {
    size_t seq_size = frame_count * sizeof(uint8_t);
    size_t dur_size = frame_count * sizeof(uint16_t);
    size_t total_size = seq_size + dur_size;
    
    int slot_id = -1;
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (!g_engine.animation_slots[i].allocated) {
            slot_id = i;
            break;
        }
    }
    if (slot_id == -1) return 255;
    
    uint8_t* dest = (uint8_t*)memory_pool_alloc(&g_engine.animation_pool, total_size, 1);
    if (!dest) return 255;
    
    memcpy(dest, frames, seq_size);
    memcpy(dest + seq_size, durations, dur_size);
    
    g_engine.animation_slots[slot_id].frame_sequence = dest;
    g_engine.animation_slots[slot_id].frame_durations = (uint16_t*)(dest + seq_size);
    g_engine.animation_slots[slot_id].frame_count = frame_count;
    g_engine.animation_slots[slot_id].allocated = true;
    g_engine.animation_slots[slot_id].size = total_size;
    
    int anim_id = -1;
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (!g_engine.animations[i].active) {
            anim_id = i;
            break;
        }
    }
    if (anim_id == -1) {
        g_engine.animation_slots[slot_id].allocated = false;
        return 255;
    }
    
    animation_t* anim = &g_engine.animations[anim_id];
    anim->frame_count = frame_count;
    anim->frame_sequence = g_engine.animation_slots[slot_id].frame_sequence;
    anim->frame_durations = g_engine.animation_slots[slot_id].frame_durations;
    anim->slot_id = slot_id;
    anim->loop = loop;
    anim->active = true;
    
    return anim_id;
}

bool animation_destroy(uint8_t animation_id) {
    if (animation_id >= MAX_ANIMATIONS || !g_engine.animations[animation_id].active) return false;
    animation_t* anim = &g_engine.animations[animation_id];
    uint8_t slot_id = anim->slot_id;
    anim->active = false;
    if (slot_id < MAX_ANIMATIONS) {
        g_engine.animation_slots[slot_id].allocated = false;
    }
    return true;
}

void animation_start(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    if (sprite->animation_id >= MAX_ANIMATIONS || !g_engine.animations[sprite->animation_id].active) return;
    animation_t* anim = &g_engine.animations[sprite->animation_id];
    anim->active = true;
    sprite->current_frame = 0;
    sprite->frame_duration = anim->frame_durations[0];
    sprite->last_frame_time = to_ms_since_boot(get_absolute_time());
}

void animation_stop(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    if (sprite->animation_id >= MAX_ANIMATIONS) return;
    g_engine.animations[sprite->animation_id].active = false;
    sprite->current_frame = 0;
}

void animation_pause(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    if (g_engine.sprites[sprite_id].animation_id >= MAX_ANIMATIONS) return;
    g_engine.animations[g_engine.sprites[sprite_id].animation_id].active = false;
}

void animation_set_frame(uint8_t sprite_id, uint8_t frame) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    if (sprite->animation_id >= MAX_ANIMATIONS || !g_engine.animations[sprite->animation_id].active) return;
    animation_t* anim = &g_engine.animations[sprite->animation_id];
    if (frame >= anim->frame_count) return;
    sprite->current_frame = frame;
    sprite->frame_duration = anim->frame_durations[frame];
    sprite->last_frame_time = to_ms_since_boot(get_absolute_time());
}

// Sprite Management with Auto-Cleanup
uint8_t sprite_create(int16_t x, int16_t y, uint8_t width, uint8_t height) {
    return sprite_create_with_cleanup(x, y, width, height, SPRITE_CLEANUP_OFF_SCREEN, 5000);
}

uint8_t sprite_create_with_cleanup(int16_t x, int16_t y, uint8_t width, uint8_t height, 
                                  sprite_cleanup_mode_t cleanup_mode, uint32_t timeout_ms) {
    for (int i = 0; i < MAX_SPRITES; i++) {
        if (!g_engine.sprites[i].active) {
            sprite_t* sprite = &g_engine.sprites[i];
            memset(sprite, 0, sizeof(sprite_t));
            
            sprite->id = i;
            sprite->x = x;
            sprite->y = y;
            sprite->width = width;
            sprite->height = height;
            sprite->active = true;
            sprite->visible = true;
            sprite->alpha = 255;
            sprite->blend_mode = BLEND_NONE;
            sprite->layer = 0;
            sprite->type = SPRITE_STATIC;
            sprite->creation_time = to_ms_since_boot(get_absolute_time());
            sprite->cleanup_mode = cleanup_mode;
            sprite->timeout_ms = timeout_ms;
            sprite->auto_cleanup_enabled = true;
            
            return i;
        }
    }
    return 255; // Invalid ID
}

void sprite_destroy(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES) return;
    
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    if (!sprite->active) return;
    
    // Mark texture slot as potentially unused
    if (sprite->texture_id < MAX_TEXTURE_SLOTS) {
        // Note: We don't immediately free the texture as other sprites might use it
        // Texture cleanup happens separately based on usage timestamps
    }
    
    sprite->active = false;
    g_engine.sprites_cleaned_up++;
}

// Sprite Cleanup Functions
void sprite_set_cleanup_mode(uint8_t sprite_id, sprite_cleanup_mode_t mode, uint32_t timeout_ms) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].cleanup_mode = mode;
    g_engine.sprites[sprite_id].timeout_ms = timeout_ms;
}

void sprite_enable_auto_cleanup(uint8_t sprite_id, bool enabled) {
    if (sprite_id >= MAX_SPRITES) return;
    g_engine.sprites[sprite_id].auto_cleanup_enabled = enabled;
}

uint32_t sprite_cleanup_off_screen(void) {
    uint32_t cleaned = 0;
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprite_t* sprite = &g_engine.sprites[i];
        if (!sprite->active || !sprite->auto_cleanup_enabled) continue;
        int16_t margin = 0;
        if (sprite->cleanup_mode == SPRITE_CLEANUP_OFF_SCREEN) {
            margin = 0;
        } else if (sprite->cleanup_mode == SPRITE_CLEANUP_FAR_OFF_SCREEN) {
            margin = SPRITE_CLEANUP_MARGIN;
        } else {
            continue;
        }
        if (is_sprite_off_screen(sprite, margin)) {
            sprite_destroy(i);
            cleaned++;
        }
    }
    return cleaned;
}

uint32_t sprite_cleanup_timed_out(void) {
    uint32_t cleaned = 0;
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprite_t* sprite = &g_engine.sprites[i];
        if (!sprite->active || !sprite->auto_cleanup_enabled) continue;
        if (sprite->cleanup_mode == SPRITE_CLEANUP_TIMEOUT && (current_time - sprite->creation_time > sprite->timeout_ms)) {
            sprite_destroy(i);
            cleaned++;
        }
    }
    return cleaned;
}

void sprite_cleanup_all_inactive(void) {
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprite_t* sprite = &g_engine.sprites[i];
        if (!sprite->active || !sprite->auto_cleanup_enabled) continue;
        if (sprite->cleanup_mode == SPRITE_CLEANUP_INACTIVE && !sprite->visible && sprite->velocity_x == 0 && sprite->velocity_y == 0) {
            sprite_destroy(i);
        }
    }
}

// Tilemap System
uint8_t tileset_create(uint16_t* texture_data, uint8_t tile_width, uint8_t tile_height, uint8_t tiles_per_row) {
    uint16_t width = tile_width * tiles_per_row;
    uint16_t height = tile_height; // Assuming single row for simplicity; adjust if multi-row needed?
    uint8_t tex_id = texture_load_from_data(texture_data, width, height, 1);
    if (tex_id == 255) return 255;
    
    int ts_id = -1;
    for (int i = 0; i < MAX_TILESETS; i++) {
        if (!g_engine.tilesets[i].active) {
            ts_id = i;
            break;
        }
    }
    if (ts_id == -1) {
        texture_destroy(tex_id);
        return 255;
    }
    
    g_engine.tilesets[ts_id].texture = &g_engine.texture_slots[tex_id].texture;
    g_engine.tilesets[ts_id].tile_width = tile_width;
    g_engine.tilesets[ts_id].tile_height = tile_height;
    g_engine.tilesets[ts_id].tiles_per_row = tiles_per_row;
    g_engine.tilesets[ts_id].active = true;
    
    return ts_id;
}

void tileset_destroy(uint8_t tileset_id) {
    if (tileset_id >= MAX_TILESETS || !g_engine.tilesets[tileset_id].active) return;
    texture_destroy(tileset_id); // Assuming texture_id == tileset_id for simplicity; adjust if needed
    g_engine.tilesets[tileset_id].active = false;
}

uint8_t tilemap_create(uint8_t tileset_id, uint16_t width, uint16_t height, uint8_t layer) {
    if (tileset_id >= MAX_TILESETS || !g_engine.tilesets[tileset_id].active) return 255;
    
    int id = -1;
    for (int i = 0; i < MAX_LAYERS; i++) {
        if (!g_engine.tile_layers[i].active) {
            id = i;
            break;
        }
    }
    if (id == -1) return 255;
    
    tile_layer_t* tl = &g_engine.tile_layers[id];
    tl->tile_map = (uint8_t*)malloc(width * height); // Using malloc as no dedicated pool .. CHANGE THIS!
    if (!tl->tile_map) return 255;
    memset(tl->tile_map, 0, width * height);
    tl->tileset_id = tileset_id;
    tl->width = width;
    tl->height = height;
    tl->layer = layer;
    tl->scroll_x = 0;
    tl->scroll_y = 0;
    tl->active = true;
    tl->visible = true;
    
    return id;
}

void tilemap_destroy(uint8_t tilemap_id) {
    if (tilemap_id >= MAX_LAYERS || !g_engine.tile_layers[tilemap_id].active) return;
    free(g_engine.tile_layers[tilemap_id].tile_map);
    g_engine.tile_layers[tilemap_id].active = false;
}

void tilemap_set_tile(uint8_t tilemap_id, uint16_t x, uint16_t y, uint8_t tile_index) {
    if (tilemap_id >= MAX_LAYERS || !g_engine.tile_layers[tilemap_id].active) return;
    tile_layer_t* tl = &g_engine.tile_layers[tilemap_id];
    if (x >= tl->width || y >= tl->height) return;
    tl->tile_map[y * tl->width + x] = tile_index;
}

void tilemap_set_scroll(uint8_t tilemap_id, int16_t scroll_x, int16_t scroll_y) {
    if (tilemap_id >= MAX_LAYERS || !g_engine.tile_layers[tilemap_id].active) return;
    g_engine.tile_layers[tilemap_id].scroll_x = scroll_x;
    g_engine.tile_layers[tilemap_id].scroll_y = scroll_y;
}

// Camera System
void camera_set_position(int16_t x, int16_t y) {
    g_engine.camera_x = x;
    g_engine.camera_y = y;
}

void camera_move(int16_t dx, int16_t dy) {
    g_engine.camera_x += dx;
    g_engine.camera_y += dy;
}

void camera_follow_sprite(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    g_engine.camera_x = sprite->x - DISPLAY_WIDTH / 2 + sprite->width / 2;
    g_engine.camera_y = sprite->y - DISPLAY_HEIGHT / 2 + sprite->height / 2;
}

// Collision Detection
bool sprite_check_collision(uint8_t sprite1_id, uint8_t sprite2_id) {
    if (sprite1_id >= MAX_SPRITES || sprite2_id >= MAX_SPRITES) return false;
    sprite_t* s1 = &g_engine.sprites[sprite1_id];
    sprite_t* s2 = &g_engine.sprites[sprite2_id];
    if (!s1->active || !s2->active) return false;
    if (s1->x + s1->width < s2->x || s1->x > s2->x + s2->width ||
        s1->y + s1->height < s2->y || s1->y > s2->y + s2->height) {
        return false;
    }
    return true;
}

collision_event_t* get_collision_events(uint8_t* count) {
    *count = g_engine.collision_count;
    return g_engine.collision_events;
}

void clear_collision_events(void) {
    g_engine.collision_count = 0;
}

// Particle Systems (Static Allocation)
uint8_t particle_system_create(float x, float y, uint16_t color, uint16_t spawn_rate) {
    int id = -1;
    for (int i = 0; i < MAX_PARTICLE_SYSTEMS; i++) {
        if (!g_engine.particle_systems[i].active) {
            id = i;
            break;
        }
    }
    if (id == -1) return 255;
    
    particle_system_t* ps = &g_engine.particle_systems[id];
    memset(ps, 0, sizeof(particle_system_t));
    ps->spawn_x = x;
    ps->spawn_y = y;
    ps->color = color;
    ps->spawn_rate = spawn_rate;
    ps->last_spawn = to_ms_since_boot(get_absolute_time());
    ps->spawn_velocity_range = 2.0f;
    ps->particle_life = 1000;
    ps->max_particles = MAX_PARTICLES / MAX_PARTICLE_SYSTEMS;
    ps->active = true;
    
    return id;
}

void particle_system_destroy(uint8_t system_id) {
    if (system_id >= MAX_PARTICLE_SYSTEMS) return;
    g_engine.particle_systems[system_id].active = false;
}

void particle_system_emit(uint8_t system_id, uint8_t count) {
    if (system_id >= MAX_PARTICLE_SYSTEMS || !g_engine.particle_systems[system_id].active) return;
    particle_system_t* ps = &g_engine.particle_systems[system_id];
    for (int i = 0; i < count && ps->active_count < ps->max_particles; i++) {
        particle_t* p = &ps->particles[ps->active_count++];
        p->x = ps->spawn_x;
        p->y = ps->spawn_y;
        p->velocity_x = (rand() % (int)(ps->spawn_velocity_range * 2) - ps->spawn_velocity_range);
        p->velocity_y = (rand() % (int)(ps->spawn_velocity_range * 2) - ps->spawn_velocity_range);
        p->acceleration_x = 0;
        p->acceleration_y = 0;
        p->color = ps->color;
        p->alpha = 255;
        p->life_time = 0;
        p->max_life = ps->particle_life;
        p->active = true;
    }
}

void particle_system_set_position(uint8_t system_id, float x, float y) {
    if (system_id >= MAX_PARTICLE_SYSTEMS) return;
    particle_system_t* ps = &g_engine.particle_systems[system_id];
    ps->spawn_x = x;
    ps->spawn_y = y;
}

// Rendering Primitives 
void graphics_draw_line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t color) {
    uint16_t* target = get_render_target();
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = x0 < x1 ? 1 : -1;
    int sy = y0 < y1 ? 1 : -1;
    int err = (dx > dy ? dx : -dy) / 2;
    int e2;
    while (true) {
        if (x0 >= 0 && x0 < DISPLAY_WIDTH && y0 >= 0 && y0 < DISPLAY_HEIGHT) {
            target[y0 * DISPLAY_WIDTH + x0] = color;
        }
        if (x0 == x1 && y0 == y1) break;
        e2 = err;
        if (e2 > -dx) { err -= dy; x0 += sx; }
        if (e2 < dy) { err += dx; y0 += sy; }
    }
}

void graphics_draw_circle(int16_t x, int16_t y, uint8_t radius, uint16_t color) {
    uint16_t* target = get_render_target();
    int f = 1 - radius;
    int ddF_x = 0;
    int ddF_y = -2 * radius;
    int px = 0;
    int py = radius;
    if (x >= 0 && x < DISPLAY_WIDTH && y + radius >= 0 && y + radius < DISPLAY_HEIGHT) target[(y + radius) * DISPLAY_WIDTH + x] = color;
    if (x >= 0 && x < DISPLAY_WIDTH && y - radius >= 0 && y - radius < DISPLAY_HEIGHT) target[(y - radius) * DISPLAY_WIDTH + x] = color;
    if (x + radius >= 0 && x + radius < DISPLAY_WIDTH && y >= 0 && y < DISPLAY_HEIGHT) target[y * DISPLAY_WIDTH + x + radius] = color;
    if (x - radius >= 0 && x - radius < DISPLAY_WIDTH && y >= 0 && y < DISPLAY_HEIGHT) target[y * DISPLAY_WIDTH + x - radius] = color;
    while (px < py) {
        px++;
        if (f >= 0) {
            py--;
            ddF_y += 2;
            f += ddF_y;
        }
        ddF_x += 2;
        f += ddF_x + 1;
        if (x + px >= 0 && x + px < DISPLAY_WIDTH && y + py >= 0 && y + py < DISPLAY_HEIGHT) target[(y + py) * DISPLAY_WIDTH + x + px] = color;
        if (x - px >= 0 && x - px < DISPLAY_WIDTH && y + py >= 0 && y + py < DISPLAY_HEIGHT) target[(y + py) * DISPLAY_WIDTH + x - px] = color;
        if (x + px >= 0 && x + px < DISPLAY_WIDTH && y - py >= 0 && y - py < DISPLAY_HEIGHT) target[(y - py) * DISPLAY_WIDTH + x + px] = color;
        if (x - px >= 0 && x - px < DISPLAY_WIDTH && y - py >= 0 && y - py < DISPLAY_HEIGHT) target[(y - py) * DISPLAY_WIDTH + x - px] = color;
        if (x + py >= 0 && x + py < DISPLAY_WIDTH && y + px >= 0 && y + px < DISPLAY_HEIGHT) target[(y + px) * DISPLAY_WIDTH + x + py] = color;
        if (x - py >= 0 && x - py < DISPLAY_WIDTH && y + px >= 0 && y + px < DISPLAY_HEIGHT) target[(y + px) * DISPLAY_WIDTH + x - py] = color;
        if (x + py >= 0 && x + py < DISPLAY_WIDTH && y - px >= 0 && y - px < DISPLAY_HEIGHT) target[(y - px) * DISPLAY_WIDTH + x + py] = color;
        if (x - py >= 0 && x - py < DISPLAY_WIDTH && y - px >= 0 && y - px < DISPLAY_HEIGHT) target[(y - px) * DISPLAY_WIDTH + x - py] = color;
    }
}

void graphics_draw_circle_filled(int16_t x, int16_t y, uint8_t radius, uint16_t color) {
    uint16_t* target = get_render_target();
    for (int dy = -radius; dy <= radius; dy++) {
        int half_width = (int)sqrt(radius * radius - dy * dy);
        for (int dx = -half_width; dx <= half_width; dx++) {
            int px = x + dx;
            int py = y + dy;
            if (px >= 0 && px < DISPLAY_WIDTH && py >= 0 && py < DISPLAY_HEIGHT) {
                target[py * DISPLAY_WIDTH + px] = color;
            }
        }
    }
}

void graphics_draw_triangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color) {
    graphics_draw_line(x0, y0, x1, y1, color);
    graphics_draw_line(x1, y1, x2, y2, color);
    graphics_draw_line(x2, y2, x0, y0, color);
}

void graphics_draw_triangle_filled(int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t x2, int16_t y2, uint16_t color) {
    uint16_t* target = get_render_target();
    // Sort by y
    if (y0 > y1) { int16_t temp = y0; y0 = y1; y1 = temp; temp = x0; x0 = x1; x1 = temp; }
    if (y0 > y2) { int16_t temp = y0; y0 = y2; y2 = temp; temp = x0; x0 = x2; x2 = temp; }
    if (y1 > y2) { int16_t temp = y1; y1 = y2; y2 = temp; temp = x1; x1 = x2; x2 = temp; }
    int total_height = y2 - y0;
    for (int i = 0; i < total_height; i++) {
        bool second_half = i > y1 - y0 || y1 == y0;
        int segment_height = second_half ? y2 - y1 : y1 - y0;
        float alpha = (float)i / total_height;
        float beta = (float)(i - (second_half ? y1 - y0 : 0)) / segment_height;
        int A_x = x0 + (x2 - x0) * alpha;
        int B_x = second_half ? x1 + (x2 - x1) * beta : x0 + (x1 - x0) * beta;
        int A_y = y0 + i;
        if (A_x > B_x) { int temp = A_x; A_x = B_x; B_x = temp; }
        for (int j = A_x; j <= B_x; j++) {
            if (j >= 0 && j < DISPLAY_WIDTH && A_y >= 0 && A_y < DISPLAY_HEIGHT) {
                target[A_y * DISPLAY_WIDTH + j] = color;
            }
        }
    }
}

// Utility Functions
void graphics_enable_double_buffering(bool enabled) {
    g_engine.double_buffering = enabled;
}

void graphics_enable_vsync(bool enabled) {
    g_engine.vsync_enabled = enabled;
}

void graphics_enable_collision_detection(bool enabled) {
    g_engine.collision_detection_enabled = enabled;
}

void graphics_enable_auto_cleanup(bool enabled) {
    g_engine.auto_cleanup_enabled = enabled;
}

uint16_t graphics_get_fps(void) {
    return g_engine.fps;
}

uint32_t graphics_get_frame_time(void) {
    return g_engine.frame_time_ms;
}

// Memory and Performance Statistics
void graphics_get_stats(graphics_stats_t* stats) {
    stats->sprites_active = 0;
    for (int i = 0; i < MAX_SPRITES; i++) {
        if (g_engine.sprites[i].active) stats->sprites_active++;
    }
    stats->sprites_cleaned_up_total = g_engine.sprites_cleaned_up;
    stats->texture_pool_used = memory_pool_get_used(&g_engine.texture_pool);
    stats->texture_pool_free = memory_pool_get_free(&g_engine.texture_pool);
    stats->animation_pool_used = memory_pool_get_used(&g_engine.animation_pool);
    stats->animation_pool_free = memory_pool_get_free(&g_engine.animation_pool);
    stats->memory_allocations = g_engine.memory_allocations;
    stats->memory_allocation_failures = g_engine.memory_allocation_failures;
    stats->fps = g_engine.fps;
    stats->frame_time_ms = g_engine.frame_time_ms;
}

void graphics_print_stats(void) {
    graphics_stats_t stats;
    graphics_get_stats(&stats);
    printf("Graphics Stats:\n");
    printf("Active Sprites: %u\n", stats.sprites_active);
    printf("Cleaned Up Sprites: %u\n", stats.sprites_cleaned_up_total);
    printf("Texture Pool: %u/%u bytes used\n", stats.texture_pool_used, stats.texture_pool_used + stats.texture_pool_free);
    printf("Animation Pool: %u/%u bytes used\n", stats.animation_pool_used, stats.animation_pool_used + stats.animation_pool_free);
    printf("Memory Allocations: %u (%u failures)\n", stats.memory_allocations, stats.memory_allocation_failures);
    printf("FPS: %u, Frame Time: %ums\n", stats.fps, stats.frame_time_ms);
}

// Color utilities
uint16_t rgb_to_rgb565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

void rgb565_to_rgb(uint16_t color, uint8_t* r, uint8_t* g, uint8_t* b) {
    *r = (color >> 8) & 0xF8;
    *g = (color >> 3) & 0xFC;
    *b = (color << 3) & 0xF8;
}

uint16_t blend_colors(uint16_t color1, uint16_t color2, uint8_t alpha) {
    if (alpha == 255) return color2;
    if (alpha == 0) return color1;
    uint8_t r1, g1, b1, r2, g2, b2;
    rgb565_to_rgb(color1, &r1, &g1, &b1);
    rgb565_to_rgb(color2, &r2, &g2, &b2);
    uint8_t inv_alpha = 255 - alpha;
    uint8_t r = (r1 * inv_alpha + r2 * alpha) / 255;
    uint8_t g = (g1 * inv_alpha + g2 * alpha) / 255;
    uint8_t b = (b1 * inv_alpha + b2 * alpha) / 255;
    return rgb_to_rgb565(r, g, b);
}

// Internal helpers
static void cleanup_sprites_automatic(void) {
    sprite_cleanup_off_screen();
    sprite_cleanup_timed_out();
    sprite_cleanup_all_inactive();
}

static bool is_sprite_off_screen(sprite_t* sprite, int16_t margin) {
    int16_t screen_x = sprite->x - g_engine.camera_x;
    int16_t screen_y = sprite->y - g_engine.camera_y;
    if (screen_x > DISPLAY_WIDTH + margin ||
        screen_x + sprite->width < -margin ||
        screen_y > DISPLAY_HEIGHT + margin ||
        screen_y + sprite->height < -margin) {
        return true;
    }
    return false;
}

static void update_sprite_animation(sprite_t* sprite) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    if (current_time - sprite->last_frame_time < sprite->frame_duration) return;
    animation_t* anim = &g_engine.animations[sprite->animation_id];
    if (!anim->active) return;
    uint8_t next_frame = sprite->current_frame + 1;
    if (next_frame >= anim->frame_count) {
        if (anim->loop) {
            next_frame = 0;
        } else {
            anim->active = false;
            return;
        }
    }
    sprite->current_frame = next_frame;
    sprite->frame_duration = anim->frame_durations[next_frame];
    sprite->last_frame_time = current_time;
}

static uint16_t* get_render_target(void) {
    return g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;
}

static void render_sprite(sprite_t* sprite) {
    uint16_t* target = get_render_target();
    texture_t* tex = &g_engine.texture_slots[sprite->texture_id].texture;
    if (!tex) return;
    int16_t screen_x = sprite->x - g_engine.camera_x;
    int16_t screen_y = sprite->y - g_engine.camera_y;
    uint8_t tex_frame = 0;
    if (sprite->animation_id < MAX_ANIMATIONS && g_engine.animations[sprite->animation_id].active) {
        animation_t* anim = &g_engine.animations[sprite->animation_id];
        tex_frame = anim->frame_sequence[sprite->current_frame];
    }
    uint16_t* frame_data = texture_get_frame_data(sprite->texture_id, tex_frame);
    if (!frame_data) return;
    for (int dy = 0; dy < tex->height; dy++) {
        for (int dx = 0; dx < tex->width; dx++) {
            int px = screen_x + dx;
            int py = screen_y + dy;
            if (px < 0 || px >= DISPLAY_WIDTH || py < 0 || py >= DISPLAY_HEIGHT) continue;
            uint16_t color = frame_data[dy * tex->width + dx];
            if (color == 0) continue; // Transparent
            if (sprite->blend_mode == BLEND_ALPHA) {
                uint16_t bg = target[py * DISPLAY_WIDTH + px];
                color = blend_colors(bg, color, sprite->alpha);
            } // Add other blend modes as needed
            target[py * DISPLAY_WIDTH + px] = color;
        }
    }
}

static void render_tilemap(tile_layer_t* layer) {
    uint16_t* target = get_render_target();
    tileset_t* ts = &g_engine.tilesets[layer->tileset_id];
    int16_t start_x = (g_engine.camera_x + layer->scroll_x) % ts->tile_width;
    int16_t start_y = (g_engine.camera_y + layer->scroll_y) % ts->tile_height;
    int start_tile_x = (g_engine.camera_x + layer->scroll_x) / ts->tile_width;
    int start_tile_y = (g_engine.camera_y + layer->scroll_y) / ts->tile_height;
    int tiles_visible_x = (DISPLAY_WIDTH / ts->tile_width) + 2;
    int tiles_visible_y = (DISPLAY_HEIGHT / ts->tile_height) + 2;
    for (int ty = 0; ty < tiles_visible_y; ty++) {
        for (int tx = 0; tx < tiles_visible_x; tx++) {
            int tile_x = (start_tile_x + tx) % layer->width;
            int tile_y = (start_tile_y + ty) % layer->height;
            uint8_t tile_index = layer->tile_map[tile_y * layer->width + tile_x];
            if (tile_index == 0) continue;
            int tile_row = tile_index / ts->tiles_per_row;
            int tile_col = tile_index % ts->tiles_per_row;
            uint16_t* tile_data = ts->texture->data + (tile_row * ts->texture->width * ts->tile_height) + (tile_col * ts->tile_width);
            int screen_x = tx * ts->tile_width - start_x;
            int screen_y = ty * ts->tile_height - start_y;
            for (int dy = 0; dy < ts->tile_height; dy++) {
                for (int dx = 0; dx < ts->tile_width; dx++) {
                    int px = screen_x + dx;
                    int py = screen_y + dy;
                    if (px < 0 || px >= DISPLAY_WIDTH || py < 0 || py >= DISPLAY_HEIGHT) continue;
                    uint16_t color = tile_data[dy * ts->texture->width + dx];
                    if (color == 0) continue;
                    target[py * DISPLAY_WIDTH + px] = color;
                }
            }
        }
    }
}

static void update_particles(particle_system_t* system) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    if (current_time - system->last_spawn >= system->spawn_rate && system->active_count < system->max_particles) {
        particle_t* p = &system->particles[system->active_count];
        p->x = system->spawn_x;
        p->y = system->spawn_y;
        p->velocity_x = (rand() % (int)(system->spawn_velocity_range * 2) - system->spawn_velocity_range);
        p->velocity_y = (rand() % (int)(system->spawn_velocity_range * 2) - system->spawn_velocity_range);
        p->acceleration_x = 0;
        p->acceleration_y = 0.1f; // Slight gravity
        p->color = system->color;
        p->alpha = 255;
        p->life_time = 0;
        p->max_life = system->particle_life;
        p->active = true;
        system->active_count++;
        system->last_spawn = current_time;
    }
    for (int i = 0; i < system->active_count; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;
        p->velocity_x += p->acceleration_x;
        p->velocity_y += p->acceleration_y;
        p->x += p->velocity_x;
        p->y += p->velocity_y;
        p->life_time += g_engine.frame_time_ms;
        if (p->life_time > p->max_life) {
            p->active = false;
            system->particles[i] = system->particles[--system->active_count];
            i--;
        } else {
            p->alpha = (uint8_t)(255 * (1.0f - (float)p->life_time / p->max_life));
        }
    }
}

static void render_particles(particle_system_t* system) {
    uint16_t* target = get_render_target();
    for (int i = 0; i < system->active_count; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;
        int16_t screen_x = (int16_t)p->x - g_engine.camera_x;
        int16_t screen_y = (int16_t)p->y - g_engine.camera_y;
        if (screen_x < 0 || screen_x >= DISPLAY_WIDTH || screen_y < 0 || screen_y >= DISPLAY_HEIGHT) continue;
        uint16_t color = blend_colors(target[screen_y * DISPLAY_WIDTH + screen_x], p->color, p->alpha);
        target[screen_y * DISPLAY_WIDTH + screen_x] = color;
    }
}

static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y) {
    // Simple point sampling (no scaling implemented here)
    uint16_t* data = texture->data + (frame * texture->width * texture->height);
    return data[y * texture->width + x];
}

void sprite_set_position(uint8_t sprite_id, int16_t x, int16_t y) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].x = x;
    g_engine.sprites[sprite_id].y = y;
}

void sprite_set_velocity(uint8_t sprite_id, int16_t vx, int16_t vy) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].velocity_x = vx;
    g_engine.sprites[sprite_id].velocity_y = vy;
}

void sprite_set_texture(uint8_t sprite_id, uint16_t* texture_data, uint8_t width, uint8_t height) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    uint8_t tex_id = texture_load_from_data(texture_data, width, height, 1);
    if (tex_id == 255) return;
    g_engine.sprites[sprite_id].texture_id = tex_id;
    g_engine.sprites[sprite_id].width = width;
    g_engine.sprites[sprite_id].height = height;
}

void sprite_set_animation(uint8_t sprite_id, uint8_t animation_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    if (animation_id >= MAX_ANIMATIONS || !g_engine.animations[animation_id].active) return;
    g_engine.sprites[sprite_id].animation_id = animation_id;
    g_engine.sprites[sprite_id].type = SPRITE_ANIMATED;
    animation_start(sprite_id);
}

void sprite_set_layer(uint8_t sprite_id, uint8_t layer) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].layer = layer;
}

void sprite_set_blend_mode(uint8_t sprite_id, blend_mode_t mode) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].blend_mode = mode;
}

void sprite_set_alpha(uint8_t sprite_id, uint8_t alpha) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].alpha = alpha;
}

void sprite_set_visibility(uint8_t sprite_id, bool visible) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].visible = visible;
}

void sprite_enable_collision(uint8_t sprite_id, bool enabled) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].collision_enabled = enabled;
}

