
## Errors

__1. Define Return Codes__

Create a set of standardized return codes as an enum to make error handling consistent and readable.

```c
typedef enum {
    SUCCESS = 0,          // Operation successful
    ERR_ALLOCATION = 1,   // Memory allocation error
    ERR_FILE = 2,         // File operation error
    ERR_OVERFLOW = 3,     // Overflow (e.g., unique ID, scope levels)
    ERR_NOT_FOUND = 4,    // Symbol not found
    ERR_INVALID = 5,      // Invalid input or state
} ReturnCode;
```

__2. Modify Functions to Return ReturnCode__

Update the functions to return meaningful error codes instead of exiting or printing directly. Functions
like initSymbolTable, addSymbol, and writeSymbolTableToFile should propagate errors.

Example 1: Handling Allocation Errors

```c
ReturnCode initSymbolTable() {
    symbolTable.entries = malloc(INITIAL_CAPACITY * sizeof(SymbolTableEntry));
    if (!symbolTable.entries) {
        return ERR_ALLOCATION;  // return error code
    }
    symbolTable.capacity = INITIAL_CAPACITY;
    symbolTable.size = 0;
    return SUCCESS;
}
```

__Example 2: Adding a Symbol__

```c
ReturnCode addSymbol(const char *name, Symbol type, int scopeLevel, int dataValueOrAddress, int *outUID) {
    if (symbolTable.size == symbolTable.capacity) {
        void *newEntries = realloc(symbolTable.entries, symbolTable.capacity * 2 * sizeof(SymbolTableEntry));
        if (!newEntries) {
            return ERR_ALLOCATION;  // return error code
        }
        symbolTable.entries = newEntries;
        symbolTable.capacity *= 2;
    }

    int uid = generateUniqueID();
    if (outUID) *outUID = uid;

    symbolTable.entries[symbolTable.size].symbolID = uid;
    symbolTable.entries[symbolTable.size].name = strdup(name);
    if (!symbolTable.entries[symbolTable.size].name) {
        return ERR_ALLOCATION;  // strdup failure
    }
    symbolTable.entries[symbolTable.size].type = type;
    symbolTable.entries[symbolTable.size].scopeLevel = scopeLevel;

    if (type == CONSTSYM) {
        symbolTable.entries[symbolTable.size].data.value = dataValueOrAddress;
    } else {
        symbolTable.entries[symbolTable.size].data.address = dataValueOrAddress;
    }

    symbolTable.size++;
    return SUCCESS;
}
```

__Example 3: Writing to a File__

```c
ReturnCode writeSymbolTableToFile(const char *filename) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        return ERR_FILE;  // file open error
    }

    serializeSymbolTable(file);

    if (fclose(file) != 0) {
        return ERR_FILE;  // file close error
    }
    return SUCCESS;
}
```

__3. Centralized Error Handling__

Create a helper function to interpret and act on return codes,
such as logging errors or performing cleanup.

```c
void handleError(ReturnCode code, const char *context) {
    switch (code) {
        case SUCCESS:
            break;  // no error
        case ERR_ALLOCATION:
            fprintf(stderr, "Error in %s: Memory allocation failed.\n", context);
            break;
        case ERR_FILE:
            fprintf(stderr, "Error in %s: File operation failed.\n", context);
            break;
        case ERR_OVERFLOW:
            fprintf(stderr, "Error in %s: Overflow occurred.\n", context);
            break;
        case ERR_NOT_FOUND:
            fprintf(stderr, "Error in %s: Symbol not found.\n", context);
            break;
        case ERR_INVALID:
            fprintf(stderr, "Error in %s: Invalid input or state.\n", context);
            break;
        default:
            fprintf(stderr, "Error in %s: Unknown error.\n", context);
            break;
    }
}
```

__4. Propagate Errors Consistently__

Update higher-level functions to check for errors from lower-level functions and
propagate them upwards if necessary.

Example: Initializing the Symbol Table and Handling Errors

```c
ReturnCode initializeSystem() {
    ReturnCode rc;

    rc = initSymbolTable();
    if (rc != SUCCESS) {
        handleError(rc, "initSymbolTable");
        return rc;
    }

    resetIDGenerator();
    return SUCCESS;
}
```

__5. Use Return Codes in the Main Logic__

Centralise error handling in the main workflow or key entry points.

```c
int main() {
    ReturnCode rc = initializeSystem();
    if (rc != SUCCESS) {
        handleError(rc, "initializeSystem");
        return rc;
    }

    int uid;
    rc = addSymbol("x", VARSYM, 0, 0, &uid);
    if (rc != SUCCESS) {
        handleError(rc, "addSymbol");
        return rc;
    }

    rc = writeSymbolTableToFile("symbol_table.json");
    if (rc != SUCCESS) {
        handleError(rc, "writeSymbolTableToFile");
        return rc;
    }

    freeSymbolTable();
    return 0;
}
```

__6. Logging and Debugging__

To enhance debugging, you can log errors to a file or provide detailed output during development.

```c
void logErrorToFile(ReturnCode code, const char *context, const char *logFile) {
    FILE *file = fopen(logFile, "a");
    if (!file) {
        perror("Error opening log file");
        return;
    }

    fprintf(file, "Error in %s: %d\n", context, code);
    fclose(file);
}
```

Benefits
- Consistency: All functions handle errors in a uniform way.
- Readability: Clear and standardised return codes.
- Scalability: Easy to add new error types or improve error handling without changing all functions.
- Debugging: Centralised error logging aids debugging and maintenance.
