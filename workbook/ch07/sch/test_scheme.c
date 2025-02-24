#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "scheme.h"
#include "memory.h"


void test_create_number() {
    Expr *num = create_number(42);

    assert(num != NULL);
    assert(num->type == NUMBER);
    assert(num->value.num == 42);

    free_expr(num);

    printf("test_create_number passed.\n");
}


void test_create_symbol() {
    Expr *sym = create_symbol("hello");

    assert(sym != NULL);
    assert(sym->type == SYMBOL);
    assert(strcmp(sym->value.sym, "hello") == 0);

    free_expr(sym);

    printf("test_create_symbol passed.\n");
}


void test_create_cons_and_accessors() {
    Expr *num = create_number(42);
    Expr *sym = create_symbol("world");
    Expr *pair = create_cons(num, sym);

    assert(pair != NULL);
    assert(pair->type == LIST);
    assert(car(pair) == num);
    assert(cdr(pair) == sym);

//  free_expr(sym);
//  free_expr(num);
    free_expr(pair); // free from top only

    printf("test_create_cons_and_accessors passed.\n");
}


void test_env_set_and_get() {
    Env *env = create_env(NULL);
    Expr *num = create_number(42);

    env_set(env, "x", num);
    Expr *retrieved = env_get(env, "x");

    assert(retrieved != NULL);
    assert(retrieved->type == NUMBER);
    assert(retrieved->value.num == 42);

//  free_expr(num);

//  for (int i = 0; i < env->size; i++) {
//      free(env->names[i]);
//  }
//  free(env->names);
//  free(env->values);
    free_env(env);

    printf("test_env_set_and_get passed.\n");
}


void test_eval_number() {
    Env *env = create_env(NULL);
    Expr *num = create_number(42);

    Expr *result = eval(num, env);
    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 42);

//  free(num);

    free_env(env);

    printf("test_eval_number passed.\n");
}


void test_quote() {
    Env *env = create_env(NULL);

    // (quote (1 2 3))
    Expr *quoted_list = create_cons(
        create_number(1),
        create_cons(
            create_number(2),
            create_cons(
                create_number(3),
                NULL
            )
        )
    );
    Expr *quote_expr = create_cons(
        create_symbol("quote"),
        create_cons(
            quoted_list,
            NULL
        )
    );

    Expr *result = eval(quote_expr, env);

    assert(result != NULL);
    assert(result->type == LIST);
    assert(car(result)->type == NUMBER && car(result)->value.num == 1);
    assert(car(cdr(result))->type == NUMBER && car(cdr(result))->value.num == 2);
    assert(car(cdr(cdr(result)))->type == NUMBER && car(cdr(cdr(result)))->value.num == 3);

//  free(quote_expr);
//  free(quoted_list);

    free_env(env);

    printf("test_quote passed.\n");
}


void test_eval() {
    Env *env = create_env(NULL);

    // (eval '(+ 1 2))
    Expr *add_expr = create_cons(
        create_symbol("+"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *quoted_add_expr = create_cons(
        create_symbol("quote"),
        create_cons(
            add_expr,
            NULL
        )
    );
    Expr *eval_expr = create_cons(
        create_symbol("eval"),
        create_cons(
            quoted_add_expr,
            NULL
        )
    );

    Expr *result = eval(eval_expr, env);

    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 3);

//  free(eval_expr);
//  free(quoted_add_expr);
//  free(add_expr);

    free_env(env);

    printf("test_eval passed.\n");
}


void test_eval_symbol() {
    Env *env = create_env(NULL);
    Expr *num = create_number(42);
    env_set(env, "x", num);

    Expr *sym = create_symbol("x");
    Expr *result = eval(sym, env);

    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 42);

//  free(sym->value.sym);
//  free(sym);
//  free(num);
//  for (int i = 0; i < env->size; i++) {
//      free(env->names[i]);
//  }
//  free(env->names);
//  free(env->values);

    free_env(env);

    printf("test_eval_symbol passed.\n");
}


void test_eval_define() {
    Env *env = create_env(NULL);
    Expr *define_expr = create_cons(
        create_symbol("define"),
        create_cons(create_symbol("x"), create_cons(create_number(42), NULL))
    );

    eval(define_expr, env);
    Expr *result = env_get(env, "x");

    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 42);

//    for (int i = 0; i < env->size; i++) {
//        free(env->names[i]);
//    }
//    free(env->names);
//    free(env->values);
//    free(define_expr->value.pair.cdr->value.pair.cdr);
//    free(define_expr->value.pair.cdr);
//   free(define_expr);

    free_env(env);

    printf("test_eval_define passed.\n");
}


void test_eval_if() {
    Env *env = create_env(NULL);
    Expr *if_expr = create_cons(
        create_symbol("if"),
        create_cons(
            create_number(1),
            create_cons(create_number(42), create_cons(create_number(0), NULL))
        )
    );

    Expr *result = eval(if_expr, env);
    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 42);

//    free(if_expr->value.pair.cdr->value.pair.cdr->value.pair.cdr);
//    free(if_expr->value.pair.cdr->value.pair.cdr);
//    free(if_expr->value.pair.cdr);
//    free(if_expr);

    free(env);
    printf("test_eval_if passed.\n");
}


void test_eval_set() {
    Env *env = create_env(NULL);

    Expr *define_expr = create_cons(
        create_symbol("define"),
        create_cons(create_symbol("x"), create_cons(create_number(42), NULL))
    );
    eval(define_expr, env);

    Expr *x_value = env_get(env, "x");
    assert(x_value != NULL);
    assert(x_value->type == NUMBER);
    assert(x_value->value.num == 42);

    Expr *set_expr = create_cons(
        create_symbol("set!"),
        create_cons(create_symbol("x"), create_cons(create_number(100), NULL))
    );
    eval(set_expr, env);

    x_value = env_get(env, "x");
    assert(x_value != NULL);
    assert(x_value->type == NUMBER);
    assert(x_value->value.num == 100);

//    for (int i = 0; i < env->size; i++) {
//        free(env->names[i]);
//    }
//    free(env->names);
//    free(env->values);
//    free(define_expr->value.pair.cdr->value.pair.cdr);
//    free(define_expr->value.pair.cdr);
//    free(define_expr);
//    free(set_expr->value.pair.cdr->value.pair.cdr);
//    free(set_expr->value.pair.cdr);
//    free(set_expr);

    free_env(env);

    printf("test_eval_set passed.\n");
}


void test_begin() {
    Env *env = create_env(NULL);

    // (begin (define x 10) (define y 20) (+ x y))
    Expr *begin_expr = create_cons(
        create_symbol("begin"),
        create_cons(
            create_cons(
                create_symbol("define"),
                create_cons(
                    create_symbol("x"),
                    create_cons(create_number(10), NULL)
                )
            ),
            create_cons(
                create_cons(
                    create_symbol("define"),
                    create_cons(
                        create_symbol("y"),
                        create_cons(create_number(20), NULL)
                    )
                ),
                create_cons(
                    create_cons(
                        create_symbol("+"),
                        create_cons(
                            create_symbol("x"),
                            create_cons(create_symbol("y"), NULL)
                        )
                    ),
                    NULL
                )
            )
        )
    );


    // Evaluate the begin expression
    Expr *result = eval(begin_expr, env);

    // Verify the result
    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 30);

    // Clean up
//    free_expr(begin_expr);
    free_env(env);

    printf("test_begin passed.\n");
}


void test_let() {
    Env *env = create_env(NULL);

    // (let ((x 10) (y 20)) (+ x y))
    Expr *let_expr = create_cons(
        create_symbol("let"),
        create_cons(
            create_cons(
                create_cons(
                    create_symbol("x"),
                    create_cons(create_number(10), NULL)
                ),
                create_cons(
                    create_cons(
                        create_symbol("y"),
                        create_cons(create_number(20), NULL)
                    ),
                    NULL
                )
            ),
            create_cons(
                create_cons(
                    create_symbol("+"),
                    create_cons(
                        create_symbol("x"),
                        create_cons(create_symbol("y"), NULL)
                    )
                ),
                NULL
            )
        )
    );

    // Evaluate the let expression
    Expr *result = eval(let_expr, env);

    // Verify the result
    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 30);

    // Clean up
    free_expr(let_expr);
    free_env(env); // Free the parent environment separately

    printf("test_let passed.\n");
}


void create_and_eval_define(Env *env, const char *var_name, Expr *value) {
    Expr *define_expr = create_cons(
        create_symbol("define"),
        create_cons(create_symbol(var_name), create_cons(value, NULL))
    );
    if (!define_expr) {
        fprintf(stderr, "Error: Failed to create define expression for %s\n", var_name);
        exit(1);
    }
    eval(define_expr, env);
}

Expr* create_condition(const char *var_name, int compare_value) {
    Expr *condition = create_cons(
        create_symbol("<"),
        create_cons(create_symbol(var_name), create_cons(create_number(compare_value), NULL))
    );
    if (!condition) {
        fprintf(stderr, "Error: Failed to create condition expression\n");
        exit(1);
    }
    return condition;
}


Expr* create_body(const char *var_name) {
    Expr *plus_expr = create_cons(
        create_symbol("+"),
        create_cons(create_symbol(var_name), create_cons(create_number(1), NULL))
    );
    if (!plus_expr) {
        fprintf(stderr, "Error: Failed to create plus expression\n");
        exit(1);
    }
    printf("before print_expr\n");
    print_expr(plus_expr);
    print_env(NULL);
    printf("after print_expr\n");

    Expr *body = create_cons(
        create_symbol("define"),
        create_cons(create_symbol(var_name), create_cons(plus_expr, NULL))
    );
    if (!body) {
        fprintf(stderr, "Error: Failed to create body expression\n");
        exit(1);
    }
    printf("before return body\n");
    print_expr(body);
    print_env(NULL);
    printf("after return body\n");


    return body;
}


void create_and_eval_while(Env *env, Expr *condition, Expr *body) {
    Expr *while_expr = create_cons(
        create_symbol("while"),
        create_cons(condition, create_cons(body, NULL))
    );
    printf("after create_and_eval_while\n");
    if (!while_expr) {
        fprintf(stderr, "Error: Failed to create while expression\n");
        exit(1);
    }
    printf("before eval\n");
    printf("condition= %s\n", condition->value.pair.car->value.pair.car->value.sym);
    printf("body= %s\n", body->value.pair.car->value.sym);
    printf("while_expr= %s\n", while_expr->value.pair.car->value.sym);

    print_env(env);
    eval(while_expr, env);
    printf("after eval\n");
}


void verify_x_value(Env *env, const char *var_name, int expected_value) {
    Expr *x_value = env_get(env, var_name);
    if (!x_value) {
        fprintf(stderr, "Error: Failed to get value of %s\n", var_name);
        exit(1);
    }
    assert(x_value != NULL);
    assert(x_value->type == NUMBER);
    assert(x_value->value.num == expected_value);
}

void test_eval_while() {

    printf("enter test_eval_while\n");
    Env *env = create_env(NULL);
    if (!env) {
        fprintf(stderr, "Error: Failed to create environment\n");
        exit(1);
    }

    printf("create_and_eval_define\n");
    create_and_eval_define(env, "x", create_number(0));

    printf("verify_x_value\n");
    verify_x_value(env, "x", 0);

    printf("create_condition\n");
    Expr *condition = create_condition("x", 5);

    printf("create_body\n");
    Expr *body = create_body("x");

    printf("create_and_eval_while\n");
    create_and_eval_while(env, condition, body);

    printf("verify_x_value\n");
    verify_x_value(env, "x", 5);


//    for (int i = 0; i < env->size; i++) {
//        free(env->names[i]);
//    }
//    free(env->names);
//    free(env->values);
//    free(env);

    free_env(env);
    printf("test_eval_while passed.\n");
}

int main() {
    test_create_number();
    test_create_symbol();
    test_create_cons_and_accessors();
    test_env_set_and_get();
    test_eval_number();
    test_quote();
    test_eval();
    test_eval_define();
    test_eval_if();
    test_eval_set();
    test_begin();
    test_let();
    test_eval_symbol();
    test_eval_while();

    printf("All tests passed.\n");
    return 0;
}
