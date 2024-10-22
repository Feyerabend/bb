#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    TYPE_INT,
    TYPE_FLOAT,
} FieldType;

// Define a field structure
typedef struct {
    FieldType type;  // Type of the field
    union {
        int int_value;
        float float_value;
    } value;         // Union for flexible data type
} Field;

// Define the object structure
typedef struct {
    char *name;      // Name
    Field *fields;   // Array of fields
    int field_count; // Count of fields
} Object;

// Define the instruction set
typedef enum {
    PRINT,           // Print fields
    INC,             // Increment integer field
    ADD,             // Add to integer field
    SUB,             // Subtract from integer field
    MUL,             // Multiply integer field
    DIV,             // Divide integer field
    HALT,            // Stop the VM
} Instruction;

// Define the instruction structure
typedef struct {
    Instruction instruction;
    int field_index; // Index of the field in the object
    int operand;     // Operand for arithmetic operations
} VMInstruction;

// Define the virtual machine structure
typedef struct {
    VMInstruction *instructions; // List of instructions
    int instruction_count;       // Total number of instructions
    int pc;                      // Program counter
} VirtualMachine;

// Function prototypes
void print_fields(Object *obj);
void modify_field(Object *obj, int field_index, int value, char operation);
Object *create_object(const char *name, Field *fields, int field_count);
VirtualMachine *create_vm(VMInstruction *instructions, int count);
void run_vm(VirtualMachine *vm, Object *obj);
void free_object(Object *obj);

// Print fields of an object
void print_fields(Object *obj) {
    printf("Object Name: %s\n", obj->name);
    for (int i = 0; i < obj->field_count; i++) {
        if (obj->fields[i].type == TYPE_INT) {
            printf("Field %d (int): %d\n", i, obj->fields[i].value.int_value);
        } else if (obj->fields[i].type == TYPE_FLOAT) {
            printf("Field %d (float): %.2f\n", i, obj->fields[i].value.float_value);
        }
    }
}

// Modify field value based on the operation
void modify_field(Object *obj, int field_index, int value, char operation) {
    if (obj->fields[field_index].type != TYPE_INT) {
        printf("Error: Cannot modify a non-integer field.\n");
        return;
    }
    switch (operation) {
        case 'I': obj->fields[field_index].value.int_value++; break; // Increment
        case 'A': obj->fields[field_index].value.int_value += value; break; // Add
        case 'S': obj->fields[field_index].value.int_value -= value; break; // Subtract
        case 'M': obj->fields[field_index].value.int_value *= value; break; // Multiply
        case 'D': 
            if (value != 0) {
                obj->fields[field_index].value.int_value /= value; // Divide
            } else {
                printf("Error: Division by zero\n");
            }
            break;
    }
}

// new object
Object *create_object(const char *name, Field *fields, int field_count) {
    Object *obj = malloc(sizeof(Object));
    obj->name = strdup(name);
    obj->fields = malloc(field_count * sizeof(Field));
    memcpy(obj->fields, fields, field_count * sizeof(Field));
    obj->field_count = field_count;
    return obj;
}

// new virtual machine
VirtualMachine *create_vm(VMInstruction *instructions, int count) {
    VirtualMachine *vm = malloc(sizeof(VirtualMachine));
    vm->instructions = instructions;
    vm->instruction_count = count;
    vm->pc = 0; // start, first instruction
    return vm;
}

// run virtual machine
void run_vm(VirtualMachine *vm, Object *obj) {
    while (vm->pc < vm->instruction_count) {
        VMInstruction current_instruction = vm->instructions[vm->pc];

        switch (current_instruction.instruction) {
            case PRINT:
                print_fields(obj);
                break;
            case INC:
                modify_field(obj, current_instruction.field_index, 0, 'I');
                break;
            case ADD:
                modify_field(obj, current_instruction.field_index, current_instruction.operand, 'A');
                break;
            case SUB:
                modify_field(obj, current_instruction.field_index, current_instruction.operand, 'S');
                break;
            case MUL:
                modify_field(obj, current_instruction.field_index, current_instruction.operand, 'M');
                break;
            case DIV:
                modify_field(obj, current_instruction.field_index, current_instruction.operand, 'D');
                break;
            case HALT:
                return; // Stop
            default:
                printf("Unknown instruction\n");
                return;
        }

        vm->pc++; // Move to the next instruction
    }
}

// Free the object and its fields
void free_object(Object *obj) {
    free(obj->fields); // Free the fields
    free(obj->name);   // Free the name
    free(obj);         // Free the object itself
}

// Build the program for ObjectA
VMInstruction *build_program_A() {
    VMInstruction *program = malloc(6 * sizeof(VMInstruction));
    program[0] = (VMInstruction){PRINT, 0, 0};  // Print field1 of ObjectA
    program[1] = (VMInstruction){ADD,   0, 5};  // Add 5 to field1 of ObjectA
    program[2] = (VMInstruction){SUB,   0, 2};  // Subtract 2 from field1 of ObjectA
    program[3] = (VMInstruction){MUL,   0, 3};  // Multiply field1 of ObjectA by 3
    program[4] = (VMInstruction){DIV,   0, 2};  // Divide field1 of ObjectA by 2
    program[5] = (VMInstruction){PRINT, 0, 0};  // Print field1 of ObjectA again
    return program;
}

// Build the program for ObjectB
VMInstruction *build_program_B() {
    VMInstruction *program = malloc(4 * sizeof(VMInstruction));
    program[0] = (VMInstruction){PRINT, 0, 0};  // Print field1 of ObjectB
    program[1] = (VMInstruction){INC,   0, 0};  // Increment field1 of ObjectB
    program[2] = (VMInstruction){ADD,   0, 10}; // Add 10 to field1 of ObjectB
    program[3] = (VMInstruction){PRINT, 0, 0};  // Print field1 of ObjectB again
    return program;
}

// Main function with cleanup
int main() {

    // Define fields for ObjectA
    Field fieldsA[2] = {
        {TYPE_INT, .value.int_value = 10},
        {TYPE_FLOAT, .value.float_value = 3.14f}
    };

    // Create ObjectA
    Object *objectA = create_object("ObjectA", fieldsA, 2);
    VMInstruction *programA = build_program_A(); // Build the program for ObjectA
    VirtualMachine *vmA = create_vm(programA, 6); // Create VM for ObjectA
    run_vm(vmA, objectA); // Run the VM
    free(programA);
    free(vmA);
    free_object(objectA); // Clean up for ObjectA

    // Define fields for ObjectB
    Field fieldsB[2] = {
        {TYPE_INT, .value.int_value = 20},
        {TYPE_FLOAT, .value.float_value = 6.28f}
    };

    // Create ObjectB
    Object *objectB = create_object("ObjectB", fieldsB, 2);
    VMInstruction *programB = build_program_B(); // Build the program for ObjectB
    VirtualMachine *vmB = create_vm(programB, 4); // Create VM for ObjectB
    run_vm(vmB, objectB); // Run the VM
    free(programB);
    free(vmB);
    free_object(objectB); // Clean up for ObjectB

    return 0;
}


/*
// Define ObjectA
Object ObjectA {
    int field1 = 10;
    float field2 = 3.14;
}

// Define ObjectB
Object ObjectB {
    int field1 = 20;
    float field2 = 6.28;
}

// Define Program for ObjectA
Program ProgramA {
    PRINT ObjectA.field1;            // Print field1 of ObjectA
    ADD ObjectA.field1, 5;           // Add 5 to field1 of ObjectA
    SUB ObjectA.field1, 2;           // Subtract 2 from field1 of ObjectA
    MUL ObjectA.field1, 3;           // Multiply field1 of ObjectA by 3
    DIV ObjectA.field1, 2;           // Divide field1 of ObjectA by 2
    PRINT ObjectA.field1;            // Print field1 of ObjectA again
}

// Define Program for ObjectB
Program ProgramB {
    PRINT ObjectB.field1;            // Print field1 of ObjectB
    INC ObjectB.field1;              // Increment field1 of ObjectB
    ADD ObjectB.field1, 10;          // Add 10 to field1 of ObjectB
    PRINT ObjectB.field1;            // Print field1 of ObjectB again
}
*/
