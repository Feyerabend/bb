
## Minimal Scheme: Schr

This code implements a simple Scheme/Lisp-like interpreter in C. It includes fundamental
Lisp structures, an evaluator, an environment for symbol lookup, support for functions
(both built-in and user-defined), and basic test cases. Below are the key aspects worth noting:

1. Data Structures
- LispObject: Represents a Lisp value, which can be a number, symbol, list, or function.
- LispList: Represents a linked list (similar to cons cells in Lisp).
- LispFunction: Encapsulates functions, supporting both built-in functions and user-defined lambdas.
- Environment: Implements a symbol table (scoped environment) where symbols are mapped to values.

2. Memory Management and Object Creation
- Functions like make_number(), make_symbol(), and make_list() allocate memory dynamically.
- strdup() is used for copying strings to avoid modifying original literals.

3. Evaluation (eval function)
- Evaluates different types of Lisp expressions:
- Numbers return themselves.
- Symbols are looked up in the environment.
- Lists are evaluated as function applications or special forms.
- Handles special forms like:
- quote to return unevaluated expressions.
- define to define new variables.
- lambda to create functions.
- Implements tail call optimisation by using a loop instead of recursion when evaluating functions.

4. Function Application (apply_function function)
- Evaluates function arguments before calling the function.
- Distinguishes between built-in and user-defined functions.

5. Built-in Functions
- Arithmetic: +, -, *
- Conditional evaluation: if
- Equality check: eq?
- Recursive factorial function (builtin_fact), using memoization to store previously computed values.

6. Environment (env_lookup, env_define)
- Supports a hierarchical scope system where variables are looked up in enclosing environments.

7. Testing and Debugging
- The DEBUG macro is used to print evaluation steps.
- The run_tests function contains various test cases for numbers, symbols, addition, quoting, lambda expressions, and factorial.

Key Takeaways
- This interpreter captures essential Lisp semantics while keeping the implementation compact.
- Tail call optimisation allows efficient recursion handling.
- Symbol resolution follows a simple lexical scoping rule.
- Memoization optimises recursive computations like factorial.
- Error handling is minimal (e.g., missing memory management for garbage collection).



### Test 1: Number

```c
LispObject *num = make_number(42);
LispObject *result = eval(num, env);
printf("Test 1: %f (expected: 42.0)\n", result->number);
```

*Scheme Expression*
```scheme
42
```

*Explanation*:
- The expression is simply the number `42`.



### Test 2: Symbol

```c
LispObject *symbol = make_symbol("x");
env_define(env, "x", make_number(10));
result = eval(symbol, env);
printf("Test 2: %f (expected: 10.0)\n", result->number);
```

**Scheme Expression**:
```scheme
(define x 10)
x
```

**Explanation**:
- The symbol `x` is defined as `10`.
- Evaluating `x` returns `10`.

---

### **3. Test 3: Addition**
**Code**:
```c
LispObject *one = make_number(1);
LispObject *two = make_number(2);
LispObject *three = make_number(3);
LispObject *plus = make_symbol("+");
LispObject *args[] = {plus, one, two, three};
LispList *expr = make_list_from_array(args, 4);
result = eval(make_list(expr), env);
printf("Test 3: %f (expected: 6.0)\n", result->number);
```

**Scheme Expression**:
```scheme
(+ 1 2 3)
```

**Explanation**:
- The expression adds the numbers `1`, `2`, and `3`, resulting in `6`.

---

### **4. Test 4: Quote**
**Code**:
```c
LispObject *quote = make_symbol("quote");
LispObject *list_args[] = {one, two, three};
LispList *quoted_list = make_list_from_array(list_args, 3);
LispObject *quote_args[] = {quote, make_list(quoted_list)};
LispList *quote_expr = make_list_from_array(quote_args, 2);
result = eval(make_list(quote_expr), env);
```

**Scheme Expression**:
```scheme
(quote (1 2 3))
```

**Explanation**:
- The `quote` special form prevents evaluation of the list `(1 2 3)`.
- The result is the list `(1 2 3)`.

---

### **5. Test 5: Lambda**
**Code**:
```c
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
```

**Scheme Expression**:
```scheme
((lambda (x) (+ x 1)) 5)
```

**Explanation**:
- A lambda function is defined with one parameter `x`.
- The body of the lambda is `(+ x 1)`.
- The lambda is applied to the argument `5`, resulting in `6`.

---

### **6. Test 6: Recursive Factorial**
**Code**:
```c
LispObject *n = make_symbol("n");
LispList *fact_params_list = cons(n, NULL);
LispObject *fact_params = make_list(fact_params_list);

LispObject *eq_list = make_list(
    make_list_from_array((LispObject*[]){make_symbol("eq?"), n, make_number(0)}, 3)
);

LispObject *minus_expr = make_list(
    make_list_from_array((LispObject*[]){make_symbol("-"), n, make_number(1)}, 3)
);

LispObject *fact_call = make_list(
    make_list_from_array((LispObject*[]){make_symbol("fact"), minus_expr}, 2)
);

LispObject *mult_expr = make_list(
    make_list_from_array((LispObject*[]){make_symbol("*"), n, fact_call}, 3)
);

LispObject *fact_body = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("if"),
        eq_list,
        make_number(1),
        mult_expr
    }, 4)
);

LispObject *lambda_fact = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("lambda"),
        fact_params,
        fact_body
    }, 3)
);

env_define(env, "fact", eval(lambda_fact, env));

LispObject *fact_call_expr = make_list(
    make_list_from_array((LispObject*[]){make_symbol("fact"), make_number(5)}, 2)
);
result = eval(fact_call_expr, env);
printf("Test 6: Factorial of 5: %f (expected: 120.0)\n", result->number);
```

**Scheme Expression**:
```scheme
(define fact
  (lambda (n)
    (if (eq? n 0)
        1
        (* n (fact (- n 1)))))

(fact 5)
```

**Explanation**:
- A recursive factorial function is defined using `lambda`.
- The base case is `(eq? n 0)`, which returns `1`.
- The recursive case multiplies `n` by the factorial of `(- n 1)`.
- The function is called with `5`, resulting in `120`.

---

### **7. Test 7: Tail-Recursive Sum**
**Code**:
```c
LispObject *acc = make_symbol("acc");

LispObject *sum_eq = make_list(
    make_list_from_array((LispObject*[]){make_symbol("eq?"), n, make_number(0)}, 3)
);

LispObject *sum_minus = make_list(
    make_list_from_array((LispObject*[]){make_symbol("-"), n, make_number(1)}, 3)
);

LispObject *sum_add = make_list(
    make_list_from_array((LispObject*[]){make_symbol("+"), acc, n}, 3)
);

LispObject *sum_recurse = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("sum"),
        sum_minus,
        sum_add
    }, 3)
);

LispObject *sum_body = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("if"),
        sum_eq,
        acc,
        sum_recurse
    }, 4)
);

LispObject *lambda_sum = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("lambda"),
        make_list(cons(n, cons(acc, NULL))),
        sum_body
    }, 3)
);

env_define(env, "sum", eval(lambda_sum, env));

LispObject *sum_call = make_list(
    make_list_from_array((LispObject*[]){
        make_symbol("sum"),
        make_number(1000),
        make_number(0)
    }, 3)
);
result = eval(sum_call, env);
printf("Test 7: Sum from 0 to 1000: %f (expected: 500500.0)\n", result->number);
```

**Scheme Expression**:
```scheme
(define sum
  (lambda (n acc)
    (if (eq? n 0)
        acc
        (sum (- n 1) (+ acc n)))))

(sum 1000 0)
```

**Explanation**:
- A tail-recursive sum function is defined using `lambda`.
- The base case is `(eq? n 0)`, which returns `acc`.
- The recursive case adds `n` to `acc` and calls `sum` with `(- n 1)`.
- The function is called with `1000` and `0`, resulting in `500500`.

---

### **Summary**
Here’s how the **AST formulations** in the code correspond to **classical Scheme expressions**:

| Test | Scheme Expression |
|------|-------------------|
| 1    | `42`              |
| 2    | `(define x 10)` and `x` |
| 3    | `(+ 1 2 3)`       |
| 4    | `(quote (1 2 3))` |
| 5    | `((lambda (x) (+ x 1)) 5)` |
| 6    | `(define fact (lambda (n) (if (eq? n 0) 1 (* n (fact (- n 1)))))` and `(fact 5)` |
| 7    | `(define sum (lambda (n acc) (if (eq? n 0) acc (sum (- n 1) (+ acc n)))))` and `(sum 1000 0)` |

