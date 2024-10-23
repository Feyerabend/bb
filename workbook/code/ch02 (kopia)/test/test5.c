#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    TYPE_INT,
    TYPE_FLOAT,
} FieldType;

// define a field structure
typedef struct {
    FieldType type;  // type of the field
    union {
        int int_value;
        float float_value;
    } value;         // union for flexible data type
} Field;

// define the object structure
typedef struct {
    char *name;      // name
    Field *fields;   // array of fields
    int field_count; // count of fields
    char **methods;  // array of method mnemonics
    int method_count; // count of methods
} Object;

// define the instruction set
typedef enum {
    PRINT,           // print fields
    INC,             // increment integer field
    ADD,             // add to integer field
    SUB,             // subtract from integer field
    MUL,             // multiply integer field
    DIV,             // divide integer field
    HALT,            // stop the VM
} Instruction;

// define the instruction structure
typedef struct {
    Instruction instruction;
    int field_index; // index of the field in the object
    int operand;     // operand for arithmetic operations
} VMInstruction;

// define the virtual machine structure
typedef struct {
    VMInstruction *instructions; // list of instructions
    int instruction_count;       // total number of instructions
    int pc;                      // program counter
} VirtualMachine;

// fwd. decl.
void print_fields(Object *obj);
void increment_field(Object *obj, int field_index);
void add_to_field(Object *obj, int field_index, int value);
void subtract_from_field(Object *obj, int field_index, int value);
void multiply_field(Object *obj, int field_index, int value);
void divide_field(Object *obj, int field_index, int value);

// method impl.
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

void increment_field(Object *obj, int field_index) {
    if (obj->fields[field_index].type == TYPE_INT) {
        obj->fields[field_index].value.int_value++;
    } else {
        printf("Error: Cannot increment a non-integer field.\n");
    }
}

void add_to_field(Object *obj, int field_index, int value) {
    if (obj->fields[field_index].type == TYPE_INT) {
        obj->fields[field_index].value.int_value += value;
    } else {
        printf("Error: Cannot add to a non-integer field.\n");
    }
}

void subtract_from_field(Object *obj, int field_index, int value) {
    if (obj->fields[field_index].type == TYPE_INT) {
        obj->fields[field_index].value.int_value -= value;
    } else {
        printf("Error: Cannot subtract from a non-integer field.\n");
    }
}

void multiply_field(Object *obj, int field_index, int value) {
    if (obj->fields[field_index].type == TYPE_INT) {
        obj->fields[field_index].value.int_value *= value;
    } else {
        printf("Error: Cannot multiply a non-integer field.\n");
    }
}

void divide_field(Object *obj, int field_index, int value) {
    if (value != 0) {
        if (obj->fields[field_index].type == TYPE_INT) {
            obj->fields[field_index].value.int_value /= value;
        } else {
            printf("Error: Cannot divide a non-integer field.\n");
        }
    } else {
        printf("Error: Division by zero\n");
    }
}

Object *create_object(const char *name, Field *fields, int field_count) {
    Object *obj = malloc(sizeof(Object));
    obj->name = strdup(name);
    obj->fields = malloc(field_count * sizeof(Field));
    memcpy(obj->fields, fields, field_count * sizeof(Field));
    obj->field_count = field_count;
    obj->method_count = 0;
    obj->methods = NULL;
    return obj;
}

// VM functions
VirtualMachine *create_vm(VMInstruction *instructions, int count) {
    VirtualMachine *vm = malloc(sizeof(VirtualMachine));
    vm->instructions = instructions;
    vm->instruction_count = count;
    vm->pc = 0; // start at the first instruction
    return vm;
}

void run_vm(VirtualMachine *vm, Object *obj) {
    while (vm->pc < vm->instruction_count) {
        VMInstruction current_instruction = vm->instructions[vm->pc];

        switch (current_instruction.instruction) {
            case PRINT:
                print_fields(obj);
                break;
            case INC:
                increment_field(obj, current_instruction.field_index);
                break;
            case ADD:
                add_to_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case SUB:
                subtract_from_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case MUL:
                multiply_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case DIV:
                divide_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case HALT:
                return; // stop
            default:
                printf("Unknown instruction\n");
                return;
        }

        vm->pc++; // move to next instruction
    }
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



void compile_and_run() {
    // Define fields for ObjectA
    Field fieldsA[2];
    fieldsA[0].type = TYPE_INT;
    fieldsA[0].value.int_value = 10;

    fieldsA[1].type = TYPE_FLOAT;
    fieldsA[1].value.float_value = 3.14f;

    // Create ObjectA
    Object *objectA = create_object("ObjectA", fieldsA, 2);

    // Define fields for ObjectB
    Field fieldsB[2];
    fieldsB[0].type = TYPE_INT;
    fieldsB[0].value.int_value = 20;

    fieldsB[1].type = TYPE_FLOAT;
    fieldsB[1].value.float_value = 6.28f;

    // Create ObjectB
    Object *objectB = create_object("ObjectB", fieldsB, 2);

    // Build the program for ObjectA
    VMInstruction *programA = malloc(6 * sizeof(VMInstruction));
    programA[0] = (VMInstruction){PRINT, 0, 0}; // Print field1 of ObjectA
    programA[1] = (VMInstruction){ADD, 0, 5};   // Add 5 to field1 of ObjectA
    programA[2] = (VMInstruction){SUB, 0, 2};   // Subtract 2 from field1 of ObjectA
    programA[3] = (VMInstruction){MUL, 0, 3};   // Multiply field1 of ObjectA by 3
    programA[4] = (VMInstruction){DIV, 0, 2};   // Divide field1 of ObjectA by 2
    programA[5] = (VMInstruction){PRINT, 0, 0}; // Print field1 of ObjectA again

    // Create and run VM for ObjectA
    VirtualMachine *vmA = create_vm(programA, 6);
    run_vm(vmA, objectA);

    // Build the program for ObjectB
    VMInstruction *programB = malloc(4 * sizeof(VMInstruction));
    programB[0] = (VMInstruction){PRINT, 0, 0}; // Print field1 of ObjectB
    programB[1] = (VMInstruction){INC, 0, 0};   // Increment field1 of ObjectB
    programB[2] = (VMInstruction){ADD, 0, 10};  // Add 10 to field1 of ObjectB
    programB[3] = (VMInstruction){PRINT, 0, 0}; // Print field1 of ObjectB again

    // Create and run VM for ObjectB
    VirtualMachine *vmB = create_vm(programB, 4);
    run_vm(vmB, objectB);

    // Clean up (not shown for brevity)
}


int main() {
    compile_and_run();

    return 0;
}