#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 256
#define MAX_KEY_LENGTH 128
#define MAX_VALUE_LENGTH 128

typedef struct Node {
    char key[MAX_KEY_LENGTH];
    char value[MAX_VALUE_LENGTH];
    struct Node *parent;
    struct Node *children;
    struct Node *next;
} Node;

Node *create_node(const char *key, const char *value) {
    Node *node = (Node *)malloc(sizeof(Node));
    if (!node) {
        fprintf(stderr, "Memory allocation failed.\n");
        exit(EXIT_FAILURE);
    }
    strncpy(node->key, key, MAX_KEY_LENGTH);
    if (value) {
        strncpy(node->value, value, MAX_VALUE_LENGTH);
    } else {
        node->value[0] = '\0';
    }
    node->parent = NULL;
    node->children = NULL;
    node->next = NULL;
    return node;
}

void add_child(Node *parent, Node *child) {
    child->parent = parent;
    if (!parent->children) {
        parent->children = child;
    } else {
        Node *sibling = parent->children;
        while (sibling->next) {
            sibling = sibling->next;
        }
        sibling->next = child;
    }
}

int parse_line(const char *line, char *key, char *value, int *indent_level) {
    const char *trimmed_line = line + strspn(line, " "); // skip .. more?
    *indent_level = (trimmed_line - line) / 2;          // indent
    const char *colon = strchr(trimmed_line, ':');
    if (!colon) {
        return 0;
    }
    strncpy(key, trimmed_line, colon - trimmed_line);
    key[colon - trimmed_line] = '\0';
    const char *value_start = colon + 1;
    while (*value_start == ' ') value_start++; // skip .. move?
    strncpy(value, value_start, MAX_VALUE_LENGTH);
    return 1;
}

Node *parse_yaml(FILE *file) {
    char line[MAX_LINE_LENGTH];
    Node *root = create_node("root", NULL);
    Node *current = root;
    int current_indent = -1;

    while (fgets(line, MAX_LINE_LENGTH, file)) {
        // skip ..
        if (line[0] == '\n' || line[0] == '#') {
            continue;
        }

        char key[MAX_KEY_LENGTH];
        char value[MAX_VALUE_LENGTH];
        int indent_level;

        if (!parse_line(line, key, value, &indent_level)) {
            fprintf(stderr, "Invalid YAML line: %s", line);
            exit(EXIT_FAILURE);
        }

        // indent ..
        while (indent_level <= current_indent) {
            current = current->parent;
            current_indent--;
        }

        Node *new_node = create_node(key, strlen(value) > 0 ? value : NULL);
        add_child(current, new_node);
        if (!strlen(value)) { // no value? parent node
            current = new_node;
            current_indent = indent_level;
        }
    }

    return root;
}

void print_symbol_table(Node *node, int depth) {
    for (int i = 0; i < depth; i++) {
        printf("  ");
    }
    printf("%s: %s\n", node->key, node->value[0] ? node->value : "");
    Node *child = node->children;
    while (child) {
        print_symbol_table(child, depth + 1);
        child = child->next;
    }
}

void free_tree(Node *node) {
    if (!node) return;
    Node *child = node->children;
    while (child) {
        Node *next_child = child->next;
        free_tree(child);
        child = next_child;
    }
    free(node);
}

int main() {
    const char *yaml_file_path = "sample.symbol";
    FILE *file = fopen(yaml_file_path, "r");
    if (!file) {
        fprintf(stderr, "YAML file '%s' not found.\n", yaml_file_path);
        return EXIT_FAILURE;
    }

    Node *symbol_table = parse_yaml(file);
    fclose(file);

    printf("Parsed Symbol Table:\n");
    print_symbol_table(symbol_table, 0);

    free_tree(symbol_table);
    return EXIT_SUCCESS;
}
