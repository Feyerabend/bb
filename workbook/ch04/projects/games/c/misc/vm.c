/*
 * game scripting vm
 * an experimental bytecode interpreter for game logic
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>


// instruction set

typedef enum {
    // Stack operations
    OP_PUSH,           // Push constant onto stack
    OP_POP,            // Pop from stack
    OP_DUP,            // Duplicate top of stack
    OP_SWAP,           // Swap top two stack values
    
    // Arithmetic
    OP_ADD,            // a + b
    OP_SUB,            // a - b
    OP_MUL,            // a * b
    OP_DIV,            // a / b
    OP_NEG,            // -a
    
    // Comparison
    OP_EQ,             // a == b
    OP_LT,             // a < b
    OP_GT,             // a > b
    OP_AND,            // a && b
    OP_OR,             // a || b
    OP_NOT,            // !a
    
    // Control flow
    OP_JUMP,           // Unconditional jump
    OP_JUMP_IF_FALSE,  // Conditional jump
    OP_CALL,           // Call procedure
    OP_RETURN,         // Return from procedure
    
    // Variables
    OP_LOAD_LOCAL,     // Load local variable
    OP_STORE_LOCAL,    // Store local variable
    OP_LOAD_GLOBAL,    // Load global variable
    OP_STORE_GLOBAL,   // Store global variable
    
    // Entity operations
    OP_CREATE_ENTITY,  // Create new entity
    OP_GET_COMPONENT,  // Get component from entity
    OP_SET_COMPONENT,  // Set component on entity
    OP_DESTROY_ENTITY, // Destroy entity
    OP_QUERY_ENTITIES, // Query entities by components
    
    // Event operations
    OP_EMIT_EVENT,     // Emit game event
    OP_SUBSCRIBE,      // Subscribe to event
    
    // Factory operations
    OP_CREATE_PLAYER,   // Factory: create player
    OP_CREATE_ENEMY,    // Factory: create enemy
    OP_CREATE_PLATFORM, // Factory: create platform
    OP_CREATE_COIN,     // Factory: create collectible
    
    // Advanced
    OP_CLOSURE,        // Create closure
    OP_PATTERN_MATCH,  // Pattern matching dispatch
    
    OP_HALT            // Stop execution
} OpCode;



// value types

typedef enum {
    VAL_NIL,
    VAL_BOOL,
    VAL_NUMBER,
    VAL_ENTITY,
    VAL_STRING,
    VAL_PROCEDURE,
    VAL_CLOSURE,
    VAL_NATIVE
} ValueType;

typedef struct Value Value;
typedef struct VM VM;

typedef struct {
    int address;
    int arity;
    int local_count;
} Procedure;

typedef struct {
    Procedure* proc;
    Value* upvalues;
    int upvalue_count;
} Closure;

typedef Value (*NativeFunction)(VM* vm, int arg_count);

struct Value {
    ValueType type;
    union {
        bool boolean;
        double number;
        int entity;
        char* string;
        Procedure* procedure;
        Closure* closure;
        NativeFunction native;
    } as;
};

// Value constructors
Value make_nil() {
    return (Value){.type = VAL_NIL};
}

Value make_bool(bool b) {
    return (Value){.type = VAL_BOOL, .as.boolean = b};
}

Value make_number(double n) {
    return (Value){.type = VAL_NUMBER, .as.number = n};
}

Value make_entity(int id) {
    return (Value){.type = VAL_ENTITY, .as.entity = id};
}

Value make_string(const char* str) {
    Value v = {.type = VAL_STRING};
    v.as.string = strdup(str);
    return v;
}

bool is_truthy(Value v) {
    if (v.type == VAL_NIL) return false;
    if (v.type == VAL_BOOL) return v.as.boolean;
    return true;
}

void value_print(Value v) {
    switch (v.type) {
        case VAL_NIL: printf("nil"); break;
        case VAL_BOOL: printf(v.as.boolean ? "true" : "false"); break;
        case VAL_NUMBER: printf("%g", v.as.number); break;
        case VAL_ENTITY: printf("Entity(%d)", v.as.entity); break;
        case VAL_STRING: printf("\"%s\"", v.as.string); break;
        case VAL_PROCEDURE: printf("<proc@%d>", v.as.procedure->address); break;
        case VAL_CLOSURE: printf("<closure>"); break;
        case VAL_NATIVE: printf("<native fn>"); break;
    }
}


// call frame for procedure calls

typedef struct {
    Procedure* procedure;
    int ip;              // Instruction pointer
    int stack_base;      // Base of this frame's stack
    Value* locals;       // Local variables
    int local_count;
} CallFrame;

#define MAX_FRAMES 64
#define STACK_SIZE 1024


// vm

struct VM {
    uint8_t* code;           // Bytecode
    int code_size;
    int ip;                  // Instruction pointer
    
    Value stack[STACK_SIZE]; // Value stack
    int stack_top;
    
    CallFrame frames[MAX_FRAMES];
    int frame_count;
    
    Value globals[256];      // Global variables
    
    Procedure procedures[64]; // Loaded procedures
    int procedure_count;
    
    // Game world integration
    void* world;             // World*
    void* event_system;      // EventSystem*
    
    // Native function registry
    struct {
        const char* name;
        NativeFunction fn;
    } natives[32];
    int native_count;
};


void vm_init(VM* vm, void* world, void* event_system) {
    vm->code = NULL;
    vm->code_size = 0;
    vm->ip = 0;
    vm->stack_top = 0;
    vm->frame_count = 0;
    vm->procedure_count = 0;
    vm->native_count = 0;
    vm->world = world;
    vm->event_system = event_system;
    
    for (int i = 0; i < 256; i++) {
        vm->globals[i] = make_nil();
    }
}

void vm_load_code(VM* vm, uint8_t* code, int size) {
    vm->code = malloc(size);
    memcpy(vm->code, code, size);
    vm->code_size = size;
    vm->ip = 0;
}

void vm_free(VM* vm) {
    if (vm->code) free(vm->code);
    
    // Free string values
    for (int i = 0; i < vm->stack_top; i++) {
        if (vm->stack[i].type == VAL_STRING) {
            free(vm->stack[i].as.string);
        }
    }
}



// stack operations

void push(VM* vm, Value value) {
    assert(vm->stack_top < STACK_SIZE);
    vm->stack[vm->stack_top++] = value;
}

Value pop(VM* vm) {
    assert(vm->stack_top > 0);
    return vm->stack[--vm->stack_top];
}

Value peek(VM* vm, int distance) {
    return vm->stack[vm->stack_top - 1 - distance];
}




// bytecode reading

uint8_t read_byte(VM* vm) {
    return vm->code[vm->ip++];
}

uint16_t read_short(VM* vm) {
    uint16_t value = (vm->code[vm->ip] << 8) | vm->code[vm->ip + 1];
    vm->ip += 2;
    return value;
}

double read_constant(VM* vm) {
    uint64_t bits = 0;
    for (int i = 0; i < 8; i++) {
        bits = (bits << 8) | read_byte(vm);
    }
    double value;
    memcpy(&value, &bits, sizeof(double));
    return value;
}


// procedure calls

bool call_procedure(VM* vm, Procedure* proc, int arg_count) {
    if (arg_count != proc->arity) {
        printf("ERROR: Expected %d args, got %d\n", proc->arity, arg_count);
        return false;
    }
    
    if (vm->frame_count >= MAX_FRAMES) {
        printf("ERROR: Stack overflow\n");
        return false;
    }
    
    CallFrame* frame = &vm->frames[vm->frame_count++];
    frame->procedure = proc;
    frame->ip = vm->ip;
    frame->stack_base = vm->stack_top - arg_count;
    frame->local_count = proc->local_count;
    
    // Allocate locals
    frame->locals = calloc(proc->local_count, sizeof(Value));
    
    // Copy arguments to locals
    for (int i = 0; i < arg_count; i++) {
        frame->locals[i] = vm->stack[frame->stack_base + i];
    }
    
    // Jump to procedure
    vm->ip = proc->address;
    
    return true;
}

void return_from_call(VM* vm) {
    if (vm->frame_count == 0) return;
    
    // Get return value
    Value result = pop(vm);
    
    CallFrame* frame = &vm->frames[--vm->frame_count];
    
    // Restore stack
    vm->stack_top = frame->stack_base;
    
    // Free locals
    free(frame->locals);
    
    // Restore IP
    if (vm->frame_count > 0) {
        vm->ip = frame->ip;
    }
    
    // Push return value
    push(vm, result);
}


// native instr.

Value native_print(VM* vm, int arg_count) {
    for (int i = 0; i < arg_count; i++) {
        Value v = vm->stack[vm->stack_top - arg_count + i];
        value_print(v);
        if (i < arg_count - 1) printf(" ");
    }
    printf("\n");
    vm->stack_top -= arg_count;
    return make_nil();
}

Value native_random(VM* vm, int arg_count) {
    vm->stack_top -= arg_count;
    return make_number((double)rand() / RAND_MAX);
}

Value native_sqrt(VM* vm, int arg_count) {
    if (arg_count != 1) return make_nil();
    Value v = pop(vm);
    if (v.type != VAL_NUMBER) return make_nil();
    return make_number(sqrt(v.as.number));
}

void vm_register_native(VM* vm, const char* name, NativeFunction fn) {
    assert(vm->native_count < 32);
    vm->natives[vm->native_count].name = name;
    vm->natives[vm->native_count].fn = fn;
    vm->native_count++;
}

NativeFunction vm_find_native(VM* vm, const char* name) {
    for (int i = 0; i < vm->native_count; i++) {
        if (strcmp(vm->natives[i].name, name) == 0) {
            return vm->natives[i].fn;
        }
    }
    return NULL;
}


// pattern matching

typedef struct {
    ValueType type;
    double number_value;
    bool matches_any;
} Pattern;

bool pattern_match(Value value, Pattern pattern) {
    if (pattern.matches_any) return true;
    if (pattern.type != value.type) return false;
    
    if (pattern.type == VAL_NUMBER) {
        return value.as.number == pattern.number_value;
    }
    
    return true;
}


// vm exec

typedef enum {
    EXEC_OK,
    EXEC_ERROR,
    EXEC_HALT
} ExecResult;

ExecResult vm_execute(VM* vm) {
    while (vm->ip < vm->code_size) {
        uint8_t instruction = read_byte(vm);
        
        switch (instruction) {
            // Stack operations
            case OP_PUSH: {
                double constant = read_constant(vm);
                push(vm, make_number(constant));
                break;
            }
            
            case OP_POP: {
                pop(vm);
                break;
            }
            
            case OP_DUP: {
                push(vm, peek(vm, 0));
                break;
            }
            
            case OP_SWAP: {
                Value a = pop(vm);
                Value b = pop(vm);
                push(vm, a);
                push(vm, b);
                break;
            }
            
            // Arithmetic
            case OP_ADD: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_number(a.as.number + b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_SUB: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_number(a.as.number - b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_MUL: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_number(a.as.number * b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_DIV: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    if (b.as.number == 0) return EXEC_ERROR;
                    push(vm, make_number(a.as.number / b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_NEG: {
                Value a = pop(vm);
                if (a.type == VAL_NUMBER) {
                    push(vm, make_number(-a.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            // Comparison
            case OP_EQ: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_bool(a.as.number == b.as.number));
                } else if (a.type == VAL_BOOL && b.type == VAL_BOOL) {
                    push(vm, make_bool(a.as.boolean == b.as.boolean));
                } else {
                    push(vm, make_bool(false));
                }
                break;
            }
            
            case OP_LT: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_bool(a.as.number < b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_GT: {
                Value b = pop(vm);
                Value a = pop(vm);
                if (a.type == VAL_NUMBER && b.type == VAL_NUMBER) {
                    push(vm, make_bool(a.as.number > b.as.number));
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_AND: {
                Value b = pop(vm);
                Value a = pop(vm);
                push(vm, make_bool(is_truthy(a) && is_truthy(b)));
                break;
            }
            
            case OP_OR: {
                Value b = pop(vm);
                Value a = pop(vm);
                push(vm, make_bool(is_truthy(a) || is_truthy(b)));
                break;
            }
            
            case OP_NOT: {
                Value a = pop(vm);
                push(vm, make_bool(!is_truthy(a)));
                break;
            }
            
            // Control flow
            case OP_JUMP: {
                uint16_t offset = read_short(vm);
                vm->ip = offset;
                break;
            }
            
            case OP_JUMP_IF_FALSE: {
                uint16_t offset = read_short(vm);
                Value condition = pop(vm);
                if (!is_truthy(condition)) {
                    vm->ip = offset;
                }
                break;
            }
            
            case OP_CALL: {
                uint8_t arg_count = read_byte(vm);
                Value callee = peek(vm, arg_count);
                
                if (callee.type == VAL_PROCEDURE) {
                    // Pop callee and args
                    for (int i = 0; i <= arg_count; i++) pop(vm);
                    
                    if (!call_procedure(vm, callee.as.procedure, arg_count)) {
                        return EXEC_ERROR;
                    }
                } else if (callee.type == VAL_NATIVE) {
                    Value result = callee.as.native(vm, arg_count);
                    pop(vm); // Pop callee
                    push(vm, result);
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_RETURN: {
                return_from_call(vm);
                if (vm->frame_count == 0) {
                    return EXEC_OK;
                }
                break;
            }
            
            // Variables
            case OP_LOAD_LOCAL: {
                uint8_t slot = read_byte(vm);
                if (vm->frame_count > 0) {
                    CallFrame* frame = &vm->frames[vm->frame_count - 1];
                    if (slot < frame->local_count) {
                        push(vm, frame->locals[slot]);
                    } else {
                        return EXEC_ERROR;
                    }
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_STORE_LOCAL: {
                uint8_t slot = read_byte(vm);
                if (vm->frame_count > 0) {
                    CallFrame* frame = &vm->frames[vm->frame_count - 1];
                    if (slot < frame->local_count) {
                        frame->locals[slot] = peek(vm, 0);
                    } else {
                        return EXEC_ERROR;
                    }
                } else {
                    return EXEC_ERROR;
                }
                break;
            }
            
            case OP_LOAD_GLOBAL: {
                uint8_t slot = read_byte(vm);
                push(vm, vm->globals[slot]);
                break;
            }
            
            case OP_STORE_GLOBAL: {
                uint8_t slot = read_byte(vm);
                vm->globals[slot] = peek(vm, 0);
                break;
            }
            
            // Game-specific operations
            case OP_CREATE_PLAYER: {
                Value y = pop(vm);
                Value x = pop(vm);
                if (x.type != VAL_NUMBER || y.type != VAL_NUMBER) {
                    return EXEC_ERROR;
                }
                
                // Call factory_create_player(world, x, y)
                // EntityID id = factory_create_player(vm->world, x.as.number, y.as.number);
                int id = 1; // Placeholder
                push(vm, make_entity(id));
                break;
            }
            
            case OP_CREATE_ENEMY: {
                Value patrol_end = pop(vm);
                Value patrol_start = pop(vm);
                Value speed = pop(vm);
                Value y = pop(vm);
                Value x = pop(vm);
                
                // EnemyParams params = {speed.as.number, patrol_start.as.number, patrol_end.as.number};
                // EntityID id = factory_create_enemy(vm->world, x.as.number, y.as.number, &params);
                int id = 2; // Placeholder
                push(vm, make_entity(id));
                break;
            }
            
            case OP_EMIT_EVENT: {
                Value data = pop(vm);
                Value value = pop(vm);
                Value entity = pop(vm);
                Value type = pop(vm);
                
                // GameEvent event = {type.as.number, entity.as.entity, value.as.number, NULL};
                // event_system_emit(vm->event_system, vm->world, &event);
                push(vm, make_nil());
                break;
            }
            
            case OP_HALT: {
                return EXEC_HALT;
            }
            
            default:
                printf("Unknown opcode: %d\n", instruction);
                return EXEC_ERROR;
        }
    }
    
    return EXEC_OK;
}


// bytecode assembler

typedef struct {
    uint8_t* code;
    int size;
    int capacity;
} BytecodeBuilder;

void builder_init(BytecodeBuilder* b) {
    b->capacity = 256;
    b->code = malloc(b->capacity);
    b->size = 0;
}

void builder_emit(BytecodeBuilder* b, uint8_t byte) {
    if (b->size >= b->capacity) {
        b->capacity *= 2;
        b->code = realloc(b->code, b->capacity);
    }
    b->code[b->size++] = byte;
}

void builder_emit_short(BytecodeBuilder* b, uint16_t value) {
    builder_emit(b, (value >> 8) & 0xFF);
    builder_emit(b, value & 0xFF);
}

void builder_emit_constant(BytecodeBuilder* b, double value) {
    uint64_t bits;
    memcpy(&bits, &value, sizeof(double));
    for (int i = 7; i >= 0; i--) {
        builder_emit(b, (bits >> (i * 8)) & 0xFF);
    }
}

int builder_current_address(BytecodeBuilder* b) {
    return b->size;
}



// high-level script examples

void compile_spawn_enemy_script(BytecodeBuilder* b) {
    /*
    Script (pseudocode):
    
    proc spawn_enemy(x, y):
        enemy = create_enemy(x, y, 40, x-50, x+50)
        return enemy
    
    proc game_logic():
        if score > 100:
            spawn_enemy(300, 200)
    */
    
    // Main program
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 300);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 200);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 40);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 250);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 350);
    
    builder_emit(b, OP_CREATE_ENEMY);
    
    builder_emit(b, OP_HALT);
}

void compile_event_handler_script(BytecodeBuilder* b) {
    /*
    Script:
    
    proc on_coin_collected(entity, value):
        score = load_global(0)
        score = score + value
        store_global(0, score)
        
        if score > 500:
            emit_event(EVENT_GAME_WON, 0, 0, nil)
    */
    
    // Load score (global 0)
    builder_emit(b, OP_LOAD_GLOBAL);
    builder_emit(b, 0);
    
    // Load value parameter (local 1)
    builder_emit(b, OP_LOAD_LOCAL);
    builder_emit(b, 1);
    
    // Add
    builder_emit(b, OP_ADD);
    
    // Store back to global
    builder_emit(b, OP_STORE_GLOBAL);
    builder_emit(b, 0);
    
    // Check if score > 500
    builder_emit(b, OP_LOAD_GLOBAL);
    builder_emit(b, 0);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 500);
    
    builder_emit(b, OP_GT);
    
    // Jump if false (skip event emission)
    builder_emit(b, OP_JUMP_IF_FALSE);
    int jump_addr = builder_current_address(b);
    builder_emit_short(b, 0); // Placeholder
    
    // Emit victory event
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 5); // EVENT_GAME_WON
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 0);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 0);
    
    builder_emit(b, OP_PUSH);
    builder_emit_constant(b, 0);
    
    builder_emit(b, OP_EMIT_EVENT);
    
    // Patch jump address
    int end_addr = builder_current_address(b);
    b->code[jump_addr] = (end_addr >> 8) & 0xFF;
    b->code[jump_addr + 1] = end_addr & 0xFF;
    
    builder_emit(b, OP_RETURN);
}


// usage

void vm_demo() {
    printf("--- Game VM Demo ---\n\n");
    
    VM vm;
    vm_init(&vm, NULL, NULL);
    
    // Register native functions
    vm_register_native(&vm, "print", native_print);
    vm_register_native(&vm, "random", native_random);
    vm_register_native(&vm, "sqrt", native_sqrt);
    
    // Compile a simple script
    BytecodeBuilder builder;
    builder_init(&builder);
    
    // Script: calculate 10 + 20 * 3
    builder_emit(&builder, OP_PUSH);
    builder_emit_constant(&builder, 10);
    
    builder_emit(&builder, OP_PUSH);
    builder_emit_constant(&builder, 20);
    
    builder_emit(&builder, OP_PUSH);
    builder_emit_constant(&builder, 3);
    
    builder_emit(&builder, OP_MUL);
    builder_emit(&builder, OP_ADD);
    
    builder_emit(&builder, OP_HALT);
    
    // Load and execute
    vm_load_code(&vm, builder.code, builder.size);
    
    ExecResult result = vm_execute(&vm);
    
    if (result == EXEC_OK || result == EXEC_HALT) {
        printf("Result: ");
        value_print(vm.stack[vm.stack_top - 1]);
        printf("\n");
    } else {
        printf("Execution error!\n");
    }
    
    // Cleanup
    vm_free(&vm);
    free(builder.code);
    
    printf("\n--- Demo Complete ---\n");
}


int main() {
    vm_demo();
    return 0;
}
