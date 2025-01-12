#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"
#include "lexer.h"
#include "parser.h"
#include "symbol_table.h"
#include "scope.h"


void processFile(const char* sourceFilename, const char* tokenFilename, const char* annotatedTokenFilename, const char* astFilename, const char* symbolFilename) {

    initParser();

//    initSymbolTable();
//    ScopeManager manager;
    

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
    traverseAST(root, 0);
    printSymbolTable();

    writeASTToJSON(root, astFilename);
    printf("ast saved to %s\n", astFilename);

    writeSymbolTableToFile(symbolFilename);
    printf("symbol table saved to %s\n", symbolFilename);

    if (root) {
        freeNode(root);
    }
    printf("done.\n");
}

int main(int argc, char* argv[]) {
    if (argc != 6) {
        fprintf(stderr, "Usage: %s <source-file> <token-output-file> <token-annotated-output-file> <ast-output-file> <symbol-table-output-dir> .. (%d)\n", argv[0], argc);
        return EXIT_FAILURE;
    }

    const char* sourceFile = argv[1];
    const char* tokenFile = argv[2];
    const char* annTokenFile = argv[3];
    const char* astFile = argv[4];
    const char* symbolFile = argv[5];

    processFile(sourceFile, tokenFile, annTokenFile, astFile, symbolFile);

    return EXIT_SUCCESS;
}
