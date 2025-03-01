#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define DEBUG(msg, ...) printf("[DEBUG] %s:%d: " msg "\n", __FILE__, __LINE__, ##__VA_ARGS__)
#define GC_THRESHOLD 1024

typedef struct Environment Environment;
typedef struct LispObject LispObject;
typedef struct LispList LispList;
typedef struct LispFunction LispFunction;

struct Environment {
    Environment *parent;
    char *symbol;
    LispObject *value;
    Environment *next;
};

typedef enum {
    TYPE_NUMBER,
    TYPE_SYMBOL,
    TYPE_LIST,
    TYPE_FUNCTION
} LispType;

struct LispObject {
    LispType type;
    bool marked;
    union {
        double number;
        char *symbol;
        LispList *list;
        LispFunction *fn;
    };
};

struct LispList {
    LispObject *car;
    LispList *cdr;
};

struct LispFunction {
    bool is_builtin;
    union {
        LispObject *(*builtin)(LispList *, Environment *);
        struct {
            LispList *params;
            LispObject *body;
            Environment *env;
        };
    };
};

typedef struct {
    LispObject **objects;
    size_t count;
    size_t capacity;
} ObjectPool;

ObjectPool object_pool;

// fwd decl func
void error(const char *msg);
void init_object_pool();
void free_object_pool();
LispObject *make_number(double value);
LispObject *make_symbol(char *value);
LispObject *make_list(LispList *list);
LispObject *make_function(LispFunction *fn);
LispList *create_cons(LispObject *car, LispList *cdr);
void free_lisp_list(LispList *list);
void free_lisp_function(LispFunction *fn);
void mark(LispObject *obj);
void mark_environment(Environment *env);
void sweep();
void gc(Environment *env);
void check_gc(Environment *env);
LispObject *env_lookup(Environment *env, char *symbol);
void env_define(Environment *env, char *symbol, LispObject *value);
LispObject *eval_tail_recursive(LispObject *expr, Environment *env);
LispObject *eval(LispObject *expr, Environment *env);
LispObject *builtin_add(LispList *args, Environment *env);
LispObject *builtin_sub(LispList *args, Environment *env);
LispObject *builtin_mul(LispList *args, Environment *env);
LispObject *builtin_if(LispList *args, Environment *env);
LispObject *builtin_eq(LispList *args, Environment *env);
LispObject *builtin_map(LispList *args, Environment *env);
LispObject *builtin_filter(LispList *args, Environment *env);
LispObject *builtin_fact(LispList *args, Environment *env);
LispObject *builtin_delay(LispList *args, Environment *env);
LispObject *builtin_force(LispList *args, Environment *env);
Environment *default_environment();
LispList *make_list_from_array(LispObject **objects, int count);
void run_tests();

void error(const char *msg) {
    fprintf(stderr, "Error: %s\n", msg);
    exit(EXIT_FAILURE);
}

void init_object_pool() {
    object_pool.capacity = 1024;
    object_pool.count = 0;
    object_pool.objects = malloc(object_pool.capacity * sizeof(LispObject *));
    if (!object_pool.objects) error("Failed to allocate memory for object pool");
    DEBUG("Initialized object pool with capacity %zu", object_pool.capacity);
}

void free_object_pool() {
    for (size_t i = 0; i < object_pool.count; i++) {
        free(object_pool.objects[i]);
    }
    free(object_pool.objects);
    DEBUG("Freed object pool");
}

LispObject *make_number(double value) {
    LispObject *obj = malloc(sizeof(LispObject));
    if (!obj) error("Failed to allocate memory for number object");
    obj->type = TYPE_NUMBER;
    obj->marked = false;
    obj->number = value;

    if (object_pool.count >= object_pool.capacity) {
        object_pool.capacity *= 2;
        object_pool.objects = realloc(object_pool.objects, object_pool.capacity * sizeof(LispObject *));
        if (!object_pool.objects) error("Failed to reallocate memory for object pool");
        DEBUG("Expanded object pool capacity to %zu", object_pool.capacity);
    }
    object_pool.objects[object_pool.count++] = obj;

    DEBUG("Created number object: %f", value);
    return obj;
}

LispObject *make_symbol(char *value) {
    LispObject *obj = malloc(sizeof(LispObject));
    if (!obj) error("Failed to allocate memory for symbol object");
    obj->type = TYPE_SYMBOL;
    obj->marked = false;
    obj->symbol = strdup(value);
    if (!obj->symbol) error("Failed to duplicate symbol string");

    if (object_pool.count >= object_pool.capacity) {
        object_pool.capacity *= 2;
        object_pool.objects = realloc(object_pool.objects, object_pool.capacity * sizeof(LispObject *));
        if (!object_pool.objects) error("Failed to reallocate memory for object pool");
        DEBUG("Expanded object pool capacity to %zu", object_pool.capacity);
    }
    object_pool.objects[object_pool.count++] = obj;

    DEBUG("Created symbol object: %s", value);
    return obj;
}

LispObject *make_list(LispList *list) {
    LispObject *obj = malloc(sizeof(LispObject));
    if (!obj) error("Failed to allocate memory for list object");
    obj->type = TYPE_LIST;
    obj->marked = false;
    obj->list = list;

    if (object_pool.count >= object_pool.capacity) {
        object_pool.capacity *= 2;
        object_pool.objects = realloc(object_pool.objects, object_pool.capacity * sizeof(LispObject *));
        if (!object_pool.objects) error("Failed to reallocate memory for object pool");
        DEBUG("Expanded object pool capacity to %zu", object_pool.capacity);
    }
    object_pool.objects[object_pool.count++] = obj;

    DEBUG("Created list object");
    return obj;
}

LispObject *make_function(LispFunction *fn) {
    LispObject *obj = malloc(sizeof(LispObject));
    if (!obj) error("Failed to allocate memory for function object");
    obj->type = TYPE_FUNCTION;
    obj->marked = false;
    obj->fn = fn;

    if (object_pool.count >= object_pool.capacity) {
        object_pool.capacity *= 2;
        object_pool.objects = realloc(object_pool.objects, object_pool.capacity * sizeof(LispObject *));
        if (!object_pool.objects) error("Failed to reallocate memory for object pool");
        DEBUG("Expanded object pool capacity to %zu", object_pool.capacity);
    }
    object_pool.objects[object_pool.count++] = obj;

    DEBUG("Created function object");
    return obj;
}

LispList *create_cons(LispObject *car, LispList *cdr) {
    LispList *list = malloc(sizeof(LispList));
    if (!list) error("Failed to allocate memory for cons cell");
    list->car = car;
    list->cdr = cdr;
    DEBUG("Created cons: car=%p, cdr=%p", (void *)car, (void *)cdr);
    return list;
}

void free_lisp_list(LispList *list) {
    while (list != NULL) {
        LispList *temp = list;
        list = list->cdr;
        free(temp);
    }
}

void free_lisp_function(LispFunction *fn) {
    if (!fn->is_builtin) {
        free_lisp_list(fn->params);
        free(fn->body);
    }
    free(fn);
}

void mark(LispObject *obj) {
    if (obj == NULL || obj->marked) return;
    DEBUG("Marking object: %p (type: %d)", (void *)obj, obj->type);
    obj->marked = true;

    switch (obj->type) {
        case TYPE_LIST:
            if (obj->list) {
                mark(obj->list->car);
                mark((LispObject *)obj->list->cdr);
            }
            break;
        case TYPE_FUNCTION:
            if (!obj->fn->is_builtin) {
                mark((LispObject *)obj->fn->params);
                mark(obj->fn->body);
            }
            break;
        default:
            break;
    }
}

void mark_environment(Environment *env) {
    while (env) {
        if (env->value) {
            DEBUG("Marking environment value: %p", (void *)env->value);
            mark(env->value);
        }
        env = env->next;
    }
}

void sweep() {
    size_t i = 0;
    DEBUG("Starting sweep phase");
    while (i < object_pool.count) {
        if (!object_pool.objects[i]->marked) {
            DEBUG("Sweeping object: %p (type: %d)", (void *)object_pool.objects[i], object_pool.objects[i]->type);
            free(object_pool.objects[i]);
            object_pool.objects[i] = object_pool.objects[--object_pool.count];
        } else {
            DEBUG("Object %p is still reachable, unmarking", (void *)object_pool.objects[i]);
            object_pool.objects[i]->marked = false;
            i++;
        }
    }
    DEBUG("Sweep phase completed");
}

void gc(Environment *env) {
    DEBUG("Starting garbage collection");
    mark_environment(env);
    sweep();
    DEBUG("Garbage collection completed");
}

void check_gc(Environment *env) {
    if (object_pool.count >= GC_THRESHOLD) {
        gc(env);
    }
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
    error("Unbound symbol");
    return NULL; // not reached
}

void env_define(Environment *env, char *symbol, LispObject *value) {
    Environment *frame = malloc(sizeof(Environment));
    if (!frame) error("Failed to allocate memory for environment frame");
    frame->parent = NULL;
    frame->symbol = strdup(symbol);
    if (!frame->symbol) error("Failed to duplicate symbol string");
    frame->value = value;
    frame->next = env->next;
    env->next = frame;
    DEBUG("Defined symbol: %s -> %p", symbol, (void *)value);
}

LispObject *eval_tail_recursive(LispObject *expr, Environment *env) {
    while (1) {
        switch (expr->type) {
            case TYPE_NUMBER:
                return expr;
            case TYPE_SYMBOL:
                return env_lookup(env, expr->symbol);
            case TYPE_FUNCTION:
                return expr;
            case TYPE_LIST: {
                LispList *list = expr->list;
                if (!list) return expr;

                LispObject *car = list->car;
                LispList *cdr = list->cdr;

                if (car->type == TYPE_SYMBOL) {
                    if (strcmp(car->symbol, "quote") == 0) {
                        return cdr->car;
                    } else if (strcmp(car->symbol, "define") == 0) {
                        LispObject *name = cdr->car;
                        LispObject *value = eval_tail_recursive(cdr->cdr->car, env);
                        env_define(env, name->symbol, value);
                        return value;
                    } else if (strcmp(car->symbol, "lambda") == 0) {
                        LispFunction *fn = malloc(sizeof(LispFunction));
                        if (!fn) error("Failed to allocate memory for function");
                        fn->is_builtin = false;
                        fn->params = cdr->car->list;
                        fn->body = cdr->cdr->car;
                        fn->env = env;
                        return make_function(fn);
                    }
                }

                LispObject *fn_obj = eval_tail_recursive(car, env);
                if (!fn_obj || fn_obj->type != TYPE_FUNCTION) {
                    error("Not a function");
                }

                LispList *args = NULL;
                LispList **tail = &args;
                while (cdr != NULL) {
                    LispObject *arg_val = eval_tail_recursive(cdr->car, env);
                    *tail = create_cons(arg_val, NULL);
                    tail = &(*tail)->cdr;
                    cdr = cdr->cdr;
                }

                if (!fn_obj->fn->is_builtin) {
                    Environment *new_env = malloc(sizeof(Environment));
                    if (!new_env) error("Failed to allocate memory for new environment");
                    new_env->parent = fn_obj->fn->env;
                    new_env->symbol = NULL;
                    new_env->value = NULL;
                    new_env->next = NULL;

                    LispList *params = fn_obj->fn->params;
                    LispList *arg_values = args;
                    while (params != NULL && arg_values != NULL) {
                        env_define(new_env, params->car->symbol, arg_values->car);
                        params = params->cdr;
                        arg_values = arg_values->cdr;
                    }

                    expr = fn_obj->fn->body;
                    env = new_env;
                    continue;
                } else {
                    return fn_obj->fn->builtin(args, env);
                }
            }
            default:
                error("Invalid expression type");
        }
    }
}


LispObject *eval(LispObject *expr, Environment *env) {
    return eval_tail_recursive(expr, env);
}


LispObject *builtin_add(LispList *args, Environment *env) {
    double result = 0;
    while (args != NULL) {
        result += args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}


LispObject *builtin_sub(LispList *args, Environment *env) {
    double result = args->car->number;
    args = args->cdr;
    while (args != NULL) {
        result -= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}


LispObject *builtin_mul(LispList *args, Environment *env) {
    double result = 1;
    while (args != NULL) {
        result *= args->car->number;
        args = args->cdr;
    }
    return make_number(result);
}


LispObject *builtin_if(LispList *args, Environment *env) {
    LispObject *cond = args->car;
    LispObject *then_expr = args->cdr->car;
    LispObject *else_expr = args->cdr->cdr->car;
    return (cond->number != 0) ? then_expr : else_expr;
}


LispObject *builtin_eq(LispList *args, Environment *env) {
    LispObject *a = args->car;
    LispObject *b = args->cdr->car;
    return (a->number == b->number) ? make_number(1) : make_number(0);
}


LispObject *builtin_map(LispList *args, Environment *env) {
    if (args == NULL || args->car == NULL || args->car->type != TYPE_FUNCTION) {
        error("map expects a function as its first argument");
    }
    LispObject *fn_obj = args->car;
    LispList *list = args->cdr->car->list;

    LispList *result = NULL;
    LispList **tail = &result;

    while (list != NULL) {
        LispObject *arg = list->car;

        // create a new list: (fn_obj arg)
        LispList *fn_and_arg = create_cons(fn_obj, create_cons(arg, NULL));
        LispObject *fn_and_arg_expr = make_list(fn_and_arg);

        // evaluate (fn_obj arg)
        LispObject *mapped_value = eval_tail_recursive(fn_and_arg_expr, env);

        // append the result to the output list
        *tail = create_cons(mapped_value, NULL);
        tail = &(*tail)->cdr;

        list = list->cdr;
    }

    return make_list(result);
}


LispObject *builtin_filter(LispList *args, Environment *env) {
    if (args == NULL || args->car == NULL || args->car->type != TYPE_FUNCTION) {
        error("filter expects a function as its first argument");
    }
    LispObject *fn_obj = args->car;
    LispList *list = args->cdr->car->list;

    LispList *result = NULL;
    LispList **tail = &result;

    while (list != NULL) {
        LispObject *arg = list->car;

        // create a new list: (fn_obj arg)
        LispList *fn_and_arg = create_cons(fn_obj, create_cons(arg, NULL));
        LispObject *fn_and_arg_expr = make_list(fn_and_arg);

        // evaluate (fn_obj arg)
        LispObject *filter_result = eval_tail_recursive(fn_and_arg_expr, env);

        if (filter_result->number != 0) {
            *tail = create_cons(arg, NULL);
            tail = &(*tail)->cdr;
        }

        list = list->cdr;
    }

    return make_list(result);
}

// really? builtin_fact?
LispObject *builtin_fact(LispList *args, Environment *env) {
    if (args == NULL || args->car->type != TYPE_NUMBER) {
        error("fact expects a number");
    }
    double n = args->car->number;
    if (n == 0) {
        return make_number(1);
    } else {
        LispObject *arg = make_number(n - 1);
        LispList *fact_args = create_cons(arg, NULL);
        return make_number(n * builtin_fact(fact_args, env)->number);
    }
}


LispObject *builtin_delay(LispList *args, Environment *env) {
    if (args == NULL) {
        error("delay expects an expression");
    }
    return make_function(&(LispFunction){
        .is_builtin = false,
        .params = NULL,
        .body = args->car
    });
}

LispObject *builtin_force(LispList *args, Environment *env) {
    if (args == NULL || args->car->type != TYPE_FUNCTION) {
        error("force expects a thunk");
    }
    return eval_tail_recursive(args->car->fn->body, env);
}


Environment *default_environment() {
    Environment *env = malloc(sizeof(Environment));
    if (!env) error("Failed to allocate memory for environment");
    env->parent = NULL;
    env->symbol = NULL;
    env->value = NULL;
    env->next = NULL;


    LispFunction *add_fn = malloc(sizeof(LispFunction));
    if (!add_fn) error("Failed to allocate memory for add function");
    add_fn->is_builtin = true;
    add_fn->builtin = builtin_add;
    env_define(env, "+", make_function(add_fn));

    LispFunction *sub_fn = malloc(sizeof(LispFunction));
    if (!sub_fn) error("Failed to allocate memory for sub function");
    sub_fn->is_builtin = true;
    sub_fn->builtin = builtin_sub;
    env_define(env, "-", make_function(sub_fn));

    LispFunction *mul_fn = malloc(sizeof(LispFunction));
    if (!mul_fn) error("Failed to allocate memory for mul function");
    mul_fn->is_builtin = true;
    mul_fn->builtin = builtin_mul;
    env_define(env, "*", make_function(mul_fn));

    LispFunction *if_fn = malloc(sizeof(LispFunction));
    if (!if_fn) error("Failed to allocate memory for if function");
    if_fn->is_builtin = true;
    if_fn->builtin = builtin_if;
    env_define(env, "if", make_function(if_fn));

    LispFunction *eq_fn = malloc(sizeof(LispFunction));
    if (!eq_fn) error("Failed to allocate memory for eq function");
    eq_fn->is_builtin = true;
    eq_fn->builtin = builtin_eq;
    env_define(env, "eq?", make_function(eq_fn));

    LispFunction *map_fn = malloc(sizeof(LispFunction));
    if (!map_fn) error("Failed to allocate memory for map function");
    map_fn->is_builtin = true;
    map_fn->builtin = builtin_map;
    env_define(env, "map", make_function(map_fn));

    LispFunction *filter_fn = malloc(sizeof(LispFunction));
    if (!filter_fn) error("Failed to allocate memory for filter function");
    filter_fn->is_builtin = true;
    filter_fn->builtin = builtin_filter;
    env_define(env, "filter", make_function(filter_fn));

    LispFunction *fact_fn = malloc(sizeof(LispFunction));
    if (!fact_fn) error("Failed to allocate memory for fact function");
    fact_fn->is_builtin = true;
    fact_fn->builtin = builtin_fact;
    env_define(env, "fact", make_function(fact_fn));

    LispFunction *delay_fn = malloc(sizeof(LispFunction));
    if (!delay_fn) error("Failed to allocate memory for delay function");
    delay_fn->is_builtin = true;
    delay_fn->builtin = builtin_delay;
    env_define(env, "delay", make_function(delay_fn));

    LispFunction *force_fn = malloc(sizeof(LispFunction));
    if (!force_fn) error("Failed to allocate memory for force function");
    force_fn->is_builtin = true;
    force_fn->builtin = builtin_force;
    env_define(env, "force", make_function(force_fn));

    // really only for testing
    LispObject *double_fn = make_function(&(LispFunction){
        .is_builtin = false,
        .params = create_cons(make_symbol("x"), NULL),
        .body = make_list(create_cons(make_symbol("*"), create_cons(make_symbol("x"), create_cons(make_number(2), NULL))))
    });
    env_define(env, "double", double_fn);

    return env;
}

// helper
LispList *make_list_from_array(LispObject **objects, int count) {
    LispList *list = NULL;
    for (int i = count - 1; i >= 0; i--) {
        list = create_cons(objects[i], list);
    }
    return list;
}


void run_tests() {
    Environment *env = default_environment();

    // Test 1: Basic arithmetic
    LispObject *num = make_number(42);
    LispObject *result = eval(num, env);
    printf("Test 1: %f (expected: 42.0)\n", result->number);

    // Test 2: Symbol lookup
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

    /*
    // Test 4: Map
    LispObject *double_fn = env_lookup(env, "double");
    if (double_fn == NULL || double_fn->type != TYPE_FUNCTION) {
        error("double is not a function");
    }

    LispList *map_list = create_cons(one, create_cons(two, create_cons(three, NULL)));
    LispObject *map_args[] = {double_fn, make_list(map_list)};
    LispList *map_expr = make_list_from_array(map_args, 2);
    result = eval(make_list(map_expr), env);

    if (result->type == TYPE_LIST) {
        LispList *result_list = result->list;
        printf("Test 4: Map result: ");
        while (result_list != NULL) {
            printf("%f ", result_list->car->number);
            result_list = result_list->cdr;
        }
        printf("(expected: 2.0 4.0 6.0)\n");
    } else {
        printf("Test 4: Map failed (expected a list)\n");
    }



    // Test 5: Reduce
    LispList *reduce_list = create_cons(one, create_cons(two, create_cons(three, NULL)));
    LispObject *reduce_args[] = {plus, make_number(0), make_list(reduce_list)};
    LispList *reduce_expr = make_list_from_array(reduce_args, 3);
    result = eval(make_list(reduce_expr), env);
    printf("Test 5: Reduce result: %f (expected: 6.0)\n", result->number);

    */

    gc(env);
}

int main() {
    init_object_pool();
    run_tests();
    free_object_pool();
    return 0;
}