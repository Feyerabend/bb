#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "tokens.h"

#define MAX_TOKENS 1000
#define MAX_SYM_LEN 128

typedef struct {
    Symbol type;
    char value[MAX_SYM_LEN];  // store the value of the token (such as identifier or number) < 128
    int line;                 // line number where the token was found
    int column;               // column number where the token was found
} Token;

// global array of tokens
Token tokens[MAX_TOKENS];
int currentTokenIndex = 0;
int totalTokens = 0;

// read tokenized file and populate token array
void readTokens(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open tokenized file %s\n", filename);
        exit(1);
    }

    char tokenType[MAX_SYM_LEN];
    int line = 1;  // start line
    int column = 1;  // start column

    while (fscanf(file, "%s", tokenType) != EOF) {
        // init token with line and column info
        Token token = { NOP, "", line, column };

        if (strcmp(tokenType, "IDENT") == 0) {
            token.type = IDENT;
            fscanf(file, "%s", token.value);
        } else if (strcmp(tokenType, "NUMBER") == 0) {
            token.type = NUMBER;
            fscanf(file, "%s", token.value);
        } else if (strcmp(tokenType, "LPAREN") == 0) {
            token.type = LPAREN;
        } else if (strcmp(tokenType, "RPAREN") == 0) {
            token.type = RPAREN;
        } else if (strcmp(tokenType, "TIMES") == 0) {
            token.type = TIMES;
        } else if (strcmp(tokenType, "SLASH") == 0) {
            token.type = SLASH;
        } else if (strcmp(tokenType, "PLUS") == 0) {
            token.type = PLUS;
        } else if (strcmp(tokenType, "MINUS") == 0) {
            token.type = MINUS;
        } else if (strcmp(tokenType, "EQL") == 0) {
            token.type = EQL;
        } else if (strcmp(tokenType, "NEQ") == 0) {
            token.type = NEQ;
        } else if (strcmp(tokenType, "LSS") == 0) {
            token.type = LSS;
        } else if (strcmp(tokenType, "LEQ") == 0) {
            token.type = LEQ;
        } else if (strcmp(tokenType, "GTR") == 0) {
            token.type = GTR;
        } else if (strcmp(tokenType, "GEQ") == 0) {
            token.type = GEQ;
        } else if (strcmp(tokenType, "CALLSYM") == 0) {
            token.type = CALLSYM;
        } else if (strcmp(tokenType, "BEGINSYM") == 0) {
            token.type = BEGINSYM;
        } else if (strcmp(tokenType, "SEMICOLON") == 0) {
            token.type = SEMICOLON;
        } else if (strcmp(tokenType, "ENDSYM") == 0) {
            token.type = ENDSYM;
        } else if (strcmp(tokenType, "IFSYM") == 0) {
            token.type = IFSYM;
        } else if (strcmp(tokenType, "WHILESYM") == 0) {
            token.type = WHILESYM;
        } else if (strcmp(tokenType, "BECOMES") == 0) {
            token.type = BECOMES;
        } else if (strcmp(tokenType, "THENSYM") == 0) {
            token.type = THENSYM;
        } else if (strcmp(tokenType, "DOSYM") == 0) {
            token.type = DOSYM;
        } else if (strcmp(tokenType, "CONSTSYM") == 0) {
            token.type = CONSTSYM;
        } else if (strcmp(tokenType, "COMMA") == 0) {
            token.type = COMMA;
        } else if (strcmp(tokenType, "VARSYM") == 0) {
            token.type = VARSYM;
        } else if (strcmp(tokenType, "PROCSYM") == 0) {
            token.type = PROCSYM;
        } else if (strcmp(tokenType, "PERIOD") == 0) {
            token.type = PERIOD;
        } else if (strcmp(tokenType, "ODDSYM") == 0) {
            token.type = ODDSYM;
        } else if (strcmp(tokenType, "ENDOFLINE") == 0) {
            token.type = ENDOFLINE;
        } else {
            token.type = NOP;
        }

        // add token to array
        tokens[totalTokens++] = token;

        // update column count
        // assumes space or newline after token
        column += strlen(token.value) + 1;

        // check if need to increment line number
        // ENDOFLINE really only used here
        if (token.type == ENDOFLINE) {
            line++;
            column = 1; // reset column on new line
        }
    }
    fclose(file);
}

// get next token
Token nextToken() {
    if (currentTokenIndex < totalTokens) {
        return tokens[currentTokenIndex++];
    } else {
        // return an end-of-file token with no line/column info
        Token endToken = { ENDOFFILE, "", 0, 0 };
        return endToken;
    }
}

// used by main
int readTokensFromFile(const char *tokenFilename) {
    readTokens(tokenFilename);
    return 0; // future check
}

// used by main
void printTokens() {
    Token token;
    while ((token = nextToken()).type != ENDOFFILE) {
        printf("Token: %d, Value: %s, Line: %d, Column: %d\n", 
            token.type, token.value, token.line, token.column);
    }
}