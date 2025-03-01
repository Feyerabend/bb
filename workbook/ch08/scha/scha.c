#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define DEBUG(msg, ...) printf("[DEBUG] " msg "\n", ##__VA_ARGS__)


typedef enum {
    TYPE_NUMBER,
    TYPE_SYMBOL,
    TYPE_LIST,
    TYPE_FUNCTION
} LispType;

typedef struct LispObject {
    LispType type;
    union {
        double number;
        char* symbol;
        struct LispList* list;
        struct LispFunction* fn;
    };
} LispObject;

typedef struct LispList {
    LispObject* car;
    struct LispList* cdr;
} LispList;

typedef struct LispFunction {
    bool is_builtin;
    union {
        LispObject* (*builtin)(struct LispList*);
        struct { LispList* params; LispObject* body; struct Environment* env; };
    };
} LispFunction;

typedef struct Environment {
    struct Environment* parent;
    char* symbol;
    LispObject* value;
    struct Environment* next;
} Environment;


LispObject* make_number(double value) {
    LispObject* obj = malloc(sizeof(LispObject));
    obj->type = TYPE_NUMBER;
    obj->number = value;
    return obj;
}

LispObject* make_symbol(const char* value) {
    LispObject* obj = malloc(sizeof(LispObject));
    obj->type = TYPE_SYMBOL;
    obj->symbol = strdup(value);
    return obj;
}

LispObject* make_list(LispList* list) {
    LispObject* obj = malloc(sizeof(LispObject));
    obj->type = TYPE_LIST;
    obj->list = list;
    return obj;
}

LispObject* make_function(LispFunction* fn) {
    LispObject* obj = malloc(sizeof(LispObject));
    obj->type = TYPE_FUNCTION;
    obj->fn = fn;
    return obj;
}

LispList* cons(LispObject* car, LispList* cdr) {
    LispList* list = malloc(sizeof(LispList));
    list->car = car;
    list->cdr = cdr;
    return list;
}


LispObject* builtin_add(LispList* args) {
    double sum = 0;
    while (args) {
        if (args->car->type != TYPE_NUMBER) {
            fprintf(stderr, "Error: + expects numbers\n");
            exit(1);
        }
        sum += args->car->number;
        args = args->cdr;
    }
    return make_number(sum);
}

LispObject* builtin_mul(LispList* args) {
    double product = 1;
    while (args) {
        if (args->car->type != TYPE_NUMBER) {
            fprintf(stderr, "Error: * expects numbers\n");
            exit(1);
        }
        product *= args->car->number;
        args = args->cdr;
    }
    return make_number(product);
}

LispObject* builtin_sub(LispList* args) {
    if (!args || !args->cdr) {
        fprintf(stderr, "Error: - expects at least two numbers\n");
        exit(1);
    }
    double result = args->car->number;
    args = args->cdr;
    while (args) {
        if (args->car->type != TYPE_NUMBER) {
            fprintf(stderr, "Error: - expects numbers\n");
            exit(1);
        }
        result -= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

LispObject* builtin_eq(LispList* args) {
    if (!args || !args->cdr) {
        fprintf(stderr, "Error: eq? expects two arguments\n");
        exit(1);
    }
    LispObject* first = args->car;
    LispObject* second = args->cdr->car;
    if (first->type != second->type) {
        return make_number(0);
    }
    switch (first->type) {
        case TYPE_NUMBER:
            return make_number(first->number == second->number);
        case TYPE_SYMBOL:
            return make_number(strcmp(first->symbol, second->symbol) == 0);
        default:
            return make_number(0);
    }
}

// tail recursion core
LispObject* eval(LispObject* expr, Environment* env);

LispObject* apply_function(LispObject* fn, LispList* args) {
    if (fn->fn->is_builtin) {
        return fn->fn->builtin(args);
    } else {
        LispFunction* user_fn = fn->fn;
        Environment* new_env = malloc(sizeof(Environment));
        new_env->parent = user_fn->env;  // function's environment, not the current one
        new_env->symbol = NULL;
        new_env->value = NULL;
        new_env->next = NULL;

        // bind parameters to arguments
        LispList* params = user_fn->params;
        LispList* arg_values = args;
        while (params && arg_values) {
            Environment* frame = malloc(sizeof(Environment));
            frame->symbol = strdup(params->car->symbol);
            frame->value = arg_values->car;
            frame->next = new_env->next;
            new_env->next = frame;
            params = params->cdr;
            arg_values = arg_values->cdr;
        }

        return eval(user_fn->body, new_env);
    }
}


LispObject* eval(LispObject* expr, Environment* env) {
    while (1) {  // tail recursion loop
        switch (expr->type) {
            case TYPE_NUMBER: return expr;
            case TYPE_SYMBOL: {
                Environment* curr = env;
                while (curr) {
                    Environment* local = curr;
                    while (local) {
                        if (local->symbol && strcmp(local->symbol, expr->symbol) == 0)
                            return local->value;
                        local = local->next;
                    }
                    curr = curr->parent;
                }
                fprintf(stderr, "Unbound symbol: %s\n", expr->symbol);
                exit(1);
            }
            case TYPE_LIST: {
                LispList* list = expr->list;
                if (!list) return expr;

                // special forms FIRST
                if (list->car->type == TYPE_SYMBOL) {
                    if (strcmp(list->car->symbol, "lambda") == 0) {
                        // (lambda params body)
                        if (!list->cdr || !list->cdr->cdr) {
                            fprintf(stderr, "Syntax error: lambda requires parameters and body\n");
                            exit(1);
                        }
                        LispFunction* fn = malloc(sizeof(LispFunction));
                        fn->is_builtin = false;
                        fn->params = list->cdr->car->list;  // params
                        fn->body = list->cdr->cdr->car;     // body
                        fn->env = env;                      // current env
                        return make_function(fn);
                    } else if (strcmp(list->car->symbol, "if") == 0) {
                        // (if condition then-expr else-expr)
                        if (!list->cdr || !list->cdr->cdr || !list->cdr->cdr->cdr) {
                            fprintf(stderr, "Syntax error: if requires 3 arguments\n");
                            exit(1);
                        }
                        LispObject* condition = eval(list->cdr->car, env);
                        if (condition->type != TYPE_NUMBER) {
                            fprintf(stderr, "Error: if condition must evaluate to a number\n");
                            exit(1);
                        }
                        if (condition->number != 0) {
                            expr = list->cdr->cdr->car;    // then branch
                        } else {
                            expr = list->cdr->cdr->cdr->car; // else branch
                        }
                        continue;  // tail call optimisation
                    }
                }

                // if not special form, evaluate function
                LispObject* fn = eval(list->car, env);
                LispList* args = NULL;
                LispList** tail = &args;
                LispList* current = list->cdr;
                while (current) {
                    *tail = cons(eval(current->car, env), NULL);
                    tail = &(*tail)->cdr;
                    current = current->cdr;
                }

                if (fn->fn->is_builtin) {
                    return fn->fn->builtin(args);
                } else {
                    // tail call optimisation: create new environment
                    LispFunction* user_fn = fn->fn;
                    Environment* new_env = malloc(sizeof(Environment));
                    new_env->parent = user_fn->env;
                    new_env->symbol = NULL;
                    new_env->value = NULL;
                    new_env->next = NULL;

                    // bind parameters to arguments
                    LispList* params = user_fn->params;
                    LispList* arg_values = args;
                    while (params && arg_values) {
                        Environment* frame = malloc(sizeof(Environment));
                        frame->symbol = strdup(params->car->symbol);
                        frame->value = arg_values->car;
                        frame->next = new_env->next;
                        new_env->next = frame;
                        params = params->cdr;
                        arg_values = arg_values->cdr;
                    }

                    expr = user_fn->body;
                    env = new_env;
                    continue;
                }
            }
            default: {
                fprintf(stderr, "Invalid expression type: %d\n", expr->type);
                exit(1);
            }
        }
    }
}

void run_test(const char* description, LispObject* expr, double expected, Environment* env) {
    LispObject* result = eval(expr, env);
    if (result->type == TYPE_NUMBER && result->number == expected) {
        printf("[PASS] %s -> %f\n", description, expected);
    } else {
        printf("[FAIL] %s (Expected: %f, Got: %f)\n", description, expected, result->number);
    }
}

void test_arithmetic(Environment* env) {

    LispObject* add_test = make_list(cons(make_symbol("+"), cons(make_number(2), cons(make_number(3), NULL))));
    run_test("Addition (+ 2 3)", add_test, 5, env);


    LispObject* sub_test = make_list(cons(make_symbol("-"), cons(make_number(10), cons(make_number(4), NULL))));
    run_test("Subtraction (- 10 4)", sub_test, 6, env);


    LispObject* mul_test = make_list(cons(make_symbol("*"), cons(make_number(3), cons(make_number(4), NULL))));
    run_test("Multiplication (* 3 4)", mul_test, 12, env);
}

void test_conditionals(Environment* env) {

    LispObject* if_true = make_list(cons(make_symbol("if"), cons(make_number(1), cons(make_number(42), cons(make_number(0), NULL)))));
    run_test("If-true (if 1 42 0)", if_true, 42, env);


    LispObject* if_false = make_list(cons(make_symbol("if"), cons(make_number(0), cons(make_number(0), cons(make_number(42), NULL)))));
    run_test("If-false (if 0 0 42)", if_false, 42, env);
}

void test_lambda(Environment* env) {

    //  lambda closure
LispObject* closure_test = make_list(cons(
    make_symbol("lambda"), 
    cons(
        make_list(cons(make_symbol("x"), NULL)),  // parameters: (x)
        cons(
            make_list(cons(make_symbol("+"), cons(make_symbol("x"), cons(make_number(10), NULL)))),  // body: (+ x 10)
            NULL
        )
    )
));
    LispObject* closure_result = eval(closure_test, env);
    LispList* args = cons(make_number(5), NULL);
    LispObject* result = apply_function(closure_result, args);
    printf("[TEST] Lambda closure: (+ x 10) where x=5 -> %f\n", result->number);
}


// simulating the tail-recursive sum function
LispObject* create_sum_function() {
    LispObject* n = make_symbol("n");
    LispObject* acc = make_symbol("acc");

    // create (- n 1)
    LispObject* minus_expr = make_list(cons(
        make_symbol("-"),
        cons(n, cons(make_number(1), NULL))
    ));

    // create (+ acc n)
    LispObject* plus_expr = make_list(cons(
        make_symbol("+"),
        cons(acc, cons(n, NULL))
    ));

    // create (sum (- n 1) (+ acc n))
    LispObject* sum_call = make_list(cons(
        make_symbol("sum"),
        cons(minus_expr, cons(plus_expr, NULL))
    ));

    // create (if (eq? n 0) acc (sum (- n 1) (+ acc n)))
    LispObject* if_expr = make_list(cons(
        make_symbol("if"),
        cons(
            make_list(cons(make_symbol("eq?"), cons(n, cons(make_number(0), NULL)))),
            cons(acc, cons(sum_call, NULL))
        )
    ));

    // create (lambda (n acc) ...)
    LispObject* lambda_expr = make_list(cons(
        make_symbol("lambda"),
        cons(
            make_list(cons(n, cons(acc, NULL))),
            cons(if_expr, NULL)
        )
    ));

    return lambda_expr;
}


int main() {
    Environment* env = malloc(sizeof(Environment));
    env->parent = NULL;
    env->symbol = NULL;
    env->value = NULL;
    env->next = NULL;


    LispFunction* add_fn = malloc(sizeof(LispFunction));
    add_fn->is_builtin = true;
    add_fn->builtin = builtin_add;
    Environment* add_frame = malloc(sizeof(Environment));
    add_frame->symbol = strdup("+");
    add_frame->value = make_function(add_fn);
    add_frame->next = env->next;
    env->next = add_frame;

    LispFunction* sub_fn = malloc(sizeof(LispFunction));
    sub_fn->is_builtin = true;
    sub_fn->builtin = builtin_sub;
    Environment* sub_frame = malloc(sizeof(Environment));
    sub_frame->symbol = strdup("-");
    sub_frame->value = make_function(sub_fn);
    sub_frame->next = env->next;
    env->next = sub_frame;

    LispFunction* eq_fn = malloc(sizeof(LispFunction));
    eq_fn->is_builtin = true;
    eq_fn->builtin = builtin_eq;
    Environment* eq_frame = malloc(sizeof(Environment));
    eq_frame->symbol = strdup("eq?");
    eq_frame->value = make_function(eq_fn);
    eq_frame->next = env->next;
    env->next = eq_frame;

    /*
    // Debug: Print the environment after adding eq?
    printf("Environment after adding eq?:\n");
    Environment* debug_curr = env;
    while (debug_curr) {
        if (debug_curr->symbol) {
            printf("  %s -> %p\n", debug_curr->symbol, debug_curr->value);
        }
        debug_curr = debug_curr->next;
    }*/

    // Define tail-recursive sum function
    LispObject* sum_fn = create_sum_function();

    // Add sum function to the environment
    Environment* sum_frame = malloc(sizeof(Environment));
    sum_frame->symbol = strdup("sum");
    sum_frame->value = eval(sum_fn, env);
    sum_frame->next = env->next;
    env->next = sum_frame;

    // Call (sum 1000 0)
    LispList* args = cons(make_number(1000), cons(make_number(0), NULL));
    LispObject* result = apply_function(sum_frame->value, args);
    
    printf("Sum from 0 to 1000: %f\n", result->number);  //  output 500500.0

    free(add_frame->symbol);
    free(add_frame);
    free(sub_frame->symbol);
    free(sub_frame);
    free(eq_frame->symbol);
    free(eq_frame);
    free(sum_frame->symbol);
    free(sum_frame);
    free(env);
    free(result);

    return 0;
}