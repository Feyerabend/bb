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

void test_less_than() {
    Env *env = create_env(NULL);

    // Test (< 1 2)
    Expr *less_than_expr = create_cons(
        create_symbol("<"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *less_than_result = eval(less_than_expr, env);

    // result is 1 (true)
    assert(less_than_result != NULL);
    assert(less_than_result->type == NUMBER);
    assert(less_than_result->value.num == 1);

    // (< 2 1)
    Expr *less_than_expr2 = create_cons(
        create_symbol("<"),
        create_cons(
            create_number(2),
            create_cons(
                create_number(1),
                NULL
            )
        )
    );
    Expr *less_than_result2 = eval(less_than_expr2, env);

    // result is 0 (false)
    assert(less_than_result2 != NULL);
    assert(less_than_result2->type == NUMBER);
    assert(less_than_result2->value.num == 0);

    free_env(env);
    printf("test_less_than passed.\n");
}

void test_greater_than() {
    Env *env = create_env(NULL);

    // Test (> 2 1)
    Expr *greater_than_expr = create_cons(
        create_symbol(">"),
        create_cons(
            create_number(2),
            create_cons(
                create_number(1),
                NULL
            )
        )
    );
    Expr *greater_than_result = eval(greater_than_expr, env);

    // result is 1 (true)
    assert(greater_than_result != NULL);
    assert(greater_than_result->type == NUMBER);
    assert(greater_than_result->value.num == 1);

    // (> 1 2)
    Expr *greater_than_expr2 = create_cons(
        create_symbol(">"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *greater_than_result2 = eval(greater_than_expr2, env);

    // result is 0 (false)
    assert(greater_than_result2 != NULL);
    assert(greater_than_result2->type == NUMBER);
    assert(greater_than_result2->value.num == 0);

    free_env(env);
    printf("test_greater_than passed.\n");
}

void test_equal_to() {
    Env *env = create_env(NULL);

    // Test (= 2 2)
    Expr *equal_to_expr = create_cons(
        create_symbol("="),
        create_cons(
            create_number(2),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *equal_to_result = eval(equal_to_expr, env);

    // result is 1 (true)
    assert(equal_to_result != NULL);
    assert(equal_to_result->type == NUMBER);
    assert(equal_to_result->value.num == 1);

    // (= 1 2)
    Expr *equal_to_expr2 = create_cons(
        create_symbol("="),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *equal_to_result2 = eval(equal_to_expr2, env);

    // result is 0 (false)
    assert(equal_to_result2 != NULL);
    assert(equal_to_result2->type == NUMBER);
    assert(equal_to_result2->value.num == 0);

    free_env(env);
    printf("test_equal_to passed.\n");
}

void test_car2() {
    Env *env = create_env(NULL);

    // (car (list 1 2 3))
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                create_cons(
                    create_number(3),
                    NULL
                )
            )
        )
    );
    Expr *car_expr = create_cons(
        create_symbol("car"),
        create_cons(list_expr, NULL)
    );
    Expr *car_result = eval(car_expr, env);

    // result is 1
    assert(car_result != NULL);
    assert(car_result->type == NUMBER);
    assert(car_result->value.num == 1);

    free_env(env);
    printf("test_car passed.\n");
}

void test_cdr2() {
    Env *env = create_env(NULL);

    // Test (cdr (list 1 2 3))
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                create_cons(
                    create_number(3),
                    NULL
                )
            )
        )
    );
    Expr *cdr_expr = create_cons(
        create_symbol("cdr"),
        create_cons(list_expr, NULL)
    );
    Expr *cdr_result = eval(cdr_expr, env);

    // Verify the result is (2 3)
    assert(cdr_result != NULL);
    assert(cdr_result->type == LIST);
    assert(car(cdr_result)->value.num == 2); // First element is 2
    assert(car(cdr(cdr_result))->value.num == 3); // Second element is 3
    assert(cdr(cdr(cdr_result)) == NULL); // End of list

    free_env(env);
    printf("test_cdr passed.\n");
}

void test_create_cons_and_accessors() {
    Expr *num = create_number(42);
    Expr *sym = create_symbol("world");
    Expr *pair = create_cons(num, sym);

    assert(pair != NULL);
    assert(pair->type == LIST);
    assert(car(pair) == num);
    assert(cdr(pair) == sym);

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

    Expr *result = eval(begin_expr, env);

    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 30);

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

    Expr *result = eval(let_expr, env);

    assert(result != NULL);
    assert(result->type == NUMBER);
    assert(result->value.num == 30);

    free_expr(let_expr); // needed?
    free_env(env);

    printf("test_let passed.\n");
}


// section

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

    Expr *body = create_cons(
        create_symbol("define"),
        create_cons(create_symbol(var_name), create_cons(plus_expr, NULL))
    );
    if (!body) {
        fprintf(stderr, "Error: Failed to create body expression\n");
        exit(1);
    }

    return body;
}


void create_and_eval_while(Env *env, Expr *condition, Expr *body) {
    Expr *while_expr = create_cons(
        create_symbol("while"),
        create_cons(condition, create_cons(body, NULL))
    );

    if (!while_expr) {
        fprintf(stderr, "Error: Failed to create while expression\n");
        exit(1);
    }

    eval(while_expr, env);
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
    Env *env = create_env(NULL);
    if (!env) {
        fprintf(stderr, "Error: Failed to create environment\n");
        exit(1);
    }

    create_and_eval_define(env, "x", create_number(0));
    verify_x_value(env, "x", 0);

    Expr *condition = create_condition("x", 5);
    Expr *body = create_body("x");
    create_and_eval_while(env, condition, body);

    verify_x_value(env, "x", 5);

    free_env(env);
    printf("test_eval_while passed.\n");
}

void test_predicates() {
    Env *env = create_env(NULL);

    // null?
    Expr *null_expr = create_cons(
        create_symbol("null?"),
        create_cons(
            create_list((Expr*[]){NULL}), // empty list
            NULL
        )
    );
    Expr *null_result = eval(null_expr, env);
    assert(null_result != NULL);
    assert(null_result->type == NUMBER);
    assert(null_result->value.num == 1);

    // number?
    Expr *num_expr = create_cons(
        create_symbol("number?"),
        create_cons(
            create_number(42), // number
            NULL
        )
    );
    Expr *num_result = eval(num_expr, env);
    assert(num_result != NULL);
    assert(num_result->type == NUMBER);
    assert(num_result->value.num == 1);

    // symbol?
    Expr *sym_expr = create_cons(
        create_symbol("symbol?"),
        create_cons(
            create_symbol("hello"), // symbol (literal)
            NULL
        )
    );
    Expr *sym_result = eval(sym_expr, env);
    assert(sym_result != NULL);
    assert(sym_result->type == NUMBER);
    assert(sym_result->value.num == 1);

    // equal?
    Expr *equal_expr = create_cons(
        create_symbol("equal?"),
        create_cons(
            create_cons(create_number(1), create_cons(create_number(2), NULL)), // pair
            create_cons(
                create_cons(create_number(1), create_cons(create_number(2), NULL)), // same pair (copy)
                NULL
            )
        )
    );
    Expr *equal_result = eval(equal_expr, env);
    assert(equal_result != NULL);
    assert(equal_result->type == NUMBER);
    assert(equal_result->value.num == 1);

    free_env(env);
    printf("test_predicates passed.\n");
}

void test_pair() {
    Env *env = create_env(NULL);

    // pair (1 . 2)
    Expr *pair = create_cons(create_number(1), create_number(2));

    // expression (pair? (1 . 2))
    Expr *pair_expr = create_cons(
        create_symbol("pair?"),
        create_cons(
            pair,
            NULL
        )
    );
    Expr *pair_result = eval(pair_expr, env);
    print_expr(pair_result); printf("\n");

    assert(pair_result != NULL);
    assert(pair_result->type == NUMBER);
    assert(pair_result->value.num == 1);

    free_env(env);
    printf("test_predicates passed.\n");
}

void test_equal_pair() {
    Env *env = create_env(NULL);

    // equal? with identical pairs
    Expr *equal_expr = create_cons(
        create_symbol("equal?"),
        create_cons(
            create_cons(create_number(1), create_number(2)), // Pair (1 . 2)
            create_cons(
                create_cons(create_number(1), create_number(2)), // Pair (1 . 2)
                NULL
            )
        )
    );
    Expr *equal_result = eval(equal_expr, env);
    assert(equal_result != NULL);
    assert(equal_result->type == NUMBER);
    assert(equal_result->value.num == 1);

    free_env(env);
    printf("test_equal passed.\n");
}

void test_equal() {
    Env *env = create_env(NULL);

    // (eq? 'hello 'hello)
    Expr *eq_expr = create_cons(
        create_symbol("equal?"),
        create_cons(
            create_cons(create_symbol("quote"), create_cons(create_symbol("hello"), NULL)), // '(hello)
            create_cons(
                create_cons(create_symbol("quote"), create_cons(create_symbol("hello"), NULL)), // '(hello)
                NULL
            )
        )
    );

    Expr *eq_result = eval(eq_expr, env);
    assert(eq_result != NULL);
    assert(eq_result->type == NUMBER);
    assert(eq_result->value.num == 1);

    free_env(env);
    printf("test_eq passed.\n");
}

void test_cons() {
    Env *env = create_env(NULL);

    // cons
    Expr *cons_expr = create_cons(
        create_symbol("cons"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *cons_result = eval(cons_expr, env);
    assert(cons_result != NULL);
    assert(cons_result->type == LIST);
    assert(car(cons_result)->value.num == 1);
    assert(cdr(cons_result)->value.num == 2);

    free_env(env);
    printf("test_cons passed.\n");
}

void test_car() {
    Env *env = create_env(NULL);

    // car
    Expr *car_expr = create_cons(
        create_symbol("car"),
        create_cons(
            create_cons(create_number(1), create_number(2)),
            NULL
        )
    );
    Expr *car_result = eval(car_expr, env);
    assert(car_result != NULL);
    assert(car_result->type == NUMBER);
    assert(car_result->value.num == 1);

    free_env(env);
    printf("test_car passed.\n");
}

void test_cdr() {
    Env *env = create_env(NULL);

    // cdr
    Expr *cdr_expr = create_cons(
        create_symbol("cdr"),
        create_cons(
            create_cons(create_number(1), create_number(2)),
            NULL
        )
    );
    Expr *cdr_result = eval(cdr_expr, env);
    assert(cdr_result != NULL);
    assert(cdr_result->type == NUMBER);
    assert(cdr_result->value.num == 2);

    free_env(env);
    printf("test_cdr passed.\n");
}

void test_list() {
    Env *env = create_env(NULL);

    // list
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                NULL
            )
        )
    );
    Expr *list_result = eval(list_expr, env);

    assert(list_result != NULL);
    assert(list_result->type == LIST);
    assert(car(list_result)->value.num == 1);
    assert(car(cdr(list_result))->value.num == 2);

    free_env(env);
    printf("test_list passed.\n");
}

void test_list_basic() {
    Env *env = create_env(NULL);

    // (list 1 2 3)
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(1),
            create_cons(
                create_number(2),
                create_cons(
                    create_number(3),
                    NULL
                )
            )
        )
    );
    Expr *list_result = eval(list_expr, env);

    assert(list_result != NULL);
    assert(list_result->type == LIST);
    assert(car(list_result)->value.num == 1); // First = 1
    assert(car(cdr(list_result))->value.num == 2); // Second = 2
    assert(car(cdr(cdr(list_result)))->value.num == 3); // Third = 3
    assert(cdr(cdr(cdr(list_result))) == NULL); // End of list

    free_env(env);
    printf("test_list_basic passed.\n");
}

void test_list_empty() {
    Env *env = create_env(NULL);

    // (list) should return an empty list, not NULL
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_empty_list()
    );

    printf("empty list: ");
    print_expr(list_expr);
    Expr *list_result = eval(list_expr, env);

    printf("eval empty list: ");
    print_expr(list_result);

    // Ensure it returns a valid empty list instead of NULL
    assert(list_result != NULL);
    assert(is_empty_list(list_result)); // Check for empty list

    free_env(env);
    printf("test_list_empty passed.\n");
}

void test_list_nested() {
    Env *env = create_env(NULL);

    // (list 1 (list 2 3) 4)
    Expr *inner_list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(2),
            create_cons(
                create_number(3),
                NULL
            )
        )
    );
    Expr *list_expr = create_cons(
        create_symbol("list"),
        create_cons(
            create_number(1),
            create_cons(
                inner_list_expr,
                create_cons(
                    create_number(4),
                    NULL
                )
            )
        )
    );
    Expr *list_result = eval(list_expr, env);

    assert(list_result != NULL);
    assert(list_result->type == LIST);

    print_expr(list_result); printf("\n");

    // First = 1
    assert(car(list_result)->value.num == 1);

    // Second = (2 3)
    Expr *nested_list = car(cdr(list_result));
    assert(nested_list != NULL);
    assert(nested_list->type == LIST);
    assert(car(nested_list)->value.num == 2); // First e= 2
    assert(car(cdr(nested_list))->value.num == 3); // Second = 3
    assert(cdr(cdr(nested_list)) == NULL); // End of nested list

    // Third = 4
    assert(car(cdr(cdr(list_result)))->value.num == 4);

    // End of list
    assert(cdr(cdr(cdr(list_result))) == NULL);

    free_env(env);
    printf("test_list_nested passed.\n");
}


int main() {
    test_create_number();
    test_create_symbol();
    test_less_than();
    test_greater_than();
    test_equal_to();
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
    test_predicates();
    test_pair();
    test_equal();
    test_equal_pair();
    test_car();
    test_car2();
    test_cdr();
    test_cdr2();
    test_cons();
    test_list();
    test_list_basic();
    test_list_empty();
    test_list_nested();

    printf("All tests passed.\n");
    return 0;
}
