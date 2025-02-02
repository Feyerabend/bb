#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "vm.h"

#define MAX_PROGRAM_SIZE 1000
#define MAX_LABELS 100
#define MAX_MEMORY 100

#define MAX_LINE_LENGTH 100
#define MAX_LABEL_LENGTH 50
#define MAX_VAR_LENGTH 50
#define MAX_CALL_STACK 100

#define MAX_ARGS 3  // maximum arguments for control flow instructions


// fwd decl.
void add_label(TACVirtualMachine *vm, const char *label, int index);
int find_label_index(TACVirtualMachine *vm, const char *label);
int find_memory_index(TACVirtualMachine *vm, const char *key);
void add_to_memory(TACVirtualMachine *vm, const char *key, int value);
void parse_load_instruction(TACVirtualMachine *vm, char *var, char *arg);
void parse_arithmetic_operation(TACVirtualMachine *vm, char *var, char *op, char *arg1, char *arg2);
void parse_instruction(TACVirtualMachine *vm, char *line);
int get_operand_value(TACVirtualMachine *vm, char *operand);
void parse_control_flow(TACVirtualMachine *vm, char *op, char **args, int arg_count);

void init_vm(TACVirtualMachine *vm) {
    vm->pc = 0;
    vm->call_stack_index = -1;  // -1 (empty stack)
    vm->program_size = 0;
    vm->label_count = 0;
    vm->memory_size = 0;

    vm->labels = malloc(MAX_LABELS * sizeof(Label));
    vm->memory = malloc(MAX_MEMORY * sizeof(MemoryEntry));
    vm->call_stack = malloc(MAX_CALL_STACK * sizeof(int));

    if (!vm->labels || !vm->memory || !vm->call_stack) {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(1);
    }
}


void add_label(TACVirtualMachine *vm, const char *label, int index) {
    if (vm->label_count >= MAX_LABELS) {
        printf("Error: Too many labels.\n");
        exit(1);
    }

    strncpy(vm->labels[vm->label_count].label, label, MAX_LABEL_LENGTH);
    vm->labels[vm->label_count].index = index;
    vm->label_count++;
    printf("Label added: %s at index %d\n", label, index);
}


int find_label_index(TACVirtualMachine *vm, const char *label) {
    for (int i = 0; i < vm->label_count; i++) {
        if (strcmp(vm->labels[i].label, label) == 0) {
            return vm->labels[i].index;
        }
    }
    printf("Error: Label %s not found.\n", label);
    exit(1);
}


int find_memory_index(TACVirtualMachine *vm, const char *key) {
    for (int i = 0; i < vm->memory_size; i++) {
        if (strcmp(vm->memory[i].key, key) == 0) {
            return i;
        }
    }
    return -1;
}


void add_to_memory(TACVirtualMachine *vm, const char *key, int value) {
    int index = find_memory_index(vm, key);
    if (index == -1) {
        if (vm->memory_size >= MAX_MEMORY) {
            printf("Error: Memory full.\n");
            exit(1);
        }
        strncpy(vm->memory[vm->memory_size].key, key, MAX_VAR_LENGTH);
        vm->memory[vm->memory_size].value = value;
        vm->memory_size++;
        printf("Added to memory: %s = %d\n", key, value);
    } else {
        vm->memory[index].value = value;
        printf("Updated memory: %s = %d\n", key, value);
    }
}


void load_program(TACVirtualMachine *vm, const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open file %s\n", filename);
        exit(1);
    }

    char line[MAX_LINE_LENGTH];
    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = 0;  // no newline
        if (strlen(line) > 0) {
            if (vm->program_size >= MAX_PROGRAM_SIZE) {
                printf("Error: Program too large.\n");
                exit(1);
            }
            strncpy(vm->program[vm->program_size], line, MAX_LINE_LENGTH);
            if (line[strlen(line) - 1] == ':') {  // Label
                char label[MAX_LABEL_LENGTH];
                strncpy(label, line, strlen(line) - 1);
                label[strlen(line) - 1] = '\0';
                add_label(vm, label, vm->program_size);
            }
            vm->program_size++;
        }
    }
    fclose(file);
    printf("Program loaded with %d instructions\n", vm->program_size);
}

void parse_load_instruction(TACVirtualMachine *vm, char *var, char *arg) {
    int value;
    if (isdigit(arg[0])) {
        value = atoi(arg);
    } else {
        int idx = find_memory_index(vm, arg); // check if arg is a variable
        if (idx == -1) {
            printf("Error: Variable %s not found in memory.\n", arg);
            exit(1);  // terminate if undefined
        }
        value = vm->memory[idx].value;
    }
    add_to_memory(vm, var, value);
    printf("Loaded value %d into %s\n", value, var);
}


void parse_arithmetic_operation(TACVirtualMachine *vm, char *var, char *op, char *arg1, char *arg2) {
    int val1 = get_operand_value(vm, arg1);
    int val2 = get_operand_value(vm, arg2);

    if (strcmp(op, "+") == 0) {
        add_to_memory(vm, var, val1 + val2);
    } else if (strcmp(op, "-") == 0) {
        add_to_memory(vm, var, val1 - val2);
    } else if (strcmp(op, "*") == 0) {
        add_to_memory(vm, var, val1 * val2);
    } else if (strcmp(op, "/") == 0) {
        add_to_memory(vm, var, val1 / val2);
    } else if (strcmp(op, ">") == 0) {
        add_to_memory(vm, var, val1 > val2 ? 1 : 0);
    } else if (strcmp(op, "<") == 0) {
        add_to_memory(vm, var, val1 < val2 ? 1 : 0);
    } else if (strcmp(op, "!=") == 0) {
        add_to_memory(vm, var, val1 != val2 ? 1 : 0);
    } else if (strcmp(op, "<=") == 0) {
        add_to_memory(vm, var, val1 <= val2 ? 1 : 0);
    } else if (strcmp(op, ">=") == 0) {
        add_to_memory(vm, var, val1 >= val2 ? 1 : 0);
    }
    printf("Performed %s operation on %s and %s, result stored in %s\n", op, arg1, arg2, var);
}

void parse_control_flow(TACVirtualMachine *vm, char *op, char **args, int arg_count) {
    if (strcmp(op, "IF_NOT") == 0) {
        // Format: IF_NOT <condition> GOTO <label>
        if (arg_count < 2 || strcmp(args[1], "GOTO") != 0) {
            printf("Invalid IF_NOT instruction: %s\n", op);
            exit(1);
        }
        char *condition = args[0];
        char *label = args[2];
        int value = get_operand_value(vm, condition);
        if (!value) {
            vm->pc = find_label_index(vm, label);
        }
    } 
    else if (strcmp(op, "GOTO") == 0) {
        // Format: GOTO <label>
        if (arg_count < 1) {
            printf("Invalid GOTO instruction\n");
            exit(1);
        }
        char *label = args[0];
        vm->pc = find_label_index(vm, label);
    } 
    else if (strcmp(op, "CALL") == 0) {

        // Format: CALL <label> <return_label>
        if (arg_count < 1) {
            printf("Invalid CALL instruction\n");
            exit(1);
        }
        char *label = args[0];  // Procedure label
       // char *return_label = args[1];  // Return label

        if (vm->call_stack_index >= MAX_CALL_STACK - 1) {
            printf("Error: Call stack overflow.\n");
            exit(1);
        }

        // Push the return address (current pc + 1) onto the call stack
        vm->call_stack[++vm->call_stack_index] = vm->pc + 1;

        // Jump to the target label
        vm->pc = find_label_index(vm, label);
        printf("CALL: Jumping to label %s, return address %d\n", label, vm->call_stack[vm->call_stack_index]);
    } 
    else if (strcmp(op, "RETURN") == 0) {
        if (vm->call_stack_index < 0) {
            printf("Error: RETURN without call stack.\n");
            exit(1);
        }
        // Pop the return address from the call stack and set pc to it
        vm->pc = vm->call_stack[vm->call_stack_index--];
        printf("RETURN: Returning to address %d\n", vm->pc);
    }
}

void parse_instruction(TACVirtualMachine *vm, char *line) {
    char line_copy[MAX_LINE_LENGTH];
    strncpy(line_copy, line, MAX_LINE_LENGTH);
    line_copy[MAX_LINE_LENGTH - 1] = '\0';

    char *saveptr;
    char *token = strtok_r(line_copy, " ", &saveptr);
    if (!token) return;

    // labels (e.g. 'main:'!)
    if (token[strlen(token) - 1] == ':') {
        return;
    }

    if (strcmp(token, "HALT") == 0) {
        vm->pc = vm->program_size;
        return;
    }

    if (strcmp(token, "IF_NOT") == 0 || strcmp(token, "GOTO") == 0 ||
        strcmp(token, "CALL") == 0 || strcmp(token, "RETURN") == 0) {
        
        char *args[MAX_ARGS];
        int arg_count = 0;
        while (arg_count < MAX_ARGS && (args[arg_count] = strtok_r(NULL, " ", &saveptr)) != NULL) {
            arg_count++;
        }
        
        parse_control_flow(vm, token, args, arg_count);
        return;
    }

    // variable assignments (e.g. sum.g = t4)
    char *equals = strtok_r(NULL, " ", &saveptr);
    if (!equals || strcmp(equals, "=") != 0) {
        printf("Invalid instruction: %s\n", line);
        exit(1);
    }

    char *op = strtok_r(NULL, " ", &saveptr);  // operator (LOAD, +, -, etc.)
    char *arg1 = strtok_r(NULL, " ", &saveptr);  // first operand (if any)
    char *arg2 = strtok_r(NULL, " ", &saveptr);  // second operand (if any)

    // 1: simple assignment (sum.g = t4)
    if (!op) {
        printf("Error: Missing operand in instruction: %s\n", line);
        exit(1);
    } else if (!arg1) {
        // assignment (no operator, e.g. sum.g = t4)
        int value = get_operand_value(vm, op);
        add_to_memory(vm, token, value);
        printf("Assigned %s = %d\n", token, value);
    }
    // 2: LOAD operation (t0 = LOAD 4)
    else if (strcmp(op, "LOAD") == 0) {
        parse_load_instruction(vm, token, arg1);
    }
    // 3: arithmetic operation (t2 = + t0 t1)
    else {
        parse_arithmetic_operation(vm, token, op, arg1, arg2);
    }
}

void execute_program(TACVirtualMachine *vm) {
    // start execution at first instruction if no main label is found?
    int main_index = find_label_index(vm, "main");
    if (main_index == -1) {
        printf("No 'main' label found. Starting execution from the first instruction.\n");
        vm->pc = 0;  // start at the beginning
    } else {
        vm->pc = main_index;  // start at the 'main' label
    }

    while (vm->pc < vm->program_size) {
        char *original_line = vm->program[vm->pc];
        printf("Executing instruction at pc %d: %s\n", vm->pc, original_line);
        parse_instruction(vm, original_line);
        if (vm->pc < vm->program_size) {
            vm->pc++;
        }
    }
}

/*void execute_program(TACVirtualMachine *vm) {
    // Ensure the program has a 'main' label
    int main_index = find_label_index(vm, "main");
    if (main_index == -1) {
        printf("Error: No 'main' label found. Program cannot start.\n");
        exit(1);
    }

    // Start execution at the 'main' label
    vm->pc = main_index;

    while (vm->pc < vm->program_size) {
        char *original_line = vm->program[vm->pc];
        printf("Executing instruction at pc %d: %s\n", vm->pc, original_line);
        parse_instruction(vm, original_line);
        if (vm->pc < vm->program_size) {
            vm->pc++;
        }
    }
}*/


// get the value of an operand (variable or constant)
int get_operand_value(TACVirtualMachine *vm, char *operand) {
    if (isdigit(operand[0])) {
        return atoi(operand);
    } else {
        int idx = find_memory_index(vm, operand);
        if (idx == -1) {
            printf("Error: Variable %s not found in memory.\n", operand);
            exit(1);
        }
        return vm->memory[idx].value;
    }
}
