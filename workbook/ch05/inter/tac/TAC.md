
## TAC: Three Address Code (TAC)

Besides expressions, a complete TAC representation also includes constructs for control flow,
function calls, memory management, and other programming features.

__1. Basic Concepts__

- Instruction Format: Each TAC instruction has at most three operands:
  * x = y op z (binary operation)
  * x = op y (unary operation)
  * x = y (assignment)
- Temporary Variables: Intermediate results are stored in temporary variables, usually denoted as t1, t2, etc.
- Labels: Used to denote targets for jumps and branches.


__2. Representing Expressions__

TAC can represent arithmetic, logical, and relational expressions:
- Arithmetic: t1 = a + b
- Logical: t2 = a && b
- Relational: t3 = a < b

Example:

```assembly
t1 = x + y
t2 = t1 * z
result = t2
```

__3. Conditional Branching__

TAC supports conditional statements using comparisons and jumps:
- if-goto: Conditional jump to a label if a condition is true.
- goto: Unconditional jump to a label.

Example (if-else):

```assembly
t1 = x < 10
if t1 goto label_1
y = y + 1
goto label_2
label_1:
y = y - 1
label_2:
```

__4. Loops__

Loops are represented using labels and jumps:
- While Loop:

```assembly
label_1:
t1 = x < 10
if not t1 goto label_2
x = x + 1
goto label_1
label_2:
```

- For Loop:

```assembly
i = 0
label_1:
t1 = i < 10
if not t1 goto label_2
body_of_loop
i = i + 1
goto label_1
label_2:
```

__5. Function Calls__

TAC handles function calls with param, call, and return instructions:
- param: Push a parameter onto the call stack.
- call: Invoke a function with a specified number of parameters.
- return: Return a value from a function.

Example (function call):

```assembly
param a
param b
call add, 2  # Call `add` with 2 parameters
result = t1  # Capture the return value in `result`
```

__6. Arrays and Memory__

TAC can represent arrays and memory access:
- Array Access:
  - Read: t1 = arr[i]
  - Write: arr[i] = t2
- Pointers:
  - Dereference: t3 = *p
  - Address-of: p = &x

Example:

```assembly
t1 = arr[i]
t2 = t1 + 1
arr[i] = t2
```

__7. Object-Oriented Features__

For object-oriented languages, TAC can represent method calls and member access:
- Member Access: t1 = obj.field
- Method Calls: t2 = obj.method()

Example:

```assembly
param obj
call obj.method, 1
t1 = t2  # Capture the return value
```

__8. Error Handling__

Control flow for exceptions can be represented using labels and jumps:

```assembly
label_try:
t1 = x / y
goto label_end
label_catch:
t2 = "Division by zero"
goto label_end
label_end:
```

__9. Advanced Features__

Phi Functions (for SSA): To handle merging variables at control flow joins.

```assembly
t1 = phi(x1, x2)
```

Inline Assembly: To include specific low-level instructions directly.


### Example: Full TAC Program

Here’s a TAC representation of a simple program:

```c
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

TAC Representation:

```assembly
label factorial:
param n
t1 = n <= 1
if t1 goto label_base_case
t2 = n - 1
param t2
call factorial, 1
t3 = t2 * n
return t3
label_base_case:
return 1
```

Benefits of TAC
- Simplified Analysis: Easier for compilers to analyze, optimize, and generate machine code.
- Portability: Language-neutral representation simplifies targeting multiple architectures.
- Optimisation: Enables techniques like dead-code elimination, constant folding, and register allocation.
