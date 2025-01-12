#include <stdio.h>
#include <stdlib.h>

#include "lexer.h"
#include "parser.h"
#include "symbol_table.h"
#include "scope.h"

void initScopeManager(ScopeManager *manager) {
    manager->currentScopeLevel = 0;
}

int enterScope(ScopeManager *manager) {
    if (manager->currentScopeLevel < MAX_SCOPE_LEVELS) {
        manager->scopeStack[manager->currentScopeLevel++] = manager->currentScopeLevel;
        return 0;
    } else {
        fprintf(stderr, "Error: Maximum scope levels exceeded\n");
        return -1;
    }
}

int exitScope(ScopeManager *manager) {
    if (manager->currentScopeLevel > 0) {
        manager->currentScopeLevel--;
        return 0;
    } else {
        fprintf(stderr, "Error: Scope underflow\n");
        return -1;
    }
}

void cleanupScopeManager(ScopeManager *manager) {
    while (manager->currentScopeLevel > 0) {
        exitScope(manager);
    }
    // if added allocated fields free them ..
}

int getCurrentScopeLevel(ScopeManager *manager) {
    return manager->currentScopeLevel;
}
