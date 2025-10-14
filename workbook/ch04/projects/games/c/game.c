#include "game.h"
#include "sprites.h"
#include <stdio.h>

// helpers

// Simple hash function
static unsigned int hash(int key) {
    return (unsigned int)key % 100;
}

void array_init(Array* arr, int elem_size) {
    arr->elem_size = elem_size;
    arr->size = 0;
    arr->capacity = 8;
    arr->data = malloc(arr->capacity * elem_size);
}

void array_add(Array* arr, void* item) {
    if (arr->size >= arr->capacity) {
        arr->capacity *= 2;
        arr->data = realloc(arr->data, arr->capacity * arr->elem_size);
    }
    memcpy((char*)arr->data + arr->size * arr->elem_size, item, arr->elem_size);
    arr->size++;
}

void* array_get(Array* arr, int index) {
    if (index >= arr->size) return NULL;
    return (char*)arr->data + index * arr->elem_size;
}

void array_free(Array* arr) {
    if (arr->data) free(arr->data);
    arr->data = NULL;
    arr->size = 0;
}

void hashmap_init(HashMap* map, int capacity) {
    map->entries = calloc(capacity, sizeof(MapEntry));
    map->capacity = capacity;
    map->size = 0;
}

void hashmap_put(HashMap* map, int key, void* value) {
    unsigned int idx = hash(key) % map->capacity;
    MapEntry* entry = &map->entries[idx];
    
    if (!entry->value) {
        entry->key = key;
        entry->value = value;
        entry->next = NULL;
    } else {
        while (entry->next) entry = entry->next;
        entry->next = malloc(sizeof(MapEntry));
        entry->next->key = key;
        entry->next->value = value;
        entry->next->next = NULL;
    }
    map->size++;
}

void* hashmap_get(HashMap* map, int key) {
    unsigned int idx = hash(key) % map->capacity;
    MapEntry* entry = &map->entries[idx];
    
    while (entry && entry->value) {
        if (entry->key == key) return entry->value;
        entry = entry->next;
    }
    return NULL;
}

int hashmap_contains(HashMap* map, int key) {
    return hashmap_get(map, key) != NULL;
}

void hashmap_free(HashMap* map) {
    for (int i = 0; i < map->capacity; i++) {
        MapEntry* entry = map->entries[i].next;
        while (entry) {
            MapEntry* next = entry->next;
            free(entry);
            entry = next;
        }
    }
    free(map->entries);
}


// world

void world_init(World* world) {
    world->next_entity_id = 1;
    hashmap_init(&world->entity_components, 100);
    hashmap_init(&world->components, 20);
    hashmap_init(&world->component_entities, 20);
    array_init(&world->systems, sizeof(System*));
    world->camera_x = 0.0f;
    world->camera_y = 0.0f;
    world->game_over = false;
    world->score = 0;
    world->player_entity = 0;
}

EntityID world_create_entity(World* world) {
    EntityID id = world->next_entity_id++;
    Array* comp_types = malloc(sizeof(Array));
    array_init(comp_types, sizeof(int));
    hashmap_put(&world->entity_components, id, comp_types);
    return id;
}

void world_add_component(World* world, EntityID entity, int type, void* data, int data_size) {
    if (!hashmap_contains(&world->entity_components, entity)) return;
    
    HashMap* type_map = hashmap_get(&world->components, type);
    if (!type_map) {
        type_map = malloc(sizeof(HashMap));
        hashmap_init(type_map, 100);
        hashmap_put(&world->components, type, type_map);
    }
    
    void* comp_copy = malloc(data_size);
    memcpy(comp_copy, data, data_size);
    hashmap_put(type_map, entity, comp_copy);
    
    Array* entities_with_type = hashmap_get(&world->component_entities, type);
    if (!entities_with_type) {
        entities_with_type = malloc(sizeof(Array));
        array_init(entities_with_type, sizeof(EntityID));
        hashmap_put(&world->component_entities, type, entities_with_type);
    }
    array_add(entities_with_type, &entity);
    
    Array* entity_comps = hashmap_get(&world->entity_components, entity);
    array_add(entity_comps, &type);
}

void* world_get_component(World* world, EntityID entity, int type) {
    HashMap* type_map = hashmap_get(&world->components, type);
    if (!type_map) return NULL;
    return hashmap_get(type_map, entity);
}

int world_has_component(World* world, EntityID entity, int type) {
    Array* entity_comps = hashmap_get(&world->entity_components, entity);
    if (!entity_comps) return 0;
    for (int i = 0; i < entity_comps->size; i++) {
        int* comp_type = array_get(entity_comps, i);
        if (*comp_type == type) return 1;
    }
    return 0;
}

Array world_query(World* world, int* required, int req_count) {
    Array result;
    array_init(&result, sizeof(EntityID));
    
    if (req_count == 0) return result;
    
    Array* base_set = hashmap_get(&world->component_entities, required[0]);
    if (!base_set) return result;
    
    for (int i = 0; i < base_set->size; i++) {
        EntityID* entity = array_get(base_set, i);
        int has_all = 1;
        for (int j = 1; j < req_count; j++) {
            if (!world_has_component(world, *entity, required[j])) {
                has_all = 0;
                break;
            }
        }
        if (has_all) array_add(&result, entity);
    }
    return result;
}

void world_add_system(World* world, System* system) {
    array_add(&world->systems, &system);
}

void world_update(World* world, float dt) {
    for (int i = 0; i < world->systems.size; i++) {
        System** sys_ptr = array_get(&world->systems, i);
        if (*sys_ptr && (*sys_ptr)->update) {
            (*sys_ptr)->update(*sys_ptr, world, dt);
        }
    }
}

void world_destroy_entity(World* world, EntityID entity) {
    // Mark components as destroyed but don't free yet (simple approach)
    Array* entity_comps = hashmap_get(&world->entity_components, entity);
    if (entity_comps) {
        array_free(entity_comps);
        free(entity_comps);
    }
}

void world_free(World* world) {
    // Free all systems
    for (int i = 0; i < world->systems.size; i++) {
        System** sys_ptr = array_get(&world->systems, i);
        if (*sys_ptr && (*sys_ptr)->cleanup) {
            (*sys_ptr)->cleanup(*sys_ptr);
        }
        free(*sys_ptr);
    }
    array_free(&world->systems);
    
    hashmap_free(&world->entity_components);
    hashmap_free(&world->components);
    hashmap_free(&world->component_entities);
}


// collision

bool check_collision(float x1, float y1, float w1, float h1,
                     float x2, float y2, float w2, float h2) {
    return x1 < x2 + w2 && x1 + w1 > x2 &&
           y1 < y2 + h2 && y1 + h1 > y2;
}



// input

void input_update(System* self, World* world, float dt) {
    InputSystem* sys = (InputSystem*)self;
    
    if (world->game_over) return;
    
    int required[] = {CT_PLAYER, CT_POSITION, CT_VELOCITY, CT_PHYSICS};
    Array entities = world_query(world, required, 4);
    
    for (int i = 0; i < entities.size; i++) {
        EntityID* entity = array_get(&entities, i);
        PlayerComponent* player = world_get_component(world, *entity, CT_PLAYER);
        VelocityComponent* vel = world_get_component(world, *entity, CT_VELOCITY);
        
        // Horizontal movement
        float move_speed = 80.0f;
        if (button_pressed(BUTTON_A)) {
            vel->x = -move_speed;
        } else if (button_pressed(BUTTON_B)) {
            vel->x = move_speed;
        } else {
            vel->x *= 0.8f; // Friction when no input
        }
        
        // Jump
        bool jump_pressed = button_pressed(BUTTON_Y);
        if (jump_pressed && !sys->last_jump_pressed) {
            if (player->on_ground || player->jump_count < player->max_jumps) {
                vel->y = -150.0f;
                player->jump_count++;
                player->on_ground = false;
            }
        }
        sys->last_jump_pressed = jump_pressed;
    }
    
    array_free(&entities);
}

InputSystem* create_input_system(void) {
    InputSystem* sys = malloc(sizeof(InputSystem));
    sys->base.update = input_update;
    sys->base.cleanup = NULL;
    sys->last_jump_pressed = false;
    return sys;
}


// physics

void physics_update(System* self, World* world, float dt) {
    int required[] = {CT_POSITION, CT_VELOCITY, CT_PHYSICS};
    Array entities = world_query(world, required, 3);
    
    for (int i = 0; i < entities.size; i++) {
        EntityID* entity = array_get(&entities, i);
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        VelocityComponent* vel = world_get_component(world, *entity, CT_VELOCITY);
        PhysicsComponent* phys = world_get_component(world, *entity, CT_PHYSICS);
        
        // Apply gravity
        if (phys->affected_by_gravity) {
            vel->y += phys->gravity * dt;
            if (vel->y > phys->max_fall_speed) {
                vel->y = phys->max_fall_speed;
            }
        }
        
        // Update position
        pos->x += vel->x * dt;
        pos->y += vel->y * dt;
        
        // Prevent falling through world bounds
        if (pos->y > DISPLAY_HEIGHT - 16) {
            pos->y = DISPLAY_HEIGHT - 16;
            vel->y = 0;
            
            PlayerComponent* player = world_get_component(world, *entity, CT_PLAYER);
            if (player) {
                player->on_ground = true;
                player->jump_count = 0;
            }
        }
        
        // Keep in horizontal bounds
        if (pos->x < 0) pos->x = 0;
        if (pos->x > 800) pos->x = 800;
    }
    
    array_free(&entities);
}

PhysicsSystem* create_physics_system(void) {
    PhysicsSystem* sys = malloc(sizeof(PhysicsSystem));
    sys->base.update = physics_update;
    sys->base.cleanup = NULL;
    return sys;
}



// collision system

void collision_update(System* self, World* world, float dt) {
    int player_required[] = {CT_PLAYER, CT_POSITION, CT_COLLIDER, CT_VELOCITY};
    Array players = world_query(world, player_required, 4);
    
    int platform_required[] = {CT_PLATFORM, CT_POSITION, CT_COLLIDER};
    Array platforms = world_query(world, platform_required, 3);
    
    int enemy_required[] = {CT_ENEMY, CT_POSITION, CT_COLLIDER};
    Array enemies = world_query(world, enemy_required, 3);
    
    int collectible_required[] = {CT_COLLECTIBLE, CT_POSITION, CT_COLLIDER};
    Array collectibles = world_query(world, collectible_required, 3);
    
    // Player vs Platforms
    for (int i = 0; i < players.size; i++) {
        EntityID* player_ent = array_get(&players, i);
        PositionComponent* p_pos = world_get_component(world, *player_ent, CT_POSITION);
        ColliderComponent* p_col = world_get_component(world, *player_ent, CT_COLLIDER);
        VelocityComponent* p_vel = world_get_component(world, *player_ent, CT_VELOCITY);
        PlayerComponent* player = world_get_component(world, *player_ent, CT_PLAYER);
        
        player->on_ground = false;
        
        for (int j = 0; j < platforms.size; j++) {
            EntityID* plat_ent = array_get(&platforms, j);
            PositionComponent* plat_pos = world_get_component(world, *plat_ent, CT_POSITION);
            ColliderComponent* plat_col = world_get_component(world, *plat_ent, CT_COLLIDER);
            PlatformComponent* platform = world_get_component(world, *plat_ent, CT_PLATFORM);
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              plat_pos->x, plat_pos->y, plat_col->width, plat_col->height)) {
                
                // Landing on top
                if (p_vel->y > 0 && p_pos->y + p_col->height - 5 < plat_pos->y + plat_col->height) {
                    p_pos->y = plat_pos->y - p_col->height;
                    p_vel->y = 0;
                    player->on_ground = true;
                    player->jump_count = 0;
                }
                // Hit from below
                else if (p_vel->y < 0 && !platform->one_way) {
                    p_pos->y = plat_pos->y + plat_col->height;
                    p_vel->y = 0;
                }
                
                // Side collisions
                if (!platform->one_way) {
                    if (p_vel->x > 0) {
                        p_pos->x = plat_pos->x - p_col->width;
                        p_vel->x = 0;
                    } else if (p_vel->x < 0) {
                        p_pos->x = plat_pos->x + plat_col->width;
                        p_vel->x = 0;
                    }
                }
            }
        }
        
        // Player vs Enemies
        for (int j = 0; j < enemies.size; j++) {
            EntityID* enemy_ent = array_get(&enemies, j);
            PositionComponent* e_pos = world_get_component(world, *enemy_ent, CT_POSITION);
            ColliderComponent* e_col = world_get_component(world, *enemy_ent, CT_COLLIDER);
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              e_pos->x, e_pos->y, e_col->width, e_col->height)) {
                
                // Stomp on enemy
                if (p_vel->y > 0 && p_pos->y + p_col->height - 5 < e_pos->y + e_col->height / 2) {
                    world_destroy_entity(world, *enemy_ent);
                    p_vel->y = -100.0f;
                    world->score += 100;
                } else {
                    // Take damage
                    player->lives--;
                    if (player->lives <= 0) {
                        world->game_over = true;
                    }
                    p_pos->x -= 20 * (p_vel->x > 0 ? 1 : -1);
                    p_vel->x = -p_vel->x * 2;
                }
            }
        }
        
        // Player vs Collectibles
        for (int j = 0; j < collectibles.size; j++) {
            EntityID* coll_ent = array_get(&collectibles, j);
            CollectibleComponent* coll = world_get_component(world, *coll_ent, CT_COLLECTIBLE);
            
            if (coll->collected) continue;
            
            PositionComponent* c_pos = world_get_component(world, *coll_ent, CT_POSITION);
            ColliderComponent* c_col = world_get_component(world, *coll_ent, CT_COLLIDER);
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              c_pos->x, c_pos->y, c_col->width, c_col->height)) {
                coll->collected = true;
                world->score += coll->points;
            }
        }
    }
    
    array_free(&players);
    array_free(&platforms);
    array_free(&enemies);
    array_free(&collectibles);
}

CollisionSystem* create_collision_system(void) {
    CollisionSystem* sys = malloc(sizeof(CollisionSystem));
    sys->base.update = collision_update;
    sys->base.cleanup = NULL;
    return sys;
}


// enemy ai system

void enemy_ai_update(System* self, World* world, float dt) {
    int required[] = {CT_ENEMY, CT_POSITION, CT_VELOCITY};
    Array entities = world_query(world, required, 3);
    
    for (int i = 0; i < entities.size; i++) {
        EntityID* entity = array_get(&entities, i);
        EnemyComponent* enemy = world_get_component(world, *entity, CT_ENEMY);
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        VelocityComponent* vel = world_get_component(world, *entity, CT_VELOCITY);
        
        // Simple patrol AI
        vel->x = enemy->move_speed * enemy->move_direction;
        
        if (pos->x <= enemy->patrol_start) {
            enemy->move_direction = 1.0f;
            pos->x = enemy->patrol_start;
        } else if (pos->x >= enemy->patrol_end) {
            enemy->move_direction = -1.0f;
            pos->x = enemy->patrol_end;
        }
    }
    
    array_free(&entities);
}

EnemyAISystem* create_enemy_ai_system(void) {
    EnemyAISystem* sys = malloc(sizeof(EnemyAISystem));
    sys->base.update = enemy_ai_update;
    sys->base.cleanup = NULL;
    return sys;
}


// render system

void render_update(System* self, World* world, float dt) {
    // Clear screen
    display_clear(COLOR_CYAN);
    
    // Update camera to follow player
    if (world->player_entity > 0) {
        PositionComponent* player_pos = world_get_component(world, world->player_entity, CT_POSITION);
        if (player_pos) {
            world->camera_x = player_pos->x - DISPLAY_WIDTH / 2;
            if (world->camera_x < 0) world->camera_x = 0;
        }
    }
    
    // Draw platforms
    int platform_required[] = {CT_PLATFORM, CT_POSITION, CT_SPRITE};
    Array platforms = world_query(world, platform_required, 3);
    
    for (int i = 0; i < platforms.size; i++) {
        EntityID* entity = array_get(&platforms, i);
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        SpriteComponent* sprite = world_get_component(world, *entity, CT_SPRITE);
        
        int screen_x = (int)(pos->x - world->camera_x);
        int screen_y = (int)pos->y;
        
        if (screen_x + sprite->width >= 0 && screen_x < DISPLAY_WIDTH) {
            display_fill_rect(screen_x, screen_y, sprite->width, sprite->height, sprite->color);
        }
    }
    array_free(&platforms);
    
    // Draw collectibles
    int coll_required[] = {CT_COLLECTIBLE, CT_POSITION, CT_SPRITE};
    Array collectibles = world_query(world, coll_required, 3);
    
    for (int i = 0; i < collectibles.size; i++) {
        EntityID* entity = array_get(&collectibles, i);
        CollectibleComponent* coll = world_get_component(world, *entity, CT_COLLECTIBLE);
        
        if (coll->collected) continue;
        
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        SpriteComponent* sprite = world_get_component(world, *entity, CT_SPRITE);
        
        int screen_x = (int)(pos->x - world->camera_x);
        int screen_y = (int)pos->y;
        
        if (screen_x + sprite->width >= 0 && screen_x < DISPLAY_WIDTH) {
            display_fill_rect(screen_x, screen_y, sprite->width, sprite->height, sprite->color);
        }
    }
    array_free(&collectibles);
    
    // Draw enemies
    int enemy_required[] = {CT_ENEMY, CT_POSITION, CT_SPRITE};
    Array enemies = world_query(world, enemy_required, 3);
    
    for (int i = 0; i < enemies.size; i++) {
        EntityID* entity = array_get(&enemies, i);
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        SpriteComponent* sprite = world_get_component(world, *entity, CT_SPRITE);
        
        int screen_x = (int)(pos->x - world->camera_x);
        int screen_y = (int)pos->y;
        
        if (screen_x + sprite->width >= 0 && screen_x < DISPLAY_WIDTH) {
            display_fill_rect(screen_x, screen_y, sprite->width, sprite->height, sprite->color);
        }
    }
    array_free(&enemies);
    
    // Draw player
    int player_required[] = {CT_PLAYER, CT_POSITION, CT_SPRITE};
    Array players = world_query(world, player_required, 3);
    
    for (int i = 0; i < players.size; i++) {
        EntityID* entity = array_get(&players, i);
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        SpriteComponent* sprite = world_get_component(world, *entity, CT_SPRITE);
        
        int screen_x = (int)(pos->x - world->camera_x);
        int screen_y = (int)pos->y;
        
        display_fill_rect(screen_x, screen_y, sprite->width, sprite->height, sprite->color);
    }
    array_free(&players);
    
    // Draw UI
    char score_text[32];
    snprintf(score_text, sizeof(score_text), "Score: %d", world->score);
    display_draw_string(5, 5, score_text, COLOR_WHITE, COLOR_BLACK);
    
    // Draw lives
    if (world->player_entity > 0) {
        PlayerComponent* player = world_get_component(world, world->player_entity, CT_PLAYER);
        if (player) {
            char lives_text[32];
            snprintf(lives_text, sizeof(lives_text), "Lives: %d", player->lives);
            display_draw_string(5, 15, lives_text, COLOR_WHITE, COLOR_BLACK);
        }
    }
    
    // Game over screen
    if (world->game_over) {
        display_draw_string(DISPLAY_WIDTH/2 - 30, DISPLAY_HEIGHT/2, "GAME OVER", COLOR_RED, COLOR_BLACK);
    }
}

RenderSystem* create_render_system(void) {
    RenderSystem* sys = malloc(sizeof(RenderSystem));
    sys->base.update = render_update;
    sys->base.cleanup = NULL;
    return sys;
}


// game init

void game_create_level(World* world) {
    // Create ground platforms
    for (int i = 0; i < 10; i++) {
        EntityID platform = world_create_entity(world);
        
        PositionComponent pos = {i * 80.0f, 220.0f};
        world_add_component(world, platform, CT_POSITION, &pos, sizeof(PositionComponent));
        
        SpriteComponent sprite = {COLOR_GREEN, 80, 20, NULL};
        world_add_component(world, platform, CT_SPRITE, &sprite, sizeof(SpriteComponent));
        
        ColliderComponent collider = {80, 20, 0, 0};
        world_add_component(world, platform, CT_COLLIDER, &collider, sizeof(ColliderComponent));
        
        PlatformComponent plat = {true, false};
        world_add_component(world, platform, CT_PLATFORM, &plat, sizeof(PlatformComponent));
    }
    
    // Create floating platforms
    EntityID plat1 = world_create_entity(world);
    PositionComponent pos1 = {150.0f, 180.0f};
    world_add_component(world, plat1, CT_POSITION, &pos1, sizeof(PositionComponent));
    SpriteComponent sprite1 = {COLOR_GREEN, 60, 15, NULL};
    world_add_component(world, plat1, CT_SPRITE, &sprite1, sizeof(SpriteComponent));
    ColliderComponent collider1 = {60, 15, 0, 0};
    world_add_component(world, plat1, CT_COLLIDER, &collider1, sizeof(ColliderComponent));
    PlatformComponent plat1_comp = {true, false};
    world_add_component(world, plat1, CT_PLATFORM, &plat1_comp, sizeof(PlatformComponent));
    
    EntityID plat2 = world_create_entity(world);
    PositionComponent pos2 = {280.0f, 150.0f};
    world_add_component(world, plat2, CT_POSITION, &pos2, sizeof(PositionComponent));
    SpriteComponent sprite2 = {COLOR_GREEN, 60, 15, NULL};
    world_add_component(world, plat2, CT_SPRITE, &sprite2, sizeof(SpriteComponent));
    ColliderComponent collider2 = {60, 15, 0, 0};
    world_add_component(world, plat2, CT_COLLIDER, &collider2, sizeof(ColliderComponent));
    PlatformComponent plat2_comp = {true, false};
    world_add_component(world, plat2, CT_PLATFORM, &plat2_comp, sizeof(PlatformComponent));
    
    EntityID plat3 = world_create_entity(world);
    PositionComponent pos3 = {420.0f, 180.0f};
    world_add_component(world, plat3, CT_POSITION, &pos3, sizeof(PositionComponent));
    SpriteComponent sprite3 = {COLOR_GREEN, 60, 15, NULL};
    world_add_component(world, plat3, CT_SPRITE, &sprite3, sizeof(SpriteComponent));
    ColliderComponent collider3 = {60, 15, 0, 0};
    world_add_component(world, plat3, CT_COLLIDER, &collider3, sizeof(ColliderComponent));
    PlatformComponent plat3_comp = {true, false};
    world_add_component(world, plat3, CT_PLATFORM, &plat3_comp, sizeof(PlatformComponent));
    
    // Create enemies
    EntityID enemy1 = world_create_entity(world);
    PositionComponent e_pos1 = {200.0f, 200.0f};
    world_add_component(world, enemy1, CT_POSITION, &e_pos1, sizeof(PositionComponent));
    VelocityComponent e_vel1 = {0, 0};
    world_add_component(world, enemy1, CT_VELOCITY, &e_vel1, sizeof(VelocityComponent));
    SpriteComponent e_sprite1 = {COLOR_RED, 12, 12, NULL};
    world_add_component(world, enemy1, CT_SPRITE, &e_sprite1, sizeof(SpriteComponent));
    ColliderComponent e_collider1 = {12, 12, 0, 0};
    world_add_component(world, enemy1, CT_COLLIDER, &e_collider1, sizeof(ColliderComponent));
    EnemyComponent e_comp1 = {30.0f, 1.0f, 150.0f, 250.0f};
    world_add_component(world, enemy1, CT_ENEMY, &e_comp1, sizeof(EnemyComponent));
    PhysicsComponent e_phys1 = {400.0f, 200.0f, 0.9f, true};
    world_add_component(world, enemy1, CT_PHYSICS, &e_phys1, sizeof(PhysicsComponent));
    
    EntityID enemy2 = world_create_entity(world);
    PositionComponent e_pos2 = {400.0f, 160.0f};
    world_add_component(world, enemy2, CT_POSITION, &e_pos2, sizeof(PositionComponent));
    VelocityComponent e_vel2 = {0, 0};
    world_add_component(world, enemy2, CT_VELOCITY, &e_vel2, sizeof(VelocityComponent));
    SpriteComponent e_sprite2 = {COLOR_RED, 12, 12, NULL};
    world_add_component(world, enemy2, CT_SPRITE, &e_sprite2, sizeof(SpriteComponent));
    ColliderComponent e_collider2 = {12, 12, 0, 0};
    world_add_component(world, enemy2, CT_COLLIDER, &e_collider2, sizeof(ColliderComponent));
    EnemyComponent e_comp2 = {40.0f, -1.0f, 350.0f, 470.0f};
    world_add_component(world, enemy2, CT_ENEMY, &e_comp2, sizeof(EnemyComponent));
    PhysicsComponent e_phys2 = {400.0f, 200.0f, 0.9f, true};
    world_add_component(world, enemy2, CT_PHYSICS, &e_phys2, sizeof(PhysicsComponent));
    
    // Create collectibles (coins)
    for (int i = 0; i < 5; i++) {
        EntityID coin = world_create_entity(world);
        PositionComponent c_pos = {100.0f + i * 100.0f, 130.0f};
        world_add_component(world, coin, CT_POSITION, &c_pos, sizeof(PositionComponent));
        SpriteComponent c_sprite = {COLOR_YELLOW, 8, 8, NULL};
        world_add_component(world, coin, CT_SPRITE, &c_sprite, sizeof(SpriteComponent));
        ColliderComponent c_collider = {8, 8, 0, 0};
        world_add_component(world, coin, CT_COLLIDER, &c_collider, sizeof(ColliderComponent));
        CollectibleComponent c_comp = {50, false};
        world_add_component(world, coin, CT_COLLECTIBLE, &c_comp, sizeof(CollectibleComponent));
    }
    
    // Create player
    EntityID player = world_create_entity(world);
    world->player_entity = player;
    
    PositionComponent p_pos = {50.0f, 180.0f};
    world_add_component(world, player, CT_POSITION, &p_pos, sizeof(PositionComponent));
    
    VelocityComponent p_vel = {0, 0};
    world_add_component(world, player, CT_VELOCITY, &p_vel, sizeof(VelocityComponent));
    
    SpriteComponent p_sprite = {COLOR_BLUE, 14, 14, NULL};
    world_add_component(world, player, CT_SPRITE, &p_sprite, sizeof(SpriteComponent));
    
    ColliderComponent p_collider = {14, 14, 0, 0};
    world_add_component(world, player, CT_COLLIDER, &p_collider, sizeof(ColliderComponent));
    
    PlayerComponent p_player = {false, 0, 2, 3};
    world_add_component(world, player, CT_PLAYER, &p_player, sizeof(PlayerComponent));
    
    PhysicsComponent p_phys = {400.0f, 300.0f, 0.85f, true};
    world_add_component(world, player, CT_PHYSICS, &p_phys, sizeof(PhysicsComponent));
}

void game_init(World* world) {
    world_init(world);
    
    // Add systems in order
    world_add_system(world, (System*)create_input_system());
    world_add_system(world, (System*)create_enemy_ai_system());
    world_add_system(world, (System*)create_physics_system());
    world_add_system(world, (System*)create_collision_system());
    world_add_system(world, (System*)create_render_system());
    
    // Create level entities
    game_create_level(world);
}

