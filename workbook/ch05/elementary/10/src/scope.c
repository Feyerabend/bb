#include <stdio.h>
#include <stdlib.h>

#include "lexer.h"
#include "parser.h"
#include "symbol_table.h"
#include "scope.h"

void initScopeManager(ScopeManager *manager) {
    manager->currentScopeLevel = 0;
}

void enterScope(ScopeManager *manager) {
    if (manager->currentScopeLevel < MAX_SCOPE_LEVELS) {
        manager->scopeStack[manager->currentScopeLevel++] = manager->currentScopeLevel;
    } else {
        printf("Error: Maximum scope levels exceeded\n");
        exit(1);  // or handle error more gracefully
    }
}

void exitScope(ScopeManager *manager) {
    if (manager->currentScopeLevel > 0) {
        manager->currentScopeLevel--;
    } else {
        printf("Error: Scope underflow\n");
        exit(1);  // or handle error more gracefully
    }
}

int getCurrentScopeLevel(ScopeManager *manager) {
    return manager->currentScopeLevel;
}
