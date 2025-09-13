#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "graphics_engine.h"


// Global engine state (now with static allocation)
static graphics_engine_t g_engine = { 0 };
static bool g_initialized = false;


// Static memory pools (no malloc/free!)
static uint8_t texture_pool_memory[TEXTURE_POOL_SIZE];
static uint8_t animation_pool_memory[ANIMATION_POOL_SIZE];


// Forward declarations for internal functions
static void update_sprite_animation(sprite_t* sprite);
static void render_sprite(sprite_t* sprite);
static void render_tilemap(tile_layer_t* layer);
static void update_particles(particle_system_t* system);
static void render_particles(particle_system_t* system);
static bool is_sprite_off_screen(sprite_t* sprite, int16_t margin);
static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y);
static void cleanup_sprites_automatic(void);


// Helper function implementations
static bool is_sprite_off_screen(sprite_t* sprite, int16_t margin) {
    if (!sprite) return false;
    
    int16_t left = -margin - sprite->width;
    int16_t right = DISPLAY_WIDTH + margin;
    int16_t top = -margin - sprite->height;
    int16_t bottom = DISPLAY_HEIGHT + margin;
    
    return (sprite->x < left || sprite->x > right || 
            sprite->y < top || sprite->y > bottom);
}


// Animation helper functions
static void update_sprite_animation(sprite_t* sprite) {
    if (!sprite || sprite->animation_id >= MAX_ANIMATIONS) return;
    
    animation_t* anim = &g_engine.animations[sprite->animation_id];
    if (!anim->active || anim->frame_count == 0) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Check if it's time to advance frame
    if (current_time - sprite->last_frame_time >= sprite->frame_duration) {
        sprite->current_frame++;
        
        if (sprite->current_frame >= anim->frame_count) {
            if (anim->loop) {
                sprite->current_frame = 0;
            } else {
                sprite->current_frame = anim->frame_count - 1;
            }
        }
        
        // Update frame duration for next frame
        if (anim->frame_durations) {
            sprite->frame_duration = anim->frame_durations[sprite->current_frame];
        }
        
        sprite->last_frame_time = current_time;
    }
}


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
    // Simple pool allocator doesn't
    // support individual free operations
    // Memory is reclaimed when the pool
    // is reset or defragmented
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
    
    printf("Initializing Graphics Engine V2 (Static Memory)...\n");
    
    // Initialize base display system
    if (!display_pack_init()) {
        printf("Failed to initialize display pack\n");
        return false;
    }
    
    // Initialize engine state (all static now!)
    memset(&g_engine, 0, sizeof(graphics_engine_t));
    
    // Initialize memory pools
    if (!memory_pool_init(&g_engine.texture_pool, TEXTURE_POOL_SIZE)) {
        printf("Failed to initialize texture pool\n");
        return false;
    }
    
    if (!memory_pool_init(&g_engine.animation_pool, ANIMATION_POOL_SIZE)) {
        printf("Failed to initialize animation pool\n");
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
    printf("Graphics Engine V2 initialized successfully\n");
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
    printf("Graphics Engine V2 shutdown\n");
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


// Texture Management
uint8_t texture_load_from_data(uint16_t* data, uint16_t width, uint16_t height, uint8_t frames) {
    if (!data || width == 0 || height == 0 || frames == 0) return 255;
    
    size_t texture_size = sizeof(uint16_t) * width * height * frames;
    
    // Find free texture slot
    for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
        if (!g_engine.texture_slots[i].allocated) {
            // Allocate from texture pool
            void* tex_data = memory_pool_alloc(&g_engine.texture_pool, texture_size, 4);
            if (!tex_data) {
                printf("Failed to allocate texture memory: %zu bytes needed\n", texture_size);
                return 255;
            }
            
            // Copy texture data
            memcpy(tex_data, data, texture_size);
            
            // Set up texture slot
            g_engine.texture_slots[i].texture.data = (uint16_t*)tex_data;
            g_engine.texture_slots[i].texture.width = width;
            g_engine.texture_slots[i].texture.height = height;
            g_engine.texture_slots[i].texture.frame_count = frames;
            g_engine.texture_slots[i].texture.size = texture_size;
            g_engine.texture_slots[i].allocated = true;
            g_engine.texture_slots[i].size = texture_size;
            g_engine.texture_slots[i].last_used = to_ms_since_boot(get_absolute_time());
            
            return i;
        }
    }
    
    printf("No free texture slots available\n");
    return 255;
}


bool texture_destroy(uint8_t texture_id) {
    if (texture_id >= MAX_TEXTURE_SLOTS || !g_engine.texture_slots[texture_id].allocated) {
        return false;
    }
    
    // Mark slot as free (memory will be reclaimed during defrag)
    g_engine.texture_slots[texture_id].allocated = false;
    return true;
}


uint16_t* texture_get_frame_data(uint8_t texture_id, uint8_t frame) {
    if (texture_id >= MAX_TEXTURE_SLOTS || !g_engine.texture_slots[texture_id].allocated) {
        return NULL;
    }
    
    texture_t* tex = &g_engine.texture_slots[texture_id].texture;
    if (frame >= tex->frame_count) return NULL;
    
    size_t frame_size = tex->width * tex->height;
    return tex->data + (frame * frame_size);
}


void texture_cleanup_unused(uint32_t max_age_ms) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    for (int i = 0; i < MAX_TEXTURE_SLOTS; i++) {
        if (g_engine.texture_slots[i].allocated) {
            uint32_t age = current_time - g_engine.texture_slots[i].last_used;
            if (age > max_age_ms) {
                texture_destroy(i);
            }
        }
    }
}


// Animation Management
uint8_t animation_create(uint8_t frame_count, uint8_t* frames, uint16_t* durations, bool loop) {
    if (frame_count == 0 || !frames || !durations) return 255;
    
    // Find free animation slot
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (!g_engine.animations[i].active) {
            size_t frames_size = sizeof(uint8_t) * frame_count;
            size_t durations_size = sizeof(uint16_t) * frame_count;
            
            // Allocate from animation pool
            void* frames_data = memory_pool_alloc(&g_engine.animation_pool, frames_size, 1);
            if (!frames_data) return 255;
            
            void* durations_data = memory_pool_alloc(&g_engine.animation_pool, durations_size, 2);
            if (!durations_data) return 255;
            
            // Copy animation data
            memcpy(frames_data, frames, frames_size);
            memcpy(durations_data, durations, durations_size);
            
            // Set up animation
            g_engine.animations[i].id = i;
            g_engine.animations[i].frame_count = frame_count;
            g_engine.animations[i].frame_sequence = (uint8_t*)frames_data;
            g_engine.animations[i].frame_durations = (uint16_t*)durations_data;
            g_engine.animations[i].loop = loop;
            g_engine.animations[i].active = true;
            g_engine.animations[i].slot_id = i;
            
            return i;
        }
    }
    return 255;
}


bool animation_destroy(uint8_t animation_id) {
    if (animation_id >= MAX_ANIMATIONS || !g_engine.animations[animation_id].active) {
        return false;
    }
    
    g_engine.animations[animation_id].active = false;
    return true;
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


// Sprite property setters
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
    
    // Load texture and assign to sprite
    uint8_t tex_id = texture_load_from_data(texture_data, width, height, 1);
    if (tex_id != 255) {
        g_engine.sprites[sprite_id].texture_id = tex_id;
        g_engine.sprites[sprite_id].width = width;
        g_engine.sprites[sprite_id].height = height;
    }
}


void sprite_set_animation(uint8_t sprite_id, uint8_t animation_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    if (animation_id >= MAX_ANIMATIONS || !g_engine.animations[animation_id].active) return;
    
    g_engine.sprites[sprite_id].animation_id = animation_id;
    g_engine.sprites[sprite_id].current_frame = 0;
    g_engine.sprites[sprite_id].last_frame_time = to_ms_since_boot(get_absolute_time());
    
    if (g_engine.animations[animation_id].frame_durations) {
        g_engine.sprites[sprite_id].frame_duration = g_engine.animations[animation_id].frame_durations[0];
    }
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
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    for (int i = 0; i < MAX_SPRITES; i++) {
        sprite_t* sprite = &g_engine.sprites[i];
        if (!sprite->active || !sprite->auto_cleanup_enabled) continue;
        
        bool should_cleanup = false;
        
        switch (sprite->cleanup_mode) {
            case SPRITE_CLEANUP_OFF_SCREEN:
                should_cleanup = is_sprite_off_screen(sprite, 0);
                break;
                
            case SPRITE_CLEANUP_FAR_OFF_SCREEN:
                should_cleanup = is_sprite_off_screen(sprite, SPRITE_CLEANUP_MARGIN);
                break;
                
            case SPRITE_CLEANUP_TIMEOUT:
                should_cleanup = (current_time - sprite->creation_time > sprite->timeout_ms);
                break;
                
            case SPRITE_CLEANUP_INACTIVE:
                should_cleanup = !sprite->visible && 
                                (sprite->velocity_x == 0 && sprite->velocity_y == 0);
                break;
                
            case SPRITE_CLEANUP_NONE:
            default:
                break;
        }
        
        if (should_cleanup) {
            sprite_destroy(i);
            cleaned++;
        }
    }
    
    return cleaned;
}


static void cleanup_sprites_automatic(void) {
    sprite_cleanup_off_screen();
}


// Collision detection
bool sprite_check_collision(uint8_t sprite1_id, uint8_t sprite2_id) {
    if (sprite1_id >= MAX_SPRITES || sprite2_id >= MAX_SPRITES) return false;
    
    sprite_t* s1 = &g_engine.sprites[sprite1_id];
    sprite_t* s2 = &g_engine.sprites[sprite2_id];
    
    if (!s1->active || !s2->active) return false;
    
    // Simple AABB collision
    return !(s1->x + s1->width < s2->x || 
             s2->x + s2->width < s1->x ||
             s1->y + s1->height < s2->y ||
             s2->y + s2->height < s1->y);
}


collision_event_t* get_collision_events(uint8_t* count) {
    if (count) *count = g_engine.collision_count;
    return g_engine.collision_events;
}


void clear_collision_events(void) {
    g_engine.collision_count = 0;
}


// Particle system implementation
static void update_particles(particle_system_t* system) {
    if (!system || !system->active) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Spawn new particles
    if (current_time - system->last_spawn >= system->spawn_rate) {
        for (int i = 0; i < system->max_particles; i++) {
            if (!system->particles[i].active) {
                particle_t* p = &system->particles[i];
                p->x = system->spawn_x;
                p->y = system->spawn_y;
                p->velocity_x = (rand() % 200 - 100) / 100.0f * system->spawn_velocity_range;
                p->velocity_y = (rand() % 200 - 100) / 100.0f * system->spawn_velocity_range;
                p->acceleration_x = 0;
                p->acceleration_y = 0.1f; // Gravity
                p->color = system->color;
                p->alpha = 255;
                p->life_time = 0;
                p->max_life = system->particle_life;
                p->active = true;
                system->active_count++;
                break;
            }
        }
        system->last_spawn = current_time;
    }
    
    // Update existing particles
    for (int i = 0; i < system->max_particles; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;
        
        // Update physics
        p->velocity_x += p->acceleration_x;
        p->velocity_y += p->acceleration_y;
        p->x += p->velocity_x;
        p->y += p->velocity_y;
        
        // Update lifetime
        p->life_time++;
        if (p->life_time >= p->max_life) {
            p->active = false;
            system->active_count--;
        } else {
            // Fade out
            p->alpha = 255 * (p->max_life - p->life_time) / p->max_life;
        }
    }
}


// Rendering functions
void graphics_engine_render(void) {
    if (!g_initialized) return;
    
    // Clear buffer
    uint16_t* buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;
    memset(buffer, 0, sizeof(uint16_t) * DISPLAY_WIDTH * DISPLAY_HEIGHT);
    
    // Render layers in order
    for (int layer = 0; layer < 8; layer++) {
        // Render tilemaps
        for (int i = 0; i < MAX_LAYERS; i++) {
            if (g_engine.tile_layers[i].active && 
                g_engine.tile_layers[i].visible && 
                g_engine.tile_layers[i].layer == layer) {
                render_tilemap(&g_engine.tile_layers[i]);
            }
        }
        
        // Render sprites
        for (int i = 0; i < MAX_SPRITES; i++) {
            if (g_engine.sprites[i].active && 
                g_engine.sprites[i].visible && 
                g_engine.sprites[i].layer == layer) {
                render_sprite(&g_engine.sprites[i]);
            }
        }
    }
    
    // Render particle systems (always on top)
    for (int i = 0; i < MAX_PARTICLE_SYSTEMS; i++) {
        if (g_engine.particle_systems[i].active) {
            render_particles(&g_engine.particle_systems[i]);
        }
    }
    // Swap buffers if double buffering
    if (g_engine.double_buffering) {
        display_pack_swap_buffers();
    } else if (g_engine.vsync_enabled) {
        display_pack_wait_vsync();
    }
}


static void render_sprite(sprite_t* sprite) {
    if (!sprite || !sprite->active || !sprite->visible) return;

    // Check if sprite is off-screen
    if (is_sprite_off_screen(sprite, 0)) return;

    // Get texture data
    if (sprite->texture_id >= MAX_TEXTURE_SLOTS || 
        !g_engine.texture_slots[sprite->texture_id].allocated) return;

    texture_t* tex = &g_engine.texture_slots[sprite->texture_id].texture;
    uint16_t* frame_data = texture_get_frame_data(sprite->texture_id, sprite->current_frame);
    if (!frame_data) return;

    // Adjust for camera position
    int16_t screen_x = sprite->x - g_engine.camera_x;
    int16_t screen_y = sprite->y - g_engine.camera_y;

    // Clip to screen boundaries
    int16_t start_x = screen_x < 0 ? -screen_x : 0;
    int16_t start_y = screen_y < 0 ? -screen_y : 0;
    int16_t end_x = sprite->width;
    int16_t end_y = sprite->height;
    
    if (screen_x + end_x > DISPLAY_WIDTH) end_x = DISPLAY_WIDTH - screen_x;
    if (screen_y + end_y > DISPLAY_HEIGHT) end_y = DISPLAY_HEIGHT - screen_y;

    if (end_x <= start_x || end_y <= start_y) return;

    uint16_t* buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;

    // Render pixel by pixel
    for (int16_t y = start_y; y < end_y; y++) {
        for (int16_t x = start_x; x < end_x; x++) {
            // Sample texture
            uint16_t color = sample_texture(tex, sprite->current_frame, x, y);
            
            // Skip transparent pixels
            if (color == 0 && sprite->alpha == 255) continue;

            // Apply alpha blending
            if (sprite->alpha < 255 && sprite->blend_mode == BLEND_ALPHA) {
                uint16_t bg_color = buffer[(screen_y + y) * DISPLAY_WIDTH + (screen_x + x)];
                
                // Simple alpha blending for RGB565
                uint8_t alpha = sprite->alpha;
                uint8_t inv_alpha = 255 - alpha;
                
                uint16_t r1 = (color >> 11) & 0x1F;
                uint16_t g1 = (color >> 5) & 0x3F;
                uint16_t b1 = color & 0x1F;
                
                uint16_t r2 = (bg_color >> 11) & 0x1F;
                uint16_t g2 = (bg_color >> 5) & 0x3F;
                uint16_t b2 = bg_color & 0x1F;
                
                uint16_t r = ((r1 * alpha + r2 * inv_alpha) >> 8) & 0x1F;
                uint16_t g = ((g1 * alpha + g2 * inv_alpha) >> 8) & 0x3F;
                uint16_t b = ((b1 * alpha + b2 * inv_alpha) >> 8) & 0x1F;
                
                color = (r << 11) | (g << 5) | b;
            }
            
            // Draw pixel
            if (screen_x + x >= 0 && screen_x + x < DISPLAY_WIDTH &&
                screen_y + y >= 0 && screen_y + y < DISPLAY_HEIGHT) {
                display_pack_draw_pixel(buffer, screen_x + x, screen_y + y, color);
            }
        }
    }
}


static void render_tilemap(tile_layer_t* layer) {
    if (!layer || !layer->active || !layer->visible) return;

    // Adjust for camera position
    int16_t cam_x = g_engine.camera_x;
    int16_t cam_y = g_engine.camera_y;

    // Calculate visible tile range
    int16_t tile_width = layer->tile_width;
    int16_t tile_height = layer->tile_height;
    
    int16_t start_tile_x = cam_x / tile_width;
    int16_t start_tile_y = cam_y / tile_height;
    int16_t end_tile_x = (cam_x + DISPLAY_WIDTH + tile_width - 1) / tile_width;
    int16_t end_tile_y = (cam_y + DISPLAY_HEIGHT + tile_height - 1) / tile_height;

    // Clamp to map boundaries
    if (start_tile_x < 0) start_tile_x = 0;
    if (start_tile_y < 0) start_tile_y = 0;
    if (end_tile_x > layer->width) end_tile_x = layer->width;
    if (end_tile_y > layer->height) end_tile_y = layer->height;

    uint16_t* buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;

    // Render each tile
    for (int16_t ty = start_tile_y; ty < end_tile_y; ty++) {
        for (int16_t tx = start_tile_x; tx < end_tile_x; tx++) {
            uint16_t tile_id = layer->tiles[ty * layer->width + tx];
            if (tile_id == 0) continue; // Skip empty tiles

            // Get texture for tile
            if (tile_id >= MAX_TEXTURE_SLOTS || !g_engine.texture_slots[tile_id].allocated) continue;
            texture_t* tex = &g_engine.texture_slots[tile_id].texture;
            uint16_t* tile_data = texture_get_frame_data(tile_id, 0);
            if (!tile_data) continue;

            // Calculate screen position
            int16_t screen_x = tx * tile_width - cam_x;
            int16_t screen_y = ty * tile_height - cam_y;

            // Render tile pixel by pixel
            for (int16_t y = 0; y < tile_height; y++) {
                for (int16_t x = 0; x < tile_width; x++) {
                    if (screen_x + x < 0 || screen_x + x >= DISPLAY_WIDTH ||
                        screen_y + y < 0 || screen_y + y >= DISPLAY_HEIGHT) continue;

                    uint16_t color = sample_texture(tex, 0, x, y);
                    if (color == 0) continue; // Skip transparent pixels

                    display_pack_draw_pixel(buffer, screen_x + x, screen_y + y, color);
                }
            }
        }
    }
}


static void render_particles(particle_system_t* system) {
    if (!system || !system->active || system->active_count == 0) return;

    uint16_t* buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;

    // Render each active particle
    for (int i = 0; i < system->max_particles; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;

        // Adjust for camera position
        int16_t screen_x = (int16_t)(p->x - g_engine.camera_x);
        int16_t screen_y = (int16_t)(p->y - g_engine.camera_y);

        // Check if particle is on screen
        if (screen_x < 0 || screen_x >= DISPLAY_WIDTH ||
            screen_y < 0 || screen_y >= DISPLAY_HEIGHT) continue;

        // Apply alpha if needed
        uint16_t color = p->color;
        if (p->alpha < 255) {
            uint16_t bg_color = buffer[screen_y * DISPLAY_WIDTH + screen_x];
            
            // Simple alpha blending for RGB565
            uint8_t alpha = p->alpha;
            uint8_t inv_alpha = 255 - alpha;
            
            uint16_t r1 = (color >> 11) & 0x1F;
            uint16_t g1 = (color >> 5) & 0x3F;
            uint16_t b1 = color & 0x1F;
            
            uint16_t r2 = (bg_color >> 11) & 0x1F;
            uint16_t g2 = (bg_color >> 5) & 0x3F;
            uint16_t b2 = bg_color & 0x1F;
            
            uint16_t r = ((r1 * alpha + r2 * inv_alpha) >> 8) & 0x1F;
            uint16_t g = ((g1 * alpha + g2 * inv_alpha) >> 8) & 0x3F;
            uint16_t b = ((b1 * alpha + b2 * inv_alpha) >> 8) & 0x1F;
            
            color = (r << 11) | (g << 5) | b;
        }

        // Draw particle (single pixel for simplicity)
        display_pack_draw_pixel(buffer, screen_x, screen_y, color);
    }
}


static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y) {
    if (!texture || x >= texture->width || y >= texture->height || frame >= texture->frame_count) {
        return 0; // Return transparent color for invalid samples
    }

    size_t frame_size = texture->width * texture->height;
    size_t index = (frame * frame_size) + (y * texture->width) + x;
    return texture->data[index];
}


void graphics_enable_double_buffering(bool enabled) {
    if (!g_initialized)
        return;
    g_engine.double_buffering = enabled;
}


