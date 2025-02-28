#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define DEBUG(msg, ...) printf("[DEBUG] " msg "\n", ##__VA_ARGS__)

// Types
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

// Function prototypes
LispObject *make_number(double value);
LispObject *make_symbol(char *value);
LispObject *make_list(LispList *list);
LispObject *make_function(LispFunction *fn);
LispList *cons(LispObject *car, LispList *cdr);
LispObject *env_lookup(Environment *env, char *symbol);
void env_define(Environment *env, char *symbol, LispObject *value);
LispObject *eval(LispObject *expr, Environment *env);
LispObject *apply_function(LispObject *fn, LispList *args);
LispList *make_list_from_array(LispObject **objects, int count);

// Helper functions
LispObject *make_number(double value) {
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_NUMBER;
    obj->number = value;
    return obj;
}

LispObject *make_symbol(char *value) {
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_SYMBOL;
    obj->symbol = strdup(value);
    return obj;
}

LispObject *make_list(LispList *list) {
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_LIST;
    obj->list = list;
    return obj;
}

LispObject *make_function(LispFunction *fn) {
    LispObject *obj = malloc(sizeof(LispObject));
    obj->type = TYPE_FUNCTION;
    obj->fn = fn;
    return obj;
}

LispList *cons(LispObject *car, LispList *cdr) {
    LispList *list = malloc(sizeof(LispList));
    list->car = car;
    list->cdr = cdr;
    return list;
}

LispObject *env_lookup(Environment *env, char *symbol) {
    while (env != NULL) {
        Environment *frame = env;
        while (frame != NULL) {
            if (frame->symbol != NULL && strcmp(frame->symbol, symbol) == 0) {
                return frame->value;
            }
            frame = frame->next;
        }
        env = env->parent;
    }
    fprintf(stderr, "Unbound symbol: %s\n", symbol);
    exit(1);
}

void env_define(Environment *env, char *symbol, LispObject *value) {
    Environment *frame = malloc(sizeof(Environment));
    frame->parent = NULL;
    frame->symbol = strdup(symbol);
    frame->value = value;
    frame->next = env->next;
    env->next = frame;
}

LispObject *eval(LispObject *expr, Environment *env) {
    while (1) {
        DEBUG("Evaluating expression of type: %d", expr->type);
        switch (expr->type) {
            case TYPE_NUMBER:
                DEBUG("Returning number: %f", expr->number);
                return expr;
            case TYPE_SYMBOL:
                DEBUG("Looking up symbol: %s", expr->symbol);
                return env_lookup(env, expr->symbol);
            case TYPE_FUNCTION:
                DEBUG("Returning function");
                return expr;
            case TYPE_LIST: {
                DEBUG("Evaluating list");
                LispList *list = expr->list;
                if (list == NULL) return expr;
                LispObject *car = list->car;
                LispList *cdr = list->cdr;

                // Handle special forms
                if (car->type == TYPE_SYMBOL) {
                    DEBUG("Handling special form: %s", car->symbol);
                    if (strcmp(car->symbol, "quote") == 0) {
                        DEBUG("Returning quoted expression");
                        return cdr->car;
                    } else if (strcmp(car->symbol, "define") == 0) {
                        DEBUG("Defining symbol: %s", cdr->car->symbol);
                        LispObject *name = cdr->car;
                        LispObject *value = eval(cdr->cdr->car, env);
                        env_define(env, name->symbol, value);
                        return value;
                    } else if (strcmp(car->symbol, "lambda") == 0) {
                        DEBUG("Creating lambda function");
                        LispFunction *fn = malloc(sizeof(LispFunction));
                        fn->is_builtin = false;
                        fn->params = cdr->car->list;
                        fn->body = cdr->cdr->car;
                        fn->env = env;
                        return make_function(fn);
                    }
                }

                // Evaluate the function
                DEBUG("Evaluating function");
                LispObject *fn_obj = eval(car, env);
                if (fn_obj->type != TYPE_FUNCTION) {
                    fprintf(stderr, "Not a function: %d\n", fn_obj->type);
                    exit(1);
                }

                // Evaluate arguments in correct order
                DEBUG("Evaluating arguments");
                LispList *args = NULL;
                LispList **tail = &args;
                while (cdr != NULL) {
                    LispObject *arg_val = eval(cdr->car, env);
                    *tail = cons(arg_val, NULL);
                    tail = &(*tail)->cdr;
                    cdr = cdr->cdr;
                }

                if (fn_obj->fn->is_builtin) {
                    DEBUG("Applying built-in function");
                    return fn_obj->fn->builtin(args);
                } else {
                    DEBUG("Applying user-defined function");
                    // Tail call: set expr to body and env to new_env
                    expr = fn_obj->fn->body;
                    env = fn_obj->fn->env;
                    continue; // Continue the loop to evaluate body without recursion
                }
                break;
            }
            default:
                fprintf(stderr, "Invalid expression type: %d\n", expr->type);
                exit(1);
        }
    }
}

// Built-in functions
LispObject *builtin_add(LispList *args) {
    double result = 0;
    while (args != NULL) {
        result += args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

LispObject *builtin_sub(LispList *args) {
    double result = args->car->number;
    args = args->cdr;
    while (args != NULL) {
        result -= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

LispObject *builtin_mul(LispList *args) {
    double result = 1;
    while (args != NULL) {
        result *= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}

LispObject *builtin_if(LispList *args) {
    LispObject *cond = args->car;
    LispObject *then_expr = args->cdr->car;
    LispObject *else_expr = args->cdr->cdr->car;
    return (cond->number != 0) ? then_expr : else_expr;
}

LispObject *builtin_eq(LispList *args) {
    LispObject *a = args->car;
    LispObject *b = args->cdr->car;
    return (a->number == b->number) ? make_number(1) : make_number(0);
}

// Memoization for factorial
typedef struct MemoEntry {
    double n;
    double result;
    struct MemoEntry *next;
} MemoEntry;

MemoEntry *memo_table = NULL;

double memo_lookup(double n) {
    MemoEntry *entry = memo_table;
    while (entry != NULL) {
        if (entry->n == n) {
            return entry->result;
        }
        entry = entry->next;
    }
    return -1; // Not found
}

void memo_store(double n, double result) {
    MemoEntry *entry = malloc(sizeof(MemoEntry));
    entry->n = n;
    entry->result = result;
    entry->next = memo_table;
    memo_table = entry;
}

LispObject *builtin_fact(LispList *args) {
    double n = args->car->number;
    double result = memo_lookup(n);
    if (result != -1) {
        return make_number(result);
    }

    if (n == 0) {
        result = 1;
    } else {
        LispObject *arg = make_number(n - 1);
        LispList *fact_args = cons(arg, NULL);
        result = n * builtin_fact(fact_args)->number;
    }

    memo_store(n, result);
    return make_number(result);
}

// Default environment
Environment *default_environment() {
    Environment *env = malloc(sizeof(Environment));
    env->parent = NULL;
    env->symbol = NULL;
    env->value = NULL;
    env->next = NULL;

    LispFunction *add_fn = malloc(sizeof(LispFunction));
    add_fn->is_builtin = true;
    add_fn->builtin = builtin_add;
    env_define(env, "+", make_function(add_fn));

    LispFunction *sub_fn = malloc(sizeof(LispFunction));
    sub_fn->is_builtin = true;
    sub_fn->builtin = builtin_sub;
    env_define(env, "-", make_function(sub_fn));

    LispFunction *mul_fn = malloc(sizeof(LispFunction));
    mul_fn->is_builtin = true;
    mul_fn->builtin = builtin_mul;
    env_define(env, "*", make_function(mul_fn));

    LispFunction *if_fn = malloc(sizeof(LispFunction));
    if_fn->is_builtin = true;
    if_fn->builtin = builtin_if;
    env_define(env, "if", make_function(if_fn));

    LispFunction *eq_fn = malloc(sizeof(LispFunction));
    eq_fn->is_builtin = true;
    eq_fn->builtin = builtin_eq;
    env_define(env, "eq?", make_function(eq_fn));

    return env;
}

// Helper function to create a list from an array
LispList *make_list_from_array(LispObject **objects, int count) {
    LispList *list = NULL;
    for (int i = count - 1; i >= 0; i--) {
        list = cons(objects[i], list);
    }
    return list;
}

// Test cases
void run_tests() {
    DEBUG("Running tests");
    Environment *env = default_environment();

    // Declare variables for factorial and sum tests
    LispObject *n = make_symbol("n");
    LispObject *acc = make_symbol("acc");

    // Test 1: Number
    LispObject *num = make_number(42);
    LispObject *result = eval(num, env);
    printf("Test 1: %f (expected: 42.0)\n", result->number);

    // Test 2: Symbol
    LispObject *symbol = make_symbol("x");
    env_define(env, "x", make_number(10));
    result = eval(symbol, env);
    printf("Test 2: %f (expected: 10.0)\n", result->number);

    // Test 3: Addition
    LispObject *one = make_number(1);
    LispObject *two = make_number(2);
    LispObject *three = make_number(3);
    LispObject *plus = make_symbol("+");
    LispObject *args[] = {plus, one, two, three};
    LispList *expr = make_list_from_array(args, 4);
    result = eval(make_list(expr), env);
    printf("Test 3: %f (expected: 6.0)\n", result->number);

    // Test 4: Quote
    LispObject *quote = make_symbol("quote");
    LispObject *list_args[] = {one, two, three};
    LispList *quoted_list = make_list_from_array(list_args, 3);
    LispObject *quote_args[] = {quote, make_list(quoted_list)};
    LispList *quote_expr = make_list_from_array(quote_args, 2);
    result = eval(make_list(quote_expr), env);

    // Check list length correctly
    int length = 0;
    LispList *current = result->list;
    while (current != NULL) {
        length++;
        current = current->cdr;
    }
    printf("Test 4: List length: %d (expected: 3)\n", length);

    // Test 5: Lambda
    LispObject *lambda = make_symbol("lambda");
    LispObject *x = make_symbol("x"); // Parameter
    LispObject *params = make_list(cons(x, NULL)); // Parameter list: (x)
    LispObject *body = make_list(
        cons(
            make_symbol("+"),
            cons(
                x, // Use the parameter x
                cons(make_number(1), NULL)
            )
        )
    );
    LispObject *lambda_args[] = {lambda, params, body};
    LispList *lambda_expr = make_list_from_array(lambda_args, 3);
    LispObject *lambda_fn = eval(make_list(lambda_expr), env);

    // Apply the lambda function to the argument 5
    LispObject *arg = make_number(5);
    LispObject *apply_args[] = {lambda_fn, arg};
    LispList *apply_expr = make_list_from_array(apply_args, 2);
    result = eval(make_list(apply_expr), env);
    printf("Test 5: %f (expected: 6.0)\n", result->number);

    // Test 6: Recursive factorial (memoized)
    LispFunction *fact_fn = malloc(sizeof(LispFunction));
    fact_fn->is_builtin = true;
    fact_fn->builtin = builtin_fact;
    env_define(env, "fact", make_function(fact_fn));

    LispObject *fact_call = make_list(
        make_list_from_array((LispObject*[]){make_symbol("fact"), make_number(5)}, 2)
    );
    result = eval(fact_call, env);
    printf("Test 6: Factorial of 5: %f (expected: 120.0)\n", result->number);
}

// Main function
int main() {
    run_tests();
    return 0;
}