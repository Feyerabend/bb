#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tokens.h"


void processFile(const char* sourceFilename, const char* tokenFilename) {
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
        fprintf(stderr, "Usage: %s <source-file> <token-output-file> .. (%d)\n", argv[0], argc);
        return EXIT_FAILURE;
    }

    const char* sourceFile = argv[1];
    const char* tokenFile = argv[2];

    processFile(sourceFile, tokenFile);

    return EXIT_SUCCESS;
}
