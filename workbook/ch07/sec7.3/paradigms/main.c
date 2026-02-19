#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>


typedef enum {
    OP_PUSH,
    OP_ADD,
    OP_MUL,
    OP_DUP,
    OP_SWAP,
    OP_DROP,
    OP_PRINT,
    OP_HALT
} OpCode;

typedef struct {
    OpCode op;
    double value;   // only used for PUSH
} Instruction;

#define STACK_MAX 256

typedef struct {
    double data[STACK_MAX];
    int top;
} Stack;


void push(Stack *s, double v) {
    s->data[s->top++] = v;
}

double pop(Stack *s) {
    return s->data[--s->top];
}


void run(Instruction *code) {
    Stack stack = {.top = 0};
    int ip = 0;

    while (1) {
        Instruction instr = code[ip++];

        switch (instr.op) {

            case OP_PUSH:
                push(&stack, instr.value);
                break;

            case OP_ADD: {
                double a = pop(&stack);
                double b = pop(&stack);
                push(&stack, b + a);
                break;
            }

            case OP_MUL: {
                double a = pop(&stack);
                double b = pop(&stack);
                push(&stack, b * a);
                break;
            }

            case OP_DUP: {
                double a = pop(&stack);
                push(&stack, a);
                push(&stack, a);
                break;
            }

            case OP_SWAP: {
                double a = pop(&stack);
                double b = pop(&stack);
                push(&stack, a);
                push(&stack, b);
                break;
            }

            case OP_DROP:
                pop(&stack);
                break;

            case OP_PRINT:
                printf("%f\n", pop(&stack));
                break;

            case OP_HALT:
                return;
        }
    }
}


typedef struct {
    const char *name;
    OpCode op;
} Word;


Word dictionary[] = {
    {"add",   OP_ADD},
    {"mul",   OP_MUL},
    {"dup",   OP_DUP},
    {"swap",  OP_SWAP},
    {"drop",  OP_DROP},
    {"print", OP_PRINT},
    {NULL,    OP_HALT}
};

OpCode lookup(const char *token) {
    for (int i = 0; dictionary[i].name; i++) {
        if (strcmp(dictionary[i].name, token) == 0)
            return dictionary[i].op;
    }
    return -1;  // not found
}


/*
int main() {
    const char *source = "3 4 add print 5 mul print";
    char *token;
    char buffer[256];
    Instruction code[256];
    int ip = 0;

    strncpy(buffer, source, sizeof(buffer));
    token = strtok(buffer, " ");

    while (token) {
        OpCode op = lookup(token);
        if (op != -1) {
            code[ip++] = (Instruction){.op = op};
        } else {
            code[ip++] = (Instruction){.op = OP_PUSH, .value = atof(token)};
        }
        token = strtok(NULL, " ");
    }
    code[ip++] = (Instruction){.op = OP_HALT};

    run(code);
    return 0;
}*/


//(--------------



int is_number(const char *s) {
    if (*s == '-' || *s == '+') s++;
    while (*s) {
        if (!isdigit(*s) && *s != '.') return 0;
        s++;
    }
    return 1;
}


int compile(const char *source, Instruction *code) {
    char buffer[64];
    int ci = 0;
    int ip = 0;

    for (int i = 0; ; i++) {
        char c = source[i];

        if (c == ' ' || c == '\n' || c == '\0') {
            if (ci == 0) {
                if (c == '\0') break;
                continue;
            }

            buffer[ci] = '\0';
            ci = 0;

            if (is_number(buffer)) {
                code[ip++] = (Instruction){OP_PUSH, atof(buffer)};
            } else {
                OpCode op = lookup(buffer);
                if (op == -1) {
                    printf("Unknown word: %s\n", buffer);
                    exit(1);
                }
                code[ip++] = (Instruction){op, 0};
            }

            if (c == '\0') break;
        } else {
            buffer[ci++] = c;
        }
    }

    code[ip++] = (Instruction){OP_HALT, 0};
    return ip;
}


int main() {
    const char *source = "3 4 dup add mul print";

    Instruction code[256];
    compile(source, code);

    run(code);
}

