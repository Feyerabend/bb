#ifndef TAC_H
#define TAC_H

#include "ast.h"

typedef struct TAC {
    char *op;
    char *arg1;
    char *arg2;
    char *result;
    struct TAC *next;
} TAC;

extern void exportTAC(const char *filename);
extern char *genTAC(ASTNode *node);
extern char *generateTAC(ASTNode *node, const char* proc_name);
extern void printTAC(const char *filename);
extern void freeTAC();

extern void parseTAC(const char *filename) ;

#endif  // TAC_H
