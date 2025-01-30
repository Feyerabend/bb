#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ast.h"
#include "symbol_table.h"
#include "tac.h"


// global list of TAC instructions
TAC *tac_head = NULL;
TAC *tac_tail = NULL;

// counter for generating temporary variables
int temp_counter = 0;
int label_counter = 0;

// generate a new temporary variable
char *newTemp() {
    char *temp = malloc(16);
    snprintf(temp, 16, "t%d", temp_counter++);
    return temp;
}

char *newLabel() {
    char *label = malloc(16);
    snprintf(label, 16, "L%d", label_counter++);
    return label;
}

void emitTAC(const char *op, const char *arg1, const char *arg2, const char *result) {
    TAC *new_tac = malloc(sizeof(TAC));
    if (!new_tac) {
        fprintf(stderr, "Memory allocation failed for TAC instruction\n");
        exit(EXIT_FAILURE);
    }

    new_tac->op = strdup(op);
    new_tac->arg1 = arg1 ? strdup(arg1) : NULL;
    new_tac->arg2 = arg2 ? strdup(arg2) : NULL;
    new_tac->result = result ? strdup(result) : NULL;
    new_tac->next = NULL;

    if (!tac_head) {
        tac_head = tac_tail = new_tac;
    } else {
        tac_tail->next = new_tac;
        tac_tail = new_tac;
    }
}

void freeTAC() {
    TAC *current = tac_head;
    while (current) {
        TAC *next = current->next;
        free(current->op);
        free(current->arg1);
        free(current->arg2);
        free(current->result);
        free(current);
        current = next;
    }
    tac_head = tac_tail = NULL;
}


char *generateTAC(ASTNode *node) {
    if (!node) return NULL;

    switch (node->type) {

        case NODE_BLOCK: {
            if (strcmp(node->value, "main") == 0) {
                emitTAC("LABEL", NULL, NULL, "main"); // label: 'main'
                for (int i = 0; i < node->childCount; i++) {
                    generateTAC(node->children[i]); // assignments and CALL
                }
            } else {
                // generic block (no label)
                for (int i = 0; i < node->childCount; i++) {
                    generateTAC(node->children[i]);
                }
            }
            return NULL;
        }

        case NODE_PROC_DECL: {
            emitTAC("LABEL", NULL, NULL, node->value); // label: procedure name
            generateTAC(node->children[0]); // procedure body
            emitTAC("RETURN", NULL, NULL, NULL); // return from procedure
            return NULL;
        }

        case NODE_WHILE: {
            char *start_label = newLabel();
            char *end_label = newLabel();
            emitTAC("LABEL", NULL, NULL, start_label); // L0:

            // evaluate condition (e.g. b != 0)
            char *cond_temp = generateTAC(node->children[0]); // t2 = != t0 t1
            emitTAC("IF_NOT", cond_temp, end_label, NULL); // IF_NOT t2 GOTO L1

            generateTAC(node->children[1]); // nested block

            emitTAC("GOTO", start_label, NULL, NULL); // GOTO L0
            emitTAC("LABEL", NULL, NULL, end_label); // L1:
            return NULL;
        }

        case NODE_CONDITION: {
            if (node->childCount != 2) {
                fprintf(stderr, "Error: CONDITION node must have two children\n");
                exit(1);
            }
            if (strcmp(node->value, "#") == 0) {
                //  "#" --> "!="
                char *left = generateTAC(node->children[0]);
                char *right = generateTAC(node->children[1]);
                char *result = newTemp();
                emitTAC("!=", left, right, result);
                return result;
            }
            char *left = generateTAC(node->children[0]);
            char *right = generateTAC(node->children[1]);
            char *result = newTemp();
            emitTAC(node->value, left, right, result); // t5 = > t3 t4
            return result;
        }

        case NODE_IF: {
            char *cond_temp = generateTAC(node->children[0]); // eval condition
            char *skip_label = newLabel();
            emitTAC("IF_NOT", cond_temp, skip_label, NULL); // IF_NOT cond_temp GOTO L2

            // IF body (assignment)
            generateTAC(node->children[1]);

            emitTAC("LABEL", NULL, NULL, skip_label); // L2:
            return NULL;
        }

        case NODE_ASSIGNMENT: {
            char *temp = generateTAC(node->children[0]);
            if (temp) {
                emitTAC("=", temp, NULL, node->value); // squ = t2
            } else {
                fprintf(stderr, "Error: Assignment has no value\n");
            }
            return NULL;
        }

        case NODE_OPERATOR: {
            // operator (e.g. -, +)
            char *left = generateTAC(node->children[0]);
            char *right = generateTAC(node->children[1]);
            char *result = newTemp();
            emitTAC(node->value, left, right, result); // t8 = - t6 t7
            return result;
        }

        case NODE_EXPRESSION: {
            // expression (forward to child)
            // asymmetric tree, so we can't just return the result of the left child!
            return generateTAC(node->children[0]);
        }

        case NODE_IDENTIFIER: {
            // load variable into temporary
            char *temp = newTemp();
            emitTAC("LOAD", node->value, NULL, temp); // t0 = LOAD b
            return temp;
        }

        case NODE_NUMBER: {
            // load constant into temporary
            char *temp = newTemp();
            emitTAC("LOAD", node->value, NULL, temp); // t1 = LOAD 0
            return temp;
        }

        case NODE_CONST_DECL: {
            char *value_temp = generateTAC(node->children[0]);
            emitTAC("=", value_temp, NULL, node->value);
            return NULL;
        }

        case NODE_CALL: {
            emitTAC("CALL", node->value, NULL, NULL);
            return NULL;
        }

        default:
            // other nodes (VAR_DECL, etc.)
            for (int i = 0; i < node->childCount; i++) {
                generateTAC(node->children[i]);
            }
            return NULL;
    }
}

void printTAC() {
    TAC *current = tac_head;
    while (current) {

        if (strcmp(current->op, "LABEL") == 0) {
            printf("%s:\n", current->result);

        } else if (strcmp(current->op, "IF_NOT") == 0) {
            printf("IF_NOT %s GOTO %s\n", current->arg1, current->arg2); // conditional jumps

        } else if (strcmp(current->op, "GOTO") == 0) {
            printf("GOTO %s\n", current->arg1); // unconditional jumps

        } else if (strcmp(current->op, "CALL") == 0) {
            printf("CALL %s\n", current->arg1); // procedure calls

        } else if (strcmp(current->op, "LOAD") == 0) {
            printf("%s = LOAD %s\n", current->result, current->arg1); // loads

        } else if (strcmp(current->op, "RETURN") == 0) {
            printf("RETURN\n"); // procedure return

        } else if (strcmp(current->op, "=") == 0) {  // assignments
            printf("%s = %s\n", current->result, current->arg1);

        } else {
            // standard ops (+, -, !=)
            printf("%s = %s %s %s\n", current->result, current->op, current->arg1, current->arg2);
        }
        current = current->next;
    }
}

void exportTACFile(FILE *file) {
    TAC *current = tac_head;
    while (current) {
        fprintf(file, "TYPE: %s\n", current->op);
        fprintf(file, "ARG1: %s\n", current->arg1 ? current->arg1 : "NULL");
        fprintf(file, "ARG2: %s\n", current->arg2 ? current->arg2 : "NULL");
        fprintf(file, "RESULT: %s\n\n", current->result ? current->result : "NULL");  // Empty line as separator
        current = current->next;
    }
}

void exportTAC(const char *filename) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Error opening file");
        exit(1);
    }
    exportTACFile(file);
    fclose(file);
}

// --- TAC parser ---

void parseTAC(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening file");
        return;
    }

    char line[128], op[32], arg1[32], arg2[32], result[32];

    while (fgets(line, sizeof(line), file)) {
        if (strncmp(line, "TYPE:", 5) == 0) {
            sscanf(line, "TYPE: %s", op);
        } else if (strncmp(line, "ARG1:", 5) == 0) {
            sscanf(line, "ARG1: %s", arg1);
        } else if (strncmp(line, "ARG2:", 5) == 0) {
            sscanf(line, "ARG2: %s", arg2);
        } else if (strncmp(line, "RESULT:", 7) == 0) {
            sscanf(line, "RESULT: %s", result);
            // Now we have a complete instruction
            printf("Parsed TAC - OP: %s, ARG1: %s, ARG2: %s, RESULT: %s\n",
                   op, arg1, arg2, result);
        }
    }

    fclose(file);
}
