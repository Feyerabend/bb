#include "game.h"
#include "sprites.h"
#include <stdio.h>
#include <assert.h>
#include <math.h>

#define WORLD_WIDTH 3200
#define GROUND_HEIGHT 220
#define TILE_SIZE 32

#define GRAVITY 800.0f
#define MAX_FALL_SPEED 400.0f
#define WALK_SPEED 100.0f
#define RUN_SPEED 150.0f
#define JUMP_SPEED -250.0f
#define DOUBLE_JUMP_SPEED -220.0f
#define FRICTION 0.82f
#define AIR_FRICTION 0.95f
#define ACCELERATION 800.0f


// events ..

typedef enum {
    EVENT_COIN_COLLECTED,
    EVENT_ENEMY_DEFEATED,
    EVENT_PLAYER_DAMAGED,
    EVENT_PLAYER_DIED,
    EVENT_GAME_OVER
} EventType;

typedef struct {
    EventType type;
    EntityID entity;
    int value;
    void* data;
} GameEvent;

typedef struct EventListener {
    void (*on_event)(World* world, GameEvent* event);
    struct EventListener* next;
} EventListener;

typedef struct {
    EventListener* listeners[5];  // One list per event type
} EventSystem;

void event_system_init(EventSystem* sys) {
    for (int i = 0; i < 5; i++) {
        sys->listeners[i] = NULL;
    }
}

void event_system_subscribe(EventSystem* sys, EventType type, 
                           void (*callback)(World*, GameEvent*)) {
    EventListener* listener = malloc(sizeof(EventListener));
    listener->on_event = callback;
    listener->next = sys->listeners[type];
    sys->listeners[type] = listener;
}

void event_system_emit(EventSystem* sys, World* world, GameEvent* event) {
    EventListener* listener = sys->listeners[event->type];
    while (listener) {
        listener->on_event(world, event);
        listener = listener->next;
    }
}

void event_system_free(EventSystem* sys) {
    for (int i = 0; i < 5; i++) {
        EventListener* listener = sys->listeners[i];
        while (listener) {
            EventListener* next = listener->next;
            free(listener);
            listener = next;
        }
    }
}


// event handlers
void on_coin_collected(World* world, GameEvent* event) {
    world->score += event->value;
}

void on_enemy_defeated(World* world, GameEvent* event) {
    world->score += event->value;
}

void on_player_damaged(World* world, GameEvent* event) {
    if (world->player_entity > 0) {
        PlayerComponent* player = world_get_component(world, world->player_entity, CT_PLAYER);
        if (player) {
            player->lives--;
            if (player->lives <= 0) {
                GameEvent game_over = {EVENT_GAME_OVER, world->player_entity, 0, NULL};
                event_system_emit(world->event_system, world, &game_over);
            }
        }
    }
}

void on_game_over(World* world, GameEvent* event) {
    world->game_over = true;
}



// player state pattern

typedef struct PlayerState PlayerState;
struct PlayerState {
    void (*enter)(PlayerComponent* player, VelocityComponent* vel);
    void (*update)(PlayerComponent* player, VelocityComponent* vel, float dt);
    void (*handle_jump)(PlayerComponent* player, VelocityComponent* vel, PlayerState** next_state);
    const char* name;
};

// fwd decl
extern PlayerState STATE_IDLE;
extern PlayerState STATE_WALKING;
extern PlayerState STATE_JUMPING;
extern PlayerState STATE_FALLING;

// idle State
void idle_enter(PlayerComponent* p, VelocityComponent* v) {
    v->x = 0;
}

void idle_update(PlayerComponent* p, VelocityComponent* v, float dt) {
    if (fabsf(v->x) > 1.0f) {
        p->state = &STATE_WALKING;
    }
    if (!p->on_ground) {
        p->state = &STATE_FALLING;
    }
}

void idle_handle_jump(PlayerComponent* p, VelocityComponent* v, PlayerState** next) {
    if (p->on_ground) {
        v->y = JUMP_SPEED;
        p->on_ground = false;
        p->jump_count = 1;
        *next = &STATE_JUMPING;
    }
}

PlayerState STATE_IDLE = {idle_enter, idle_update, idle_handle_jump, "idle"};

// walk state
void walking_enter(PlayerComponent* p, VelocityComponent* v) {}

void walking_update(PlayerComponent* p, VelocityComponent* v, float dt) {
    if (fabsf(v->x) < 1.0f) {
        p->state = &STATE_IDLE;
    }
    if (!p->on_ground) {
        p->state = &STATE_FALLING;
    }
}

void walking_handle_jump(PlayerComponent* p, VelocityComponent* v, PlayerState** next) {
    idle_handle_jump(p, v, next);
}

PlayerState STATE_WALKING = {walking_enter, walking_update, walking_handle_jump, "walking"};

// jump state
void jumping_enter(PlayerComponent* p, VelocityComponent* v) {}

void jumping_update(PlayerComponent* p, VelocityComponent* v, float dt) {
    if (v->y > 0) {
        p->state = &STATE_FALLING;
    }
}

void jumping_handle_jump(PlayerComponent* p, VelocityComponent* v, PlayerState** next) {
    if (p->jump_count < p->max_jumps) {
        v->y = DOUBLE_JUMP_SPEED;
        p->jump_count++;
    }
}

PlayerState STATE_JUMPING = {jumping_enter, jumping_update, jumping_handle_jump, "jumping"};

// falling state
void falling_enter(PlayerComponent* p, VelocityComponent* v) {}

void falling_update(PlayerComponent* p, VelocityComponent* v, float dt) {
    if (p->on_ground) {
        if (fabsf(v->x) > 1.0f) {
            p->state = &STATE_WALKING;
        } else {
            p->state = &STATE_IDLE;
        }
    }
}

void falling_handle_jump(PlayerComponent* p, VelocityComponent* v, PlayerState** next) {
    jumping_handle_jump(p, v, next);
}

PlayerState STATE_FALLING = {falling_enter, falling_update, falling_handle_jump, "falling"};



// object pool for entities

typedef struct {
    EntityID* ids;
    int* active;
    int capacity;
    int count;
} EntityPool;

void entity_pool_init(EntityPool* pool, int capacity) {
    pool->ids = malloc(sizeof(EntityID) * capacity);
    pool->active = calloc(capacity, sizeof(int));
    pool->capacity = capacity;
    pool->count = 0;
}

EntityID entity_pool_acquire(EntityPool* pool, World* world) {
    for (int i = 0; i < pool->count; i++) {
        if (!pool->active[i]) {
            pool->active[i] = 1;
            return pool->ids[i];
        }
    }
    
    if (pool->count < pool->capacity) {
        EntityID id = world_create_entity(world);
        pool->ids[pool->count] = id;
        pool->active[pool->count] = 1;
        pool->count++;
        return id;
    }
    
    return 0;
}

void entity_pool_release(EntityPool* pool, EntityID id) {
    for (int i = 0; i < pool->count; i++) {
        if (pool->ids[i] == id) {
            pool->active[i] = 0;
            return;
        }
    }
}

void entity_pool_free(EntityPool* pool) {
    free(pool->ids);
    free(pool->active);
}



// entity factories

typedef struct {
    float width;
    float height;
    bool solid;
    bool one_way;
} PlatformParams;

typedef struct {
    float speed;
    float patrol_start;
    float patrol_end;
} EnemyParams;

typedef struct {
    int points;
} CollectibleParams;

// platform factory
EntityID factory_create_platform(World* world, float x, float y, PlatformParams* params) {
    EntityID entity = world_create_entity(world);
    
    PositionComponent pos = {x, y};
    world_add_component(world, entity, CT_POSITION, &pos, sizeof(PositionComponent));
    
    SpriteComponent sprite = {0x07E0, (uint8_t)params->width, (uint8_t)params->height, NULL};
    world_add_component(world, entity, CT_SPRITE, &sprite, sizeof(SpriteComponent));
    
    ColliderComponent collider = {params->width, params->height, 0, 0};
    world_add_component(world, entity, CT_COLLIDER, &collider, sizeof(ColliderComponent));
    
    PlatformComponent plat = {params->solid, params->one_way};
    world_add_component(world, entity, CT_PLATFORM, &plat, sizeof(PlatformComponent));
    
    return entity;
}

// enemy factory
EntityID factory_create_enemy(World* world, float x, float y, EnemyParams* params) {
    EntityID entity = world_create_entity(world);
    
    PositionComponent pos = {x, y};
    world_add_component(world, entity, CT_POSITION, &pos, sizeof(PositionComponent));
    
    VelocityComponent vel = {0, 0};
    world_add_component(world, entity, CT_VELOCITY, &vel, sizeof(VelocityComponent));
    
    SpriteComponent sprite = {COLOR_RED, 14, 14, NULL};
    world_add_component(world, entity, CT_SPRITE, &sprite, sizeof(SpriteComponent));
    
    ColliderComponent collider = {14, 14, 0, 0};
    world_add_component(world, entity, CT_COLLIDER, &collider, sizeof(ColliderComponent));
    
    EnemyComponent enemy = {
        params->speed,
        1.0f,
        params->patrol_start,
        params->patrol_end
    };
    world_add_component(world, entity, CT_ENEMY, &enemy, sizeof(EnemyComponent));
    
    PhysicsComponent phys = {GRAVITY, MAX_FALL_SPEED, 0.9f, true};
    world_add_component(world, entity, CT_PHYSICS, &phys, sizeof(PhysicsComponent));
    
    return entity;
}

// collectible factory
EntityID factory_create_collectible(World* world, float x, float y, CollectibleParams* params) {
    EntityID entity = world_create_entity(world);
    
    PositionComponent pos = {x, y};
    world_add_component(world, entity, CT_POSITION, &pos, sizeof(PositionComponent));
    
    SpriteComponent sprite = {COLOR_YELLOW, 10, 10, NULL};
    world_add_component(world, entity, CT_SPRITE, &sprite, sizeof(SpriteComponent));
    
    ColliderComponent collider = {10, 10, 0, 0};
    world_add_component(world, entity, CT_COLLIDER, &collider, sizeof(ColliderComponent));
    
    CollectibleComponent coll = {params->points, false};
    world_add_component(world, entity, CT_COLLECTIBLE, &coll, sizeof(CollectibleComponent));
    
    return entity;
}

// player factory
EntityID factory_create_player(World* world, float x, float y) {
    EntityID entity = world_create_entity(world);
    
    PositionComponent pos = {x, y};
    world_add_component(world, entity, CT_POSITION, &pos, sizeof(PositionComponent));
    
    VelocityComponent vel = {0, 0};
    world_add_component(world, entity, CT_VELOCITY, &vel, sizeof(VelocityComponent));
    
    SpriteComponent sprite = {COLOR_BLUE, 16, 16, NULL};
    world_add_component(world, entity, CT_SPRITE, &sprite, sizeof(SpriteComponent));
    
    ColliderComponent collider = {16, 16, 0, 0};
    world_add_component(world, entity, CT_COLLIDER, &collider, sizeof(ColliderComponent));
    
    PlayerComponent player = {false, 0, 2, 3, &STATE_IDLE};
    world_add_component(world, entity, CT_PLAYER, &player, sizeof(PlayerComponent));
    
    PhysicsComponent phys = {GRAVITY, MAX_FALL_SPEED, FRICTION, true};
    world_add_component(world, entity, CT_PHYSICS, &phys, sizeof(PhysicsComponent));
    
    return entity;
}


// entity builder pattern

typedef struct {
    World* world;
    EntityID entity;
} EntityBuilder;

EntityBuilder* builder_create(World* world) {
    EntityBuilder* builder = malloc(sizeof(EntityBuilder));
    builder->world = world;
    builder->entity = world_create_entity(world);
    return builder;
}

EntityBuilder* builder_position(EntityBuilder* b, float x, float y) {
    PositionComponent pos = {x, y};
    world_add_component(b->world, b->entity, CT_POSITION, &pos, sizeof(PositionComponent));
    return b;
}

EntityBuilder* builder_velocity(EntityBuilder* b, float vx, float vy) {
    VelocityComponent vel = {vx, vy};
    world_add_component(b->world, b->entity, CT_VELOCITY, &vel, sizeof(VelocityComponent));
    return b;
}

EntityBuilder* builder_sprite(EntityBuilder* b, uint16_t color, uint8_t w, uint8_t h) {
    SpriteComponent sprite = {color, w, h, NULL};
    world_add_component(b->world, b->entity, CT_SPRITE, &sprite, sizeof(SpriteComponent));
    return b;
}

EntityBuilder* builder_collider(EntityBuilder* b, float w, float h) {
    ColliderComponent col = {w, h, 0, 0};
    world_add_component(b->world, b->entity, CT_COLLIDER, &col, sizeof(ColliderComponent));
    return b;
}

EntityBuilder* builder_physics(EntityBuilder* b) {
    PhysicsComponent phys = {GRAVITY, MAX_FALL_SPEED, FRICTION, true};
    world_add_component(b->world, b->entity, CT_PHYSICS, &phys, sizeof(PhysicsComponent));
    return b;
}

EntityID builder_build(EntityBuilder* b) {
    EntityID id = b->entity;
    free(b);
    return id;
}



// input systems
void input_update(System* self, World* world, float dt) {
    if (!self || !world || world->game_over) return;
    InputSystem* sys = (InputSystem*)self;
    
    int required[] = {CT_PLAYER, CT_POSITION, CT_VELOCITY, CT_PHYSICS};
    Array entities = world_query(world, required, 4);
    
    for (int i = 0; i < entities.size; i++) {
        EntityID* entity = array_get(&entities, i);
        if (!entity) continue;
        
        PlayerComponent* player = world_get_component(world, *entity, CT_PLAYER);
        VelocityComponent* vel = world_get_component(world, *entity, CT_VELOCITY);
        
        if (!player || !vel) continue;
        
        bool left = button_pressed(BUTTON_A);
        bool right = button_pressed(BUTTON_B);
        bool jump = button_pressed(BUTTON_Y);
        
        // Horizontal movement
        float target_speed = 0;
        if (left) target_speed = -WALK_SPEED;
        else if (right) target_speed = WALK_SPEED;
        
        if (target_speed != 0) {
            float accel = player->on_ground ? ACCELERATION : ACCELERATION * 0.6f;
            vel->x += (target_speed - vel->x) * accel * dt;
        } else {
            float friction = player->on_ground ? FRICTION : AIR_FRICTION;
            vel->x *= friction;
            if (fabsf(vel->x) < 1.0f) vel->x = 0;
        }
        
        if (vel->x < -WALK_SPEED) vel->x = -WALK_SPEED;
        if (vel->x > WALK_SPEED) vel->x = WALK_SPEED;
        
        // Jump with state machine
        if (jump && !sys->last_jump_pressed && player->state) {
            PlayerState* old_state = player->state;
            player->state->handle_jump(player, vel, &player->state);
            if (player->state != old_state && player->state->enter) {
                player->state->enter(player, vel);
            }
        }
        
        if (!jump && vel->y < 0) {
            vel->y *= 0.5f;
        }
        
        // Update state
        if (player->state && player->state->update) {
            PlayerState* old_state = player->state;
            player->state->update(player, vel, dt);
            if (player->state != old_state && player->state->enter) {
                player->state->enter(player, vel);
            }
        }
        
        sys->last_jump_pressed = jump;
    }
    
    array_free(&entities);
}

// collision system
void collision_update(System* self, World* world, float dt) {
    if (!self || !world) return;
    
    int player_required[] = {CT_PLAYER, CT_POSITION, CT_COLLIDER, CT_VELOCITY};
    Array players = world_query(world, player_required, 4);
    
    int platform_required[] = {CT_PLATFORM, CT_POSITION, CT_COLLIDER};
    Array platforms = world_query(world, platform_required, 3);
    
    int enemy_required[] = {CT_ENEMY, CT_POSITION, CT_COLLIDER};
    Array enemies = world_query(world, enemy_required, 3);
    
    int collectible_required[] = {CT_COLLECTIBLE, CT_POSITION, CT_COLLIDER};
    Array collectibles = world_query(world, collectible_required, 3);
    
    for (int i = 0; i < players.size; i++) {
        EntityID* player_ent = array_get(&players, i);
        if (!player_ent) continue;
        
        PositionComponent* p_pos = world_get_component(world, *player_ent, CT_POSITION);
        ColliderComponent* p_col = world_get_component(world, *player_ent, CT_COLLIDER);
        VelocityComponent* p_vel = world_get_component(world, *player_ent, CT_VELOCITY);
        PlayerComponent* player = world_get_component(world, *player_ent, CT_PLAYER);
        
        if (!p_pos || !p_col || !p_vel || !player) continue;
        
        player->on_ground = false;
        
        // Platform collision (same logic)
        for (int j = 0; j < platforms.size; j++) {
            EntityID* plat_ent = array_get(&platforms, j);
            if (!plat_ent) continue;
            
            PositionComponent* plat_pos = world_get_component(world, *plat_ent, CT_POSITION);
            ColliderComponent* plat_col = world_get_component(world, *plat_ent, CT_COLLIDER);
            PlatformComponent* platform = world_get_component(world, *plat_ent, CT_PLATFORM);
            
            if (!plat_pos || !plat_col || !platform) continue;
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              plat_pos->x, plat_pos->y, plat_col->width, plat_col->height)) {
                
                float px = p_pos->x + p_col->width / 2;
                float py = p_pos->y + p_col->height / 2;
                float bx = plat_pos->x + plat_col->width / 2;
                float by = plat_pos->y + plat_col->height / 2;
                
                float dx = px - bx;
                float dy = py - by;
                float wx = (p_col->width + plat_col->width) / 2;
                float wy = (p_col->height + plat_col->height) / 2;
                
                float cross_w = wx * dy;
                float cross_h = wy * dx;
                
                if (cross_w > cross_h) {
                    if (cross_w > -cross_h) {
                        if (!platform->one_way && p_vel->y < 0) {
                            p_pos->y = plat_pos->y + plat_col->height;
                            p_vel->y = 0;
                        }
                    } else {
                        if (!platform->one_way) {
                            p_pos->x = plat_pos->x - p_col->width;
                            p_vel->x = 0;
                        }
                    }
                } else {
                    if (cross_w > -cross_h) {
                        if (!platform->one_way) {
                            p_pos->x = plat_pos->x + plat_col->width;
                            p_vel->x = 0;
                        }
                    } else {
                        if (p_vel->y > 0) {
                            p_pos->y = plat_pos->y - p_col->height;
                            p_vel->y = 0;
                            player->on_ground = true;
                            player->jump_count = 0;
                        }
                    }
                }
            }
        }
        
        // Enemy collision with events
        for (int j = 0; j < enemies.size; j++) {
            EntityID* enemy_ent = array_get(&enemies, j);
            if (!enemy_ent) continue;
            
            PositionComponent* e_pos = world_get_component(world, *enemy_ent, CT_POSITION);
            ColliderComponent* e_col = world_get_component(world, *enemy_ent, CT_COLLIDER);
            
            if (!e_pos || !e_col) continue;
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              e_pos->x, e_pos->y, e_col->width, e_col->height)) {
                
                if (p_vel->y > 50 && p_pos->y + p_col->height - 5 < e_pos->y + e_col->height / 2) {
                    // Defeated enemy - emit event
                    GameEvent event = {EVENT_ENEMY_DEFEATED, *enemy_ent, 100, NULL};
                    event_system_emit(world->event_system, world, &event);
                    
                    world_destroy_entity(world, *enemy_ent);
                    p_vel->y = JUMP_SPEED * 0.6f;
                } else {
                    // Player damaged - emit event
                    GameEvent event = {EVENT_PLAYER_DAMAGED, *player_ent, 1, NULL};
                    event_system_emit(world->event_system, world, &event);
                    
                    if (!world->game_over) {
                        float dir = (p_pos->x < e_pos->x) ? -1.0f : 1.0f;
                        p_vel->x = dir * 120.0f;
                        p_vel->y = -100.0f;
                    }
                }
            }
        }
        
        // Collectibles with events
        for (int j = 0; j < collectibles.size; j++) {
            EntityID* coll_ent = array_get(&collectibles, j);
            if (!coll_ent) continue;
            
            CollectibleComponent* coll = world_get_component(world, *coll_ent, CT_COLLECTIBLE);
            if (!coll || coll->collected) continue;
            
            PositionComponent* c_pos = world_get_component(world, *coll_ent, CT_POSITION);
            ColliderComponent* c_col = world_get_component(world, *coll_ent, CT_COLLIDER);
            
            if (!c_pos || !c_col) continue;
            
            if (check_collision(p_pos->x, p_pos->y, p_col->width, p_col->height,
                              c_pos->x, c_pos->y, c_col->width, c_col->height)) {
                coll->collected = true;
                
                // Emit coin collected event
                GameEvent event = {EVENT_COIN_COLLECTED, *coll_ent, coll->points, NULL};
                event_system_emit(world->event_system, world, &event);
                
                world_destroy_entity(world, *coll_ent);
            }
        }
    }
    
    array_free(&players);
    array_free(&platforms);
    array_free(&enemies);
    array_free(&collectibles);
}



// level creation

void game_create_level(World* world) {
    assert(world);
    
    // Ground platforms using factory
    int ground_count = (WORLD_WIDTH / TILE_SIZE);
    PlatformParams ground_params = {TILE_SIZE, 20, true, false};
    
    for (int i = 0; i < ground_count; i++) {
        factory_create_platform(world, i * (float)TILE_SIZE, GROUND_HEIGHT, &ground_params);
    }
    
    // Floating platforms using factory
    struct {float x, y, w;} floating[] = {
        {200, 180, 64}, {320, 150, 64}, {480, 170, 96},
        {640, 140, 64}, {800, 160, 80}, {960, 130, 96},
        {1120, 170, 64}, {1280, 140, 80}, {1440, 160, 64},
        {1600, 130, 96}, {1760, 150, 64}, {1920, 140, 80},
        {2080, 170, 64}, {2240, 140, 96}, {2400, 160, 64},
        {2560, 130, 80}, {2720, 150, 64}, {2880, 140, 96}
    };
    
    for (int i = 0; i < sizeof(floating) / sizeof(floating[0]); i++) {
        PlatformParams params = {floating[i].w, 12, true, false};
        factory_create_platform(world, floating[i].x, floating[i].y, &params);
    }
    
    // Enemies using factory
    struct {float x, y, float start, float end, float speed;} enemy_data[] = {
        {300, 200, 250, 400, 40}, {550, 150, 500, 650, 45},
        {850, 140, 800, 950, 35}, {1200, 160, 1150, 1350, 40},
        {1500, 130, 1450, 1650, 50}, {1850, 140, 1800, 2000, 45},
        {2150, 160, 2100, 2300, 40}, {2500, 130, 2450, 2650, 50},
        {2850, 140, 2800, 3000, 45}
    };
    
    for (int i = 0; i < sizeof(enemy_data) / sizeof(enemy_data[0]); i++) {
        EnemyParams params = {enemy_data[i].speed, enemy_data[i].start, enemy_data[i].end};
        factory_create_enemy(world, enemy_data[i].x, enemy_data[i].y, &params);
    }
    
    // Coins using factory
    CollectibleParams coin_params = {50};
    for (int i = 0; i < 30; i++) {
        float coin_x = 200.0f + i * 100.0f + (i % 3) * 20.0f;
        float coin_y = 90.0f + (i % 4) * 25.0f;
        factory_create_collectible(world, coin_x, coin_y, &coin_params);
    }
    
    // Player using factory (or builder for demonstration)
    world->player_entity = factory_create_player(world, 50.0f, 180.0f);
    
    // Alternative: Using builder pattern
    // world->player_entity = builder_create(world)
    //     ->position(50, 180)
    //     ->velocity(0, 0)
    //     ->sprite(COLOR_BLUE, 16, 16)
    //     ->collider(16, 16)
    //     ->physics()
    //     ->build();
}




void game_init(World* world) {
    assert(world);
    
    world_init(world);
    
    // Initialize event system
    world->event_system = malloc(sizeof(EventSystem));
    event_system_init(world->event_system);
    
    // Subscribe to events
    event_system_subscribe(world->event_system, EVENT_GAME_OVER, on_game_over);
    
    // Add systems in correct order
    world_add_system(world, (System*)create_input_system());
    world_add_system(world, (System*)create_enemy_ai_system());
    world_add_system(world, (System*)create_physics_system());
    world_add_system(world, (System*)create_collision_system());
    world_add_system(world, (System*)create_render_system());
    
    // Create level using factories
    game_create_level(world);
}



/*

Add later to game.h:
--- Event system ---

// Forward declaration for state pattern
typedef struct PlayerState PlayerState;

// Updated PlayerComponent with state
typedef struct {
    bool on_ground;
    int jump_count;
    int lives;
    int max_jumps;
    PlayerState* state;  // NEW: State machine
} PlayerComponent;

// Event system in World
typedef struct EventSystem EventSystem;

typedef struct {
    // ... existing fields ...
    EventSystem* event_system;  // NEW: Event system
    EntityPool* entity_pools[10];  // NEW: Object pools
} World;

--- Game memento for save/load ---
*/


// save/load game state

typedef struct {
    int score;
    int lives;
    float player_x;
    float player_y;
    float camera_x;
    bool game_over;
    
    // Serialized entity data
    int entity_count;
    struct {
        EntityID id;
        float x, y;
        bool collected;  // For collectibles
        bool alive;      // For enemies
    } entities[100];
} GameMemento;

GameMemento* game_save(World* world) {
    GameMemento* memento = malloc(sizeof(GameMemento));
    
    memento->score = world->score;
    memento->game_over = world->game_over;
    memento->camera_x = world->camera_x;
    
    if (world->player_entity > 0) {
        PlayerComponent* player = world_get_component(world, world->player_entity, CT_PLAYER);
        PositionComponent* pos = world_get_component(world, world->player_entity, CT_POSITION);
        
        if (player) memento->lives = player->lives;
        if (pos) {
            memento->player_x = pos->x;
            memento->player_y = pos->y;
        }
    }
    
    // Save collectibles and enemies state
    memento->entity_count = 0;
    
    int coll_required[] = {CT_COLLECTIBLE, CT_POSITION};
    Array collectibles = world_query(world, coll_required, 2);
    
    for (int i = 0; i < collectibles.size && memento->entity_count < 100; i++) {
        EntityID* entity = array_get(&collectibles, i);
        if (!entity) continue;
        
        PositionComponent* pos = world_get_component(world, *entity, CT_POSITION);
        CollectibleComponent* coll = world_get_component(world, *entity, CT_COLLECTIBLE);
        
        if (pos && coll) {
            memento->entities[memento->entity_count].id = *entity;
            memento->entities[memento->entity_count].x = pos->x;
            memento->entities[memento->entity_count].y = pos->y;
            memento->entities[memento->entity_count].collected = coll->collected;
            memento->entity_count++;
        }
    }
    
    array_free(&collectibles);
    return memento;
}

void game_load(World* world, GameMemento* memento) {
    if (!world || !memento) return;
    
    world->score = memento->score;
    world->game_over = memento->game_over;
    world->camera_x = memento->camera_x;
    
    if (world->player_entity > 0) {
        PlayerComponent* player = world_get_component(world, world->player_entity, CT_PLAYER);
        PositionComponent* pos = world_get_component(world, world->player_entity, CT_POSITION);
        VelocityComponent* vel = world_get_component(world, world->player_entity, CT_VELOCITY);
        
        if (player) player->lives = memento->lives;
        if (pos) {
            pos->x = memento->player_x;
            pos->y = memento->player_y;
        }
        if (vel) {
            vel->x = 0;
            vel->y = 0;
        }
    }
    
    // Restore collectibles state
    for (int i = 0; i < memento->entity_count; i++) {
        CollectibleComponent* coll = world_get_component(world, 
            memento->entities[i].id, CT_COLLECTIBLE);
        
        if (coll) {
            coll->collected = memento->entities[i].collected;
        }
    }
}

void game_memento_free(GameMemento* memento) {
    free(memento);
}



// template method pattern

typedef struct {
    System base;
    void (*pre_update)(World* world, float dt);
    void (*post_update)(World* world, float dt);
} TemplateSystem;

void template_system_update(System* self, World* world, float dt) {
    TemplateSystem* sys = (TemplateSystem*)self;
    
    if (sys->pre_update) {
        sys->pre_update(world, dt);
    }
    
    // Main update logic here
    
    if (sys->post_update) {
        sys->post_update(world, dt);
    }
}



// collision strategies

typedef struct {
    void (*resolve)(PositionComponent* p1, VelocityComponent* v1, 
                   ColliderComponent* c1,
                   PositionComponent* p2, ColliderComponent* c2);
} CollisionStrategy;

void resolve_solid_collision(PositionComponent* p1, VelocityComponent* v1, 
                            ColliderComponent* c1,
                            PositionComponent* p2, ColliderComponent* c2) {
    float px = p1->x + c1->width / 2;
    float py = p1->y + c1->height / 2;
    float bx = p2->x + c2->width / 2;
    float by = p2->y + c2->height / 2;
    
    float dx = px - bx;
    float dy = py - by;
    float wx = (c1->width + c2->width) / 2;
    float wy = (c1->height + c2->height) / 2;
    
    float cross_w = wx * dy;
    float cross_h = wy * dx;
    
    if (cross_w > cross_h) {
        if (cross_w > -cross_h) {
            // Bottom
            if (v1->y < 0) {
                p1->y = p2->y + c2->height;
                v1->y = 0;
            }
        } else {
            // Left
            p1->x = p2->x - c1->width;
            v1->x = 0;
        }
    } else {
        if (cross_w > -cross_h) {
            // Right
            p1->x = p2->x + c2->width;
            v1->x = 0;
        } else {
            // Top
            if (v1->y > 0) {
                p1->y = p2->y - c1->height;
                v1->y = 0;
            }
        }
    }
}

void resolve_bounce_collision(PositionComponent* p1, VelocityComponent* v1, 
                             ColliderComponent* c1,
                             PositionComponent* p2, ColliderComponent* c2) {
    v1->x = -v1->x * 0.8f;
    v1->y = -v1->y * 0.8f;
}

CollisionStrategy SOLID_STRATEGY = {resolve_solid_collision};
CollisionStrategy BOUNCE_STRATEGY = {resolve_bounce_collision};


// shared resource manager

typedef struct {
    uint16_t color;
    uint8_t width;
    uint8_t height;
} SpriteTemplate;

typedef struct {
    float speed;
    int health;
    int points_value;
} EnemyTemplate;

typedef struct {
    HashMap sprite_templates;
    HashMap enemy_templates;
} ResourceManager;

void resource_manager_init(ResourceManager* rm) {
    hashmap_init(&rm->sprite_templates, 20);
    hashmap_init(&rm->enemy_templates, 10);
    
    // Register common templates
    SpriteTemplate* player_sprite = malloc(sizeof(SpriteTemplate));
    *player_sprite = (SpriteTemplate){COLOR_BLUE, 16, 16};
    hashmap_put(&rm->sprite_templates, 1, player_sprite);
    
    SpriteTemplate* enemy_sprite = malloc(sizeof(SpriteTemplate));
    *enemy_sprite = (SpriteTemplate){COLOR_RED, 14, 14};
    hashmap_put(&rm->sprite_templates, 2, enemy_sprite);
    
    SpriteTemplate* coin_sprite = malloc(sizeof(SpriteTemplate));
    *coin_sprite = (SpriteTemplate){COLOR_YELLOW, 10, 10};
    hashmap_put(&rm->sprite_templates, 3, coin_sprite);
    
    // Enemy templates
    EnemyTemplate* basic_enemy = malloc(sizeof(EnemyTemplate));
    *basic_enemy = (EnemyTemplate){40.0f, 1, 100};
    hashmap_put(&rm->enemy_templates, 1, basic_enemy);
    
    EnemyTemplate* fast_enemy = malloc(sizeof(EnemyTemplate));
    *fast_enemy = (EnemyTemplate){70.0f, 1, 150};
    hashmap_put(&rm->enemy_templates, 2, fast_enemy);
}

SpriteTemplate* resource_manager_get_sprite(ResourceManager* rm, int id) {
    return (SpriteTemplate*)hashmap_get(&rm->sprite_templates, id);
}

EnemyTemplate* resource_manager_get_enemy(ResourceManager* rm, int id) {
    return (EnemyTemplate*)hashmap_get(&rm->enemy_templates, id);
}

void resource_manager_free(ResourceManager* rm) {
    for (int i = 0; i < rm->sprite_templates.capacity; i++) {
        MapEntry* entry = &rm->sprite_templates.entries[i];
        while (entry && entry->value) {
            free(entry->value);
            entry->value = NULL;
            entry = entry->next;
        }
    }
    
    for (int i = 0; i < rm->enemy_templates.capacity; i++) {
        MapEntry* entry = &rm->enemy_templates.entries[i];
        while (entry && entry->value) {
            free(entry->value);
            entry->value = NULL;
            entry = entry->next;
        }
    }
    
    hashmap_free(&rm->sprite_templates);
    hashmap_free(&rm->enemy_templates);
}



// command pattern for input remapping

typedef struct Command Command;
struct Command {
    void (*execute)(World* world, EntityID entity, float dt);
    void (*undo)(World* world, EntityID entity, float dt);
};

void jump_execute(World* world, EntityID entity, float dt) {
    PlayerComponent* player = world_get_component(world, entity, CT_PLAYER);
    VelocityComponent* vel = world_get_component(world, entity, CT_VELOCITY);
    
    if (!player || !vel) return;
    
    if (player->on_ground) {
        vel->y = JUMP_SPEED;
        player->on_ground = false;
        player->jump_count = 1;
    } else if (player->jump_count < player->max_jumps) {
        vel->y = DOUBLE_JUMP_SPEED;
        player->jump_count++;
    }
}

void move_left_execute(World* world, EntityID entity, float dt) {
    VelocityComponent* vel = world_get_component(world, entity, CT_VELOCITY);
    if (vel) vel->x = -WALK_SPEED;
}

void move_right_execute(World* world, EntityID entity, float dt) {
    VelocityComponent* vel = world_get_component(world, entity, CT_VELOCITY);
    if (vel) vel->x = WALK_SPEED;
}

Command JUMP_COMMAND = {jump_execute, NULL};
Command MOVE_LEFT_COMMAND = {move_left_execute, NULL};
Command MOVE_RIGHT_COMMAND = {move_right_execute, NULL};

typedef struct {
    Command* jump;
    Command* move_left;
    Command* move_right;
} InputMapper;

void input_mapper_init(InputMapper* mapper) {
    mapper->jump = &JUMP_COMMAND;
    mapper->move_left = &MOVE_LEFT_COMMAND;
    mapper->move_right = &MOVE_RIGHT_COMMAND;
}

// Can be used to remap controls dynamically
void input_mapper_remap_jump(InputMapper* mapper, Command* new_command) {
    mapper->jump = new_command;
}


// entity hierarchies

typedef struct {
    EntityID parent;
    Array children;  // Array of EntityIDs
    float offset_x;
    float offset_y;
} HierarchyComponent;

void hierarchy_update_children(World* world, EntityID parent_id) {
    HierarchyComponent* hierarchy = world_get_component(world, parent_id, CT_HIERARCHY);
    if (!hierarchy) return;
    
    PositionComponent* parent_pos = world_get_component(world, parent_id, CT_POSITION);
    if (!parent_pos) return;
    
    for (int i = 0; i < hierarchy->children.size; i++) {
        EntityID* child_id = array_get(&hierarchy->children, i);
        if (!child_id) continue;
        
        HierarchyComponent* child_hier = world_get_component(world, *child_id, CT_HIERARCHY);
        PositionComponent* child_pos = world_get_component(world, *child_id, CT_POSITION);
        
        if (child_hier && child_pos) {
            child_pos->x = parent_pos->x + child_hier->offset_x;
            child_pos->y = parent_pos->y + child_hier->offset_y;
            
            // Recursively update grandchildren
            hierarchy_update_children(world, *child_id);
        }
    }
}

void game_init_enhanced(World* world) {
    // Subscribe to all game events
    event_system_subscribe(world->event_system, EVENT_COIN_COLLECTED, on_coin_collected);
    event_system_subscribe(world->event_system, EVENT_ENEMY_DEFEATED, on_enemy_defeated);
    event_system_subscribe(world->event_system, EVENT_PLAYER_DAMAGED, on_player_damaged);
    event_system_subscribe(world->event_system, EVENT_GAME_OVER, on_game_over);

    // Object Pool for collectibles (reuse destroyed coins)
    world->entity_pools[0] = malloc(sizeof(EntityPool));
    entity_pool_init(world->entity_pools[0], 64);   // up to 64 reusable coin IDs

    // (Other pools could be added here for enemies, bullets, etc.)
    for (int i = 1; i < 10; ++i) {
        world->entity_pools[i] = NULL;
    }

    // Input system needs to remember the previous jump button state
    InputSystem* input_sys = (InputSystem*)world->systems.data[0]; // first system
    input_sys->last_jump_pressed = false;
}
