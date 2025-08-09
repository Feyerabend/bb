
## Model Checking

Model checking is an automatic technique used to verify finite-state systems against desired properties,
typically specified in temporal logics such as LTL or CTL. It systematically explores all
possible states and transitions of the system to ensure correctness, such as absence of deadlocks,
assertion violations, or safety properties. Model checking is widely used in hardware verification,
protocol analysis, and increasingly in software verification.

For a virtual machine (VM), model checking can verify properties like "the VM never reaches an invalid
instruction" or "a certain safety condition always holds during execution."

Say we have a VM:
- A program counter (PC)
- A register (R)
- A fixed, finite instruction set:
- INC: increment R
- DEC: decrement R if > 0
- JNZ offset: jump if R ≠ 0
- HALT: stop execution

This VM is finite-state because R and PC have bounded ranges (e.g., R in [0..2], PC in program length).

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

### Overview

Thus, *model checking* is a formal verification technique used to automatically verify whether a finite-state
system satisfies a specified property, typically expressed in temporal logic such as *Linear Temporal Logic* (LTL)
or *Computation Tree Logic* ([CTL](./ctl/)). It systematically explores all possible states and transitions of a system
to ensure correctness, detecting issues like deadlocks, assertion violations, or violations of safety and liveness
properties. Model checking is widely applied in hardware verification, protocol analysis, and software systems
to ensure reliability and correctness.

#### Concepts

- System Representation: A system is modeled as a Kripke structure, a finite transition system where states
  are labeled with atomic propositions (indicating properties true in that state) and transitions represent
  possible state changes.

- Temporal Logic Specifications:
    - LTL (Linear Temporal Logic): Describes properties along a single sequence of states, suitable for
      reasoning about event sequences (e.g., "eventually something happens").
    - CTL (Computation Tree Logic): Handles branching time, allowing quantification over possible future
      paths from a state (e.g., "in all possible futures, a condition holds").
    - CTL*: A superset combining LTL and CTL, enabling complex nested temporal and path operators.
    - Probabilistic Variants: Used in systems with probabilistic transitions, such as Markov chains.

* Verification Process: The model checker constructs the Kripke structure from the system (e.g., a program
  or hardware design) and exhaustively checks whether the specified property holds across all reachable
  states. If a property is violated, a counterexample (an execution trace showing the violation) is generated.

* Applications: Ensures system correctness in critical domains like hardware circuits, network protocols,
  and concurrent software, verifying properties such as "the system never reaches an invalid state" or
  "a resource is always eventually available."


#### Example: vmmodel.c

Consider a simple virtual machine (VM) with:

- A program counter (PC) to track the current instruction.
- A single register (R) with a bounded range (e.g., 0 to 1000).
- A finite instruction set:
    - INC: Increments R (within bounds).
    - DEC: Decrements R if positive.
    - JNZ offset: Jumps to a new PC (offset from current PC) if R ≠ 0.
    - HALT: Stops execution.
    - SET n: Sets R to a specific value n.
    - ADD n: Adds n to R (within bounds).
    - SUB n: Subtracts n from R (within bounds).

The VM's state is defined by (PC, R, halted), where PC is bounded by the program length, R is bounded
by a maximum value, and halted indicates whether execution has stopped. Model checking this VM involves:

- Building a state space where each state is a tuple (PC, R, halted).
- Exploring all reachable states from an initial state (e.g., PC=0, R=0, halted=false).
- Verifying properties like "the PC never goes out of bounds" or "the VM always eventually halts."

The provided vmmodel.c implements a model checker for such a VM, using a hash set to track visited
states and a stack for depth-first exploration. It supports dynamic program loading and checks for
invalid states (e.g., out-of-bounds PC or invalid instructions), reporting metrics like states
explored and maximum stack depth.

__Benefits__
- Exhaustive verification ensures no corner cases are missed.
- Counterexamples help diagnose and fix system errors.
- Applicable to both hardware and software systems.

__Challenges__
- State Explosion: The number of states grows exponentially with system complexity, requiring
  optimisations like hash-based state storage or symbolic model checking.
- Specification Complexity: Writing correct temporal logic specifications can be non-trivial.
- Scalability: Large systems may require abstraction or partial verification to be feasible.

Model checking, actually rooted in the modal logic semantics of Kanger, Hintikka, and Kripke,
remains a cornerstone of formal verification, balancing rigorous logical foundations with
practical algorithmic techniques.

