
## Model Checking

Model checking is an automatic technique used to verify finite-state systems against desired properties, typically specified in temporal logics such as LTL or CTL. It systematically explores all possible states and transitions of the system to ensure correctness, such as absence of deadlocks, assertion violations, or safety properties. Model checking is widely used in hardware verification, protocol analysis, and increasingly in software verification.

For a virtual machine (VM), model checking can verify properties like "the VM never reaches an invalid instruction" or "a certain safety condition always holds during execution."


- A program counter (PC)
- A register (R)
- A fixed, finite instruction set:
- INC: increment R
- DEC: decrement R if > 0
- JNZ offset: jump if R ≠ 0
- HALT: stop execution

This VM is finite-state because R and PC have bounded ranges (e.g., R in [0..2], PC in program length).

model.c

```c
#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PROGRAM 10
#define MAX_STATES 1000

typedef enum { INC, DEC, JNZ, HALT } OpCode;

typedef struct {
    OpCode op;
    int offset;  // only used for JNZ
} Instruction;

typedef struct {
    int pc;
    int r;
    bool halted;
} State;

Instruction program[MAX_PROGRAM] = {
    {INC, 0},          // r = 1
    {JNZ, 2},          // if r != 0 jump +2
    {INC, 0},          // skipped if jump taken
    {DEC, 0},          // decrement r
    {JNZ, -3},         // if r != 0 jump -3 (loop)
    {HALT, 0}          // stop
};

int program_length = 6;

typedef struct {
    State states[MAX_STATES];
    int count;
} StateSet;

bool states_equal(State a, State b) {
    return a.pc == b.pc && a.r == b.r && a.halted == b.halted;
}

bool state_in_set(StateSet *set, State s) {
    for (int i = 0; i < set->count; i++) {
        if (states_equal(set->states[i], s)) return true;
    }
    return false;
}

void add_state(StateSet *set, State s) {
    if (set->count < MAX_STATES) {
        set->states[set->count++] = s;
    } else {
        printf("State set overflow!\n");
    }
}

void print_state(State s) {
    printf("State(pc=%d, r=%d, halted=%d)\n", s.pc, s.r, s.halted);
}

bool model_check() {
    StateSet visited = { .count = 0 };
    StateSet stack = { .count = 0 };

    State initial = { .pc = 0, .r = 0, .halted = false };
    add_state(&stack, initial);

    while (stack.count > 0) {
        // Pop last state
        State current = stack.states[--stack.count];

        if (state_in_set(&visited, current)) continue;
        add_state(&visited, current);

        if (current.halted) continue;

        if (current.pc < 0 || current.pc >= program_length) {
            printf("Error: PC out of bounds at state ");
            print_state(current);
            return false;
        }

        Instruction instr = program[current.pc];

        switch (instr.op) {
            case INC: {
                int new_r = current.r < 2 ? current.r + 1 : current.r;
                State next = { current.pc + 1, new_r, false };
                if (!state_in_set(&visited, next)) add_state(&stack, next);
                break;
            }
            case DEC: {
                int new_r = current.r > 0 ? current.r - 1 : current.r;
                State next = { current.pc + 1, new_r, false };
                if (!state_in_set(&visited, next)) add_state(&stack, next);
                break;
            }
            case JNZ: {
                if (current.r != 0) {
                    State jump_state = { current.pc + instr.offset, current.r, false };
                    if (!state_in_set(&visited, jump_state)) add_state(&stack, jump_state);
                }
                State fallthrough = { current.pc + 1, current.r, false };
                if (!state_in_set(&visited, fallthrough)) add_state(&stack, fallthrough);
                break;
            }
            case HALT: {
                State halted_state = { current.pc, current.r, true };
                if (!state_in_set(&visited, halted_state)) add_state(&stack, halted_state);
                break;
            }
            default:
                printf("Invalid instruction\n");
                return false;
        }
    }
    printf("Model checking complete: no invalid states found.\n");
    return true;
}

int main() {
    if (!model_check()) {
        printf("Model checking failed.\n");
        return 1;
    }
    return 0;
}
```

