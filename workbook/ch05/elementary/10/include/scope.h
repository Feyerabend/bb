#ifndef SCOPE_H
#define SCOPE_H

#define MAX_SCOPE_LEVELS 100

typedef struct {
    int scopeStack[MAX_SCOPE_LEVELS];
    int currentScopeLevel;
} ScopeManager;

extern ScopeManager manager; // decl of global scope manager

extern void initScopeManager(ScopeManager *manager);
extern void enterScope(ScopeManager *manager);
extern void exitScope(ScopeManager *manager);
extern int getCurrentScopeLevel(ScopeManager *manager);

#endif  // SCOPE_H