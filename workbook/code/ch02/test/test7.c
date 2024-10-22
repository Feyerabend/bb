#include <stdio.h>
#include <stdlib.h>

#define STACK_SIZE 100
#define LOCALS_SIZE 40

// opcodes
#define HALT 0
#define ALLOC 1
#define DEALLOC 2
#define PUSH 3
#define POP 4
#define ST 5
#define LD 6
#define ARG 7
#define RVAL 8
#define CRET 9
#define PRINT 10

typedef struct {
    int stack[STACK_SIZE];   // data stack for frame
    int locals[LOCALS_SIZE]; // local variables
    int sp;                  // stack pointer
    int returnValue;         // special: return value for frame
} Frame;

// define a frame stack structure
// to keep track of multiple frames
typedef struct FrameStack {
    Frame* frames[STACK_SIZE];  // stack of frames
    int fp;                     // frame pointer
} FrameStack;

typedef struct VM {
    int* code;         // instruction code array
    int pc;            // program counter
    int code_length;   // length of the code array
    FrameStack fstack; // frame stack for handling multiple frames
} VM;

int frame(VM* vm) {
    return vm->fstack.fp;
}

int next(VM* vm) {
    return vm->code[vm->pc++];
}

void initFrameStack(FrameStack* fstack) {
    fstack->fp = -1;  // init. frame pointer to -1 (empty)
}

// push a new frame onto the frame stack
int pushFrame(VM* vm) {
    if (vm->fstack.fp >= STACK_SIZE - 1) {
        printf("Frame stack overflow!\n");
        exit(EXIT_FAILURE);
    }
    printf("Before new frame no. %d\n", vm->fstack.fp);
    Frame* frame = (Frame*) malloc(sizeof(Frame));
    frame->sp = -1;  // init. stack pointer for the frame's stack
    frame->returnValue = 0;
    vm->fstack.frames[++(vm->fstack.fp)] = frame;
    printf("Pushed new frame. Total frames: %d\n", vm->fstack.fp + 1);
    return vm->fstack.fp;  // return the current frame index
}

// pop top frame from frame stack
int popFrame(VM* vm) {
    if (vm->fstack.fp < 0) {
        printf("Frame stack underflow!\n");
        exit(EXIT_FAILURE);
    }
    free(vm->fstack.frames[vm->fstack.fp--]);
    printf("Popped frame. Remaining frames: %d\n", vm->fstack.fp + 1);
    return vm->fstack.fp + 1;  // popped frame index
}

// access specific frame by index in frame stack (0 is bottom-most frame)
Frame* getFrame(VM* vm, int frameIndex) {
    if (frameIndex < 0 || frameIndex > vm->fstack.fp) {
        printf("Invalid frame index: %d\n", frameIndex);
        return NULL;
    }
    return vm->fstack.frames[frameIndex];
}

/*
// Example: Manipulate a frame's local variable at a given index
void manipulateFrame(VM* vm, int frameIndex, int localIndex, int newValue) {
    Frame* frame = getFrame(vm, frameIndex);
    if (frame != NULL) {
        if (localIndex < 0 || localIndex >= LOCALS_SIZE) {
            printf("Invalid local variable index: %d\n", localIndex);
            return;
        }
        frame->locals[localIndex] = newValue;
        printf("Frame %d local[%d] updated to %d\n", frameIndex, localIndex, newValue);
    }
}*/

// push value onto the current frame's stack
void push(VM* vm, int value) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp >= STACK_SIZE - 1) {
        printf("Stack overflow in frame!\n");
        exit(EXIT_FAILURE);
    }
    frame->stack[++(frame->sp)] = value;
}

// pop value from current frame's stack
int pop(VM* vm) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp < 0) {
        printf("Stack underflow in frame!\n");
        exit(EXIT_FAILURE);
    }
    return frame->stack[(frame->sp)--];
}

// store value in local variable array of current frame
void store(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        printf("Invalid local variable index: %d\n", index);
        exit(EXIT_FAILURE);
    }
    int value = pop(vm);
    vm->fstack.frames[vm->fstack.fp]->locals[index] = value;
}

// load value from local variable array of current frame
void load(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        printf("Invalid local variable index: %d\n", index);
        exit(EXIT_FAILURE);
    }
    int value = vm->fstack.frames[vm->fstack.fp]->locals[index];
    push(vm, value);
}

/*
// transfer value from source frame's stack to destination frame's local variable
void transferStackToLocal(VM* vm, int srcFrameIdx, int destFrameIdx, int localIndex) {
    // Check for valid source and destination frame indices
    if (srcFrameIdx < 0 || srcFrameIdx > vm->fstack.fp || destFrameIdx < 0 || destFrameIdx > vm->fstack.fp) {
        printf("Invalid frame index!\n");
        return;
    }

    Frame* srcFrame = vm->fstack.frames[srcFrameIdx];
    Frame* destFrame = vm->fstack.frames[destFrameIdx];

    // Check if the source frame's stack is not empty
    if (srcFrame->sp < 0) {
        printf("Source frame's stack is empty!\n");
        return;
    }

    // Pop the value from the source frame's stack
    int value = srcFrame->stack[srcFrame->sp--];

    // Store the value into the destination frame's locals array
    if (localIndex >= 0 && localIndex < LOCALS_SIZE) {
        destFrame->locals[localIndex] = value;
        printf("Transferred value %d from source frame stack to destination frame local[%d].\n", value, localIndex);
    } else {
        printf("Invalid local index in the destination frame!\n");
    }
}*/

int transferStackToLocals(VM* vm, int index) {

    // move pc
    int num = next(vm);

    Frame* currentFrame = vm->fstack.frames[index];
    Frame* prevFrame = vm->fstack.frames[index - 1];

    // pop values from previous frame's stack
    for (int i = 0; i < num; ++i) {
        if (prevFrame->sp < 0) {
            printf("Not enough values on the previous frame's stack!\n");
            exit(EXIT_FAILURE);
        }

        // pop from previous frame and store in current frame's locals
        int value = prevFrame->stack[prevFrame->sp--];
        if (i < LOCALS_SIZE) {
            currentFrame->locals[i] = value;
            printf("Transferred value %d to local %d of the current frame.\n", value, i);
        } else {
            printf("Error: Too many arguments for local storage!\n");
            exit(EXIT_FAILURE);
        }
    }
    return num;
}

// transfer top value from source frame's stack to destination frame's return value
void transferStackToReturnValue(VM* vm, int srcFrameIdx, int destFrameIdx) {
    // valid source and destination frame indices, only
    if (srcFrameIdx < 0 || srcFrameIdx > vm->fstack.fp || destFrameIdx < 0 || destFrameIdx > vm->fstack.fp) {
        printf("Invalid frame index!\n");
        return;
    }

    Frame* srcFrame = vm->fstack.frames[srcFrameIdx];
    Frame* destFrame = vm->fstack.frames[destFrameIdx];

    // if source frame's stack is not empty
    if (srcFrame->sp < 0) {
        printf("Source frame's stack is empty!\n");
        return;
    }
    // could be: int value = 0; instead of empty message

    // pop value from the source frame's stack
    int value = srcFrame->stack[srcFrame->sp--];

    // store value into the destination frame's return value
    destFrame->returnValue = value;
    printf("Transferred value %d from source frame stack to destination frame's return value.\n", value);
}

// create new VM with given code and code length
VM* newVM(int* code, int code_length) {
    VM* vm = (VM*)malloc(sizeof(VM));
    if (vm == NULL) {
        return NULL;
    }
    vm->code = code;
    vm->pc = 0;  // hardcoded beginning of the code
    vm->code_length = code_length;
    initFrameStack(&(vm->fstack));
    return vm;
}

void freeVM(VM* vm) {
    while (vm->fstack.fp >= 0) {
        popFrame(vm);  // free all frames
    }
    free(vm);
}

void run(VM* vm) {
    // index used for arbitrary temp. values
    int opcode, index;

    while (1) {
        if (vm->pc >= vm->code_length) {
            printf("Program counter out of bounds!\n");
            return;
        }

        opcode = next(vm); //vm->code[vm->pc++];  // Fetch the next instruction
        printf("Executing opcode: %d\n", opcode);

        switch (opcode) {

            case ALLOC: // ALLOC (push a new frame)
                index = pushFrame(vm);
                printf("ALLOC frame no. %d\n", index);
                break;

            case DEALLOC: // DEALLOC (pop the top frame)
                index = popFrame(vm);
                printf("DELLOC frame no. %d\n", index);
                break;

            case PUSH: // PUSH (push a literal value onto the stack)
                if (vm->pc >= vm->code_length) {
                    printf("PUSH instruction missing value!\n");
                    return;
                }
                push(vm, next(vm));
                break;

            case POP:  // POP (pop the value from the stack and discard)
                index = pop(vm);
                printf("POP value = %d\n", index);
                break;

            case LD:  // LD (load from local variable array)
                if (vm->pc >= vm->code_length) {
                    printf("LD instruction missing index!\n");
                    return;
                }
                index = next(vm);
                printf("LD at index = %d\n", index);
                load(vm, index);
                break;

            case ST:  // ST (store in local variable array)
                if (vm->pc >= vm->code_length) {
                    printf("ST instruction missing index!\n");
                    return;
                }
                index = next(vm);
                printf("ST at index = %d\n", index);
                store(vm, index);
                break;

            case RVAL:
                index = frame(vm); // vm->fstack.fp;
                if (index == 0) {
                    printf("No previous frame to transfer value to!\n");
                    break;
                }

                // transfer
                transferStackToReturnValue(vm, index, index - 1);
                break;

            case ARG: // transfer from stack in frame before to locals in next
                index = frame(vm);
                if (index == 0) {
                    printf("No previous frame to transfer value to!\n");
                    break;
                }

                index = transferStackToLocals(vm, index);
                // use the index here to reserve the locals from use, only read?
                break;

            case CRET:
                index = vm->fstack.frames[vm->fstack.fp]->returnValue;
                push(vm, index);
                break;

            case PRINT:
                // printf("Top of stack: %d\n", pop(vm));
                printf("PRINT value: %d\n", pop(vm));
                break;

            case HALT:  // stop execution
                printf("Program HALT.\n");
                return;

            default:
                printf("Unknown opcode: %d\n", opcode);
                return;
        }
    }
}

int main() {

    int code[] = {

        ALLOC,      // ALLOC (main frame)
        PUSH, 1024, // PUSH 1024 (first argument)
        PUSH, 2048, // PUSH 2048 (second argument)
        PUSH, 1234, // PUSH 1234 (third argument)

           ALLOC,      // ALLOC (function frame)
           ARG, 2,     // ARG 2 (pass two arguments to new frame)

           PUSH, 99,   // PUSH 99 locally
           LD, 1,      // LD (load from from local 1 to stack)
           PRINT,      // PRINT (print result from the stack)
           LD, 0,      // LD (load from from local 0 to stack)
           PRINT,      // PRINT (print result from the stack)
 
           RVAL,       // RVAL (return result to the previous frame)
           DEALLOC,    // DEALLOC (deallocate function frame)
           CRET,       // CRET (copy return value to current stack)

        PRINT,      // PRINT (print result from the stack)
        PRINT,      // PRINT (print result from the stack)
        HALT        // HALT

    };
    int code_size = sizeof(code) / sizeof(code[0]);

    VM* vm = newVM(code, code_size);
    pushFrame(vm);  // allocate a main frame (base) at start
    run(vm);
    freeVM(vm);

    return 0;
}

