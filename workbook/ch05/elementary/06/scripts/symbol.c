#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// sizes for strings and arrays, change as needed
#define MAX_KEY_LEN 256
#define MAX_VALUE_LEN 1024
#define MAX_CHILDREN 128

typedef struct Node {
    char type[MAX_KEY_LEN];
    char value[MAX_KEY_LEN];
    struct Node *children[MAX_CHILDREN];
    int child_count;
} Node;

typedef struct Symbol {
    char name[MAX_KEY_LEN];
    char type[MAX_KEY_LEN];
    char scope[MAX_KEY_LEN];
    char value[MAX_VALUE_LEN];
} Symbol;

typedef struct Scope {
    Symbol variables[MAX_CHILDREN];
    int variable_count;
} Scope;

typedef struct SymbolTable {
    Scope global_scope;
    Scope procedures[MAX_CHILDREN];
    int procedure_count;
} SymbolTable;


// parse simple JSON file (replaceable by library?)
Node *parse_ast(const char *filename) {
    //TODO Implement a basic JSON parser
    return NULL;
}

void yaml_format(FILE *output, SymbolTable *table) {
    fprintf(output, "# Constants\n");
    for (int i = 0; i < table->global_scope.variable_count; ++i) {
        Symbol *symbol = &table->global_scope.variables[i];
        if (strcmp(symbol->type, "constant") == 0) {
            fprintf(output, "%s:\n  type: %s\n  value: %s\n", 
                    symbol->name, symbol->type, symbol->value);
        }
    }

    fprintf(output, "\n# Variables and Procedures\n");
    for (int i = 0; i < table->global_scope.variable_count; ++i) {
        Symbol *symbol = &table->global_scope.variables[i];
        if (strcmp(symbol->type, "variable") == 0) {
            fprintf(output, "%s:\n  type: %s\n", 
                    symbol->name, symbol->type);
        }
    }

    for (int i = 0; i < table->procedure_count; ++i) {
        fprintf(output, "%s:\n  type: procedure\n  scope:\n", table->procedures[i].variables[0].name);
        for (int j = 0; j < table->procedures[i].variable_count; ++j) {
            Symbol *symbol = &table->procedures[i].variables[j];
            fprintf(output, "    %s:\n      type: %s\n", symbol->name, symbol->type);
        }
    }
}

// extract constants from AST
void extract_constants(Node *node, SymbolTable *table) {
    if (!node) return;

    if (strcmp(node->type, "CONST_DECL") == 0) {
        Symbol symbol;
        strcpy(symbol.name, node->value);
        strcpy(symbol.type, "constant");
        if (node->child_count > 0 && strcmp(node->children[0]->type, "NUMBER") == 0) {
            strcpy(symbol.value, node->children[0]->value);
        } else {
            strcpy(symbol.value, "null");
        }
        table->global_scope.variables[table->global_scope.variable_count++] = symbol;
    }

    for (int i = 0; i < node->child_count; ++i) {
        extract_constants(node->children[i], table);
    }
}

// extract variables and procedures from AST
void extract_symbols(Node *node, SymbolTable *table, Scope *current_scope) {
    if (!node) return;

    if (strcmp(node->type, "VAR_DECL") == 0) {
        Symbol symbol;
        strcpy(symbol.name, node->value);
        strcpy(symbol.type, "variable");
        strcpy(symbol.scope, current_scope == &table->global_scope ? "global" : "local");
        current_scope->variables[current_scope->variable_count++] = symbol;
    } else if (strcmp(node->type, "PROC_DECL") == 0) {
        Scope *new_scope = &table->procedures[table->procedure_count++];
        Symbol symbol;
        strcpy(symbol.name, node->value);
        strcpy(symbol.type, "procedure");
        table->global_scope.variables[table->global_scope.variable_count++] = symbol;

        for (int i = 0; i < node->child_count; ++i) {
            extract_symbols(node->children[i], table, new_scope);
        }
    }

    for (int i = 0; i < node->child_count; ++i) {
        extract_symbols(node->children[i], table, current_scope);
    }
}

int main(int argc, char *argv[]) {
    char inputfile[MAX_KEY_LEN] = "";
    char outputfile[MAX_KEY_LEN] = "";

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-i") == 0 && i + 1 < argc) {
            strcpy(inputfile, argv[++i]);
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            strcpy(outputfile, argv[++i]);
        }
    }

    if (strlen(inputfile) == 0) {
        fprintf(stderr, "Usage: program -i <inputfile> -o <outputfile>\n");
        return EXIT_FAILURE;
    }

    Node *ast = parse_ast(inputfile);
    if (!ast) {
        fprintf(stderr, "Failed to parse input file: %s\n", inputfile);
        return EXIT_FAILURE;
    }

    SymbolTable table = {0};
    extract_constants(ast, &table);
    extract_symbols(ast, &table, &table.global_scope);

    FILE *output = (strlen(outputfile) > 0) ? fopen(outputfile, "w") : stdout;
    if (!output) {
        fprintf(stderr, "Failed to open output file: %s\n", outputfile);
        return EXIT_FAILURE;
    }

    yaml_format(output, &table);

    if (output != stdout) fclose(output);
    return EXIT_SUCCESS;
}
