
## Intermediate Code: LLVM

__Build__

```shell
make clean
make samples
```

From the richness of the *Abstract Syntax Tree* (AST) we can build our code. This time it
will be intermediate into *Three Address Code* (TAC), a step before building the ultimate goal of
more executable code.

__View__

..

### Overview and Uses

*Three-Address Code (TAC)* is an intermediate representation used in compilers. It is a low-level,
linear representation of code that simplifies the translation from high-level source code to
machine code. TAC is called "three-address" because each instruction typically involves at most
three operands: two for the input and one for the output. This makes it easier to optimise and
translate into machine code.


__Characteristics of TAC__

1. *Simplicity*: Each TAC instruction is simple and typically performs a single operation.

2. *Explicit Temporaries*: Intermediate results are stored in temporary variables, making the flow of data explicit.

3. *Low-Level Abstraction*: TAC is closer to machine code than high-level languages but still retains some abstraction.

4. *Linear Structure*: TAC is represented as a sequence of instructions, making it easy to manipulate and optimize.


__Typical TAC Instructions__

- *Assignment*: `x = y op z` (e.g. `t1 = a + b`)

- *Copy*: `x = y` (e.g. `t2 = t1`)

- *Unary Operations*: `x = op y` (e.g. `t3 = -t2`)

- *Conditional Jumps*: `if x relop y goto L` (e.g. `if t1 < t2 goto L1`)

- *Unconditional Jumps*: `goto L` (e.g. `goto L2`)

- *Function Calls*: `call func, args` (e.g. `call foo, t1, t2`)

- *Return*: `return x` (e.g. `return t3`)


__Example__

```c
a = b + c * d;
if (a > 10) {
    x = a - 5;
} else {
    x = a + 5;
}
```

The corresponding TAC might look like:

```
t1 = c * d
t2 = b + t1
a = t2
if a > 10 goto L1
t3 = a + 5
x = t3
goto L2
L1:
t4 = a - 5
x = t4
L2:
```

__TAC in Compilers__

1. *Intermediate Representation*:
   - After parsing the source code, the compiler generates TAC as an intermediate step between the
     high-level code and the target machine code.
   - TAC is easier to optimise and analyse than the original source code.

2. *Optimization*:
   - Many compiler optimisations, such as constant folding, dead code elimination, and common
     subexpression elimination, are performed on TAC.
   - The linear structure of TAC makes it easier to apply these transformations.

3. *Code Generation*:
   - TAC is closer to machine code, so it simplifies the process of generating assembly or machine code.
   - Each TAC instruction can be directly mapped to one or more machine instructions.

4. *Control Flow Analysis*:
   - TAC makes control flow explicit through jump instructions (`goto`, `if-goto`), which helps in
     analysing loops, conditionals, and other control structures.

5. *Temporary Variables*:
   - TAC introduces temporary variables to store intermediate results, which helps in managing registers
     and memory during code generation.


__Pros__

- *Portability*: TAC is independent of the target machine architecture, making it easier to retarget the
  compiler to different platforms.
- *Modularity*: Separates the front-end (parsing) and back-end (code generation) of the compiler, allowing
  for easier maintenance and extension.
- *Optimisation*: The explicit nature of TAC makes it suitable for applying various optimisations.


__Cons__

- *Verbosity*: TAC can be more verbose than high-level code, as it breaks down complex expressions into simpler instructions.
- *Temporary Variables*: The use of temporary variables can increase the complexity of the code, especially for large programs.

In summary, Three-Address Code is a crucial intermediate representation in compilers, bridging the gap between
high-level source code and low-level machine code. It simplifies optimization, analysis, and code generation,
making it a fundamental tool in compiler design.


### Example

..