// fortran_interpreter.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_PROGRAM_LINES 1000
#define MAX_VARIABLES 100
#define MAX_LINE_LENGTH 256

typedef enum { ASSIGN, GOTO, IFGOTO, PRINT, END } InstructionType;

typedef struct {
    InstructionType type;
    char var1[32];
    char var2[32];
    char op[4];
    char label[10];
    char expr[128];
} Instruction;

typedef struct {
    char name[32];
    double value;
} Variable;

Instruction program[MAX_PROGRAM_LINES];
int program_size = 0;
int labels[MAX_PROGRAM_LINES]; // label number -> program index

Variable variables[MAX_VARIABLES];
int variable_count = 0;

int find_variable(const char* name) {
    for (int i = 0; i < variable_count; i++) {
        if (strcmp(variables[i].name, name) == 0)
            return i;
    }
    return -1;
}

void set_variable(const char* name, double value) {
    int idx = find_variable(name);
    if (idx >= 0) {
        variables[idx].value = value;
    } else {
        if (variable_count >= MAX_VARIABLES) {
            fprintf(stderr, "Error: Too many variables.\n");
            exit(1);
        }
        strncpy(variables[variable_count].name, name, sizeof(variables[variable_count].name) - 1);
        variables[variable_count].name[sizeof(variables[variable_count].name) - 1] = '\0';
        variables[variable_count].value = value;
        variable_count++;
    }
}

double get_variable(const char* name) {
    int idx = find_variable(name);
    if (idx >= 0)
        return variables[idx].value;
    fprintf(stderr, "Error: Undefined variable '%s'\n", name);
    exit(1);
}

double eval_expr(const char* expr);

void parse_line(char* line) {
    char* p = line;
    while (isspace(*p)) p++;

    // Check for label
    if (isdigit(*p)) {
        char label_str[10];
        int i = 0;
        while (isdigit(*p) && i < (int)(sizeof(label_str) - 1)) {
            label_str[i++] = *p++;
        }
        label_str[i] = '\0';
        while (isspace(*p)) p++;
        int label_num = atoi(label_str);
        if (label_num < 0 || label_num >= MAX_PROGRAM_LINES) {
            fprintf(stderr, "Error: Invalid label number %d\n", label_num);
            exit(1);
        }
        labels[label_num] = program_size;
    }

    if (strncmp(p, "IF", 2) == 0) {
        p += 2;
        while (isspace(*p)) p++;
        if (*p != '(') {
            fprintf(stderr, "Error: Expected '(' after IF\n");
            exit(1);
        }
        p++;
        char condition[64];
        int i = 0;
        while (*p && *p != ')' && i < (int)(sizeof(condition) - 1)) {
            condition[i++] = *p++;
        }
        condition[i] = '\0';
        if (*p != ')') {
            fprintf(stderr, "Error: Expected ')' after condition\n");
            exit(1);
        }
        p++;
        while (isspace(*p)) p++;
        if (strncmp(p, "GOTO", 4) != 0) {
            fprintf(stderr, "Error: Expected GOTO after IF (...)\n");
            exit(1);
        }
        p += 4;
        while (isspace(*p)) p++;
        char label_target[10];
        sscanf(p, "%9s", label_target);

        Instruction instr = {0};
        instr.type = IFGOTO;
        strncpy(instr.expr, condition, sizeof(instr.expr) - 1);
        strncpy(instr.label, label_target, sizeof(instr.label) - 1);
        program[program_size++] = instr;
    } else if (strncmp(p, "GOTO", 4) == 0) {
        p += 4;
        while (isspace(*p)) p++;
        char label_target[10];
        sscanf(p, "%9s", label_target);

        Instruction instr = {0};
        instr.type = GOTO;
        strncpy(instr.label, label_target, sizeof(instr.label) - 1);
        program[program_size++] = instr;
    } else if (strncmp(p, "PRINT", 5) == 0) {
        p += 5;
        while (isspace(*p)) p++;
        if (*p == '*') p++;
        if (*p == ',') p++;
        while (isspace(*p)) p++;
        char varname[32];
        sscanf(p, "%31s", varname);

        Instruction instr = {0};
        instr.type = PRINT;
        strncpy(instr.var1, varname, sizeof(instr.var1) - 1);
        program[program_size++] = instr;
    } else if (strncmp(p, "END", 3) == 0) {
        Instruction instr = {0};
        instr.type = END;
        program[program_size++] = instr;
    } else {
        char varname[32];
        if (sscanf(p, "%31s", varname) != 1) {
            fprintf(stderr, "Error: Syntax error in assignment\n");
            exit(1);
        }
        p += strlen(varname);
        while (isspace(*p)) p++;
        if (*p != '=') {
            fprintf(stderr, "Error: Expected '=' in assignment\n");
            exit(1);
        }
        p++;
        while (isspace(*p)) p++;
        Instruction instr = {0};
        instr.type = ASSIGN;
        strncpy(instr.var1, varname, sizeof(instr.var1) - 1);
        strncpy(instr.expr, p, sizeof(instr.expr) - 1);
        program[program_size++] = instr;
    }
}

double eval_simple_expr(const char* expr) {
    char token1[32], token2[32], op;
    if (sscanf(expr, "%31s %c %31s", token1, &op, token2) == 3) {
        double v1 = isalpha(token1[0]) ? get_variable(token1) : atof(token1);
        double v2 = isalpha(token2[0]) ? get_variable(token2) : atof(token2);
        switch (op) {
            case '+': return v1 + v2;
            case '-': return v1 - v2;
            case '*': return v1 * v2;
            case '/':
                if (v2 == 0) {
                    fprintf(stderr, "Error: Division by zero\n");
                    exit(1);
                }
                return v1 / v2;
            default:
                fprintf(stderr, "Error: Unknown operator '%c'\n", op);
                exit(1);
        }
    } else {
        if (isalpha(expr[0]))
            return get_variable(expr);
        else
            return atof(expr);
    }
}

double eval_expr(const char* expr) {
    return eval_simple_expr(expr);
}

int eval_condition(const char* cond) {
    char left[32], right[32];
    char cmp[4];
    int i = 0;

    if (strstr(cond, ".EQ.") != NULL) {
        sscanf(cond, "%31s .EQ. %31s", left, right);
        strcpy(cmp, "==");
    } else if (strstr(cond, ".NE.") != NULL) {
        sscanf(cond, "%31s .NE. %31s", left, right);
        strcpy(cmp, "!=");
    } else if (strstr(cond, ".LT.") != NULL) {
        sscanf(cond, "%31s .LT. %31s", left, right);
        strcpy(cmp, "<");
    } else if (strstr(cond, ".LE.") != NULL) {
        sscanf(cond, "%31s .LE. %31s", left, right);
        strcpy(cmp, "<=");
    } else if (strstr(cond, ".GT.") != NULL) {
        sscanf(cond, "%31s .GT. %31s", left, right);
        strcpy(cmp, ">");
    } else if (strstr(cond, ".GE.") != NULL) {
        sscanf(cond, "%31s .GE. %31s", left, right);
        strcpy(cmp, ">=");
    } else {
        fprintf(stderr, "Error: Malformed condition '%s'\n", cond);
        exit(1);
    }

    double v1 = isalpha(left[0]) ? get_variable(left) : atof(left);
    double v2 = isalpha(right[0]) ? get_variable(right) : atof(right);

    if (strcmp(cmp, "==") == 0) return v1 == v2;
    if (strcmp(cmp, "!=") == 0) return v1 != v2;
    if (strcmp(cmp, "<") == 0)  return v1 < v2;
    if (strcmp(cmp, "<=") == 0) return v1 <= v2;
    if (strcmp(cmp, ">") == 0)  return v1 > v2;
    if (strcmp(cmp, ">=") == 0) return v1 >= v2;

    return 0;
}

void run_program() {
    int pc = 0;
    while (pc < program_size) {
        Instruction* instr = &program[pc];
        switch (instr->type) {
            case ASSIGN:
                set_variable(instr->var1, eval_expr(instr->expr));
                pc++;
                break;
            case GOTO: {
                int target = atoi(instr->label);
                if (target < 0 || target >= MAX_PROGRAM_LINES || labels[target] == -1) {
                    fprintf(stderr, "Error: Invalid GOTO label %d\n", target);
                    exit(1);
                }
                pc = labels[target];
                break;
            }
            case IFGOTO: {
                int target = atoi(instr->label);
                if (target < 0 || target >= MAX_PROGRAM_LINES || labels[target] == -1) {
                    fprintf(stderr, "Error: Invalid IFGOTO label %d\n", target);
                    exit(1);
                }
                if (eval_condition(instr->expr))
                    pc = labels[target];
                else
                    pc++;
                break;
            }
            case PRINT:
                printf("%.6f\n", get_variable(instr->var1));
                pc++;
                break;
            case END:
                return;
        }
    }
}

void load_program_from_string(const char* code) {
    for (int i = 0; i < MAX_PROGRAM_LINES; i++)
        labels[i] = -1; // init labels to invalid
    char buffer[MAX_LINE_LENGTH];
    const char* p = code;
    while (*p) {
        int i = 0;
        while (*p && *p != '\n') {
            if (i < MAX_LINE_LENGTH - 1)
                buffer[i++] = *p++;
            else
                p++;
        }
        buffer[i] = '\0';
        if (*p == '\n') p++;
        if (i > 0)
            parse_line(buffer);
    }
}

int main() {
    const char* program_code =
        "      N = 5\n"
        "      FACT = 1\n"
        "10    IF (N .GT. 1) GOTO 20\n"
        "      PRINT *, FACT\n"
        "      GOTO 30\n"
        "20    FACT = FACT * N\n"
        "      N = N - 1\n"
        "      GOTO 10\n"
        "30    END\n";

    load_program_from_string(program_code);
    run_program();
    return 0;
}