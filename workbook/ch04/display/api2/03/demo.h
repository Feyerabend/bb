#ifndef DEMO_H
#define DEMO_H
typedef struct {
    uint8_t player_sprite;
    uint8_t enemies[8];
    uint8_t bullets[16];
    uint8_t particle_system;
    uint8_t tilemap;
    int16_t player_x, player_y;
    uint32_t last_bullet_time;
    uint32_t enemy_spawn_timer;
    uint16_t score;
    bool game_running;
} game_state_t;
extern game_state_t game;
extern uint16_t bullet_texture[4*4];
void draw_ui(void);
#endif
