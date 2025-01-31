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

// append the appropriate suffix to variable names
char* getModifiedName(const char* name, const char* proc_name, int isGlobal) {
    char* modifiedName;
    if (isGlobal) {
        modifiedName = malloc(strlen(name) + 3); // +3 for ".g\0"
        sprintf(modifiedName, "%s.g", name);
    } else {
        modifiedName = malloc(strlen(proc_name) + strlen(name) + 4); // proc_name + "." + name + ".l\0"
        sprintf(modifiedName, "%s.%s.l", proc_name, name);
    }
    return modifiedName;
}

// check if a variable is local to procedure
int isLocalVariable(const char* proc_name, const char* var_name) {
    Procedure* proc = procedures;
    while (proc) {
        if (strcmp(proc->name, proc_name) == 0) {
            // found procedure, check its local variables
            Variable* local_var = proc->local_vars;
            while (local_var) {
                if (strcmp(local_var->name, var_name) == 0) {
                    return 1; // variable local
                }
                local_var = local_var->next;
            }
            break; // procedure found, but variable not local
        }
        proc = proc->next;
    }
    return 0; // variable not local
}

// check if a variable global
int isGlobalVariable(const char* var_name) {
    Variable* global_var = global_vars;
    while (global_var) {
        if (strcmp(global_var->name, var_name) == 0) {
            return 1; // global
        }
        global_var = global_var->next;
    }
    return 0; // variable not global
}


char *generateTAC(ASTNode *node, const char* proc_name) {
    if (!node) return NULL;

    switch (node->type) {

        case NODE_BLOCK: {
            if (strcmp(node->value, "main") == 0) {
                emitTAC("LABEL", NULL, NULL, "main"); // label: 'main'
                for (int i = 0; i < node->childCount; i++) {
                    generateTAC(node->children[i], "main"); // assignments and CALL
                }
            } else {
                // generic block (no label)
                for (int i = 0; i < node->childCount; i++) {
                    generateTAC(node->children[i], proc_name);
                }
            }
            return NULL;
        }

        case NODE_PROC_DECL: {
            emitTAC("LABEL", NULL, NULL, node->value); // label: procedure name
            generateTAC(node->children[0], node->value); // procedure body
            emitTAC("RETURN", NULL, NULL, NULL); // return from procedure
            return NULL;
        }

        case NODE_WHILE: {
            char *start_label = newLabel();
            char *end_label = newLabel();
            emitTAC("LABEL", NULL, NULL, start_label); // L0:

            // evaluate condition (e.g. b != 0)
            char *cond_temp = generateTAC(node->children[0], proc_name); // t2 = != t0 t1
            emitTAC("IF_NOT", cond_temp, end_label, NULL); // IF_NOT t2 GOTO L1

            generateTAC(node->children[1], proc_name); // nested block

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
                char *left = generateTAC(node->children[0], proc_name);
                char *right = generateTAC(node->children[1], proc_name);
                char *result = newTemp();
                emitTAC("!=", left, right, result);
                return result;
            }
            char *left = generateTAC(node->children[0], proc_name);
            char *right = generateTAC(node->children[1], proc_name);
            char *result = newTemp();
            emitTAC(node->value, left, right, result); // t5 = > t3 t4
            return result;
        }

        case NODE_IF: {
            char *cond_temp = generateTAC(node->children[0], proc_name); // eval condition
            char *skip_label = newLabel();
            emitTAC("IF_NOT", cond_temp, skip_label, NULL); // IF_NOT cond_temp GOTO L2

            // IF body (assignment)
            generateTAC(node->children[1], proc_name);

            emitTAC("LABEL", NULL, NULL, skip_label); // L2:
            return NULL;
        }

        case NODE_ASSIGNMENT: {
            char* temp = generateTAC(node->children[0], proc_name);
            if (temp) {
                if (isLocalVariable(proc_name, node->value)) {
                    char* modifiedName = getModifiedName(node->value, proc_name, 0); // Local variable
                    emitTAC("=", temp, NULL, modifiedName);
                    free(modifiedName);
                } else if (isGlobalVariable(node->value)) {
                    char* modifiedName = getModifiedName(node->value, proc_name, 1); // Global variable
                    emitTAC("=", temp, NULL, modifiedName);
                    free(modifiedName);
                } else {
                    emitTAC("=", temp, NULL, node->value); // Temporary variable or unknown
                }
            } else {
                fprintf(stderr, "Error: Assignment has no value\n");
            }
            return NULL;
        }

        case NODE_OPERATOR: {
            // operator (e.g. -, +)
            char *left = generateTAC(node->children[0], proc_name);
            char *right = generateTAC(node->children[1], proc_name);
            char *result = newTemp();
            emitTAC(node->value, left, right, result); // t8 = - t6 t7
            return result;
        }

        case NODE_TERM: {
            if (node->childCount != 2) {
                fprintf(stderr, "Error: TERM node must have two children\n");
                exit(1);
            }
            char *left = generateTAC(node->children[0], proc_name);
            char *right = generateTAC(node->children[1], proc_name);
            char *result = newTemp();
            emitTAC(node->value, left, right, result); // e.g., t4 = * t2 t3
            return result;
        }

        case NODE_FACTOR: {
            if (node->childCount == 1) {
                return generateTAC(node->children[0], proc_name); // fwrd single child
            } else if (node->childCount == 2 && strcmp(node->value, "-") == 0) {
                char *operand = generateTAC(node->children[1], proc_name);
                char *result = newTemp();
                emitTAC("NEG", operand, NULL, result); // negate factor: t6 = NEG t5
                return result;
            } else {
                fprintf(stderr, "Error: Invalid FACTOR node\n");
                exit(1);
            }
        }

        case NODE_EXPRESSION: {
            // expression (forward to child)
            // asymmetric tree, so we can't just return the result of the left child!
            return generateTAC(node->children[0], proc_name);
        }

        case NODE_IDENTIFIER: {
            // load variable into temporary
            char* modifiedName = NULL;
            if (isLocalVariable(proc_name, node->value)) {
                modifiedName = getModifiedName(node->value, proc_name, 0); // Local variable
            } else if (isGlobalVariable(node->value)) {
                modifiedName = getModifiedName(node->value, proc_name, 1); // Global variable
            } else {
                modifiedName = strdup(node->value); // Temporary variable or unknown
            }

            char* temp = newTemp();
            emitTAC("LOAD", modifiedName, NULL, temp); // t0 = LOAD b
            free(modifiedName);
            return temp;
        }

        case NODE_NUMBER: {
            // load constant into temporary
            char *temp = newTemp();
            emitTAC("LOAD", node->value, NULL, temp); // t1 = LOAD 0
            return temp;
        }

        case NODE_CONST_DECL: {
            char *value_temp = generateTAC(node->children[0], proc_name);
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
                generateTAC(node->children[i], proc_name);
            }
            return NULL;
    }
}

char *genTAC(ASTNode *node) {
    return generateTAC(node, "main");
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
