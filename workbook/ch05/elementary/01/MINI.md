

## Mini Compiler: Overview of Compiling in Practice

This example demonstrates a simple compiler for arithmetic expressions, converting
high-level input into a pseudo-assembly language.
1. Lexical Analysis: Tokenise the input.
2. Syntax Analysis: Parse tokens into an Abstract Syntax Tree (AST).
3. Semantic Analysis: Ensure the AST is valid.
4. Intermediate Code Generation: Transform the AST into a simpler representation.
5. Code Generation: Generate pseudo-assembly from the intermediate representation.


### Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

typedef enum {
    TOKEN_NUMBER,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_MULTIPLY,
    TOKEN_DIVIDE,
    TOKEN_END
} TokenType;

typedef struct {
    TokenType type;
    int value; // TOKEN_NUMBER
} Token;

typedef enum {
    AST_NUMBER,
    AST_BINARY_OP
} ASTNodeType;

typedef struct ASTNode {
    ASTNodeType type;
    int value; // numbers
    struct ASTNode *left, *right; // binary operations
    char op; // operator: +, -, *, /
} ASTNode;

// global state
const char *input;
Token current_token;

// fwd decl
void next_token();
ASTNode *parse_expression();
ASTNode *parse_term();
ASTNode *parse_factor();
void semantic_analysis(ASTNode *node);
void generate_code(ASTNode *node);
void error(const char *message);

// Lexical Analysis: Tokeniser
void next_token() {
    while (*input == ' ') input++; // skip whitespace

    if (*input == '\0') {
        current_token.type = TOKEN_END;
        return;
    }

    if (isdigit(*input)) {
        current_token.type = TOKEN_NUMBER;
        current_token.value = strtol(input, (char **)&input, 10);
        return;
    }

    switch (*input) {
        case '+': current_token.type = TOKEN_PLUS; input++; break;
        case '-': current_token.type = TOKEN_MINUS; input++; break;
        case '*': current_token.type = TOKEN_MULTIPLY; input++; break;
        case '/': current_token.type = TOKEN_DIVIDE; input++; break;
        default: error("Unexpected character");
    }
}

// Syntax Analysis: Recursive Descent Parser
ASTNode *create_node(ASTNodeType type, int value, ASTNode *left, ASTNode *right, char op) {
    ASTNode *node = (ASTNode *)malloc(sizeof(ASTNode));
    node->type = type;
    node->value = value;
    node->left = left;
    node->right = right;
    node->op = op;
    return node;
}

ASTNode *parse_expression() {
    ASTNode *node = parse_term(); // first term
    while (current_token.type == TOKEN_PLUS || current_token.type == TOKEN_MINUS) {
        char op = (current_token.type == TOKEN_PLUS) ? '+' : '-';
        next_token(); // consume operator
        node = create_node(AST_BINARY_OP, 0, node, parse_term(), op);
    }
    return node;
}

ASTNode *parse_term() {
    ASTNode *node = parse_factor(); // first factor
    while (current_token.type == TOKEN_MULTIPLY || current_token.type == TOKEN_DIVIDE) {
        char op = (current_token.type == TOKEN_MULTIPLY) ? '*' : '/';
        next_token(); // consume operator
        node = create_node(AST_BINARY_OP, 0, node, parse_factor(), op);
    }
    return node;
}

ASTNode *parse_factor() {
    if (current_token.type == TOKEN_NUMBER) {
        ASTNode *node = create_node(AST_NUMBER, current_token.value, NULL, NULL, 0);
        next_token(); // consume number
        return node;
    } else {
        error("Expected number");
        return NULL; // not reached
    }
}

// Semantic Analysis: Validate AST
void semantic_analysis(ASTNode *node) {
    if (node->type == AST_BINARY_OP) {
        semantic_analysis(node->left);
        semantic_analysis(node->right);
        if (node->op == '/' && node->right->type == AST_NUMBER && node->right->value == 0) {
            error("Division by zero");
        }
    }
}

// Code Generation: Recursive Postorder Traversal
void generate_code(ASTNode *node) {
    if (node->type == AST_NUMBER) {
        printf("PUSH %d\n", node->value);
    } else if (node->type == AST_BINARY_OP) {
        generate_code(node->left);
        generate_code(node->right);
        switch (node->op) {
            case '+': printf("ADD\n"); break;
            case '-': printf("SUB\n"); break;
            case '*': printf("MUL\n"); break;
            case '/': printf("DIV\n"); break;
        }
    }
}

void error(const char *message) {
    fprintf(stderr, "Error: %s\n", message);
    exit(EXIT_FAILURE);
}

int main() {
    char buffer[256];
    printf("Enter an arithmetic expression: ");
    if (fgets(buffer, sizeof(buffer), stdin)) {
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len - 1] == '\n') {
            buffer[len - 1] = '\0';
        }
    } else {
        error("Failed to read input");
    }

    input = buffer;
    next_token();

    // Compilation Pipeline
    ASTNode *ast = parse_expression();
    if (current_token.type != TOKEN_END) {
        error("Unexpected input after expression");
    }

    semantic_analysis(ast);
    printf("Generated Assembly:\n");
    generate_code(ast);

    return 0;
}
```

1. Lexical Analysis:
- next_token scans the input and produces tokens (TOKEN_NUMBER, TOKEN_PLUS, etc.).

2. Syntax Analysis:
- The parser constructs an Abstract Syntax Tree (AST) using recursive descent:
- Nodes represent either numbers (AST_NUMBER) or binary operations (AST_BINARY_OP).

3. Semantic Analysis:
- Ensures correctness of the AST:
    - Example: Checking for division by zero.
4. Code Generation:
- Traverses the AST in postorder and generates stack-based pseudo-assembly.



Input:

Enter an arithmetic expression: '3 + 5 * 2'

Output:

Generated Assembly:
```assembly
PUSH 3
PUSH 5
PUSH 2
MUL
ADD
```
It can be extended further with additional features like variable handling
or more complex language constructs.
