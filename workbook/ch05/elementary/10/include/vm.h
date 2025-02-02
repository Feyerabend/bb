#ifndef VM_H
#define VM_H

#define MAX_PROGRAM_SIZE 1000
#define MAX_LABELS 100
#define MAX_MEMORY_SIZE 100


typedef struct {
    char label[50];
    int index;
} Label;

typedef struct {
    char key[50];
    int value;
} MemoryEntry;

typedef struct {
    MemoryEntry *memory;
    Label *labels;
    char program[MAX_PROGRAM_SIZE][100];
    int pc;
    int *call_stack;
    int call_stack_index;
    int program_size;
    int label_count;
    int memory_size;

} TACVirtualMachine;


extern void init_vm(TACVirtualMachine *vm);
extern void load_program(TACVirtualMachine *vm, const char *filename);
extern void execute_program(TACVirtualMachine *vm);


#endif  // VM_H
