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

int recognize(Symbol s) {
    if (symbol == s) {
        return TRUE;
    } else {
        return FALSE;
    }
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
    if (recognize(IDENT)) {
        ASTNode *node = createNode(NODE_IDENTIFIER, strdup(buf), 0);
        nextSymbol();
        return node;
    } else if (recognize(NUMBER)) {
        ASTNode *node = createNode(NODE_NUMBER, strdup(buf), 0);
        nextSymbol();
        return node;
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
        ASTNode *opNode = createNode(NODE_TERM, op, 0);
        addChild(opNode, node);          // left child is the current term
        addChild(opNode, factor());      // right child is the next factor
        node = opNode;                   // update node to the new operator node
    }
    return node;
}

ASTNode *expression() {
    ASTNode *node = createNode(NODE_EXPRESSION, NULL, 0);
    if (symbol == PLUS || symbol == MINUS) {
        addChild(node, createNode(NODE_OPERATOR, symbol == PLUS ? "+" : "-", 0));
        nextSymbol();
    }
    addChild(node, term());
    while (symbol == PLUS || symbol == MINUS) {
        ASTNode *opNode = createNode(NODE_OPERATOR, symbol == PLUS ? "+" : "-", 0);
        nextSymbol();
        addChild(opNode, node);
        addChild(opNode, term());
        node = opNode;
    }
    return node;
}

ASTNode *condition() {
    if (accept(ODDSYM)) {
        ASTNode *node = createNode(NODE_CONDITION, "ODD", 0);
        addChild(node, expression());
        return node;
    } else if (accept(LPAREN)) { // enforce parentheses
        ASTNode *leftExpr = expression();
        if (symbol == EQL || symbol == NEQ || symbol == LSS || symbol == LEQ || symbol == GTR || symbol == GEQ) {
            ASTNode *node = createNode(NODE_CONDITION, symbolToString(symbol), 0);
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
    if (recognize(IDENT)) {
        ASTNode *assignNode = createNode(NODE_ASSIGNMENT, strdup(buf), 0);
        nextSymbol();
        expect(BECOMES);
        addChild(assignNode, expression());
        return assignNode;
    } else if (accept(CALLSYM)) {
        ASTNode *node = createNode(NODE_CALL, strdup(buf), 0); // name
        expect(IDENT);
        return node;
    } else if (accept(BEGINSYM)) {
        ASTNode *beginNode = createNode(NODE_BEGIN, NULL, 0);
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
        ASTNode *ifNode = createNode(NODE_IF, NULL, 0);
        addChild(ifNode, condition());
        expect(THENSYM);
        addChild(ifNode, statement());
        return ifNode;
    } else if (accept(WHILESYM)) {
        ASTNode *whileNode = createNode(NODE_WHILE, NULL, 0);
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
    ASTNode *blockNode = createNode(NODE_BLOCK, NULL, 0);
    if (accept(CONSTSYM)) {
        do {
            expect(IDENT);
            ASTNode *constNode = createNode(NODE_CONST_DECL, strdup(buf), 0); // name
            expect(EQL);
            addChild(constNode, createNode(NODE_NUMBER, strdup(buf), 0)); // number
            expect(NUMBER);
            addChild(blockNode, constNode);
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    if (accept(VARSYM)) {
        do {
            addChild(blockNode, createNode(NODE_VAR_DECL, strdup(buf), 0)); // name
            expect(IDENT);
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    while (accept(PROCSYM)) {
        ASTNode *procNode = createNode(NODE_PROC_DECL, strdup(buf), 0);
        expect(IDENT);
        expect(SEMICOLON);
        addChild(procNode, block());
        addChild(blockNode, procNode);
        expect(SEMICOLON);
    }
    addChild(blockNode, statement());
    return blockNode;
}

ASTNode *program() {
    resetTokens();
    nextSymbol();
    ASTNode *programNode = createNode(NODE_PROGRAM, NULL, 0);
    addChild(programNode, block());
    expect(PERIOD);
    return programNode;
}

