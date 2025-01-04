
## A Simple Compiler: Three-Address Code (TAC)

Three-address code (TAC) is an intermediate representation used in compilers to simplify
and organise the process of translating high-level programming languages into machine code
or another low-level representation. It provides a structured and linear way to describe
computations and data manipulations, making it easier to perform optimisations and generate
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

This decomposition into simpler steps allows the compiler to analyse and manipulate the
program more effectively.

TAC is used extensively during the middle stages of compilation, typically as part of the
intermediate representation between the front-end parsing phase and the back-end code
generation phase. By working in this form, compilers can focus on optimisations such as
constant folding, dead code elimination, and common subexpression elimination. Once the
code has been optimised in TAC form, it is easier to generate efficient machine code or
bytecode for execution.

In addition to aiding in optimisation, TAC provides a platform-independent way to represent
code. This makes it useful for compilers targeting multiple architectures, as it decouples
the high-level language from the specifics of the target hardware. For example, TAC might
be translated into assembly language for a physical CPU or into bytecode for a virtual
machine, such as the Java Virtual Machine (JVM) or the Python interpreter.

TAC is a cornerstone of modern compiler design because of its simplicity, flexibility, and
ability to support both optimisation and code generation. Its use is widespread in programming
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
results. See `folding.py`.

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


### Going Further: Optimisations and Representations in Compiler Design

Compilers are designed to take source code and transform it into machine code, but before reaching
the final code, the compiler uses intermediate representations (IRs) to optimise the program.
These optimisations improve the efficiency of the generated code in terms of both speed and size.

1. *Constant Folding and Propagation*
	- Constant Folding evaluates expressions with constant values at compile-time instead of runtime (e.g., 3 + 4 becomes 7).
	- Constant Propagation replaces variables that are known constants with their values, simplifying expressions.

2. *Common Subexpression Elimination (CSE)*
	- This optimisation eliminates repeated calculations of the same expression. For example, if
    'a * b' appears multiple times, it's computed once and reused.
	- This reduces the number of operations needed.

3. *Dead Code Elimination (DCE)*
	- DCE removes code that doesn't affect the final result of the program, such as unused variables
    or redundant computations.
	- This makes the program smaller and faster because unnecessary instructions are not executed.

The last one hasn't been exemplified yet, but more on this type can be seen in [DEAD](./DEAD.md)


### Intermediate Representations (IRs)

Compilers break down the source code into intermediate representations, which help apply optimisations.
These IRs act as a bridge between the high-level code and the low-level machine code.

1. *Three-Address Code (TAC)*
- As we have seen TAC simplifies the code into small, manageable instructions, each with one operator
  and up to two operands. It's easy to optimise and allows for clear application of optimisations like
  DCE and CSE.

2. *Directed Acyclic Graph (DAG)*
- The DAG is a graphical representation of computations, where nodes represent operations or values,
  and edges represent dependencies. DAG optimisations focus on reducing redundant computations by reusing
  previously computed values. See [DAG](./DAG.md).
- Optimisation Example: If the expression 'a * b' is used in multiple places, it is computed *once* and
  reused, reducing redundant work.

3. *Static Single Assignment (SSA)*
- SSA ensures each variable is assigned exactly once, making the program's data flow clearer. It is
  particularly useful for optimisations because it makes it easy to track where values come from and
  where they are used.
- In SSA, dead code is easy to find because if a variable is never used after assignment, it can be
  eliminated.

#### Summary

* TAC is simple and linear, making it easy to apply optimisations like Dead Code Elimination (DCE)
  and Common Subexpression Elimination (CSE). The code can be simplified and cleaned up.
* DAG goes a step further by showing relationships between operations. It makes it clear when
  computations can be reused and helps remove redundant operations.
* SSA ensures that variables are only assigned once, which makes it easier to see where and how
  data flows in the program. This helps to apply optimisations like constant propagation and dead
  code elimination effectively.

Compiler optimisations like Dead Code Elimination (DCE) and Common Subexpression Elimination (CSE)
improve the performance of the program by simplifying the code and removing unnecessary operations.
Using intermediate representations such as TAC, DAG, and SSA helps compilers better understand and 
optimise the code before generating efficient machine code. These representations allow the compiler
to apply a variety of optimisation techniques, resulting in faster and more compact programs.


### History

The development of compiler optimisation techniques has evolved over time as the need for faster
and more efficient programs grew.

__Early Days (1950s - 1960s)__
- In the early days of computing, compilers were simple and often hand-written. Programmers had
  to manually optimise their code for efficiency.
- The first optimisations focused on instruction scheduling and eliminating redundant operations.
- Dead Code Elimination (DCE) emerged as one of the first optimisation techniques, as early
  compilers started to recognise and remove unused code.

__Three-Address Code (TAC) (1960s - 1970s)__
- As compilers became more complex, the need for an intermediate representation (IR) emerged.
  TAC was one of the first such representations, designed to break down code into simpler, more
  manageable operations.
- TAC typically uses three operands per instruction, which makes it easy to apply optimisation
  techniques like Dead Code Elimination and Common Subexpression Elimination (CSE).
- DCE and CSE began being applied systematically in compilers to reduce redundant computations
  and dead code, significantly improving program performance.

__Directed Acyclic Graph (DAG) (1970s - 1980s)__
- The DAG representation became popular in the 1970s for optimising expressions. In a DAG, nodes
  represent computations, and edges represent dependencies between them.
- DAG optimisations focus on reducing redundant calculations, such as sharing the results of
  common subexpressions (e.g. computing a * b only once, even if it appears in multiple places).
- The use of DAGs allowed for more advanced optimisations, particularly in expression evaluation
  and resource sharing.

__Static Single Assignment (SSA) (1980s - 1990s)__
- In the 1980s, the Static Single Assignment (SSA) form was introduced to simplify and clarify
  data flow analysis in compilers.
- SSA ensures each variable is assigned only once, which greatly simplifies data dependency analysis
  and makes optimisation techniques like constant propagation and dead code elimination more effective.
- SSA makes it easier to track how values are propagated through the program, leading to faster optimisation.
- It became popular in modern optimising compilers and is now commonly used in languages like LLVM and GCC.

__Modern Optimisations (2000s - Present)__
- By the 2000s, optimisations in compilers had become highly sophisticated, combining techniques
  from TAC, DAG, and SSA to produce efficient machine code.
- Modern compilers like LLVM and GCC employ a variety of optimisation techniques at different stages
  using these intermediate representations.
- Advanced optimisations such as loop unrolling, vectorisation, and inlining work alongside basic
  optimisations like DCE and CSE.

