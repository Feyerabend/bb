

```
make clean
make
make samples
```

Now we have use for the grammar. In the parser, there are at least three key tasks being performed:
parsing the input, constructing an abstract syntax tree (AST), and managing a symbol table. Additionally,
the system includes basic error checking.

If we decouple the parsing logic from these other components, we end up with a simplified skeleton that looks
something like this:

```c
void factor() {
    if (accept(IDENT)) {
        ;
    } else if (accept(NUMBER)) {
        ;
    } else if (accept(LPAREN)) {
        expression();
        expect(RPAREN);
    } else {
        error("factor: syntax error");
        nextsym();
    }
}

void term() {
    factor();
    while (sym == TIMES| sym == SLASH) {
        nextsym();
        factor();
    }
}

void expression() {
    if (sym == PLUS || sym == MINUS)
        nextsym();
    term();
    while (sym == PLUS || sym == MINUS) {
        nextsym();
        term();
    }
}

void condition() {
    if (accept(ODDSYM)) {
        expression();
    } else {
        expression();
        if (sym == EQL || sym == NEQ || sym == LSS || sym == LEQ || sym == GTR || sym == GEQ) {
            nextsym();
            expression();
        } else {
            error("condition: invalid operator");
            nextsym();
        }
    }
}

void statement() {
    if (accept(IDENT)) {
        expect(BECOMES);
        expression();
    } else if (accept(CALLSYM)) {
        expect(IDENT);
    } else if (accept(BEGINSYM)) {
        do {
            statement();
        } while (accept(SEMICOLON));
        expect(ENDSYM);
    } else if (accept(IFSYM)) {
        condition();
        expect(THENSYM);
        statement();
    } else if (accept(WHILESYM)) {
        condition();
        expect(DOSYM);
        statement();
    } else {
        error("statement: syntax error");
        nextsym();
    }
}

void block() {
    if (accept(CONSTSYM)) {
        do {
            expect(IDENT);
            expect(EQL);
            expect(NUMBER);
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    if (accept(VARSYM)) {
        do {
            expect(IDENT);
        } while (accept(COMMA));
        expect(SEMICOLON);
    }
    while (accept(PROCSYM)) {
        expect(IDENT);
        expect(SEMICOLON);
        block();
        expect(SEMICOLON);
    }
    statement();
}

void program() {
    nextsym();
    block();
    expect(PERIOD);
}
```

