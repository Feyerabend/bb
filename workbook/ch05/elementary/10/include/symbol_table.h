#ifndef SYMBOL_TABLE_H
#define SYMBOL_TABLE_H

#include "lexer.h"

#define INITIAL_CAPACITY 10

typedef struct {
    int symbolID;
    char *name;
    Symbol type;
    int scopeLevel;
    union {
        int value;      // constants
        int address;    // variables and procedures
    } data;
} SymbolTableEntry;

typedef struct {
    SymbolTableEntry *entries;
    int size;
    int capacity;
} SymbolTable;

// -- symbols as strings --

typedef struct {
    Symbol symbol;
    const char *name;
} SymbolMapping;

static const SymbolMapping symbolTableNames[] = {
    {NOP, "NOP"},
    {IDENT, "IDENT"},
    {NUMBER, "NUMBER"},
    {LPAREN, "LPAREN"},
    {RPAREN, "RPAREN"},
    {TIMES, "TIMES"},
    {SLASH, "SLASH"},
    {PLUS, "PLUS"},
    {MINUS, "MINUS"},
    {EQL, "EQL"},
    {NEQ, "NEQ"},
    {LSS, "LSS"},
    {LEQ, "LEQ"},
    {GTR, "GTR"},
    {GEQ, "GEQ"},
    {CALLSYM, "CALLSYM"},
    {BEGINSYM, "BEGINSYM"},
    {SEMICOLON, "SEMICOLON"},
    {ENDSYM, "ENDSYM"},
    {IFSYM, "IFSYM"},
    {WHILESYM, "WHILESYM"},
    {BECOMES, "BECOMES"},
    {THENSYM, "THENSYM"},
    {DOSYM, "DOSYM"},
    {CONSTSYM, "CONSTSYM"},
    {COMMA, "COMMA"},
    {VARSYM, "VARSYM"},
    {PROCSYM, "PROCSYM"},
    {PERIOD, "PERIOD"},
    {ODDSYM, "ODDSYM"},
    {ENDOFFILE, "ENDOFFILE"}
};

extern int initSymbolTable();
int addSymbol(const char *name, Symbol type, int scopeLevel, int data);
int findSymbol(const char *name, int currentScopeLevel);
extern void freeSymbolTable();

extern void printSymbolTable();
extern void writeSymbolTableToFile(const char *filename);

#endif  // SYMBOL_TABLE_H