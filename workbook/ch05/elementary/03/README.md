
## Abstract Syntax Tree (AST)

__Build__

```shell
make clean
make
make samples
```

The provided code fragments illustrate the basic structure of a simple recursive descent parser for a
language close to PL/0. The parser builds an *Abstract Syntax Tree* (AST) while parsing the program's
input according to the language's grammar.

__1. Parser Workflow__

The parser reads the tokenised input and processes it using a series of functions corresponding to
various grammar rules. Each function tries to match a specific pattern in the language's grammar.
If a match is found, the parser consumes the matching token and proceeds. If no match is found,
an error is raised. (A very rudimentary error check.)

__2. AST Construction__

Each grammar rule corresponds to creating a node in the abstract syntax tree (AST). This tree represents
the structure of the parsed input, reflecting the program's syntactic structure. Each node in the
tree contains information about the language construct it represents (e.g. expressions, statements,
terms, etc.).

__3. Expected Output__

The parser is expected to construct an AST, where each node represents a construct in the source
language. The program's top-level node is a NODE_PROGRAM, and this root node's child would be a
NODE_BLOCK, which holds the core of the program (e.g. variable declarations, statements, and
procedure calls).


### Adding Context and Completing the Code

The provided snippets show functions that handle individual components of the grammar, such as
parsing factors, terms, expressions, statements, conditions, and blocks. The parser builds the
AST incrementally, starting from the root and breaking the input down into smaller components.


#### Main Parser Functions and AST Construction


__`program()`__

This function is the entry point for parsing the program. It initializes the parsing process and
creates the root of the AST.

```c
ASTNode *program() {
    resetTokens();              // reset token buffer (e.g. prepare lexer)
    nextSymbol();               // move to the next symbol (token)
    
    ASTNode *programNode = createNode(NODE_PROGRAM, NULL);  // create the root AST node (program)
    
    addChild(programNode, block());  // parse the block (which includes statements, variable declarations, etc.)
    
    expect(PERIOD);              // expect the period at the end of the program
    return programNode;          // return the constructed AST for the program
}
```

__`block()`__

A block is a key structure in the language (similar to a function or procedure scope).
It can contain constant declarations, variable declarations, procedure declarations,
and a list of statements.

```c
ASTNode *block() {
    ASTNode *blockNode = createNode(NODE_BLOCK, NULL);

    // parse constant declarations
    if (accept(CONSTSYM)) {
        do {
            expect(IDENT);       // expect an identifier (constant name)
            expect(EQL);         // expect equality symbol (=)
            expect(NUMBER);      // expect a number (constant value)
        } while (accept(COMMA)); // allow comma-separated constants
        expect(SEMICOLON);       // end of constants declaration
    }

    // parse variable declarations
    if (accept(VARSYM)) {
        do {
            expect(IDENT);       // expect an identifier (variable name)
        } while (accept(COMMA)); // allow comma-separated variables
        expect(SEMICOLON);       // end of variables declaration
    }

    // parse procedure declarations (recursive)
    while (accept(PROCSYM)) {
        expect(IDENT);            // expect a procedure name
        expect(SEMICOLON);        // expect a semicolon before the body of the procedure
        blockNode->children.push_back(block()); // recursively add the procedure's block
        expect(SEMICOLON);        // end of procedure declaration
    }

    // parse the statement(s) in the block
    statement();  // a block always ends with at least one statement

    return blockNode;  // return the created AST node for the block
}
```


__`statement()`__

A statement is an action that the program performs, such as assignments, calls, conditionals, and loops.

```c
ASTNode *statement() {
    ASTNode *stmtNode = createNode(NODE_STATEMENT, NULL);
    
    if (accept(IDENT)) {
        expect(BECOMES);       // expect the assignment operator ":="
        stmtNode->children.push_back(expression()); // parse the right-hand side expression
    } else if (accept(CALLSYM)) {
        expect(IDENT);         // expect an identifier (procedure name)
        stmtNode->type = NODE_CALL;
    } else if (accept(BEGINSYM)) {
        // handle compound statement (block of statements)
        do {
            stmtNode->children.push_back(statement());
        } while (accept(SEMICOLON));
        expect(ENDSYM);        // expect 'END' to close the block
    } else if (accept(IFSYM)) {
        // handle if-else condition
        condition();
        expect(THENSYM);
        stmtNode->children.push_back(statement());
    } else if (accept(WHILESYM)) {
        // handle while loop
        condition();
        expect(DOSYM);
        stmtNode->children.push_back(statement());
    } else {
        error("statement: syntax error");
        nextSymbol();
        return NULL;
    }

    return stmtNode;  // return the constructed statement node
}
```


__`expression() and term()`__

These functions handle arithmetic expressions and their components (like terms and factors).

```c
ASTNode *expression() {
    ASTNode *exprNode = createNode(NODE_EXPRESSION, NULL);
    
    if (sym == PLUS || sym == MINUS) {
        nextSymbol();  // handle unary plus or minus
    }
    
    exprNode->children.push_back(term());  // start with a term
    
    // continue with additional terms for the expression (addition or subtraction)
    while (sym == PLUS || sym == MINUS) {
        nextSymbol();
        exprNode->children.push_back(term());
    }
    
    return exprNode;
}

ASTNode *term() {
    ASTNode *termNode = createNode(NODE_TERM, NULL);
    termNode->children.push_back(factor());  // a term starts with a factor

    // continue with multiplication or division if necessary
    while (sym == TIMES || sym == SLASH) {
        nextSymbol();
        termNode->children.push_back(factor());
    }

    return termNode;
}
```


__`factor()`__

This function parses the basic building blocks of an expression, like numbers, variables, or sub-expressions in parentheses.

```c
ASTNode *factor() {
    ASTNode *factorNode;
    char *temp = strdup(buf);  // small memory leak: duplicate the string for the identifier or number

    if (accept(IDENT)) {
        factorNode = createNode(NODE_IDENTIFIER, temp);  // create a node for an identifier
    } else if (accept(NUMBER)) {
        factorNode = createNode(NODE_NUMBER, temp);  // create a node for a number
    } else if (accept(LPAREN)) {
        factorNode = expression();  // handle parenthesized expressions
        expect(RPAREN);
    } else {
        error("factor: syntax error");
        nextSymbol();  // move to the next symbol on error
        return NULL;
    }

    return factorNode;  // return the created factor node
}
```

### AST Nodes
- NODE_PROGRAM: Represents the entire program.
- NODE_BLOCK: Represents the body of the program, which can include declarations and statements.
- NODE_STATEMENT: Represents a single statement, such as an assignment or a function call.
- NODE_EXPRESSION: Represents an expression, including terms and factors.
- NODE_IDENTIFIER: Represents a variable or function identifier.
- NODE_NUMBER: Represents a constant number.
- NODE_CALL: Represents a procedure call.


### Conclusion

This parser, designed with recursive descent, processes the tokens generated from a lexer and
builds an Abstract Syntax Tree (AST) representing the structure of the program. Each function
in the parser corresponds to a specific rule in the grammar, and the tree nodes represent language
constructs like variables, expressions, statements, and blocks. The parser constructs this tree
step-by-step by recursively calling the appropriate parsing functions and building the corresponding
AST nodes.
