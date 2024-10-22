#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    TYPE_FLOAT,
} FieldType;

// Define a field structure
typedef struct {
    FieldType type;  
    union {
        float float_value;
    } value;         
} Field;

// Define the object structure
typedef struct {
    char *name;      
    Field *fields;   
    int field_count; 
} Object;

// Define the instruction set
typedef enum {
    PRINT,           
    ADD,             
    SUB,             
    MUL,             
    DIV,             
    HALT,           
} Instruction;

// Define the instruction structure
typedef struct {
    Instruction instruction;
    int field_index; // Index of the field to work on
    float operand;   // Operand for arithmetic instructions
} VMInstruction;

// Define the virtual machine structure
typedef struct {
    VMInstruction *instructions; 
    int instruction_count;       
    int pc;                     
} VirtualMachine;

// Function prototypes
void print_fields(Object *obj);
void add_field(Object *obj, int field_index, float value);
void run_vm(VirtualMachine *vm, Object *obj);
Object *create_object(const char *name, Field *fields, int field_count);
VMInstruction *build_c_to_f_program();
VMInstruction *build_f_to_c_program();
void free_object(Object *obj);

// Function to print fields of the object
void print_fields(Object *obj) {
    printf("Object Name: %s\n", obj->name);
    for (int i = 0; i < obj->field_count; i++) {
        if (obj->fields[i].type == TYPE_FLOAT) {
            printf("Field %d (float): %.2f\n", i, obj->fields[i].value.float_value);
        }
    }
}

// Arithmetic operations
void add_field(Object *obj, int field_index, float value) {
    if (obj->fields[field_index].type == TYPE_FLOAT) {
        obj->fields[field_index].value.float_value += value;
    }
}

void sub_field(Object *obj, int field_index, float value) {
    if (obj->fields[field_index].type == TYPE_FLOAT) {
        obj->fields[field_index].value.float_value -= value;
    }
}

void mul_field(Object *obj, int field_index, float value) {
    if (obj->fields[field_index].type == TYPE_FLOAT) {
        obj->fields[field_index].value.float_value *= value;
    }
}

void div_field(Object *obj, int field_index, float value) {
    if (obj->fields[field_index].type == TYPE_FLOAT) {
        obj->fields[field_index].value.float_value /= value;
    }
}

// Run the virtual machine
void run_vm(VirtualMachine *vm, Object *obj) {
    while (vm->pc < vm->instruction_count) {
        VMInstruction current_instruction = vm->instructions[vm->pc];

        switch (current_instruction.instruction) {
            case PRINT:
                print_fields(obj);
                break;
            case ADD:
                add_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case SUB:
                sub_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case MUL:
                mul_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case DIV:
                div_field(obj, current_instruction.field_index, current_instruction.operand);
                break;
            case HALT:
                return; 
            default:
                printf("Unknown instruction\n");
                return;
        }

        vm->pc++; 
    }
}

// Function to create an object
Object *create_object(const char *name, Field *fields, int field_count) {
    Object *obj = malloc(sizeof(Object));
    obj->name = strdup(name);
    obj->fields = malloc(field_count * sizeof(Field));
    memcpy(obj->fields, fields, field_count * sizeof(Field));
    obj->field_count = field_count;
    return obj;
}

// Build the program for Celsius to Fahrenheit conversion
VMInstruction *build_c_to_f_program() {
    VMInstruction *program = malloc(5 * sizeof(VMInstruction));
    program[0] = (VMInstruction){PRINT, 0, 0};   // Print Celsius temperature
    program[1] = (VMInstruction){MUL, 0, 9.0f / 5.0f}; // Multiply by 9/5
    program[2] = (VMInstruction){ADD, 0, 32.0f}; // Add 32
    program[3] = (VMInstruction){PRINT, 0, 0};   // Print Fahrenheit temperature
    program[4] = (VMInstruction){HALT, 0, 0};    // Halt
    return program;
}

// Build the program for Fahrenheit to Celsius conversion
VMInstruction *build_f_to_c_program() {
    VMInstruction *program = malloc(5 * sizeof(VMInstruction));
    program[0] = (VMInstruction){PRINT, 0, 0};   // Print Fahrenheit temperature
    program[1] = (VMInstruction){SUB, 0, 32.0f}; // Subtract 32
    program[2] = (VMInstruction){MUL, 0, 5.0f / 9.0f}; // Multiply by 5/9
    program[3] = (VMInstruction){PRINT, 0, 0};   // Print Celsius temperature
    program[4] = (VMInstruction){HALT, 0, 0};    // Halt
    return program;
}

// Clean up function for objects
void free_object(Object *obj) {
    free(obj->fields);
    free(obj->name);
    free(obj);
}

// Main function with cleanup
int main() {
    // Define field for Celsius
    Field celsiusField[1] = {
        {TYPE_FLOAT, .value.float_value = 25.0f}  // Example Celsius temperature
    };

    // Create Object for Celsius
    Object *celsiusObj = create_object("Celsius", celsiusField, 1);
    
    // Build and run the program for Celsius to Fahrenheit conversion
    printf("Converting Celsius to Fahrenheit:\n");
    VMInstruction *programCtoF = build_c_to_f_program(); // Build the program for Celsius to Fahrenheit
    VirtualMachine *vmCtoF = malloc(sizeof(VirtualMachine));
    vmCtoF->instructions = programCtoF;
    vmCtoF->instruction_count = 5;
    vmCtoF->pc = 0; // Program counter initialization
    run_vm(vmCtoF, celsiusObj); // Run the VM for Celsius to Fahrenheit conversion
    
    // Clean up
    free(programCtoF);
    free(vmCtoF);
    free_object(celsiusObj); // Clean up for Celsius

    // Define field for Fahrenheit
    Field fahrenheitField[1] = {
        {TYPE_FLOAT, .value.float_value = 77.0f}  // Example Fahrenheit temperature
    };

    // Create Object for Fahrenheit
    Object *fahrenheitObj = create_object("Fahrenheit", fahrenheitField, 1);
    
    // Build and run the program for Fahrenheit to Celsius conversion
    printf("Converting Fahrenheit to Celsius:\n");
    VMInstruction *programFtoC = build_f_to_c_program(); // Build the program for Fahrenheit to Celsius
    VirtualMachine *vmFtoC = malloc(sizeof(VirtualMachine));
    vmFtoC->instructions = programFtoC;
    vmFtoC->instruction_count = 5;
    vmFtoC->pc = 0; // Program counter initialization
    run_vm(vmFtoC, fahrenheitObj); // Run the VM for Fahrenheit to Celsius conversion
    
    // Clean up
    free(programFtoC);
    free(vmFtoC);
    free_object(fahrenheitObj); // Clean up for Fahrenheit

    return 0;
}


/*
// Define Celsius Object
Object Celsius {
    float temperature = 25.0; // Example temperature in Celsius
}

// Define Fahrenheit Object
Object Fahrenheit {
    float temperature = 0.0;   // Placeholder for converted temperature
}

// Define Program for Celsius to Fahrenheit conversion
Program ProgramCtoF {
    PRINT Celsius.temperature;                     // Print original Celsius temperature
    MUL Celsius.temperature, 9.0 / 5.0;            // Multiply Celsius temperature by 9/5
    ADD Celsius.temperature, 32.0;                 // Add 32 to get Fahrenheit
    Fahrenheit.temperature = Celsius.temperature;   // Store converted temperature in Fahrenheit object
    PRINT Fahrenheit.temperature;                   // Print converted Fahrenheit temperature
}

// Define Program for Fahrenheit to Celsius conversion
Program ProgramFtoC {
    PRINT Fahrenheit.temperature;                    // Print original Fahrenheit temperature
    SUB Fahrenheit.temperature, 32.0;               // Subtract 32 from Fahrenheit temperature
    MUL Fahrenheit.temperature, 5.0 / 9.0;          // Multiply by 5/9 to convert to Celsius
    Celsius.temperature = Fahrenheit.temperature;    // Store converted temperature in Celsius object
    PRINT Celsius.temperature;                       // Print converted Celsius temperature
}
*/