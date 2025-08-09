#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#define MAX_PROGRAM 100
#define MAX_STATES 10000
#define MAX_REGISTER_VALUE 1000
#define HASH_TABLE_SIZE 4096

typedef enum { 
    INC, 
    DEC, 
    JNZ, 
    HALT,
    SET,
    ADD,
    SUB
} OpCode;

typedef struct {
    OpCode op;
    int operand;  // offset for JNZ, immediate value for SET/ADD/SUB
} Instruction;

typedef struct {
    int pc;
    int r;
    bool halted;
    uint32_t hash;  // cached hash for performance
} State;

typedef struct StateNode {
    State state;
    struct StateNode* next;
} StateNode;

typedef struct {
    StateNode* buckets[HASH_TABLE_SIZE];
    int count;
} StateHashSet;

typedef struct {
    State* states;
    int count;
    int capacity;
} StateStack;

typedef struct {
    Instruction* instructions;
    int length;
    int capacity;
} Program;

Program g_program = {0};

// hash for states
uint32_t hash_state(State s) {
    if (s.hash != 0) return s.hash;
    
    uint32_t hash = 2166136261u; // FNV-1a offset basis
    hash ^= (uint32_t)s.pc;
    hash *= 16777619u; // FNV-1a prime
    hash ^= (uint32_t)s.r;
    hash *= 16777619u;
    hash ^= (uint32_t)s.halted;
    hash *= 16777619u;
    
    return hash ? hash : 1; // non-zero hash
}

State create_state(int pc, int r, bool halted) {
    State s = {pc, r, halted, 0};
    s.hash = hash_state(s);
    return s;
}

bool states_equal(State a, State b) {
    return a.pc == b.pc && a.r == b.r && a.halted == b.halted;
}

// Hash set operations
StateHashSet* create_state_set(void) {
    StateHashSet* set = calloc(1, sizeof(StateHashSet));
    return set;
}

void destroy_state_set(StateHashSet* set) {
    if (!set) return;
    
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        StateNode* node = set->buckets[i];
        while (node) {
            StateNode* next = node->next;
            free(node);
            node = next;
        }
    }
    free(set);
}

bool state_in_set(StateHashSet* set, State s) {
    if (!set) return false;
    
    uint32_t hash = s.hash ? s.hash : hash_state(s);
    int bucket = hash % HASH_TABLE_SIZE;
    
    StateNode* node = set->buckets[bucket];
    while (node) {
        if (states_equal(node->state, s)) return true;
        node = node->next;
    }
    return false;
}

bool add_state_to_set(StateHashSet* set, State s) {
    if (!set || state_in_set(set, s)) return false;
    
    uint32_t hash = s.hash ? s.hash : hash_state(s);
    int bucket = hash % HASH_TABLE_SIZE;
    
    StateNode* node = malloc(sizeof(StateNode));
    if (!node) {
        fprintf(stderr, "Memory allocation failed\n");
        return false;
    }
    
    node->state = s;
    node->state.hash = hash;
    node->next = set->buckets[bucket];
    set->buckets[bucket] = node;
    set->count++;
    
    return true;
}

// stack operations
StateStack* create_state_stack(void) {
    StateStack* stack = malloc(sizeof(StateStack));
    if (!stack) return NULL;
    
    stack->capacity = 1024;
    stack->states = malloc(sizeof(State) * stack->capacity);
    stack->count = 0;
    
    if (!stack->states) {
        free(stack);
        return NULL;
    }
    
    return stack;
}

void destroy_state_stack(StateStack* stack) {
    if (!stack) return;
    free(stack->states);
    free(stack);
}

bool push_state(StateStack* stack, State s) {
    if (!stack) return false;
    
    if (stack->count >= stack->capacity) {
        int new_capacity = stack->capacity * 2;
        State* new_states = realloc(stack->states, sizeof(State) * new_capacity);
        if (!new_states) {
            fprintf(stderr, "Stack reallocation failed\n");
            return false;
        }
        stack->states = new_states;
        stack->capacity = new_capacity;
    }
    
    stack->states[stack->count++] = s;
    return true;
}

bool pop_state(StateStack* stack, State* out) {
    if (!stack || stack->count == 0) return false;
    
    *out = stack->states[--stack->count];
    return true;
}


bool init_program(int capacity) {
    g_program.instructions = malloc(sizeof(Instruction) * capacity);
    if (!g_program.instructions) return false;
    
    g_program.capacity = capacity;
    g_program.length = 0;
    return true;
}

void destroy_program(void) {
    free(g_program.instructions);
    g_program.instructions = NULL;
    g_program.capacity = g_program.length = 0;
}

bool add_instruction(OpCode op, int operand) {
    if (g_program.length >= g_program.capacity) {
        fprintf(stderr, "Program capacity exceeded\n");
        return false;
    }
    
    g_program.instructions[g_program.length++] = (Instruction){op, operand};
    return true;
}

void print_state(State s) {
    printf("State(pc=%d, r=%d, halted=%s)\n", 
           s.pc, s.r, s.halted ? "true" : "false");
}

void print_program(void) {
    const char* op_names[] = {"INC", "DEC", "JNZ", "HALT", "SET", "ADD", "SUB"};
    
    printf("Program:\n");
    for (int i = 0; i < g_program.length; i++) {
        Instruction instr = g_program.instructions[i];
        printf("%2d: %s", i, op_names[instr.op]);
        
        if (instr.op == JNZ) {
            printf(" %+d", instr.operand);
        } else if (instr.op == SET || instr.op == ADD || instr.op == SUB) {
            printf(" %d", instr.operand);
        }
        printf("\n");
    }
    printf("\n");
}

// bounds check for register values
int clamp_register(int value) {
    if (value < 0) return 0;
    if (value > MAX_REGISTER_VALUE) return MAX_REGISTER_VALUE;
    return value;
}

typedef struct {
    bool success;
    int states_explored;
    int max_stack_depth;
    char error_message[256];
} ModelCheckResult;

ModelCheckResult model_check(bool verbose) {
    ModelCheckResult result = {false, 0, 0, ""};
    
    StateHashSet* visited = create_state_set();
    StateStack* stack = create_state_stack();
    
    if (!visited || !stack) {
        strcpy(result.error_message, "Memory allocation failed");
        goto cleanup;
    }
    
    State initial = create_state(0, 0, false);
    
    if (!push_state(stack, initial)) {
        strcpy(result.error_message, "Failed to initialize stack");
        goto cleanup;
    }
    
    if (verbose) {
        printf("Starting model check ..\n");
        print_program();
    }
    
    State current;
    while (pop_state(stack, &current)) {
        result.max_stack_depth = (stack->count > result.max_stack_depth) 
                                 ? stack->count : result.max_stack_depth;
        
        if (state_in_set(visited, current)) continue;
        
        add_state_to_set(visited, current);
        result.states_explored++;
        
        if (verbose && result.states_explored % 100 == 0) {
            printf("Explored %d states ..\n", result.states_explored);
        }
        
        if (current.halted) continue;
        
        // Bounds checking
        if (current.pc < 0 || current.pc >= g_program.length) {
            snprintf(result.error_message, sizeof(result.error_message),
                    "PC out of bounds (%d) at state with r=%d", 
                    current.pc, current.r);
            goto cleanup;
        }
        
        Instruction instr = g_program.instructions[current.pc];
        
        switch (instr.op) {
            case INC: {
                int new_r = clamp_register(current.r + 1);
                State next = create_state(current.pc + 1, new_r, false);
                if (!state_in_set(visited, next)) {
                    push_state(stack, next);
                }
                break;
            }
            
            case DEC: {
                int new_r = clamp_register(current.r - 1);
                State next = create_state(current.pc + 1, new_r, false);
                if (!state_in_set(visited, next)) {
                    push_state(stack, next);
                }
                break;
            }
            
            case SET: {
                int new_r = clamp_register(instr.operand);
                State next = create_state(current.pc + 1, new_r, false);
                if (!state_in_set(visited, next)) {
                    push_state(stack, next);
                }
                break;
            }
            
            case ADD: {
                int new_r = clamp_register(current.r + instr.operand);
                State next = create_state(current.pc + 1, new_r, false);
                if (!state_in_set(visited, next)) {
                    push_state(stack, next);
                }
                break;
            }
            
            case SUB: {
                int new_r = clamp_register(current.r - instr.operand);
                State next = create_state(current.pc + 1, new_r, false);
                if (!state_in_set(visited, next)) {
                    push_state(stack, next);
                }
                break;
            }
            
            case JNZ: {
                //  if register is non-zero
                if (current.r != 0) {
                    int jump_pc = current.pc + instr.operand;
                    if (jump_pc >= 0 && jump_pc < g_program.length) {
                        State jump_state = create_state(jump_pc, current.r, false);
                        if (!state_in_set(visited, jump_state)) {
                            push_state(stack, jump_state);
                        }
                    }
                }
                
                // try fall-through
                State fallthrough = create_state(current.pc + 1, current.r, false);
                if (!state_in_set(visited, fallthrough)) {
                    push_state(stack, fallthrough);
                }
                break;
            }
            
            case HALT: {
                State halted_state = create_state(current.pc, current.r, true);
                if (!state_in_set(visited, halted_state)) {
                    push_state(stack, halted_state);
                }
                break;
            }
            
            default:
                snprintf(result.error_message, sizeof(result.error_message),
                        "Invalid instruction at PC %d", current.pc);
                goto cleanup;
        }
    }
    
    result.success = true;
    if (verbose) {
        printf("Model checking complete!\n");
        printf("States explored: %d\n", result.states_explored);
        printf("Max stack depth: %d\n", result.max_stack_depth);
        printf("Hash set load: %.2f%%\n", 
               (double)visited->count / HASH_TABLE_SIZE * 100.0);
    }
    
cleanup:
    destroy_state_set(visited);
    destroy_state_stack(stack);
    return result;
}

// Example programs
void load_example_program_1(void) {
    printf("Loading example program 1 (simple loop) ..\n");
    
    init_program(10);
    add_instruction(INC, 0);      // r = 1
    add_instruction(JNZ, 2);      // if r != 0 jump +2
    add_instruction(INC, 0);      // skipped if jump taken
    add_instruction(DEC, 0);      // decrement r
    add_instruction(JNZ, -3);     // if r != 0 jump -3 (loop)
    add_instruction(HALT, 0);     // stop
}

void load_example_program_2(void) {
    printf("Loading example program 2 (counter with bounds) ..\n");
    
    init_program(15);
    add_instruction(SET, 5);      // r = 5
    add_instruction(DEC, 0);      // r = r - 1
    add_instruction(JNZ, -1);     // loop while r != 0
    add_instruction(ADD, 10);     // r = r + 10
    add_instruction(SUB, 3);      // r = r - 3
    add_instruction(JNZ, 1);      // if r != 0, jump +1
    add_instruction(HALT, 0);     // stop
    add_instruction(SET, 0);      // r = 0
    add_instruction(HALT, 0);     // stop
}

int main(int argc, char* argv[]) {
    bool verbose = false;
    int example = 1;
    
    // Simple argument parsing
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--verbose") == 0) {
            verbose = true;
        } else if (strcmp(argv[i], "-e2") == 0) {
            example = 2;
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            printf("Usage: %s [-v|--verbose] [-e2] [-h|--help]\n", argv[0]);
            printf("  -v, --verbose  Enable verbose output\n");
            printf("  -e2            Run example program 2 instead of 1\n");
            printf("  -h, --help     Show this help\n");
            return 0;
        }
    }
    
    // Load selected example program
    if (example == 2) {
        load_example_program_2();
    } else {
        load_example_program_1();
    }
    
    ModelCheckResult result = model_check(verbose);
    
    if (result.success) {
        printf("  Model checking completed successfully\n");
        printf("  States explored: %d\n", result.states_explored);
        printf("  Max stack depth: %d\n", result.max_stack_depth);
    } else {
        printf("  Model checking failed: %s\n", result.error_message);
        destroy_program();
        return 1;
    }
    
    destroy_program();
    return 0;
}

