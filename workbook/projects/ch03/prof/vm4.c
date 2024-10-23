#include <stdio.h>
#include <stdlib.h>
#include "profiler.h"

#define STACK_SIZE 100
#define LOCALS_SIZE 10
#define TRUE 1
#define FALSE 0

Profiler profiler;

typedef enum {
  ADD,
  ALLOC,
  CALL,
  CALLV,
  CRET,
  DEALLOC,
  HALT,
  LD,
  MUL,
  POP,
  PRINT,
  PUSH,
  RET,
  RETV,
  ST
} Opcode;

typedef struct {
    int stack[STACK_SIZE];
    int locals[LOCALS_SIZE];
    int sp;
    int returnValue;
    int returnAddress;
} Frame;

typedef struct FrameStack {
    Frame* frames[STACK_SIZE];
    int fp;
} FrameStack;

typedef struct VM {
    int* code;
    int pc;
    int code_length;
    FrameStack fstack;
    int debug;
} VM;

void freeVM(VM* vm);

char message[100];
void error(VM* vm, const char* message) {
    printf("Error: %s\n", message);
    freeVM(vm);
    exit(EXIT_FAILURE);
}

int frame(VM* vm) {
    return vm->fstack.fp;
}

int next(VM* vm) {
    if (vm->pc >= vm->code_length) {
        error(vm, "Program counter out of bounds");
    }
    return vm->code[vm->pc++];
}

void initFrameStack(FrameStack* fstack) {
    fstack->fp = -1;
}

int pushFrame(VM* vm) {
    if (vm->fstack.fp >= STACK_SIZE - 1) {
        error(vm, "Frame stack overflow");
    }
    Frame* frame = (Frame*) malloc(sizeof(Frame));
    frame->sp = -1;
    frame->returnValue = 0;
    frame->returnAddress = 0;
    vm->fstack.frames[++(vm->fstack.fp)] = frame;
    return vm->fstack.fp;
}

int popFrame(VM* vm) {
    if (vm->fstack.fp < 0) {
        error(vm, "Frame stack underflow");
    }
    Frame* currentFrame = vm->fstack.frames[vm->fstack.fp];
    vm->pc = currentFrame->returnAddress;
    free(currentFrame);
    vm->fstack.fp--;
    return vm->fstack.fp + 1;
}

Frame* getFrame(VM* vm, int frameIndex) {
    if (frameIndex < 0 || frameIndex > vm->fstack.fp) {
        snprintf(message, sizeof(message), "Invalid frame index: %d", frameIndex);
        error(vm, message);
        return NULL;
    }
    return vm->fstack.frames[frameIndex];
}

void push(VM* vm, int value) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp >= STACK_SIZE - 1) {
        error(vm, "Stack overflow in frame");
    }
    frame->stack[++(frame->sp)] = value;
}

int pop(VM* vm) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp < 0) {
        error(vm, "Stack underflow in frame");
    }
    return frame->stack[(frame->sp)--];
}

int peek(VM* vm) {
    Frame* frame = vm->fstack.frames[vm->fstack.fp];
    if (frame->sp < 0) {
        error(vm, "Stack underflow in frame");
    }
    return frame->stack[frame->sp];
}

void store(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        snprintf(message, sizeof(message), "Invalid local variable index: %d", index);
        error(vm, message);
    }
    int value = pop(vm);
    vm->fstack.frames[vm->fstack.fp]->locals[index] = value;
}

void load(VM* vm, int index) {
    if (index < 0 || index >= LOCALS_SIZE) {
        snprintf(message, sizeof(message), "Invalid local variable index: %d", index);
        error(vm, message);
    }
    int value = vm->fstack.frames[vm->fstack.fp]->locals[index];
    push(vm, value);
}

int transferStackToLocals(VM* vm, int index, int num) {
    Frame* currentFrame = vm->fstack.frames[index];
    Frame* prevFrame = vm->fstack.frames[index - 1];

    for (int i = 0; i < num; ++i) {
        if (prevFrame->sp < 0) {
            error(vm, "Not enough values on the previous frame's stack");
        }
        int value = prevFrame->stack[prevFrame->sp--];
        if (i < LOCALS_SIZE) {
            currentFrame->locals[i] = value;
        } else {
            error(vm, "Too many arguments for local storage");
        }
    }
    return num;
}

void transferStackToReturnValue(VM* vm, int srcFrameIdx, int destFrameIdx) {
    if (srcFrameIdx < 0 || srcFrameIdx > vm->fstack.fp ||
        destFrameIdx < 0 || destFrameIdx > vm->fstack.fp) {
        printf("Invalid frame index!\n");
        return;
    }
    Frame* srcFrame = vm->fstack.frames[srcFrameIdx];
    Frame* destFrame = vm->fstack.frames[destFrameIdx];
    if (srcFrame->sp < 0) {
        printf("Source frame's stack is empty!\n");
        return;
    }
    int value = srcFrame->stack[srcFrame->sp--];
    destFrame->returnValue = value;
}

VM* newVM(int* code, int code_length) {
    VM* vm = (VM*)malloc(sizeof(VM));
    if (vm == NULL) {
        return NULL;
    }
    vm->code = code;
    vm->pc = 0;
    vm->code_length = code_length;
    initFrameStack(&(vm->fstack));
    return vm;
}

void freeVM(VM* vm) {
    while (vm->fstack.fp >= 0) {
        popFrame(vm);
    }
    free(vm);
}

void run(VM* vm) {
    int opcode, index, i, j, k;
    int addr, value, frm, num;
    Frame* fr;

    profiler_start(&profiler);

    while (TRUE) {
        if (vm->pc >= vm->code_length) {
            printf("Warning: Program counter out of bounds!\n");
            return;
        }
        if (vm->debug) {
            printf("PC: %d, Opcode: %d\n", vm->pc, vm->code[vm->pc]);
        }

        clock_t start_time = clock();  // start time
        opcode = next(vm);
        switch (opcode) {

            case ALLOC:
                pushFrame(vm);
                profiler_record_push_frame(&profiler);
                break;

            case DEALLOC:
                popFrame(vm);
                profiler_record_pop_frame(&profiler);
                break;

            case CALLV:
                num = next(vm);
                addr = next(vm);
                frm = pushFrame(vm);
                fr = getFrame(vm, frm);
                fr->returnAddress = vm->pc;
                transferStackToLocals(vm, vm->fstack.fp, num);
                vm->pc = addr;
                break;

            case RETV:
                frm = frame(vm);
                if (frm == 0) {
                    printf("RETV: no previous frame to transfer value to!\n");
                    break;
                }
                transferStackToReturnValue(vm, frm, frm - 1);
                fr = vm->fstack.frames[frm];
                vm->pc = fr->returnAddress;
                popFrame(vm);
                break;

            case CALL:
                addr = next(vm);
                frm = pushFrame(vm);
                fr = getFrame(vm, frm);
                fr->returnAddress = vm->pc;
                vm->pc = addr;
                break;

            case RET:
                fr = vm->fstack.frames[vm->fstack.fp];
                vm->pc = fr->returnAddress;
                popFrame(vm);
                break;

            case PUSH:
                if (vm->pc >= vm->code_length) {
                    printf("PUSH: missing value!\n");
                    return;
                }
                push(vm, next(vm));
                profiler_record_push(&profiler);
                break;

            case POP:
                pop(vm);
                profiler_record_pop(&profiler);
                break;

            case LD:
                if (vm->pc >= vm->code_length) {
                    printf("LD: missing index!\n");
                    return;
                }
                index = next(vm);
                load(vm, index);
                break;

            case ST:
                if (vm->pc >= vm->code_length) {
                    printf("ST: missing index!\n");
                    return;
                }
                index = next(vm);
                store(vm, index);
                break;

            case CRET:
                value = vm->fstack.frames[vm->fstack.fp]->returnValue;
                push(vm, value);
                break;

            case PRINT:
                printf("PRINT: %d\n", pop(vm));
                break;

            case ADD:
                i = pop(vm);
                j = pop(vm);
                k = i + j;
                push(vm, k);
                break;

            case MUL:
                i = pop(vm);
                j = pop(vm);
                k = i * j;
                push(vm, k);
                break;

            case HALT:
                profiler_record_opcode(&profiler, opcode, start_time);
                profiler_report(&profiler);  // final report at HALT
                return;

            default:
                printf("Unknown opcode: %d\n", opcode);
                return;
        }

        profiler_record_opcode(&profiler, opcode, start_time);
    }
}

int main() {
    
    int code[] = {
        PUSH, 10,
        PUSH, 20,

        CALLV, 2, 13,
        CRET,
        PUSH, 80,
        ADD,
        PRINT,
        HALT,

        LD, 0,
        LD, 1,
        MUL,
        LD, 0,
        ADD,

        RETV,
    };
    int code_size = sizeof(code) / sizeof(code[0]);

    VM* vm = newVM(code, code_size);
    vm->debug = 0;
    pushFrame(vm);
    run(vm);
    freeVM(vm);

    return 0;
}
