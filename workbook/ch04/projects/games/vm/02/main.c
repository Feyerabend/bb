/* vm_game.c – VM-controlled game for Pimoroni DisplayPack 2.0 */
#include "pico/stdlib.h"
#include "display.h"
#include <stdlib.h>
#include <string.h>

#define MAX_ENTITIES   32
#define COMP_SIZE      16
#define MAX_CODE       2048
#define CELL_SIZE      8  // 8x8 pixel cells for visibility

/*  Flat memory (ECS)  */
static uint8_t mem[MAX_ENTITIES * COMP_SIZE];
static bool should_quit = false;

/*  Component offsets  */
#define OFF_X      0
#define OFF_Y      2
#define OFF_DX     4
#define OFF_DY     6
#define OFF_PLAYER 8
#define OFF_AI     9
#define OFF_STATE  10
#define OFF_TIMER  11

/*  Simple VM  */
typedef struct {
    uint8_t code[MAX_CODE];
    uint32_t len;
} VM;

/*  Opcodes  */
enum {
    OP_CALL_INPUT = 1,
    OP_CALL_AI,
    OP_CALL_MOVE,
    OP_CALL_CLAMP,
    OP_CALL_FLASH,
    OP_CALL_RENDER,
    OP_HALT
};

/*  Memory helpers  */
static inline int16_t read16(uint32_t e, int o) { 
    return *(int16_t*)(mem + e*COMP_SIZE + o); 
}
static inline void write16(uint32_t e, int o, int16_t v) { 
    *(int16_t*)(mem + e*COMP_SIZE + o) = v; 
}
static inline uint8_t read8(uint32_t e, int o) { 
    return mem[e*COMP_SIZE + o]; 
}
static inline void write8(uint32_t e, int o, uint8_t v) { 
    mem[e*COMP_SIZE + o] = v; 
}

/*  Game Systems (called by VM)  */
static void sys_input(uint32_t entity) {
    // Read hardware buttons
    if (button_pressed(BUTTON_Y)) {
        write16(entity, OFF_DX, 0);
        write16(entity, OFF_DY, -1);
    } else if (button_pressed(BUTTON_A)) {
        write16(entity, OFF_DX, 0);
        write16(entity, OFF_DY, 1);
    } else if (button_pressed(BUTTON_X)) {
        write16(entity, OFF_DX, -1);
        write16(entity, OFF_DY, 0);
    } else if (button_pressed(BUTTON_B)) {
        write16(entity, OFF_DX, 1);
        write16(entity, OFF_DY, 0);
    }
}

static void sys_ai(uint32_t entity) {
    if (rand() % 5 == 0) {
        write16(entity, OFF_DX, (rand() % 3) - 1);
        write16(entity, OFF_DY, (rand() % 3) - 1);
    }
}

static void sys_move(uint32_t entity) {
    int16_t x = read16(entity, OFF_X);
    int16_t y = read16(entity, OFF_Y);
    x += read16(entity, OFF_DX);
    y += read16(entity, OFF_DY);
    write16(entity, OFF_X, x);
    write16(entity, OFF_Y, y);
}

static void sys_clamp(uint32_t entity) {
    // Game field is in cell coordinates
    const int16_t max_x = (DISPLAY_WIDTH / CELL_SIZE) - 1;
    const int16_t max_y = (DISPLAY_HEIGHT / CELL_SIZE) - 1;
    
    int16_t x = read16(entity, OFF_X);
    int16_t y = read16(entity, OFF_Y);
    
    if (x < 0) x = 0;
    if (x > max_x) x = max_x;
    if (y < 0) y = 0;
    if (y > max_y) y = max_y;
    
    write16(entity, OFF_X, x);
    write16(entity, OFF_Y, y);
}

static void sys_flash(uint32_t entity) {
    if (read8(entity, OFF_STATE)) {
        uint8_t timer = read8(entity, OFF_TIMER);
        if (timer > 0) {
            write8(entity, OFF_TIMER, timer - 1);
        } else {
            write8(entity, OFF_STATE, 0);
        }
    }
}

static void sys_render(void) {
    // Clear screen
    display_clear(COLOR_BLACK);
    
    // Render all entities
    for (int e = 0; e < MAX_ENTITIES; ++e) {
        if (!read8(e, OFF_PLAYER) && !read8(e, OFF_AI)) continue;
        
        int16_t cell_x = read16(e, OFF_X);
        int16_t cell_y = read16(e, OFF_Y);
        
        // Convert cell coordinates to pixel coordinates
        uint16_t px = cell_x * CELL_SIZE;
        uint16_t py = cell_y * CELL_SIZE;
        
        // Choose color based on entity type
        uint16_t color;
        if (read8(e, OFF_PLAYER)) {
            color = COLOR_GREEN;  // Player is green
        } else if (read8(e, OFF_STATE)) {
            color = COLOR_YELLOW; // Flashing AI is yellow
        } else {
            color = COLOR_RED;    // Normal AI is red
        }
        
        // Draw entity as filled square
        display_fill_rect(px, py, CELL_SIZE, CELL_SIZE, color);
    }
}

/*  VM Interpreter  */
static void vm_run(VM *vm) {
    uint32_t pc = 0;
    
    while (pc < vm->len) {
        uint8_t op = vm->code[pc++];
        uint8_t entity;
        
        switch (op) {
            case OP_CALL_INPUT:
                entity = vm->code[pc++];
                sys_input(entity);
                break;
                
            case OP_CALL_AI:
                entity = vm->code[pc++];
                sys_ai(entity);
                break;
                
            case OP_CALL_MOVE:
                entity = vm->code[pc++];
                sys_move(entity);
                break;
                
            case OP_CALL_CLAMP:
                entity = vm->code[pc++];
                sys_clamp(entity);
                break;
                
            case OP_CALL_FLASH:
                entity = vm->code[pc++];
                sys_flash(entity);
                break;
                
            case OP_CALL_RENDER:
                sys_render();
                break;
                
            case OP_HALT:
                return;
                
            default:
                return; /* Unknown opcode, halt */
        }
    }
}

/*  Build game bytecode  */
static void build_game_code(VM *vm) {
    uint32_t i = 0;
    
    /* Handle player input */
    vm->code[i++] = OP_CALL_INPUT;
    vm->code[i++] = 0;  /* entity 0 = player */
    
    /* Update AI entities (1, 2, 3) */
    for (int e = 1; e < 4; e++) {
        vm->code[i++] = OP_CALL_AI;
        vm->code[i++] = e;
    }
    
    /* Update flash timers */
    for (int e = 1; e < 4; e++) {
        vm->code[i++] = OP_CALL_FLASH;
        vm->code[i++] = e;
    }
    
    /* Move all entities (0=player, 1-3=AI) */
    for (int e = 0; e < 4; e++) {
        vm->code[i++] = OP_CALL_MOVE;
        vm->code[i++] = e;
    }
    
    /* Clamp all entities to screen bounds */
    for (int e = 0; e < 4; e++) {
        vm->code[i++] = OP_CALL_CLAMP;
        vm->code[i++] = e;
    }
    
    /* Render everything */
    vm->code[i++] = OP_CALL_RENDER;
    
    /* Halt (end of frame) */
    vm->code[i++] = OP_HALT;
    
    vm->len = i;
}

/*  Main  */
int main(void) {
    // Initialize Pico SDK
    stdio_init_all();
    
    // Seed random number generator
    srand(time_us_32());
    
    // Initialize display and buttons
    if (display_pack_init() != DISPLAY_OK) {
        return -1;
    }
    if (buttons_init() != DISPLAY_OK) {
        return -1;
    }
    
    // Clear screen to black
    display_clear(COLOR_BLACK);
    
    // Calculate game field dimensions in cells
    const int16_t max_x = (DISPLAY_WIDTH / CELL_SIZE) - 1;
    const int16_t max_y = (DISPLAY_HEIGHT / CELL_SIZE) - 1;
    
    /* Initialize player (entity 0) at center */
    write16(0, OFF_X, max_x / 2); 
    write16(0, OFF_Y, max_y / 2);
    write8(0, OFF_PLAYER, 1);
    
    /* Initialize AI entities (1, 2, 3) at random positions */
    for (int i = 1; i < 4; ++i) {
        write16(i, OFF_X, rand() % max_x);
        write16(i, OFF_Y, rand() % max_y);
        write16(i, OFF_DX, (rand() % 3) - 1);
        write16(i, OFF_DY, (rand() % 3) - 1);
        write8(i, OFF_AI, 1);
    }
    
    /* Build VM program */
    VM vm = {0};
    build_game_code(&vm);
    
    /* Game loop: run VM each frame */
    while (!should_quit) {
        // Update button states
        buttons_update();
        
        // Run VM for this frame
        vm_run(&vm);
        
        // Frame delay (~20 FPS)
        sleep_ms(50);
    }
    
    // Cleanup
    display_cleanup();
    return 0;
}
