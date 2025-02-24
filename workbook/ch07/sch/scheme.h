#ifndef SCHEME_H
#define SCHEME_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

typedef enum { NUMBER, SYMBOL, LIST, FUNCTION, BUILTIN } Type;

// fwd decl
struct Expr;
struct Env;


typedef struct Expr {
    Type type;
    union {
        int num;
        char *sym;
        struct {
            struct Expr *car;
            struct Expr *cdr;
        } pair;
        struct Expr* (*builtin)(struct Expr **args, struct Env *env); // Use struct tags
    } value;
} Expr;


typedef struct Env {
    struct Env *parent;
    char **names;
    Expr **values;
    int size;
} Env;

// fwd decl
Expr* create_number(int num);
Expr* create_symbol(const char *sym);
Expr* create_cons(Expr *car, Expr *cdr);
Expr* car(Expr *list);
Expr* cdr(Expr *list);
Expr* create_list(Expr **elements);
Env* create_env(Env *parent);
void env_set(Env *env, const char *name, Expr *value);
Expr* env_get(Env *env, const char *name);
Expr* builtin_add(struct Expr **args, struct Env *env);
Expr* eval(Expr *expr, Env *env);
Expr* apply(Expr *func, Expr **args, Env *env);
void print_expr(Expr *expr);
void print_env(Env *env);

extern void free_expr(Expr *expr);
extern void free_env(Env *env);

#endif // SCHEME_H