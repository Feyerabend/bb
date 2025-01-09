#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"


void processFile(const char* sourceFilename, const char* tokenFilename, const char* astFilename, const char* symbolTableFilename) {
    printf("\nparsing file: %s ..\n", sourceFilename);

    printf("tokenizing input ..\n");
    int flag = fromSourceToTokens(sourceFilename, tokenFilename);
    if (flag) {
        printf("failed saving tokens to file %s.\n", tokenFilename);
    }
    printf("tokens written to %s.\n", tokenFilename);

    printf("done.\n");
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <source-file> <token-output-file> <ast-output-file> <symbol-table-output-file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char* sourceFile = argv[1];
    const char* tokenFile = argv[2];
    const char* astFile = argv[3];
    const char* symbolTableFile = argv[4];

    processFile(sourceFile, tokenFile, astFile, symbolTableFile);

    return EXIT_SUCCESS;
}

