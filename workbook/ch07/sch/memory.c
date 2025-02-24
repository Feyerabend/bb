#include <stdlib.h>
#include <string.h>

#include "memory.h"

// generic expr
Expr* alloc_expr() {
    Expr *expr = malloc(sizeof(Expr));
    if (!expr) {
        fprintf(stderr, "Error: Failed to allocate memory for expression\n");
        exit(1);
    }
    return expr;
}

// number expr
Expr* alloc_number(int num) {
    Expr *expr = alloc_expr();
    expr->type = NUMBER;
    expr->value.num = num;
    return expr;
}

// symbol expr
Expr* alloc_symbol(const char *sym) {
    Expr *expr = alloc_expr();
    expr->type = SYMBOL;
    expr->value.sym = strdup(sym);
    if (!expr->value.sym) {
        fprintf(stderr, "Error: Failed to allocate memory for symbol\n");
        exit(1);
    }
    return expr;
}

// cons expr
Expr* alloc_cons(Expr *car, Expr *cdr) {
    Expr *expr = alloc_expr();
    expr->type = LIST;
    expr->value.pair.car = car;
    expr->value.pair.cdr = cdr;
    return expr;
}

// builtin expr
Expr* alloc_builtin(Expr* (*func)(Expr **args, Env *env)) {
    Expr *expr = alloc_expr();
    expr->type = BUILTIN;
    expr->value.builtin = func;
    return expr;
}

// alloc environment
Env* alloc_env(Env *parent) {
    Env *env = malloc(sizeof(Env));
    if (!env) {
        fprintf(stderr, "Error: Failed to allocate memory for environment\n");
        exit(1);
    }

    env->parent = parent;
    env->names = NULL;
    env->values = NULL;
    env->size = 0;
    return env;
}

// free expression
void free_expr(Expr *expr) {
    if (!expr) return;

    switch (expr->type) {
        case NUMBER:
            break;

        case SYMBOL:
            free(expr->value.sym);
            break;

        case LIST:
        case FUNCTION:
            free_expr(expr->value.pair.car);
            free_expr(expr->value.pair.cdr);
            break;

        case BUILTIN:
            break;
    }

    free(expr);
}

// free environment
void free_env(Env *env) {
    if (!env) return;

    for (int i = 0; i < env->size; i++) {
        free(env->names[i]);
        free_expr(env->values[i]);
    }

    free(env->names);
    free(env->values);
    free_env(env->parent);

    free(env);
}

// mark an expression for garbage collection
void gc_mark_expr(Expr *expr) {
    (void)expr;
    // TODO: marking for garbage collection
}

// mark an environment for garbage collection
void gc_mark_env(Env *env) {
    (void)env;
    // TODO: marking for garbage collection
}

// perform garbage collection
void gc_collect() {
    // TODO
}
