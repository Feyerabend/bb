#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"

int isReserved(const char *word) {
    return
        strcmp(word, "begin") == 0 ||
        strcmp(word, "end") == 0 || 
        strcmp(word, "while") == 0 ||
        strcmp(word, "if") == 0 || 
        strcmp(word, "then") == 0 ||
        strcmp(word, "do") == 0 || 
        strcmp(word, "var") == 0 ||
        strcmp(word, "const") == 0 || 
        strcmp(word, "procedure") == 0;
}

const char* symbolToString(int symb) {
    switch (symb) {
        case EQL:
            return "=";
        case LSS:
            return "<";
        case GTR:
            return ">";
        case GEQ:
            return ">=";
        case LEQ:
            return "<=";
        case NEQ:
            return "#";
        default:
            return "Unknown symbol";
    }
}

void printsymbol(Symbol s, char *buf) {

    static const char *symbolNames[] = {
        [NOP] = "NOP",
        [IDENT] = "IDENT",
        [NUMBER] = "NUMBER",
        [LPAREN] = "LPAREN",
        [RPAREN] = "RPAREN",
        [TIMES] = "TIMES",
        [SLASH] = "SLASH",
        [PLUS] = "PLUS",
        [MINUS] = "MINUS",
        [EQL] = "EQL",
        [NEQ] = "NEQ",
        [LSS] = "LSS",
        [LEQ] = "LEQ",
        [GTR] = "GTR",
        [GEQ] = "GEQ",
        [CALLSYM] = "CALLSYM",
        [BEGINSYM] = "BEGINSYM",
        [SEMICOLON] = "SEMICOLON",
        [ENDSYM] = "ENDSYM",
        [IFSYM] = "IFSYM",
        [WHILESYM] = "WHILESYM",
        [BECOMES] = "BECOMES",
        [THENSYM] = "THENSYM",
        [DOSYM] = "DOSYM",
        [CONSTSYM] = "CONSTSYM",
        [COMMA] = "COMMA",
        [VARSYM] = "VARSYM",
        [PROCSYM] = "PROCSYM",
        [PERIOD] = "PERIOD",
        [ODDSYM] = "ODDSYM",
        [ENDOFFILE] = "ENDOFFILE"
    };

    // Print the symbol name
    if (s >= 0 && s < sizeof(symbolNames) / sizeof(symbolNames[0])) {
        if (s == IDENT || s == NUMBER) {
            printf("%s \"%s\"\n", symbolNames[s], buf); // value for IDENT/NUMBER
        } else {
            printf("%s\n", symbolNames[s]); // symbol name for others
        }
    } else {
        printf("Unknown symbol: %d\n", s); // unexpected symbols
    }
}
