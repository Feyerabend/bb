#include <stdio.h>
#include <stdlib.h>

#define STACK_SIZE 100
#define LOCALS_SIZE 40
#define OBJECT_CAPACITY 100

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

// Frame stack structure to keep track of multiple frames
typedef struct FrameStack {
    Frame* frames[STACK_SIZE];  // stack of frames
    int fp;                     // frame pointer
} FrameStack;

typedef struct {
    int* objects;  // dynamic array to hold objects
    int obj_count; // current number of objects
    int capacity;  // maximum capacity of objects
} ObjectManager;

typedef struct VM {
    int* code;         // instruction code array
    int pc;            // program counter
    int code_length;   // length of the code array
    FrameStack fstack; // frame stack for handling multiple frames
    ObjectManager objects; // Object manager
} VM;

// Function prototypes
int frame(VM* vm);
int next(VM* vm);
void initFrameStack(FrameStack* fstack);
int pushFrame(VM* vm);
int popFrame(VM* vm);
Frame* getFrame(VM* vm, int frameIndex);
void push(VM* vm, int value);
int pop(VM* vm);
void store(VM* vm, int index);
void load(VM* vm, int index);
int transferStackToLocals(VM* vm, int index);
void transferStackToReturnValue(VM* vm, int srcFrameIdx, int destFrameIdx);
VM* newVM(int* code, int code_length);
void freeVM(VM* vm);
void run(VM* vm);
void initObjectManager(ObjectManager* manager);
int createObject(ObjectManager* manager);
void setField(ObjectManager* manager, int objIndex, int fieldIndex, int value);
int getField(ObjectManager* manager, int objIndex, int fieldIndex);

// Initialize the object manager
void initObjectManager(ObjectManager* manager) {
    manager->objects = (int*)malloc(OBJECT_CAPACITY * sizeof(int)); // Dynamically allocate memory
    manager->obj_count = 0; // Initialize the object count
    manager->capacity = OBJECT_CAPACITY; // Set the capacity
}

// Create a new object
int createObject(ObjectManager* manager) {
    if (manager->obj_count >= manager->capacity) {
        printf("Object manager capacity exceeded!\n");
        return -1; // Error: capacity exceeded
    }
    manager->objects[manager->obj_count] = 0; // Initialize the object (could be more complex)
    return manager->obj_count++; // Return the current index and increment count
}

// Set a field in an object
void setField(ObjectManager* manager, int objIndex, int fieldIndex, int value) {
    if (objIndex < 0 || objIndex >= manager->obj_count) {
        printf("Invalid object index!\n");
        return;
    }
    // For simplicity, we assume a single field per object
    manager->objects[objIndex] = value; // Adjust as necessary for multiple fields
}

// Get a field from an object
int getField(ObjectManager* manager, int objIndex, int fieldIndex) {
    if (objIndex < 0 || objIndex >= manager->obj_count) {
        printf("Invalid object index!\n");
        return -1; // Error value
    }
    return manager->objects[objIndex]; // Adjust to access the correct field
}

int frame(VM* vm) {
    return vm->fstack.fp;
}

int next(VM* vm) {
    return vm->code[vm->pc++];
}

void initFrameStack(FrameStack* fstack) {
    fstack->fp = -1;  // Initialize frame pointer to -1 (empty)
}

// Push a new frame onto the frame stack
int pushFrame(VM* vm) {
    if (vm->fstack.fp >= STACK_SIZE - 1) {
        printf("Frame stack overflow!\n");
        exit(EXIT_FAILURE);
    }
    Frame* frame = (Frame*)malloc(sizeof(Frame));
    frame->sp = -1;  // Initialize stack pointer for the frame's stack
    frame->returnValue = 0;
    vm->fstack.frames[++(vm->fstack.fp)] = frame;
    printf("Pushed new frame. Total frames: %d\n", vm->fstack.fp + 1);
    return vm->fstack.fp;  // Return the current frame index
}

// Pop top frame from frame stack
int popFrame(VM* vm) {
    if (vm->fstack.fp < 0) {
        printf("Frame stack underflow!\n");
        exit(EXIT_FAILURE);
    }
    free(vm->fstack.frames[vm->fstack.fp--]);
    printf("Popped frame. Remaining frames: %d\n", vm->fstack.fp + 1);
    return vm->fstack.fp + 1;  // Popped frame index
}

// Access specific frame by index in frame stack (0 is bottom-most frame)
Frame* getFrame(VM* vm, int frameIndex) {
    if (frameIndex < 0 || frameIndex > vm->fstack.fp) {
        printf("Invalid frame index: %d\n", frameIndex);
        return NULL;
    }
    return vm->fstack.frames[frameIndex];
}

// Push value onto the current frame's stack
void push(VM* vm, int value) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp >= STACK_SIZE - 1) {
        printf("Stack overflow in frame!\n");
        exit(EXIT_FAILURE);
    }
    frame->stack[++(frame->sp)] = value;
}

// Pop value from current frame's stack
int pop(VM* vm) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp < 0) {
        printf("Stack underflow in frame!\n");
        exit(EXIT_FAILURE);
    }
    return frame->stack[(frame->sp)--];
}

// Store value in local variable array of current frame
void store(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        printf("Invalid local variable index: %d\n", index);
        exit(EXIT_FAILURE);
    }
    int value = pop(vm);
    vm->fstack.frames[vm->fstack.fp]->locals[index] = value;
}

// Load value from local variable array of current frame
void load(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        printf("Invalid local variable index: %d\n", index);
        exit(EXIT_FAILURE);
    }
    int value = vm->fstack.frames[vm->fstack.fp]->locals[index];
    push(vm, value);
}

// Transfer stack values to local variables of the current frame
int transferStackToLocals(VM* vm, int index) {
    // Move pc to get the number of arguments
    int num = next(vm);

    Frame* currentFrame = vm->fstack.frames[index];
    Frame* prevFrame = vm->fstack.frames[index - 1];

    // Pop values from previous frame's stack
    for (int i = 0; i < num; ++i) {
        if (prevFrame->sp < 0) {
            printf("Not enough values on the previous frame's stack!\n");
            exit(EXIT_FAILURE);
        }

        // Pop from previous frame and store in current frame's locals
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

// Transfer top value from source frame's stack to destination frame's return value
void transferStackToReturnValue(VM* vm, int srcFrameIdx, int destFrameIdx) {
    // Valid source and destination frame indices
    if (srcFrameIdx < 0 || srcFrameIdx > vm->fstack.fp || destFrameIdx < 0 || destFrameIdx > vm->fstack.fp) {
        printf("Invalid frame index!\n");
        return;
    }

    Frame* srcFrame = vm->fstack.frames[srcFrameIdx];
    Frame* destFrame = vm->fstack.frames[destFrameIdx];

    // If source frame's stack is not empty
    if (srcFrame->sp < 0) {
        printf("Source frame stack is empty!\n");
        return;
    }

    // Pop value from source frame's stack and set it as return value in destination frame
    destFrame->returnValue = srcFrame->stack[srcFrame->sp--];
    printf("Transferred value %d from frame %d to return value of frame %d.\n",
           destFrame->returnValue, srcFrameIdx, destFrameIdx);
}

// Create a new VM instance
VM* newVM(int* code, int code_length) {
    VM* vm = (VM*)malloc(sizeof(VM));
    vm->code = code;
    vm->pc = 0;
    vm->code_length = code_length;
    initFrameStack(&vm->fstack);
    initObjectManager(&vm->objects);
    return vm;
}

// Free the VM instance
void freeVM(VM* vm) {
    for (int i = 0; i <= vm->fstack.fp; i++) {
        free(vm->fstack.frames[i]); // Free each frame
    }
    free(vm->objects.objects); // Free objects array
    free(vm); // Finally, free the VM
}

// Run the VM, executing the instructions
void run(VM* vm) {
    while (vm->pc < vm->code_length) {
        int instruction = next(vm);
        int index;

        switch (instruction) {
            case HALT:
                printf("HALT instruction encountered. Stopping execution.\n");
                return;

            case ALLOC: // ALLOC (push a new frame)
                index = pushFrame(vm);
                printf("ALLOC frame no. %d\n", index);
                break;

            case DEALLOC: // DEALLOC (pop the top frame)
                index = popFrame(vm);
                printf("DEALLOC frame no. %d\n", index);
                break;

            case PUSH: // PUSH (push a literal value onto the stack)
                push(vm, next(vm));
                break;

            case POP: // POP (pop the value from the stack and discard)
                index = pop(vm);
                printf("POP value = %d\n", index);
                break;

            case ST: // Store to local
                store(vm, next(vm));
                break;

            case LD: // Load from local
                load(vm, next(vm));
                break;

            case ARG: // Transfer stack values to locals
                transferStackToLocals(vm, vm->fstack.fp);
                break;

            case RVAL: // Transfer value to return
                transferStackToReturnValue(vm, vm->fstack.fp - 1, vm->fstack.fp);
                break;

            case CRET: // Return from the current frame
                popFrame(vm);
                break;

            case PRINT: // Print the top value
                index = pop(vm);
                printf("PRINT value = %d\n", index);
                break;

            default:
                printf("Unknown instruction: %d\n", instruction);
                return;
        }
    }
}

// Main function for testing
int main() {
    // Example bytecode for testing
    int code[] = {
        ALLOC,          // 0
        PUSH, 10,      // 1
        ST, 0,         // 3 store 10 in local 0
        LD, 0,         // 4 load local 0
        PRINT,         // 5 should print 10
        DEALLOC,       // 6
        HALT           // 7
    };

    VM* vm = newVM(code, sizeof(code) / sizeof(int));
    run(vm);
    freeVM(vm);

    return 0;
}