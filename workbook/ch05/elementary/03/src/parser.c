#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"
#include "lexer.h"
#include "ast.h"
#include "parser.h"
#include "util.h"

#define TRUE 1
#define FALSE 0


Symbol symbol;
char buf[MAX_SYM_LEN];

void nextSymbol() {
    Token token = nextToken();
    // skip
    while (token.type == NOP || token.type == ENDOFLINE) {
        token = nextToken();
    }
    // transfer to local use
    symbol = token.type;
    strncpy(buf, token.value, MAX_SYM_LEN - 1);
    buf[MAX_SYM_LEN - 1] = '\0';
    printsymbol(symbol, buf);
}

void error(const char msg[]) {
    printf("Error: %s (buffer: \"%s\")\n", msg, buf);

    exit(EXIT_FAILURE);
}

int accept(Symbol s) {
    if (symbol == s) {
        nextSymbol();
        return TRUE;
    }
    return FALSE;
}

int expect(Symbol s) {
    if (accept(s)) {
        return TRUE;
    }
    error("expected symbol: ");
    printsymbol(s, buf);
    return FALSE;
}


// --- parsing ---

ASTNode *program();
ASTNode *block();
ASTNode *statement();
ASTNode *condition();
ASTNode *expression();
ASTNode *term();
ASTNode *factor();


ASTNode *factor() {
    char *temp = strdup(buf);
    if (accept(IDENT)) {
        return createNode(NODE_IDENTIFIER, temp);
    } else if (accept(NUMBER)) {
        return createNode(NODE_NUMBER, temp);
    } else if (accept(LPAREN)) {
        ASTNode *expr = expression();
        expect(RPAREN);
        return expr;
    } else {
        error("factor: syntax error");
        nextSymbol();
        return NULL;
    }
}

ASTNode *term() {
    ASTNode *node = factor();
    while (symbol == TIMES || symbol == SLASH) {
        char *op = strdup(symbol == TIMES ? "*" : "/");
        nextSymbol();
        ASTNode *opNode = createNode(NODE_TERM, op);
        addChild(opNode, node);          // left child is the current term
        addChild(opNode, factor());      // right child is the next factor
        node = opNode;                   // update node to the new operator node
    }
    return node;
}

ASTNode *expression() {
    ASTNode *node = createNode(NODE_EXPRESSION, NULL);
    if (symbol == PLUS || symbol == MINUS) {
        addChild(node, createNode(NODE_OPERATOR, symbol == PLUS ? "+" : "-"));
        nextSymbol();
    }
    addChild(node, term());
    while (symbol == PLUS || symbol == MINUS) {
        ASTNode *opNode = createNode(NODE_OPERATOR, symbol == PLUS ? "+" : "-");
        nextSymbol();
        addChild(opNode, node);
        addChild(opNode, term());
        node = opNode;
    }
    return node;
}

ASTNode *condition() {
    if (accept(ODDSYM)) {
        ASTNode *node = createNode(NODE_CONDITION, "ODD");
        addChild(node, expression());
        return node;
    } else if (accept(LPAREN)) { // enforce parentheses
        ASTNode *leftExpr = expression();
        if (symbol == EQL || symbol == NEQ || symbol == LSS || symbol == LEQ || symbol == GTR || symbol == GEQ) {
            ASTNode *node = createNode(NODE_CONDITION, symbolToString(symbol));
            nextSymbol();
            addChild(node, leftExpr);        // left-hand side expression
            addChild(node, expression());    // right-hand side expression
            expect(RPAREN);
            return node;
        }
    }
    error("condition: syntax error");
    nextSymbol();
    return NULL;
}

ASTNode *statement() {
    char *temp = strdup(buf);
    if (accept(IDENT)) {
        ASTNode *assignNode = createNode(NODE_ASSIGNMENT, temp);
        expect(BECOMES);
        addChild(assignNode, expression());
        return assignNode;
    } else if (accept(CALLSYM)) {
        char *name = strdup(buf);
        expect(IDENT);
        return createNode(NODE_CALL, name);
    } else if (accept(BEGINSYM)) {
        ASTNode *beginNode = createNode(NODE_BEGIN, NULL);
        do {
            addChild(beginNode, statement());           // *HACK* C-like termination
            if (!accept(SEMICOLON)) {                   // 'begin s1; s2; end'
                break; // exit if no SEMICOLON found    // rather than Pascal separation
            }                                           // 'begin s1 ; s2 end'
        } while (symbol != ENDSYM && symbol != ENDOFFILE);
        if (!accept(ENDSYM)) {
            error("statement: expected END");
        }
        return beginNode;
    } else if (accept(IFSYM)) {
        ASTNode *ifNode = createNode(NODE_IF, NULL);
        addChild(ifNode, condition());
        expect(THENSYM);
        addChild(ifNode, statement());
        return ifNode;
    } else if (accept(WHILESYM)) {
        ASTNode *whileNode = createNode(NODE_WHILE, NULL);
        addChild(whileNode, condition());
        expect(DOSYM);
        addChild(whileNode, statement());
        return whileNode;
    } else {
        error("statement: syntax error");
        nextSymbol();
        return NULL;
    }
}

ASTNode *block() {
    ASTNode *blockNode = createNode(NODE_BLOCK, NULL);
    char *name = NULL;
    char *num = NULL;
    if (accept(CONSTSYM)) {
        do {
            expect(IDENT);
            name = strdup(buf);
            expect(EQL);
            num = strdup(buf);
            expect(NUMBER);
            ASTNode *constNode = createNode(NODE_CONST_DECL, name);
            addChild(constNode, createNode(NODE_NUMBER, num));
            addChild(blockNode, constNode);
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    if (accept(VARSYM)) {
        do {
            name = strdup(buf);
            expect(IDENT);
            addChild(blockNode, createNode(NODE_VAR_DECL, name));
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    while (accept(PROCSYM)) {
        name = strdup(buf);
        expect(IDENT);
        ASTNode *procNode = createNode(NODE_PROC_DECL, name);
        expect(SEMICOLON);
        addChild(procNode, block());
        addChild(blockNode, procNode);
        expect(SEMICOLON);
    }
    addChild(blockNode, statement());
    if (name) free(name);
    if (num) free(num);
    return blockNode;
}

ASTNode *program() {
    resetTokens();
    nextSymbol();
    ASTNode *programNode = createNode(NODE_PROGRAM, NULL);
    addChild(programNode, block());
    expect(PERIOD);
    return programNode;
}

