
## A Simple Compiler: Three-Address Code (TAC)

Three-address code (TAC) is an intermediate representation used in compilers to simplify
and organize the process of translating high-level programming languages into machine code
or another low-level representation. It provides a structured and linear way to describe
computations and data manipulations, making it easier to perform optimizations and generate
target code. TAC operates on a simple principle:
*each operation involves at most three "addresses" or operands*,
typically comprising two sources and one destination.

The "addresses" in TAC are usually variables, constants, or temporary variables (often
denoted as t1, t2, etc.). These temporary variables help to break down complex expressions
into smaller, more manageable pieces. For instance, a compound expression like
'z = x + y * (a - b)' can be expressed in TAC as a sequence of instructions:

```
t1 = a - b
t2 = y * t1
t3 = x + t2
z = t3
```

This decomposition into simpler steps allows the compiler to analyze and manipulate the
program more effectively.

TAC is used extensively during the middle stages of compilation, typically as part of the
intermediate representation between the front-end parsing phase and the back-end code
generation phase. By working in this form, compilers can focus on optimizations such as
constant folding, dead code elimination, and common subexpression elimination. Once the
code has been optimized in TAC form, it is easier to generate efficient machine code or
bytecode for execution.

In addition to aiding in optimisation, TAC provides a platform-independent way to represent
code. This makes it useful for compilers targeting multiple architectures, as it decouples
the high-level language from the specifics of the target hardware. For example, TAC might
be translated into assembly language for a physical CPU or into bytecode for a virtual
machine, such as the Java Virtual Machine (JVM) or the Python interpreter.

TAC is a cornerstone of modern compiler design because of its simplicity, flexibility, and
ability to support both optimization and code generation. Its use is widespread in programming
languages ranging from C and Java to scripting languages like Python. By serving as a bridge
between high-level abstractions and low-level machine instructions, TAC plays a critical
role in translating complex programs into forms that computers can execute efficiently.


### Typical Instructions in TAC

In Three-Address Code (TAC), instructions are designed to operate on simple computations and
data manipulations, each involving at most three operands. The instructions are expressed in
a way that simplifies the representation of a program and allows for easy analysis and
optimization. Below is an overview of the most commonly used types of instructions in TAC
and their purposes.

#### Arithmetic Instructions

These instructions perform arithmetic operations on two operands and store the result in a third operand:
- `t1 = t2 + t3` (addition)
- `t1 = t2 - t3` (subtraction)
- `t1 = t2 * t3` (multiplication)
- `t1 = t2 / t3` (division)


#### Logical Instructions

Logical operations are used for comparisons or logical evaluations:
- `t1 = t2 && t3` (logical AND)
- `t1 = t2 || t3` (logical OR)
- `t1 = !t2` (logical NOT)


#### Relational Instructions

These instructions compare two values and store a boolean result (often 1 for true and 0 for false):
- `t1 = t2 < t3` (less than)
- `t1 = t2 <= t3` (less than or equal to)
- `t1 = t2 > t3` (greater than)
- `t1 = t2 >= t3` (greater than or equal to)
- `t1 = t2 == t3` (equality)
- `t1 = t2 != t3` (inequality)


#### Assignment Instructions

These are used to assign values to variables:
- `t1 = t2` (simple assignment)
- `t1 = constant` (assignment of a constant value)


#### Memory Access Instructions

These instructions handle array and pointer-like memory operations:
- `t1 = a[i]` (array access, load)
- `a[i] = t2` (array access, store)
- `t1 = *p` (dereferencing a pointer)
- `*p = t2` (storing a value at a pointer)


#### Control Flow Instructions

Control flow instructions manage the execution flow of the program:
- `if t1 goto L1` (conditional jump)
- `goto L2` (unconditional jump)
- `call func, n` (function call, with n arguments)
- `return t1` (return from a function with a value)
- `param t1` (pass a parameter to a function)
- `label L1` (mark a location in code)


#### Input/Output Instructions

These are less common in TAC but may be used in some representations:
- `read t1` (read input into t1)
- `write t1` (write the value of t1)


#### Temporary Variables

TAC makes extensive use of temporary variables (as 't1', 't2') to hold intermediate
results of computations or subexpressions. These temporaries simplify the handling
of complex expressions and facilitate optimisation.

For an expression like 'z = x + y * (a - b)', the TAC instructions might be:

```
t1 = a - b
t2 = y * t1
t3 = x + t2
z = t3
```

This breakdown demonstrates the step-by-step evaluation of the expression, with
temporary variables holding intermediate results.


#### Characteristics of TAC Instructions

TAC instructions are simple and uniform, making them easy to analyze and optimise.
By reducing complex operations into smaller steps, TAC enables compilers to perform
various optimisations like constant folding, common subexpression elimination, and
dead code elimination before generating the final code for the target machine.


### Some TAC Scripts

If we set aside the initial stages of compilation, such as lexical analysis (tokenisation)
and parsing, the process of compilation beginning with the AST can be illustrated through
a series of straightforward scripts:

```
tac.py -> comp.py -> vm.py
```


### Constant Folding

Constant folding is an optimisation technique where constant expressions in the code
are evaluated at compile time rather than runtime. This reduces computational overhead
during program execution. In the context of Three-Address Code (TAC), constant folding
simplifies TAC instructions by replacing computations involving only constants with their
results. See `opt.py`.

Example: If both operands in an expression are constants, the expression is evaluated at
compile time. Expressions like '7 + 9' are evaluated at compile time and replaced with
'16', making the expression simpler. In the code, 't2 = 7 + 9' it becomes 't2 = 16'.

*Advantages of Constant Folding in TAC*
1. Reduced Runtime Overhead: Evaluating constant expressions at compile time means fewer
   operations need to be performed at runtime.
2. Smaller Code: By removing intermediate computations, the resulting code can be shorter
   and easier to interpret.
3. Facilitates Further Optimisations: Simplified TAC enables additional techniques like
   dead code elimination and common subexpression elimination.

*Considerations*
1. Avoid Premature Folding: If constants are the result of a computation that should be
   deferred (such as I/O or runtime behavior), folding might change program semantics.
2. Impact on Debugging: Over-optimizing TAC may obscure the original structure of the code,
   making debugging harder.



### Common Subexpression Elimination (CSE)

Common Subexpression Elimination (CSE) identifies expressions that are computed
multiple times in a program and replaces them with a single computation, storing the
result in a temporary variable. This reduces redundant calculations, saving computation
time and improving runtime performance.

From the TAC:

```
x = 2025
y = 1477
t1 = x + y  # first instance
t2 = 7 + 9
t3 = 5 * t2
t4 = t3 / 2
t5 = t1 - t4
z = t5
t6 = x + y  # CSE, second
t7 = 0
```

We get a new TAC:

```
x = 2025
y = 1477
t1 = x + y
t2 = 16
t3 = 5 * t2
t4 = t3 / 2
t5 = t1 - t4
z = t5
t6 = t1
t7 = 0
```

Example of Common Subexpression Elimination (CSE): If an expression is repeated multiple times,
it's computed only *once* and then *reused*. If a subexpression like 'x + y' is computed more
than once ('t1 = x + y' and 't6 = x + y'), we *reuse* it instead of *recomputing* it.
The expression 't6 = x + y' would be removed or replaced by using 't1'.

