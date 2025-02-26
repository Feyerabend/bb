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
        char *symbol;
        struct LispList *list;
        struct LispFunction *fn;
    };
} LispObject;

typedef struct LispList {
    LispObject *car;
    struct LispList *cdr;
} LispList;

typedef struct LispFunction {
    bool is_builtin;
    union {
        LispObject *(*builtin)(struct LispList *);
        struct {
            struct LispList *params;
            LispObject *body;
            struct Environment *env;
        };
    };
} LispFunction;

typedef struct Environment {
    struct Environment *parent;
    char *symbol;
    LispObject *value;
    struct Environment *next;
} Environment;

LispObject *make_number(double value) {
    DEBUG("Creating number: %f", value);
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_NUMBER;
    obj->number = value;
    return obj;
}

LispObject *make_symbol(char *value) {
    DEBUG("Creating symbol: %s", value);
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_SYMBOL;
    obj->symbol = strdup(value);
    return obj;
}

LispObject *make_list(LispList *list) {
    DEBUG("Creating list");
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_LIST;
    obj->list = list;
    return obj;
}

LispObject *make_function(LispFunction *fn) {
    DEBUG("Creating function");
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_FUNCTION;
    obj->fn = fn;
    return obj;
}

LispList *cons(LispObject *car, LispList *cdr) {
    DEBUG("Creating cons: car=%p, cdr=%p", car, cdr);
    LispList *list = malloc(sizeof(LispList));
    list->car = car;
    list->cdr = cdr;
    return list;
}

LispObject *env_lookup(Environment *env, char *symbol) {
    DEBUG("Looking up symbol: %s", symbol);
    while (env != NULL) {
        if (env->symbol != NULL && strcmp(env->symbol, symbol) == 0) {
            DEBUG("Found symbol: %s -> %p", symbol, env->value);
            return env->value;
        }
        env = env->parent;
    }
    DEBUG("Unbound symbol: %s", symbol);
    fprintf(stderr, "Unbound symbol: %s\n", symbol);
    exit(1);
}

void env_define(Environment *env, char *symbol, LispObject *value) {
    DEBUG("Defining symbol: %s -> %p", symbol, value);
    Environment *frame = malloc(sizeof(Environment));
    frame->symbol = strdup(symbol);
    frame->value = value;
    frame->parent = env;
    frame->next = NULL;
    env->next = frame;
}

LispObject *eval(LispObject *expr, Environment *env) {
    DEBUG("Evaluating expression: %p", expr);
    switch (expr->type) {
        case TYPE_NUMBER:
            DEBUG("Number: %f", expr->number);
            return expr;
        case TYPE_SYMBOL:
            DEBUG("Symbol: %s", expr->symbol);
            return env_lookup(env, expr->symbol);
        case TYPE_LIST: {
            DEBUG("List");
            LispList *list = expr->list;
            if (list == NULL) {
                DEBUG("Empty list");
                return expr;
            }
            LispObject *car = list->car;
            LispList *cdr = list->cdr;

            if (car->type == TYPE_SYMBOL) {
                if (strcmp(car->symbol, "quote") == 0) {
                    DEBUG("Quote");
                    return cdr->car;
                } else if (strcmp(car->symbol, "define") == 0) {
                    DEBUG("Define");
                    LispObject *name = cdr->car;
                    LispObject *value = eval(cdr->cdr->car, env);
                    env_define(env, name->symbol, value);
                    return value;
                } else if (strcmp(car->symbol, "lambda") == 0) {
                    DEBUG("Lambda");
                    LispFunction *fn = malloc(sizeof(LispFunction));
                    fn->is_builtin = false;
                    fn->params = cdr->car->list;
                    fn->body = cdr->cdr->car;
                    fn->env = env;
                    return make_function(fn);
                }
            }

            DEBUG("Function application");
            LispObject *fn = eval(car, env);
            LispList *args = NULL;
            while (cdr != NULL) {
                args = cons(eval(cdr->car, env), args);
                cdr = cdr->cdr;
            }
            return fn->fn->builtin(args);
        }
        default:
            DEBUG("Invalid expression type");
            fprintf(stderr, "Invalid expression type\n");
            exit(1);
    }
}

LispObject *builtin_add(LispList *args) {
    DEBUG("Built-in add");
    double result = 0;
    while (args != NULL) {
        result += args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

LispObject *builtin_multiply(LispList *args) {
    DEBUG("Built-in multiply");
    double result = 1;
    while (args != NULL) {
        result *= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

Environment *default_environment() {
    DEBUG("Creating default environment");
    Environment *env = malloc(sizeof(Environment));
    env->parent = NULL;
    env->symbol = NULL;
    env->value = NULL;
    env->next = NULL;

    LispFunction *add_fn = malloc(sizeof(LispFunction));
    add_fn->is_builtin = true;
    add_fn->builtin = builtin_add;
    env_define(env, "+", make_function(add_fn));

    LispFunction *multiply_fn = malloc(sizeof(LispFunction));
    multiply_fn->is_builtin = true;
    multiply_fn->builtin = builtin_multiply;
    env_define(env, "*", make_function(multiply_fn));

    return env;
}

LispList *make_list_from_array(LispObject **objects, int count) {
    DEBUG("Creating list from array");
    LispList *list = NULL;
    for (int i = count - 1; i >= 0; i--) {
        list = cons(objects[i], list);
    }
    return list;
}

void run_tests() {
    DEBUG("Running tests");
    Environment *env = default_environment();

    LispObject *num = make_number(42);
    LispObject *result = eval(num, env);
    printf("Test 1: %f (expected: 42.0)\n", result->number);

    LispObject *symbol = make_symbol("x");
    env_define(env, "x", make_number(10));
    result = eval(symbol, env);
    printf("Test 2: %f (expected: 10.0)\n", result->number);

    LispObject *one = make_number(1);
    LispObject *two = make_number(2);
    LispObject *three = make_number(3);
    LispObject *plus = make_symbol("+");
    LispObject *args[] = {plus, one, two, three};
    LispList *expr = make_list_from_array(args, 4);
    result = eval(make_list(expr), env);
    printf("Test 3: %f (expected: 6.0)\n", result->number);

    LispObject *quote = make_symbol("quote");
    LispObject *list_args[] = {one, two, three};
    LispList *quoted_list = make_list_from_array(list_args, 3);
    LispObject *quote_args[] = {quote, make_list(quoted_list)};
    LispList *quote_expr = make_list_from_array(quote_args, 2);
    result = eval(make_list(quote_expr), env);
    printf("Test 4: List length: %d (expected: 3)\n", result->list ? 1 : 0);

    LispObject *lambda = make_symbol("lambda");
    LispObject *params = make_list(cons(make_symbol("x"), NULL));
    LispObject *body = make_list(cons(make_symbol("+"), cons(make_symbol("x"), cons(make_number(1), NULL))));
    LispObject *lambda_args[] = {lambda, params, body};
    LispList *lambda_expr = make_list_from_array(lambda_args, 3);
    LispObject *lambda_fn = eval(make_list(lambda_expr), env);

    LispObject *arg = make_number(5);
    LispObject *apply_args[] = {lambda_fn, arg};
    LispList *apply_expr = make_list_from_array(apply_args, 2);
    result = eval(make_list(apply_expr), env);
    printf("Test 5: %f (expected: 6.0)\n", result->number);
}

int main() {
    run_tests();
    return 0;
}