# Teaching Language Tutorial

This tutorial covers all features of our educational programming language.
The language is expression-based, statically typed, and immutable-by-default.

## Table of Contents

1. [Basic Values and Expressions](#1-basic-values-and-expressions)
2. [Variables](#2-variables)
3. [Operators](#3-operators)
4. [Control Flow](#4-control-flow)
5. [Functions](#5-functions)
6. [Classes and Objects](#6-classes-and-objects)
7. [Type System](#7-type-system)
8. [Advanced Examples](#8-advanced-examples)



## 1. Basic Values and Expressions

Everything in this language is an expression that returns a value.

### Literals

```
// Integers
42
-17
0

// Booleans
true
false

// Strings
"Hello, world!"
"Programming is fun"
```

### Simple Expressions

```
> 5 + 3
8

> 10 * 2
20

> 15 / 3
5

> true
True

> "hello"
hello
```



## 2. Variables

### Immutable Variables (let)

By default, variables are *immutable* - they cannot be changed after creation.

```
> let x = 10
> let y = 20
> let sum = x + y
30
```

*Key point:* Once you create `x` with `let`, you cannot reassign it!

### Mutable Variables (var)

Use `var` when you need to change a variable's value.

```
> var counter = 0
> counter = counter + 1
> counter = counter + 1
> counter
2
```

### Type Annotations (Optional)

You can explicitly specify types:

```
> let x: Int = 42
> let flag: Bool = true
> var name: String = "Alice"
```

The type checker will verify your annotations match the actual values.



## 3. Operators

### Arithmetic Operators

```
> let a = 10 + 5
15

> let b = 20 - 8
12

> let c = 6 * 7
42

> let d = 100 / 4
25
```

### Comparison Operators

All comparisons return `Bool`:

```
> 5 < 10
True

> 15 > 20
False

> 7 == 7
True

> 3 == 5
False
```

### Operator Precedence

Standard mathematical precedence:

```
> 2 + 3 * 4
14

> (2 + 3) * 4
20
```



## 4. Control Flow

### If-Then-Else Expressions

`if` is an *expression*, not a statement - it returns a value!

```
> let x = 10
> if x > 5 then 100 else 0
100

> let y = 3
> if y > 5 then 100 else 0
0
```

Both branches must return the same type:

```
> let age = 18
> let status = if age >= 18 then "adult" else "minor"
```

You can nest if expressions:

```
> let score = 85
> if score >= 90 then "A" else if score >= 80 then "B" else "C"
B
```

### While Loops

While loops return `Unit` (like void in other languages):

```
> var i = 0
> while i < 5 do i = i + 1
```

*Important:* While is for side effects (changing mutable variables). Most logic should use recursion and functions instead!



## 5. Functions

Functions are first-class values with static typing.

### Basic Function Definition

```
> fun add(x: Int, y: Int): Int = x + y
> add(3, 4)
7
```

Breakdown:
- `fun` - function keyword
- `add` - function name
- `(x: Int, y: Int)` - parameters with types
- `: Int` - return type
- `= x + y` - function body (single expression)

### Type Inference

The return type can often be inferred:

```
> fun double(x: Int) = x * 2
> double(5)
10
```

### Functions with If Expressions

```
> fun max(a: Int, b: Int) = if a > b then a else b
> max(10, 7)
10

> fun abs(x: Int) = if x < 0 then 0 - x else x
> abs(-5)
5
```

### Functions Calling Functions

```
> fun square(x: Int) = x * x
> fun sumOfSquares(a: Int, b: Int) = square(a) + square(b)
> sumOfSquares(3, 4)
25
```

### Recursive Functions

The language supports recursion for iteration:

```
> fun factorial(n: Int): Int = if n == 0 then 1 else n * factorial(n - 1)
> factorial(5)
120

> fun fibonacci(n: Int): Int = if n < 2 then n else fibonacci(n - 1) + fibonacci(n - 2)
> fibonacci(6)
8
```



## 6. Classes and Objects

Classes provide a minimal object model for grouping data and behavior.

### Defining a Class

```
> class Point(x: Int, y: Int) {
...     fun getX() = x
...     fun getY() = y
... }
```

Breakdown:
- `class Point` - class name
- `(x: Int, y: Int)` - constructor parameters (become fields)
- Methods defined with `fun` inside braces

### Creating Objects

Use the class name as a constructor (capitalized):

```
> Point(10, 20)
ObjectInstance(class_name='Point', fields={'x': 10, 'y': 20})
```

### Immutable Objects

Since objects are immutable by default, methods return *new* objects:

```
> class Point(x: Int, y: Int) {
...     fun move(dx: Int, dy: Int) = Point(x + dx, y + dy)
... }
> let p1 = Point(5, 10)
> let p2 = move(p1, 3, 4)
```

This creates a new `Point` rather than modifying the original!

### Example: Counter Class

```
> class Counter(value: Int) {
...     fun increment() = Counter(value + 1)
...     fun getValue() = value
... }
> let c1 = Counter(0)
> let c2 = increment(c1)
> let c3 = increment(c2)
```

### Example: Rectangle Class

```
> class Rectangle(width: Int, height: Int) {
...     fun area() = width * height
...     fun perimeter() = 2 * width + 2 * height
...     fun scale(factor: Int) = Rectangle(width * factor, height * factor)
... }
> let rect = Rectangle(5, 10)
> area(rect)
50
```



## 7. Type System

The language has *static typing* - all types are checked before running.

### Basic Types

- `Int` - integers
- `Bool` - true/false
- `String` - text
- `Unit` - represents "no value" (like void)
- Class types - e.g., `Point`, `Counter`

### Type Checking

The type checker ensures:

1. *Variables have consistent types:*
   ```
   let x: Int = 10  // ✓ OK
   let y: Int = true  // ✗ Error: type mismatch
   ```

2. *Function arguments match parameters:*
   ```
   fun add(x: Int, y: Int) = x + y
   add(3, 4)    // ✓ OK
   add(3, true) // ✗ Error: expected Int, got Bool
   ```

3. *If branches have same type:*
   ```
   if x > 0 then 10 else 20     // ✓ OK (both Int)
   if x > 0 then 10 else true   // ✗ Error: branches differ
   ```

4. *Operations use correct types:*
   ```
   5 + 3      // ✓ OK (Int + Int)
   5 + true   // ✗ Error: can't add Int and Bool
   ```

### Type Inference

You don't always need to write types:

```
> let x = 42              // Inferred as Int
> let flag = x > 10       // Inferred as Bool
> fun inc(n: Int) = n + 1 // Return type inferred as Int
```



## 8. Advanced Examples

### Example 1: Computing GCD

```
> fun gcd(a: Int, b: Int): Int = if b == 0 then a else gcd(b, a - b * (a / b))
> gcd(48, 18)
6
```

### Example 2: Sum of First N Numbers

```
> fun sumN(n: Int): Int = if n == 0 then 0 else n + sumN(n - 1)
> sumN(10)
55
```

### Example 3: Power Function

```
> fun power(base: Int, exp: Int): Int = if exp == 0 then 1 else base * power(base, exp - 1)
> power(2, 10)
1024
```

### Example 4: Bank Account Class

```
> class Account(balance: Int) {
...     fun deposit(amount: Int) = Account(balance + amount)
...     fun withdraw(amount: Int) = if amount > balance then Account(balance) else Account(balance - amount)
...     fun getBalance() = balance
... }
> let acc = Account(100)
> let acc2 = deposit(acc, 50)
> let acc3 = withdraw(acc2, 30)
> getBalance(acc3)
120
```

### Example 5: Temperature Converter

```
> fun celsiusToFahrenheit(c: Int) = c * 9 / 5 + 32
> fun fahrenheitToCelsius(f: Int) = (f - 32) * 5 / 9
> celsiusToFahrenheit(0)
32
> fahrenheitToCelsius(100)
37
```

### Example 6: Collatz Sequence Length

```
> fun collatz(n: Int): Int = if n == 1 then 0 else if n - n / 2 * 2 == 0 then 1 + collatz(n / 2) else 1 + collatz(3 * n + 1)
> collatz(10)
6
```

### Example 7: Using Mutable State (Counter Pattern)

```
> var total = 0
> var i = 1
> while i < 11 do total = total + i
> while i < 11 do i = i + 1
> total
55
```



## Quick Reference Card

### Variables
```
let x = 10          // immutable
var y = 20          // mutable
let z: Int = 30     // with type annotation
y = y + 1           // assignment (var only)
```

### Functions
```
fun name(param: Type): ReturnType = body
fun square(x: Int) = x * x
```

### Classes
```
class Name(field: Type, ...) {
    fun method() = expression
}
let obj = Name(value, ...)
```

### Control Flow
```
if condition then expr1 else expr2
while condition do expression
```

### Operators
```
+ - * /             // arithmetic
== < >              // comparison
```

### Types
```
Int, Bool, String, Unit
ClassName
```



## Tips for Learning

1. *Start simple:* Try basic arithmetic and variables first
2. *Think in expressions:* Everything returns a value, even `if`
3. *Embrace immutability:* Use `let` by default, `var` only when needed
4. *Use the type system:* Let it catch errors before running
5. *Recursive thinking:* Functions calling themselves replace loops
6. *Build up complexity:* Combine small functions into larger ones



## What's Next?

Future extensions to explore:
- *Pattern matching* - destructure data elegantly
- *Tuples* - group multiple values
- *Lists* - collections of elements
- *Higher-order functions* - functions that take/return functions
- *Modules* - organize code into namespaces

