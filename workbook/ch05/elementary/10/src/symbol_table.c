#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "symbol_table.h"
#include "tokens.h"

static SymbolTable symbolTable = { NULL, 0, 0 };

static int nextID = 1; // start from 1! (0 can be reserved for invalid/no ID)

int generateUniqueID() {
    return nextID++;
}
void resetIDGenerator() {
    nextID = 1;
}

int initSymbolTable() {
    symbolTable.entries = malloc(INITIAL_CAPACITY * sizeof(SymbolTableEntry));
    if (!symbolTable.entries) {
        perror("Failed to initialize symbol table");
        return -1;
    }
    symbolTable.capacity = INITIAL_CAPACITY;
    symbolTable.size = 0;
    return 0;
}

int addSymbol(const char *name, Symbol type, int scopeLevel, int dataValueOrAddress) {
    if (symbolTable.size == symbolTable.capacity) {
        symbolTable.capacity *= 2;
        symbolTable.entries = realloc(symbolTable.entries, symbolTable.capacity * sizeof(SymbolTableEntry));
        if (!symbolTable.entries) {
            perror("Failed to reallocate symbol table");
            exit(1);
        }
    }

    // insert symbol entry
    int uid = generateUniqueID();
    symbolTable.entries[symbolTable.size].symbolID = uid;
    symbolTable.entries[symbolTable.size].name = strdup(name);
    symbolTable.entries[symbolTable.size].type = type;
    symbolTable.entries[symbolTable.size].scopeLevel = scopeLevel;  // current scope level

    // assign value or address
    if (type == CONSTSYM) {
        symbolTable.entries[symbolTable.size].data.value = dataValueOrAddress;
    } else {
        symbolTable.entries[symbolTable.size].data.address = dataValueOrAddress;
    }

    symbolTable.size++;

    return uid;
}

int findSymbol(const char *name, int currentScopeLevel) {
    for (int i = symbolTable.size - 1; i >= 0; i--) {
        if (strcmp(symbolTable.entries[i].name, name) == 0) {
            if (symbolTable.entries[i].scopeLevel <= currentScopeLevel) {
                return 1; // found in current or outer scope
            }
        }
    }
    return 0; // not found
}

int findSymbolAtLevel(const char *name, int level) {
    for (int i = 0; i < symbolTable.size; i++) {
        if (strcmp(symbolTable.entries[i].name, name) == 0 && symbolTable.entries[i].scopeLevel == level) {
            return i;  // found at the correct/assumed scope level
        }
    }
    return -1;  // not found
}

void freeSymbolTable() {
    if (symbolTable.entries) {
        for (int i = 0; i < symbolTable.size; i++) {
            free(symbolTable.entries[i].name);  // Free each symbol name
        }
        free(symbolTable.entries);  // Free the entries array
        symbolTable.entries = NULL;  // Reset to NULL to prevent double free
        symbolTable.size = 0;
        symbolTable.capacity = 0;
    }
}

const char *getSymbolName(Symbol type) {
    const int symbolTableNamesCount = sizeof(symbolTableNames) / sizeof(symbolTableNames[0]);
    for (size_t i = 0; i < symbolTableNamesCount; i++) {
        if (symbolTableNames[i].symbol == type) {
            return symbolTableNames[i].name;
        }
    }
    return "UNKNOWN";
}

void printSymbolTable() {
    for (int i = 0; i < symbolTable.size; i++) {
        printf("%s: %s (%d) [scope: %d, value/address: %d/%d]\n",
            getSymbolName((Symbol)symbolTable.entries[i].type),
            symbolTable.entries[i].name,
            symbolTable.entries[i].symbolID,
            symbolTable.entries[i].scopeLevel,
            symbolTable.entries[i].data.value,
            symbolTable.entries[i].data.address);
    }
}

void serializeSymbolTable(FILE *output) {
    fprintf(output, "[\n");
    for (int i = 0; i < symbolTable.size; i++) {
        fprintf(output, "  {\n");
        fprintf(output, "    \"uid\": \"%d\",\n", symbolTable.entries[i].symbolID);
        fprintf(output, "    \"name\": \"%s\",\n", symbolTable.entries[i].name);
        fprintf(output, "    \"type\": \"%s\",\n", getSymbolName((Symbol)symbolTable.entries[i].type));
        fprintf(output, "    \"scopeLevel\": %d,\n", symbolTable.entries[i].scopeLevel);
        fprintf(output, "    \"value\": %d,\n", symbolTable.entries[i].data.value);
        fprintf(output, "    \"address\": %d\n", symbolTable.entries[i].data.address);
        fprintf(output, "  }");
        if (i < symbolTable.size - 1) {
            fprintf(output, ",");
        }
        fprintf(output, "\n");
    }
    fprintf(output, "]\n");
}

void writeSymbolTableToFile(const char *filename) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Failed to open file");
        return;
    }
    serializeSymbolTable(file);
    fclose(file);
}
