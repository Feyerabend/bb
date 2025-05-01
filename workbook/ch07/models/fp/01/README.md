
## Some Lisp Samples

This interpreter can naturally be extended further, but the main goal of these folders
is to illustrate how *functional languages* work. Since we did not assume prior knowledge
of functional programming, we use a simple interpreter that can test some core features
through Python. Here are two notable examples: the Y combinator and a Lisp interpreter.


### Y Combinator (Anonymous Recursion)

The Lisp interpreter doesn’t support define inside lambda, so we need a way to
create anonymous recursion. The Y combinator enables recursion without naming functions.

```lisp
(define Y
  (lambda (f)
    ((lambda (x) (f (lambda (y) ((x x) y))))
     (lambda (x) (f (lambda (y) ((x x) y)))))))

(define factorial
  (Y (lambda (fact)
       (lambda (n)
         (if (<= n 1)
             1
             (* n (fact (- n 1))))))))

(factorial 5)  ;; Output: 120
```

This defines the Y combinator and then uses it to create a recursive factorial function.



### Tiny Lisp Interpreter (Lisp in Lisp)

Let’s write a tiny Lisp evaluator inside your Lisp dialect! This interpreter will
support basic arithmetic and function application.

```lisp
(define eval
  (lambda (expr env)
    (if (list? expr)
        (if (symbol? (car expr))
            (if (= (car expr) '+) (+ (eval (cadr expr) env) (eval (caddr expr) env))
                (if (= (car expr) '-) (- (eval (cadr expr) env) (eval (caddr expr) env))
                    (if (= (car expr) '* ) (* (eval (cadr expr) env) (eval (caddr expr) env))
                        (if (= (car expr) '/') (/ (eval (cadr expr) env) (eval (caddr expr) env))
                            ((eval (car expr) env) (eval (cadr expr) env) (eval (caddr expr) env))))))
            (env expr))
        expr)))

(define qu
  (lambda (x) x))

(eval (qu (+ 1 2)) (lambda (x) x)) ;; Output: 3
```

This is a tiny interpreter inside the Lisp, evaluating basic arithmetic expressions. The ultimate test of a Lisp interpreter’s completeness is whether it can interpret itself. This is often called a meta-circular evaluator—an interpreter for Lisp written in Lisp itself.

Lisp is unique among programming languages because its syntax is directly represented as its own data structures (lists). This means that writing an interpreter for Lisp in Lisp is relatively straightforward compared to other languages. A properly functioning Lisp interpreter should be able to evaluate Lisp code that defines and runs another Lisp interpreter.

