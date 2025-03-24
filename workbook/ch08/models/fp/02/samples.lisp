;; Basic Arithmetic
(+ 1 2 3 4 5)
;; 
(- 10 5)
;; 
(* 2 3 4)
;; 
(/ 100 4 5)
;; 
5
;; Comparison Operations
(= 5 5)
;; 
(< 3 7)
;; 
(>= 10 10)
;; 
(<= 8 7)
;; 
False
;; List Operations
(cons 1 2)
;; 
(cons 1 (list 2 3 4))
;; 
(car (list 5 6 7))
;; 
(cdr (list 5 6 7))
;; 
(null? ())
;; 
(length (list 1 2 3 4))
;; 
4
;; Boolean Operations
(not True)
;; 
(and True False)
;; 
(or False True)
;; 
True
;; Type Predicates
(number? 42)
;; 
(symbol? 'x)
;; 
(list? (list 1 2))
;; 
True
;; Function Definition and Application
(define double (lambda (x) (* x 2)))
(double 5)
;; 
10
;; Recursive Functions
(define factorial
  (lambda (n)
    (if (<= n 1)
        1
        (* n (factorial (- n 1))))))
(factorial 5)
;; 
120
;; Iterative Functions using set!
(define factorial-iter
  (lambda (n)
    (let ((result 1)
          (counter 1))
      (begin
        (while (<= counter n)
          (begin
            (set! result (* result counter))
            (set! counter (+ counter 1))))
        result))))
(factorial-iter 5)
;; 
120
;; Let expressions
(let ((x 5)
      (y 10))
  (+ x y))
;; 
15
;; If expressions
(if (> 5 3)
    100
    0)
;; 
100
;; Quote
;; (quote (1 2 3))
;; 
;; (1 2 3)
;; Begin
(begin
  (define x 5)
  (define y 10)
  (+ x y))
;; 
15
;; Functional Programming Utilities
(define inc (lambda (x) (+ x 1)))
(define square (lambda (x) (* x x)))
(define double (lambda (x) (* x 2)))
;; Function Composition
(define inc-then-double
  (compose double inc))
(inc-then-double 5)
;; 
12
;; Function Pipeline
(pipe 5 double inc square)
;; 
121
;; Map, Filter, Reduce
(define numbers (list 1 2 3 4 5))
(map double numbers)
;; 
(filter (lambda (x) (> x 2)) numbers)
;; 
(reduce + numbers)
;; 
15
