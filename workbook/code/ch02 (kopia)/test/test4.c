#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Define a method type
typedef void (*Method)(void);

// Define the object structure
typedef struct {
    char *name;       // Name of the object
    int field1;      // Example field (could be anything)
    float field2;    // Another field (could be anything)
    Method *methods;  // Array of method pointers
    int method_count; // Count of methods
} Object;

// Define the instruction set with shorter mnemonics
typedef enum {
    PRINT,           // Print fields
    INC,             // Increment field1
    ADD,             // Add to field1
    SUB,             // Subtract from field1
    MUL,             // Multiply field1
    DIV,             // Divide field1
    HALT,            // Stop the VM
} Instruction;

// Define the instruction structure
typedef struct {
    Instruction instruction;
    Object *object; // Pointer to the object on which the instruction operates
    int operand;    // Additional operand for arithmetic operations
} VMInstruction;

// Define the virtual machine structure
typedef struct {
    VMInstruction *instructions; // List of instructions
    int instruction_count;       // Total number of instructions
    int pc;                      // Program counter
} VirtualMachine;

// Method implementations
void print_fields(Object *obj) {
    printf("Object Name: %s\n", obj->name);
    printf("Field1: %d, Field2: %.2f\n", obj->field1, obj->field2);
}

void increment_field1(Object *obj) {
    obj->field1++;
}

void add_to_field1(Object *obj, int value) {
    obj->field1 += value;
}

void subtract_from_field1(Object *obj, int value) {
    obj->field1 -= value;
}

void multiply_field1(Object *obj, int value) {
    obj->field1 *= value;
}

void divide_field1(Object *obj, int value) {
    if (value != 0) {
        obj->field1 /= value;
    } else {
        printf("Error: Division by zero\n");
    }
}

// Object creation
Object *create_object(const char *name, int field1, float field2) {
    Object *obj = malloc(sizeof(Object));
    obj->name = strdup(name);
    obj->field1 = field1;
    obj->field2 = field2;

    // Initialize methods
    obj->method_count = 2; // Change this if you add more methods
    obj->methods = malloc(obj->method_count * sizeof(Method));
    obj->methods[0] = (Method)print_fields;
    obj->methods[1] = (Method)increment_field1;

    return obj;
}

// Virtual Machine functions
VirtualMachine *create_vm(VMInstruction *instructions, int count) {
    VirtualMachine *vm = malloc(sizeof(VirtualMachine));
    vm->instructions = instructions;
    vm->instruction_count = count;
    vm->pc = 0; // Start at the first instruction
    return vm;
}

void run_vm(VirtualMachine *vm) {
    while (vm->pc < vm->instruction_count) {
        VMInstruction current_instruction = vm->instructions[vm->pc];

        switch (current_instruction.instruction) {
            case PRINT:
                print_fields(current_instruction.object);
                break;
            case INC:
                increment_field1(current_instruction.object);
                break;
            case ADD:
                add_to_field1(current_instruction.object, current_instruction.operand);
                break;
            case SUB:
                subtract_from_field1(current_instruction.object, current_instruction.operand);
                break;
            case MUL:
                multiply_field1(current_instruction.object, current_instruction.operand);
                break;
            case DIV:
                divide_field1(current_instruction.object, current_instruction.operand);
                break;
            case HALT:
                return; // Stop the VM
            default:
                printf("Unknown instruction\n");
                return;
        }

        vm->pc++; // Move to the next instruction
    }
}

// Program building
VMInstruction *build_program(Object *obj) {
    VMInstruction *program = malloc(6 * sizeof(VMInstruction));

    program[0].instruction = PRINT;               // Print fields
    program[0].object = obj;

    program[1].instruction = ADD;                 // Add 5 to field1
    program[1].object = obj;
    program[1].operand = 5;

    program[2].instruction = SUB;                 // Subtract 2 from field1
    program[2].object = obj;
    program[2].operand = 2;

    program[3].instruction = MUL;                 // Multiply field1 by 3
    program[3].object = obj;
    program[3].operand = 3;

    program[4].instruction = DIV;                 // Divide field1 by 2
    program[4].object = obj;
    program[4].operand = 2;

    program[5].instruction = PRINT;               // Print fields again
    program[5].object = obj;

    return program;
}

// Main function
int main() {
    // Create an object
    Object *my_object = create_object("MyObject", 10, 3.14);
    
    // Build the program
    VMInstruction *program = build_program(my_object);
    
    // Create and run the VM
    VirtualMachine *vm = create_vm(program, 6);
    run_vm(vm);

    // Clean up
    free(program);
    free(vm);
    free(my_object->methods);
    free(my_object->name);
    free(my_object);

    return 0;
}