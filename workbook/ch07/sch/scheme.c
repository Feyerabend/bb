#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "scheme.h"
#include "memory.h"

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


Expr* create_number(int num) {
    return alloc_number(num);
}

Expr* create_symbol(const char *sym) {
    return alloc_symbol(sym);
}

Expr* create_cons(Expr *car, Expr *cdr) {
    return alloc_cons(car, cdr);
}


Expr* car(Expr *list) {
    if (list && list->type == LIST) {
        return list->value.pair.car;
    }
    fprintf(stderr, "Error: CAR called on non-list of type %d\n", list ? list->type : -1);
    return NULL;
}


Expr* cdr(Expr *list) {
    if (list && list->type == LIST) {
        return list->value.pair.cdr;
    }
    fprintf(stderr, "Error: CDR called on non-list of type %d\n", list ? list->type : -1);
    return NULL;
}

Expr* create_list(Expr **elements) {
    Expr *result = NULL;
    for (int i = 0; elements[i] != NULL; i++) {
        result = create_cons(elements[i], result);
    }
    return result;
}

Expr* create_builtin(Expr* (*func)(Expr **args, Env *env)) {
    return alloc_builtin(func);
}

Env* create_env(Env *parent) {
    Env *env = alloc_env(parent);

    env_set(env, "+", alloc_builtin(builtin_add));
    return env;
}



void env_set(Env *env, const char *name, Expr *value) {
    for (int i = 0; i < env->size; i++) {
        if (strcmp(env->names[i], name) == 0) {
            free_expr(env->values[i]); // Free the old value
            env->values[i] = value;    // Set the new value
            return;
        }
    }

    // Resize the names and values arrays
    env->names = realloc(env->names, sizeof(char *) * (env->size + 1));
    env->values = realloc(env->values, sizeof(Expr *) * (env->size + 1));

    if (!env->names || !env->values) {
        fprintf(stderr, "Error: Failed to (re)allocate memory for environment\n");
        exit(1);
    }

    // Add the new name and value
    env->names[env->size] = strdup(name);
    env->values[env->size] = value;
    env->size++;
}


Expr* env_get(Env *env, const char *name) {
    for (int i = 0; i < env->size; i++) {
        if (strcmp(env->names[i], name) == 0) {
            return env->values[i];
        }
    }
    if (env->parent) {
        return env_get(env->parent, name);
    }
    fprintf(stderr, "Error: Unbound variable '%s'\n", name);
    return NULL;
}

Expr* builtin_add(struct Expr **args, struct Env *env) {
    (void)env; // mark env as unused to avoid warnings
    int sum = 0;
    for (int i = 0; args[i] != NULL; i++) {
        if (args[i]->type != NUMBER) {
            fprintf(stderr, "Error: Arguments to + must be numbers\n");
            return NULL;
        }
        sum += args[i]->value.num;
    }
    return create_number(sum);
}


Expr **eval_args(Expr *args_list, Env *env) {
    int arg_count = 0;
    Expr *temp_args = args_list;

    while (temp_args != NULL && temp_args->type == LIST) {
        arg_count++;
        temp_args = cdr(temp_args);
    }

    if (arg_count == 0) {
        return NULL;
    }

    Expr **args = malloc(sizeof(Expr *) * (arg_count + 1)); // +1 for NULL terminator
    if (!args) {
        fprintf(stderr, "Memory allocation failed in eval_args\n");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < arg_count; i++) {
        args[i] = eval(car(args_list), env);
        args_list = cdr(args_list);
    }

    // NULL-terminate the argument list
    args[arg_count] = NULL;

    return args;
}


Expr* eval(Expr *expr, Env *env) {
    if (!expr) return NULL;

    switch (expr->type) {
        case NUMBER:
            return expr;

        case SYMBOL:
            return env_get(env, expr->value.sym);

        case LIST: {
            Expr *first = car(expr);
            if (first && first->type == SYMBOL) {

                // conditions
                if (strcmp(first->value.sym, "<") == 0) {
                    Expr *arg1 = eval(car(cdr(expr)), env);
                    Expr *arg2 = eval(car(cdr(cdr(expr))), env);
                    if (arg1 && arg2 && arg1->type == NUMBER && arg2->type == NUMBER) {
                        return create_number(arg1->value.num < arg2->value.num);
                    } else {
                        fprintf(stderr, "Error: Invalid arguments to <\n");
                        return NULL;
                    }

                } else if (strcmp(first->value.sym, ">") == 0) {
                    Expr *arg1 = eval(car(cdr(expr)), env);
                    Expr *arg2 = eval(car(cdr(cdr(expr))), env);
                    if (arg1 && arg2 && arg1->type == NUMBER && arg2->type == NUMBER) {
                        return create_number(arg1->value.num > arg2->value.num);
                    } else {
                        fprintf(stderr, "Error: Invalid arguments to >\n");
                        return NULL;
                    }

                } else if (strcmp(first->value.sym, "=") == 0) {
                    Expr *arg1 = eval(car(cdr(expr)), env);
                    Expr *arg2 = eval(car(cdr(cdr(expr))), env);
                    if (arg1 && arg2 && arg1->type == NUMBER && arg2->type == NUMBER) {
                        return create_number(arg1->value.num == arg2->value.num);
                    } else {
                        fprintf(stderr, "Error: Invalid arguments to =\n");
                        return NULL;
                    }

                } else if (strcmp(first->value.sym, "begin") == 0) {
                    Expr *current = cdr(expr);
                    Expr *result = NULL;
                
                    while (current != NULL && current->type == LIST) {
                        result = eval(car(current), env);
                        current = cdr(current);
                    }
                    return result;

                } else if (strcmp(first->value.sym, "quote") == 0) {
                    return car(cdr(expr));

                } else if (strcmp(first->value.sym, "eval") == 0) {
                    Expr *arg = eval(car(cdr(expr)), env);
                    return eval(arg, env);

                } else if (strcmp(first->value.sym, "if") == 0) {
                    Expr *condition = eval(car(cdr(expr)), env);
                    if (condition && condition->value.num != 0) {
                        return eval(car(cdr(cdr(expr))), env); // then
                    } else {
                        return eval(car(cdr(cdr(cdr(expr)))), env); // else
                    }

                } else if (strcmp(first->value.sym, "set!") == 0) {
                    const char *var_name = car(cdr(expr))->value.sym;
                    Expr *value_expr = eval(car(cdr(cdr(expr))), env);

                    Env *current_env = env;
                    while (current_env) {
                        for (int i = 0; i < current_env->size; i++) {
                            if (strcmp(current_env->names[i], var_name) == 0) {
                                free_expr(current_env->values[i]);
                                current_env->values[i] = value_expr;
                                return NULL;
                            }
                        }
                        current_env = current_env->parent;
                    }

                    fprintf(stderr, "Error: Unbound variable '%s' in set!\n", var_name);
                    return NULL;

                } else if (strcmp(first->value.sym, "let") == 0) {
                    Expr *bindings = car(cdr(expr));
                    Expr *body = cdr(cdr(expr));
                    Env *local_env = create_env(env);
                
                    printf("Evaluating let form:\n");
                
                    // Evaluate bindings
                    while (bindings != NULL && bindings->type == LIST) {
                        Expr *binding = car(bindings);
                        const char *var_name = car(binding)->value.sym;
                        Expr *value = eval(car(cdr(binding)), env);
                
                        printf("  Binding %s to ", var_name);
                        print_expr(value);
                        printf("\n");
                
                        env_set(local_env, var_name, value);
                
                        bindings = cdr(bindings);
                    }
                
                    // Evaluate body
                    Expr *result = NULL;
                    while (body != NULL && body->type == LIST) {
                        printf("  Evaluating body expression: ");
                        print_expr(car(body));
                        printf("\n");
                
                        result = eval(car(body), local_env);
                
                        printf("  Result: ");
                        print_expr(result);
                        printf("\n");
                
                        body = cdr(body);
                    }
                
                    printf("Let form result: ");
                    print_expr(result);
                    printf("\n");
                
                    free_env(local_env);
                    return result;

                } else if (strcmp(first->value.sym, "define") == 0) {
                    const char *var_name = car(cdr(expr))->value.sym;
                    Expr *value_expr = eval(car(cdr(cdr(expr))), env);
                    env_set(env, var_name, value_expr);
                    return NULL;

                } else if (strcmp(first->value.sym, "lambda") == 0) {
                    Expr *params = car(cdr(expr));
                    Expr *body = car(cdr(cdr(expr)));
                    Expr *lambda = create_cons(params, body);
                    lambda->type = FUNCTION; // mark as a function
                    return lambda;

                } else if (strcmp(first->value.sym, "while") == 0) {
                    Expr *condition = car(cdr(expr));
                    Expr *body = car(cdr(cdr(expr)));

                    while (1) {
                        Expr *cond_result = eval(condition, env);
                        if (!cond_result || cond_result->value.num == 0) {
                            break; // condition false
                        }
                        eval(body, env); // exec body
                    }
                    return NULL;

                } else if (strcmp(first->value.sym, "+") == 0) {
                    Expr **args = eval_args(cdr(expr), env);
                    return builtin_add(args, env);

                } else {

                    // func application
                    Expr *func = eval(first, env);
                    if (!func || func->type != FUNCTION) {
                        fprintf(stderr, "Error: Invalid function or function application\n");
                        return NULL;
                    }

                    // avoid applying car/cdr to a function
                    if (func->type == FUNCTION) {
                        fprintf(stderr, "Function found, avoiding car/cdr on function\n");
                    }

                    Expr **args = eval_args(cdr(expr), env);
                    return apply(func, args, env);
                }

            } else {
                fprintf(stderr, "Error: First element is not a valid symbol or function, type: %d\n", first ? first->type : -1);
                return NULL;
            }
        }

        case FUNCTION:
            return expr;

        case BUILTIN:
            return NULL; // expr;
    }

    return NULL;
}


Expr* apply(Expr *func, Expr **args, Env *env) {

    if (func->type == BUILTIN) {
        return func->value.builtin(args, env);

    } else if (func->type != FUNCTION) {
        fprintf(stderr, "Error: Not a function\n");
        return NULL;
    }

    // Function consists of parameter list + body
    Expr *params = car(func);
    Expr *body = cdr(func);
    Env *local_env = create_env(env);

    // Bind params to args in new env
    while (params != NULL && params->type == LIST && args != NULL) {
        const char *param_name = car(params)->value.sym;
        Expr *arg_value = *args;
        env_set(local_env, param_name, arg_value);

        params = cdr(params);
        args++;
    }

    if (params != NULL) {
        fprintf(stderr, "Error: Mismatched number of arguments in function call\n");
        return NULL;
    }

    // Eval body of function in new env
    return eval(body, local_env);
}


void print_expr(Expr *expr) {
    if (!expr) {
        printf("()");
        return;
    }

    switch (expr->type) {
        case NUMBER:
            printf("%d", expr->value.num);
            break;

        case SYMBOL:
            printf("%s", expr->value.sym);
            break;

        case LIST:
            printf("(");
            print_expr(expr->value.pair.car);
            Expr *cdr_expr = expr->value.pair.cdr;
            while (cdr_expr && cdr_expr->type == LIST) {
                printf(" ");
                print_expr(cdr_expr->value.pair.car);
                cdr_expr = cdr(cdr_expr);
            }
            if (cdr_expr) {
                printf(" . ");
                print_expr(cdr_expr);
            }
            printf(")");
            break;

        case FUNCTION:
            printf("<function>");
            break;

        case BUILTIN:
            printf("<builtin>");
            break;
    }
}


void print_env(Env *env) {
    if (!env) return;

    for (int i = 0; i < env->size; i++) {
        printf("%s = ", env->names[i]);
        print_expr(env->values[i]);
        printf("\n");
    }

    print_env(env->parent);
}


/*
	+, -, *, /
    and, or, not
    =, <, >, <=, >=
	null?, cons, car, cdr, list
	begin, (let)
	eq?, equal?, number?, pair?, symbol?
*/
