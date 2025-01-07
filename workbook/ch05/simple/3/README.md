
### Code Generation

Code generation is the final phase of a compiler where the intermediate representation (IR)
is translated into target machine code or assembly language. The goal is to convert high-level
abstractions into instructions that can be executed by the processor. During this phase, the
compiler performs tasks like instruction selection, register allocation, and optimisation
(e.g. loop unrolling or constant folding). The generated code must adhere to the target
architecture's instruction set, register conventions, and memory model. It's essential for
achieving efficient execution of the program.


### Linkers and Loaders

After code generation, the next steps involve linking and loading:
- Linker: A linker takes object files (compiled code and libraries) and combines them into
  a single executable program. It resolves references between different parts of the program,
  such as function calls, global variables, and external libraries. It also assigns final
  memory addresses to variables and functions.
- Loader: The loader is responsible for loading the executable program into memory for
  execution. It sets up the runtime environment by allocating memory, loading code and data
  into the appropriate locations, and setting up the execution context (e.g. the program
  counter, stack pointer).

Together, the linker and loader ensure that a program is correctly assembled and prepared
for execution, with all dependencies resolved and memory organised.


### Type Systems

We have intentionally delayed the introduction of type systems in the context of compilers,
as they add significant complexity both to programs and to explanations. However, type systems
are an essential part of compilers and play an important role throughout the entire compilation
process. In this part, we'll explore how types influence various aspects of compilation,
particularly focusing on their impact on symbol tables, which are used to track variable
information. We'll also illustrate how static and dynamic type systems are handled differently
during a part of the compilation process.

Type systems, whether static or dynamic, shape how data is represented and manipulated in a
program. In a static type system, types are checked at compile-time, meaning that type errors
are caught before the program is executed. This allows the compiler to generate optimised
code, as it can rely on type information to make decisions about memory allocation, register
usage, and optimisations like inlining and constant folding.

A type system is a set of rules used to classify values and expressions in a programming
language into types (such as integer, float, string, etc.). Type systems help ensure that
operations on values are semantically correct, and they can prevent runtime errors caused
by type mismatches. A strongly typed language enforces strict rules about types, whereas 
a weakly typed language may allow more flexible type conversions. Compilers can generate
more efficient code when they know the types of variables. Static type systems check types
at compile-time, while dynamic systems do so at runtime.

In essence, type systems provide a way for developers and compilers to reason about and
manage data in a program, ensuring consistency and reliability in program behavior.
