#ifndef MEMORY_H
#define MEMORY_H

#include "scheme.h"

// alloc
Expr* alloc_expr();
Expr* alloc_number(int num);
Expr* alloc_symbol(const char *sym);
Expr* alloc_cons(Expr *car, Expr *cdr);
Expr* alloc_builtin(Expr* (*func)(Expr **args, Env *env));
Env* alloc_env(Env *parent);

// dealloc
void free_expr(Expr *expr);
void free_env(Env *env);

// gc hooks
void gc_mark_expr(Expr *expr);
void gc_mark_env(Env *env);
void gc_collect();

#endif // MEMORY_H
