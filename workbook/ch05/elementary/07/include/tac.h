#ifndef TAC_H
#define TAC_H

typedef struct TAC {
    char op[16];          // operation (e.g. "+", "-", "=", "CALL")
    char arg1[16];        // first argument
    char arg2[16];        // second argument (if applicable)
    char result[16];      // result
    struct TAC *next;     // linked list TAC instructions
} TAC;

//extern void generateTAC(ASTNode *node);
extern char *generateTAC(ASTNode *node);
extern void printTAC();


#endif  // TAC_H
