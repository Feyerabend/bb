#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"
#include "lexer.h"
#include "parser.h"
#include "ast.h"
#include "symbol_table.h"
#include "tac.h"


void processFile(const char* sourceFilename, const char* tokenFilename, const char* annotatedTokenFilename,
        const char* astFilename, const char* symbolFilename, const char* tacFilename) {

    printf("\nparsing file: %s ..\n", sourceFilename);

    // tokenisation / lexical analysis
    printf("tokenizing input ..\n");
    int flag = fromSourceToTokens(sourceFilename, tokenFilename);
    if (flag) {
        printf("failed saving tokens to file %s.\n", tokenFilename);
    }
    printf("tokens written to %s.\n", tokenFilename);

    // read tokens from file
    printf("read tokens from %s.\n", tokenFilename);
    flag = readTokensFromFile(tokenFilename);
    if (flag) {
        printf("failed reading tokens from file %s.\n", tokenFilename);
    }
    printTokens(); // DEBUG

    // read tokens with annotations in the form of where in source file
    flag = saveTokensToJson(annotatedTokenFilename);
    if (flag) {
        printf("failed to save annotated tokens to file %s.\n", annotatedTokenFilename);
    }
    printf("annotated tokens saved to %s\n", annotatedTokenFilename);

    ASTNode *root = program();
    if (!root) {
        fprintf(stderr, "Error: failed to parse program\n");
        return;
    }
    writeASTToJSON(root, astFilename);
    printf("ast saved to %s\n", astFilename);

    buildSymbolTable(root);
    traverseAST(root, 0);
    printSymbolTable();
    saveSymbolTable(symbolFilename);
    printf("symbol table saved to %s\n", symbolFilename);

    // genTAC(root);
    generateTAC(root, "main");
 //   printTAC(tacFilename);
    printTAC(NULL);

    // export TAC to file
    exportTAC(tacFilename);
    printf("tac saved to %s\n", tacFilename);
    // free TAC


    // read TAC from file
    parseTAC(tacFilename);

    // free at last
    freeTAC();
    freeSymbolTable();
    if (root) {
        freeNode(root);
    }
    printf("done.\n");
}

int main(int argc, char* argv[]) {
    if (argc != 7) {
        fprintf(stderr, "Usage: %s <source-file> <token-output-file> <token-annotated-output-file> <ast-output-file> <symbol-table-output-file> <tac-output-file> .. (%d)\n", argv[0], argc);
        return EXIT_FAILURE;
    }

    const char* sourceFile = argv[1];
    const char* tokenFile = argv[2];
    const char* annTokenFile = argv[3];
    const char* astFile = argv[4];
    const char* symbolFile = argv[5];
    const char* tacFile = argv[6];

    processFile(sourceFile, tokenFile, annTokenFile, astFile, symbolFile, tacFile);

    return EXIT_SUCCESS;
}
