#include <stdio.h>
#include <stdlib.h>

#define MAX_FRAMES 256
#define MAX_OBJECTS 256
#define MAX_STACK_SIZE 256
#define MAX_FIELDS 10 // Maximum fields per object
#define MAX_METHODS 10 // Maximum methods per object

// Enumeration for VM instructions
typedef enum {
    HALT,
    ALLOC,
    DEALLOC,
    PUSH,
    POP,
    ST,
    LD,
    ARG,
    RVAL,
    CRET,
    PRINT,
    CREATE_OBJ, // New instruction for creating an object
    GET_FIELD,   // New instruction for getting a field from an object
    SET_FIELD,   // New instruction for setting a field in an object
    CREATE_METHOD, // New instruction for creating a method
    CALL_METHOD    // New instruction for calling a method
} Instruction;

// Struct to represent a frame in the VM
typedef struct {
    int stack[MAX_STACK_SIZE];
    int sp; // Stack pointer
    int returnValue; // Value to return
} Frame;

// Struct to represent a method
typedef struct {
    int(*func)(int, int); // Pointer to the method function
    int arg_count; // Number of arguments the method takes
} Method;

// Struct to represent an object
typedef struct {
    int fields[MAX_FIELDS]; // Arbitrary number of fields
    Method methods[MAX_METHODS]; // Array of methods
    int method_count; // Number of methods
} Object;

// Struct to manage objects
typedef struct {
    Object objects[MAX_OBJECTS]; // Array of objects
    int obj_count; // Number of objects
} ObjectManager;

// Struct to represent the virtual machine
typedef struct {
    int* code; // Bytecode
    int pc; // Program counter
    int code_length; // Length of the bytecode
    Frame frames[MAX_FRAMES]; // Stack of frames
    int fp; // Frame pointer
    ObjectManager objects; // Object manager
} VM;

// Initialize the VM
void initVM(VM* vm, int* code, int code_length) {
    vm->code = code;
    vm->pc = 0;
    vm->code_length = code_length;
    vm->fp = -1; // No frames
    vm->objects.obj_count = 0; // Initialize object count
}

// Create a new object
int createObject(VM* vm) {
    if (vm->objects.obj_count >= MAX_OBJECTS) {
        printf("Object limit reached!\n");
        return -1;
    }
    Object newObj = { {0}, {NULL}, 0 }; // Initialize fields and methods
    vm->objects.objects[vm->objects.obj_count] = newObj;
    return vm->objects.obj_count++; // Return the index of the new object
}

// Get field from an object
int getField(VM* vm, int objIndex, int fieldIndex) {
    if (objIndex < 0 || objIndex >= vm->objects.obj_count) {
        printf("Object index out of bounds!\n");
        return -1;
    }
    if (fieldIndex < 0 || fieldIndex >= MAX_FIELDS) {
        printf("Field index out of bounds!\n");
        return -1;
    }
    return vm->objects.objects[objIndex].fields[fieldIndex];
}

// Set field in an object
void setField(VM* vm, int objIndex, int fieldIndex, int value) {
    if (objIndex < 0 || objIndex >= vm->objects.obj_count) {
        printf("Object index out of bounds!\n");
        return;
    }
    if (fieldIndex < 0 || fieldIndex >= MAX_FIELDS) {
        printf("Field index out of bounds!\n");
        return;
    }
    vm->objects.objects[objIndex].fields[fieldIndex] = value;
}

// Create a new method in an object
int createMethod(VM* vm, int objIndex, int(*methodFunc)(int, int), int arg_count) {
    if (objIndex < 0 || objIndex >= vm->objects.obj_count) {
        printf("Object index out of bounds!\n");
        return -1;
    }
    Object* obj = &vm->objects.objects[objIndex];
    if (obj->method_count >= MAX_METHODS) {
        printf("Method limit reached for object %d!\n", objIndex);
        return -1;
    }
    obj->methods[obj->method_count].func = methodFunc;
    obj->methods[obj->method_count].arg_count = arg_count;
    return obj->method_count++; // Return the index of the new method
}

// Call a method of an object
int callMethod(VM* vm, int objIndex, int methodIndex, int* args) {
    if (objIndex < 0 || objIndex >= vm->objects.obj_count) {
        printf("Object index out of bounds!\n");
        return -1;
    }
    Object* obj = &vm->objects.objects[objIndex];
    if (methodIndex < 0 || methodIndex >= obj->method_count) {
        printf("Method index out of bounds for object %d!\n", objIndex);
        return -1;
    }
    // Call the method and return the result
    return obj->methods[methodIndex].func(args[0], args[1]);
}

// Push a new frame
void pushFrame(VM* vm) {
    if (vm->fp + 1 >= MAX_FRAMES) {
        printf("Frame limit reached!\n");
        return;
    }
    vm->fp++;
    vm->frames[vm->fp].sp = -1; // Reset stack pointer
}

// Pop the top frame
void popFrame(VM* vm) {
    if (vm->fp < 0) {
        printf("No frames to pop!\n");
        return;
    }
    vm->fp--;
}

// Push value onto the stack
void push(VM* vm, int value) {
    if (vm->fp < 0) {
        printf("No frame to push to!\n");
        return;
    }
    Frame* frame = &vm->frames[vm->fp];
    if (frame->sp + 1 >= MAX_STACK_SIZE) {
        printf("Stack overflow!\n");
        return;
    }
    frame->stack[++frame->sp] = value;
}

// Pop value from the stack
int pop(VM* vm) {
    if (vm->fp < 0) {
        printf("No frame to pop from!\n");
        return -1;
    }
    Frame* frame = &vm->frames[vm->fp];
    if (frame->sp < 0) {
        printf("Stack underflow!\n");
        return -1;
    }
    return frame->stack[frame->sp--];
}

// The VM run function to execute instructions
void run(VM* vm) {
    while (vm->pc < vm->code_length) {
        int instruction = vm->code[vm->pc++]; // Fetch the instruction
        int index;

        switch (instruction) {
            case HALT:
                printf("HALT instruction encountered. Stopping execution.\n");
                return;

            case ALLOC: // Allocate a new frame
                pushFrame(vm);
                printf("ALLOC frame no. %d\n", vm->fp);
                break;

            case DEALLOC: // Deallocate the top frame
                popFrame(vm);
                printf("DEALLOC frame no. %d\n", vm->fp + 1);
                break;

            case PUSH: // Push a literal value onto the stack
                push(vm, vm->code[vm->pc++]);
                break;

            case POP: // Pop the value from the stack
                index = pop(vm);
                printf("POP value = %d\n", index);
                break;

            case CREATE_OBJ: // Create a new object
                index = createObject(vm);
                printf("Created object with index %d\n", index);
                break;

            case GET_FIELD: // Get field from an object
                {
                    int fieldIndex = pop(vm);
                    int objIndex = pop(vm);
                    int value = getField(vm, objIndex, fieldIndex);
                    push(vm, value);
                    printf("GET_FIELD: Object %d, Field %d, Value = %d\n", objIndex, fieldIndex, value);
                }
                break;

            case SET_FIELD: // Set field in an object
                {
                    int value = pop(vm);
                    int fieldIndex = pop(vm);
                    int objIndex = pop(vm);
                    setField(vm, objIndex, fieldIndex, value);
                    printf("SET_FIELD: Object %d, Field %d, Value = %d\n", objIndex, fieldIndex, value);
                }
                break;

            case CREATE_METHOD: // Create a new method
                {
                    int objIndex = pop(vm);
                    int arg_count = pop(vm); // Assume the argument count is on the stack
                    int(*methodFunc)(int, int) = [](int a, int b) {
                        return a + b; // Example method that adds two integers
                    };
                    int methodIndex = createMethod(vm, objIndex, methodFunc, arg_count);
                    printf("Created method %d for object %d\n", methodIndex, objIndex);
                }
                break;

            case CALL_METHOD: // Call a method of an object
                {
                    int methodIndex = pop(vm); // Method index
                    int objIndex = pop(vm); // Object index
                    int args[MAX_FIELDS] = {0}; // Array for method arguments
                    for (int i = 0; i < vm->objects.objects[objIndex].methods[methodIndex].arg_count; i++) {
                        args[i] = pop(vm); // Pop arguments from the stack
                    }
                    int result = callMethod(vm, objIndex, methodIndex, args);
                    push(vm, result); // Push the result back to the stack
                    printf("CALL_METHOD: Object %d, Method %d, Result = %d\n", objIndex, methodIndex, result);
                }
                break;

            case PRINT: // Print the top value from the stack
                {
                    int value = pop(vm);
                    printf("PRINT value = %d\n", value);
                }
                break;

            default:
                printf("Unknown instruction %d\n", instruction);
                return;
        }
    }
}

// Example of a simple main function to run the VM
int main() {
    VM vm;

    // Example bytecode to create an object, set fields, create a method, and call it
    int bytecode[] = {
        ALLOC,
        CREATE_OBJ,       // Create an object
        PUSH, 0,          // Object index (0)
        SET_FIELD,        // Set field (field index 0)
        PUSH, 42,         // Value to set
        PUSH, 0,          // Object index
        CREATE_METHOD,    // Create a method
        PUSH, 2,          // Number of arguments for the method (2)
        CALL_METHOD,      // Call the method
        PRINT,            // Print the result
        DEALLOC,
        HALT
    };

    initVM(&vm, bytecode, sizeof(bytecode) / sizeof(bytecode[0]));
    run(&vm);

    return 0;
}