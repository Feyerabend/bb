#include "engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Global engine state
static graphics_engine_t g_engine = {0};
static bool g_initialized = false;

// Internal helper functions
static void update_sprite_animation(sprite_t* sprite);
static void render_sprite(sprite_t* sprite);
static void render_tilemap(tile_layer_t* layer);
static void update_particles(particle_system_t* system);
static void render_particles(particle_system_t* system);
static bool check_sprite_bounds(sprite_t* sprite);
static void sort_sprites_by_layer(void);
static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y);

// Core Engine Functions
bool graphics_engine_init(void) {
    if (g_initialized) return true;
    
    printf("Init Graphics..\n");
    
    // Init base display system
    if (!display_pack_init()) {
        printf("Failed to initialise display pack\n");
        return false;
    }
    
    // Allocate framebuffers - enough memory?
    // Two framebuffers for a 240x135 display use 129,600 bytes, leaving about 140KB..
    g_engine.framebuffer = malloc(DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t));
    g_engine.back_buffer = malloc(DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t));
    
    if (!g_engine.framebuffer || !g_engine.back_buffer) {
        printf("Failed to allocate framebuffers\n");
        if (g_engine.framebuffer) free(g_engine.framebuffer);
        if (g_engine.back_buffer) free(g_engine.back_buffer);
        return false;
    }
    
    // Init engine state
    memset(&g_engine, 0, sizeof(graphics_engine_t));
    g_engine.framebuffer = g_engine.framebuffer; // Restore pointers
    g_engine.back_buffer = g_engine.back_buffer;
    
    // Set defaults
    g_engine.double_buffering = true;
    g_engine.collision_detection_enabled = true;
    g_engine.vsync_enabled = true;
    g_engine.camera_x = 0;
    g_engine.camera_y = 0;
    
    // Init sprite pool
    for (int i = 0; i < MAX_SPRITES; i++) {
        g_engine.sprites[i].id = i;
        g_engine.sprites[i].active = false;
    }
    
    // Init animation pool
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        g_engine.animations[i].id = i;
        g_engine.animations[i].active = false;
    }
    
    // Clear framebuffers
    memset(g_engine.framebuffer, 0, DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t));
    memset(g_engine.back_buffer, 0, DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t));
    
    g_initialized = true;
    printf("Graphics Engine initialised\n");
    return true;
}

void graphics_engine_shutdown(void) {
    if (!g_initialized) return;
    
    // Free textures
    for (int i = 0; i < MAX_SPRITES; i++) {
        if (g_engine.textures[i].data) {
            free(g_engine.textures[i].data);
        }
    }
    
    // Free animations
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (g_engine.animations[i].frame_sequence) {
            free(g_engine.animations[i].frame_sequence);
        }
        if (g_engine.animations[i].frame_durations) {
            free(g_engine.animations[i].frame_durations);
        }
    }
    
    // Free framebuffers
    if (g_engine.framebuffer) free(g_engine.framebuffer);
    if (g_engine.back_buffer) free(g_engine.back_buffer);
    
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
        
        // Check bounds
        check_sprite_bounds(sprite);
    }
    
    // Update particle systems
    for (int i = 0; i < 4; i++) {
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
    
    uint16_t* target_buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;
    
    // Clear buffer
    memset(target_buffer, 0, DISPLAY_WIDTH * DISPLAY_HEIGHT * sizeof(uint16_t));
    
    // Render tile layers (background layers)
    for (int layer = 0; layer < MAX_LAYERS; layer++) {
        for (int i = 0; i < MAX_LAYERS; i++) {
            tile_layer_t* tile_layer = &g_engine.tile_layers[i];
            if (tile_layer->active && tile_layer->visible && tile_layer->layer == layer) {
                render_tilemap(tile_layer);
            }
        }
        
        // Render sprites on this layer
        for (int i = 0; i < MAX_SPRITES; i++) {
            sprite_t* sprite = &g_engine.sprites[i];
            if (sprite->active && sprite->visible && sprite->layer == layer) {
                render_sprite(sprite);
            }
        }
    }
    
    // Render particle systems
    for (int i = 0; i < 4; i++) {
        if (g_engine.particle_systems[i].active) {
            render_particles(&g_engine.particle_systems[i]);
        }
    }
}

void graphics_engine_present(void) {
    if (!g_initialized) return;
    
    uint16_t* source_buffer = g_engine.double_buffering ? g_engine.back_buffer : g_engine.framebuffer;
    
    // Copy framebuffer to display
    for (int y = 0; y < DISPLAY_HEIGHT; y++) {
        for (int x = 0; x < DISPLAY_WIDTH; x++) {
            uint16_t color = source_buffer[y * DISPLAY_WIDTH + x];
            display_draw_pixel(x, y, color);
        }
    }
    
    // Swap buffers if double buffering
    if (g_engine.double_buffering) {
        uint16_t* temp = g_engine.framebuffer;
        g_engine.framebuffer = g_engine.back_buffer;
        g_engine.back_buffer = temp;
    }
}

// Sprite Management - textures: ~33-49KB
uint8_t sprite_create(int16_t x, int16_t y, uint8_t width, uint8_t height) {
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
            
            return i;
        }
    }
    return 255; // Invalid ID
}

void sprite_destroy(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES) return;
    g_engine.sprites[sprite_id].active = false;
    
    // Free texture if it exists
    if (g_engine.textures[sprite_id].data) {
        free(g_engine.textures[sprite_id].data);
        g_engine.textures[sprite_id].data = NULL;
    }
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
    
    // Free existing texture
    if (g_engine.textures[sprite_id].data) {
        free(g_engine.textures[sprite_id].data);
    }
    
    // Allocate new texture
    size_t data_size = width * height * sizeof(uint16_t);
    g_engine.textures[sprite_id].data = malloc(data_size);
    
    if (g_engine.textures[sprite_id].data) {
        memcpy(g_engine.textures[sprite_id].data, texture_data, data_size);
        g_engine.textures[sprite_id].width = width;
        g_engine.textures[sprite_id].height = height;
        g_engine.textures[sprite_id].frames = 1;
        g_engine.sprites[sprite_id].texture_id = sprite_id;
    }
}

void sprite_set_layer(uint8_t sprite_id, uint8_t layer) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    if (layer >= MAX_LAYERS) return;
    g_engine.sprites[sprite_id].layer = layer;
}

void sprite_set_alpha(uint8_t sprite_id, uint8_t alpha) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].alpha = alpha;
}

void sprite_set_visibility(uint8_t sprite_id, bool visible) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    g_engine.sprites[sprite_id].visible = visible;
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

// Collision Detection
bool sprite_check_collision(uint8_t sprite1_id, uint8_t sprite2_id) {
    if (sprite1_id >= MAX_SPRITES || sprite2_id >= MAX_SPRITES) return false;
    
    sprite_t* s1 = &g_engine.sprites[sprite1_id];
    sprite_t* s2 = &g_engine.sprites[sprite2_id];
    
    if (!s1->active || !s2->active || !s1->collision_enabled || !s2->collision_enabled) {
        return false;
    }
    
    // AABB collision detection
    return (s1->x < s2->x + s2->width &&
            s1->x + s1->width > s2->x &&
            s1->y < s2->y + s2->height &&
            s1->y + s1->height > s2->y);
}

collision_event_t* get_collision_events(uint8_t* count) {
    *count = g_engine.collision_count;
    return g_engine.collision_events;
}

// Rendering Primitives
void graphics_draw_line(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint16_t color) {
    // Bresenham's line algorithm
    int16_t dx = abs(x1 - x0);
    int16_t dy = abs(y1 - y0);
    int16_t sx = (x0 < x1) ? 1 : -1;
    int16_t sy = (y0 < y1) ? 1 : -1;
    int16_t err = dx - dy;
    
    while (true) {
        if (x0 >= 0 && x0 < DISPLAY_WIDTH && y0 >= 0 && y0 < DISPLAY_HEIGHT) {
            display_draw_pixel(x0, y0, color);
        }
        
        if (x0 == x1 && y0 == y1) break;
        
        int16_t e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

void graphics_draw_circle(int16_t x, int16_t y, uint8_t radius, uint16_t color) {
    // Bresenham's circle algorithm
    int16_t f = 1 - radius;
    int16_t ddF_x = 1;
    int16_t ddF_y = -2 * radius;
    int16_t px = 0;
    int16_t py = radius;
    
    display_draw_pixel(x, y + radius, color);
    display_draw_pixel(x, y - radius, color);
    display_draw_pixel(x + radius, y, color);
    display_draw_pixel(x - radius, y, color);
    
    while (px < py) {
        if (f >= 0) {
            py--;
            ddF_y += 2;
            f += ddF_y;
        }
        px++;
        ddF_x += 2;
        f += ddF_x;
        
        display_draw_pixel(x + px, y + py, color);
        display_draw_pixel(x - px, y + py, color);
        display_draw_pixel(x + px, y - py, color);
        display_draw_pixel(x - px, y - py, color);
        display_draw_pixel(x + py, y + px, color);
        display_draw_pixel(x - py, y + px, color);
        display_draw_pixel(x + py, y - px, color);
        display_draw_pixel(x - py, y - px, color);
    }
}

// Color utilities
uint16_t rgb_to_rgb565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3);
}

void rgb565_to_rgb(uint16_t color, uint8_t* r, uint8_t* g, uint8_t* b) {
    *r = (color >> 11) << 3;
    *g = ((color >> 5) & 0x3F) << 2;
    *b = (color & 0x1F) << 3;
}

uint16_t blend_colors(uint16_t color1, uint16_t color2, uint8_t alpha) {
    if (alpha == 0) return color2;
    if (alpha == 255) return color1;
    
    uint8_t r1, g1, b1, r2, g2, b2;
    rgb565_to_rgb(color1, &r1, &g1, &b1);
    rgb565_to_rgb(color2, &r2, &g2, &b2);
    
    uint8_t r = (r1 * alpha + r2 * (255 - alpha)) >> 8;
    uint8_t g = (g1 * alpha + g2 * (255 - alpha)) >> 8;
    uint8_t b = (b1 * alpha + b2 * (255 - alpha)) >> 8;
    
    return rgb_to_rgb565(r, g, b);
}

// Internal helper functions
static void update_sprite_animation(sprite_t* sprite) {
    animation_t* anim = &g_engine.animations[sprite->animation_id];
    if (!anim->active) return;
    
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    if (current_time - sprite->last_frame_time >= sprite->frame_duration) {
        sprite->current_frame++;
        
        if (sprite->current_frame >= anim->frame_count) {
            if (anim->loop) {
                sprite->current_frame = 0;
            } else {
                sprite->current_frame = anim->frame_count - 1;
            }
        }
        
        sprite->last_frame_time = current_time;
    }
}

static void render_sprite(sprite_t* sprite) {
    texture_t* texture = &g_engine.textures[sprite->texture_id];
    if (!texture->data) return;
    
    // Calculate screen position with camera offset
    int16_t screen_x = sprite->x - g_engine.camera_x;
    int16_t screen_y = sprite->y - g_engine.camera_y;
    
    // Frustum culling
    if (screen_x + sprite->width < 0 || screen_x >= DISPLAY_WIDTH ||
        screen_y + sprite->height < 0 || screen_y >= DISPLAY_HEIGHT) {
        return;
    }
    
    // Render sprite pixels
    for (int y = 0; y < sprite->height; y++) {
        for (int x = 0; x < sprite->width; x++) {
            int16_t px = screen_x + x;
            int16_t py = screen_y + y;
            
            // Bounds check
            if (px < 0 || px >= DISPLAY_WIDTH || py < 0 || py >= DISPLAY_HEIGHT) {
                continue;
            }
            
            // Sample texture
            uint16_t color = sample_texture(texture, sprite->current_frame, x, y);
            
            // Skip transparent pixels (assuming black is transparent)
            if (color == 0x0000) continue;
            
            // Apply alpha blending
            if (sprite->alpha < 255) {
                uint16_t bg_color = g_engine.double_buffering ? 
                    g_engine.back_buffer[py * DISPLAY_WIDTH + px] :
                    g_engine.framebuffer[py * DISPLAY_WIDTH + px];
                color = blend_colors(color, bg_color, sprite->alpha);
            }
            
            // Write to framebuffer or display directly
            if (g_engine.double_buffering) {
                g_engine.back_buffer[py * DISPLAY_WIDTH + px] = color;
            } else {
                display_draw_pixel(px, py, color);
            }
        }
    }
}

static void render_tilemap(tile_layer_t* layer) {
    if (!layer->active || !layer->visible) return;
    
    tileset_t* tileset = &g_engine.tilesets[layer->tileset_id];
    if (!tileset->active || !tileset->texture) return;
    
    // Calculate visible tile range
    int16_t start_tile_x = (g_engine.camera_x + layer->scroll_x) / TILE_SIZE;
    int16_t start_tile_y = (g_engine.camera_y + layer->scroll_y) / TILE_SIZE;
    int16_t end_tile_x = start_tile_x + (DISPLAY_WIDTH / TILE_SIZE) + 2;
    int16_t end_tile_y = start_tile_y + (DISPLAY_HEIGHT / TILE_SIZE) + 2;
    
    // Clamp to map bounds
    if (start_tile_x < 0) start_tile_x = 0;
    if (start_tile_y < 0) start_tile_y = 0;
    if (end_tile_x >= layer->width) end_tile_x = layer->width - 1;
    if (end_tile_y >= layer->height) end_tile_y = layer->height - 1;
    
    // Render visible tiles
    for (int ty = start_tile_y; ty <= end_tile_y; ty++) {
        for (int tx = start_tile_x; tx <= end_tile_x; tx++) {
            uint8_t tile_index = layer->tile_map[ty * layer->width + tx];
            if (tile_index == 0) continue; // Skip empty tiles
            
            // Calculate tile position on screen
            int16_t screen_x = tx * TILE_SIZE - (g_engine.camera_x + layer->scroll_x);
            int16_t screen_y = ty * TILE_SIZE - (g_engine.camera_y + layer->scroll_y);
            
            // Calculate tile source coordinates in tileset
            uint8_t tiles_per_row = tileset->tiles_per_row;
            uint8_t src_tile_x = (tile_index - 1) % tiles_per_row;
            uint8_t src_tile_y = (tile_index - 1) / tiles_per_row;
            
            // Render tile
            for (int y = 0; y < TILE_SIZE; y++) {
                for (int x = 0; x < TILE_SIZE; x++) {
                    int16_t px = screen_x + x;
                    int16_t py = screen_y + y;
                    
                    if (px < 0 || px >= DISPLAY_WIDTH || py < 0 || py >= DISPLAY_HEIGHT) {
                        continue;
                    }
                    
                    // Sample tileset texture
                    uint16_t src_x = src_tile_x * TILE_SIZE + x;
                    uint16_t src_y = src_tile_y * TILE_SIZE + y;
                    uint16_t color = sample_texture(tileset->texture, 0, src_x, src_y);
                    
                    if (color != 0x0000) { // Skip transparent
                        if (g_engine.double_buffering) {
                            g_engine.back_buffer[py * DISPLAY_WIDTH + px] = color;
                        } else {
                            display_draw_pixel(px, py, color);
                        }
                    }
                }
            }
        }
    }
}

static void update_particles(particle_system_t* system) {
    uint32_t current_time = to_ms_since_boot(get_absolute_time());
    
    // Spawn new particles
    if (current_time - system->last_spawn >= (1000 / system->spawn_rate) && 
        system->active_count < 64) {
        
        for (int i = 0; i < 64 && system->active_count < 64; i++) {
            if (!system->particles[i].active) {
                particle_t* p = &system->particles[i];
                p->active = true;
                p->x = system->spawn_x;
                p->y = system->spawn_y;
                
                // Random velocity
                float angle = ((float)rand() / RAND_MAX) * 2.0f * M_PI;
                float speed = ((float)rand() / RAND_MAX) * system->spawn_velocity_range;
                p->velocity_x = cos(angle) * speed;
                p->velocity_y = sin(angle) * speed;
                
                p->acceleration_x = 0.0f;
                p->acceleration_y = 0.1f; // Gravity
                p->color = system->color;
                p->alpha = 255;
                p->life_time = 0;
                p->max_life = system->particle_life;
                
                system->active_count++;
                system->last_spawn = current_time;
                break;
            }
        }
    }
    
    // Update existing particles
    for (int i = 0; i < 64; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;
        
        // Update physics
        p->velocity_x += p->acceleration_x;
        p->velocity_y += p->acceleration_y;
        p->x += p->velocity_x;
        p->y += p->velocity_y;
        
        // Update life
        p->life_time += g_engine.frame_time_ms;
        p->alpha = 255 * (1.0f - (float)p->life_time / p->max_life);
        
        // Remove dead particles
        if (p->life_time >= p->max_life) {
            p->active = false;
            system->active_count--;
        }
    }
}

static void render_particles(particle_system_t* system) {
    for (int i = 0; i < 64; i++) {
        particle_t* p = &system->particles[i];
        if (!p->active) continue;
        
        int16_t screen_x = (int16_t)p->x - g_engine.camera_x;
        int16_t screen_y = (int16_t)p->y - g_engine.camera_y;
        
        if (screen_x >= 0 && screen_x < DISPLAY_WIDTH && 
            screen_y >= 0 && screen_y < DISPLAY_HEIGHT) {
            
            uint16_t color = p->color;
            if (p->alpha < 255) {
                uint16_t bg_color = g_engine.double_buffering ?
                    g_engine.back_buffer[screen_y * DISPLAY_WIDTH + screen_x] :
                    0x0000;
                color = blend_colors(color, bg_color, p->alpha);
            }
            
            if (g_engine.double_buffering) {
                g_engine.back_buffer[screen_y * DISPLAY_WIDTH + screen_x] = color;
            } else {
                display_draw_pixel(screen_x, screen_y, color);
            }
        }
    }
}

static bool check_sprite_bounds(sprite_t* sprite) {
    // Optional: wrap around screen or clamp to bounds
    if (sprite->x + sprite->width < -100) {
        sprite->x = DISPLAY_WIDTH + 100;
        return true;
    }
    if (sprite->x > DISPLAY_WIDTH + 100) {
        sprite->x = -sprite->width - 100;
        return true;
    }
    return false;
}

static uint16_t sample_texture(texture_t* texture, uint8_t frame, uint8_t x, uint8_t y) {
    if (!texture->data || x >= texture->width || y >= texture->height) {
        return 0x0000;
    }
    
    // For multi-frame textures (sprite sheets)
    uint16_t frame_offset = 0;
    if (texture->frames > 1) {
        frame_offset = frame * texture->frame_width;
        if (x >= texture->frame_width) return 0x0000;
    }
    
    return texture->data[(y * texture->width) + x + frame_offset];
}

// Animation System Implementation
uint8_t animation_create(uint8_t frame_count, uint8_t* frames, uint16_t* durations, bool loop) {
    for (int i = 0; i < MAX_ANIMATIONS; i++) {
        if (!g_engine.animations[i].active) {
            animation_t* anim = &g_engine.animations[i];
            
            anim->id = i;
            anim->frame_count = frame_count;
            anim->loop = loop;
            anim->active = true;
            
            // Allocate and copy frame sequence
            anim->frame_sequence = malloc(frame_count);
            anim->frame_durations = malloc(frame_count * sizeof(uint16_t));
            
            if (anim->frame_sequence && anim->frame_durations) {
                memcpy(anim->frame_sequence, frames, frame_count);
                memcpy(anim->frame_durations, durations, frame_count * sizeof(uint16_t));
                return i;
            } else {
                // Allocation failed
                if (anim->frame_sequence) free(anim->frame_sequence);
                if (anim->frame_durations) free(anim->frame_durations);
                anim->active = false;
            }
        }
    }
    return 255; // Failed
}

void animation_start(uint8_t sprite_id) {
    if (sprite_id >= MAX_SPRITES || !g_engine.sprites[sprite_id].active) return;
    
    sprite_t* sprite = &g_engine.sprites[sprite_id];
    sprite->current_frame = 0;
    sprite->last_frame_time = to_ms_since_boot(get_absolute_time());
    
    if (sprite->animation_id < MAX_ANIMATIONS) {
        animation_t* anim = &g_engine.animations[sprite->animation_id];
        if (anim->active && anim->frame_durations) {
            sprite->frame_duration = anim->frame_durations[0];
        }
    }
}

// Particle System Implementation
uint8_t particle_system_create(float x, float y, uint16_t color, uint16_t spawn_rate) {
    for (int i = 0; i < 4; i++) {
        if (!g_engine.particle_systems[i].active) {
            particle_system_t* system = &g_engine.particle_systems[i];
            memset(system, 0, sizeof(particle_system_t));
            
            system->spawn_x = x;
            system->spawn_y = y;
            system->color = color;
            system->spawn_rate = spawn_rate;
            system->spawn_velocity_range = 2.0f;
            system->particle_life = 2000; // 2 seconds
            system->active = true;
            
            return i;
        }
    }
    return 255; // Failed
}

void particle_system_set_position(uint8_t system_id, float x, float y) {
    if (system_id >= 4) return;
    g_engine.particle_systems[system_id].spawn_x = x;
    g_engine.particle_systems[system_id].spawn_y = y;
}

// Utility Functions
void graphics_enable_double_buffering(bool enabled) {
    g_engine.double_buffering = enabled;
}

uint16_t graphics_get_fps(void) {
    return g_engine.fps;
}

uint32_t graphics_get_frame_time(void) {
    return g_engine.frame_time_ms;
}
        