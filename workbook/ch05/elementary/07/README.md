
## Intermediate Code: Three Address Code (TAC)

__Build__

```shell
make clean
make samples
```

From the richness of the *Abstract Syntax Tree* (AST) we can build our code. This time it
will be intermediate into *Three Address Code* (TAC), one step closer to the ultimate goal of
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

4. *Linear Structure*: TAC is represented as a sequence of instructions, making it easy to manipulate and optimise.


__TAC Instructions__

- *Assignment*: `x = LOAD y` (e.g. `t6 = LOAD 43`)

- *Assignment from Expression*: `x = op y z` (e.g. `t6 = + t4 x`)

- *Copy*: `x = y` (e.g. `t2 = t1`)

- *Conditional Jumps*: `IF_NOT x GOTO L` (e.g. `IF_NOT t3 GOTO L1`)

- *Unconditional Jumps*: `GOTO L` (e.g. `GOTO L2`)

- *Function Calls*: `CALL func` (e.g. `CALL gcd`)

- *Return*: `RETURN`

- *Labels*: `Ln:` (e.g. `L2:`)



__Example__

```c
const max = 10;
var counter;

begin
    while (counter < max) do
    begin
        counter := counter + 1;
    end;
end.
```

The corresponding TAC might look like:

```tac
t0 = LOAD 10
max = t0
main:
L0:
t1 = LOAD counter
t2 = LOAD max
t3 = < t1 t2
IF_NOT t3 GOTO L1
t4 = LOAD counter
t5 = LOAD 1
t6 = + t4 t5
counter = t6
GOTO L0
L1:
```

__TAC in Compilers__

1. *Intermediate Representation*:
   - After parsing the source code, the compiler generates TAC as an intermediate step between the
     high-level code and the target machine code.
   - TAC is easier to optimise and analyse than the original source code.

2. *Optimisation*:
   - Many compiler optimisations, such as constant folding, dead code elimination, and common
     subexpression elimination, are performed on TAC.
   - The linear structure of TAC makes it easier to apply these transformations.

3. *Code Generation*:
   - TAC is closer to machine code, so it simplifies the process of generating assembly or machine code.
   - Each TAC instruction can be directly mapped to one or more machine instructions.

4. *Control Flow Analysis*:
   - TAC makes control flow explicit through jump instructions (`GOTO`, `IF_NOT`), which helps in
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

In summary, Three-Address Code is a way of intermediate representation in compilers, bridging the gap between
high-level source code and low-level machine code. It simplifies optimisation, analysis, and code generation,
making it a fundamental tool in compiler design.




### Structure of a Quadruple

In the context of Intermediate Representation (IR) for compilers or interpreters, a quadruple is a data structure
used to represent a single instruction in a simplified, low-level form. The concept is commonly used in many 
compiler designs, especially in cases of representing the operations between variables or constants in a more
abstract form that can be translated into machine code or assembly language.

A quadruple typically consists of four fields (hence the name quadruple), which represent the components of a
simple instruction.
1. *Operator*: The operation or instruction to be performed (e.g. addition, subtraction, multiplication, assignment).
2. *Argument 1*: The first operand, which could be a constant, a variable, or a temporary variable.
3. *Argument 2*: The second operand, which can also be a constant, a variable, or another temporary variable.
4. *Result*: The variable or temporary variable that will store the result of the operation.

Example of a Quadruple:

Let’s say we have a simple addition operation like 'a = b + c'.
Or, represented as prefix order 'a = + b c'.

The corresponding quadruple might look like this:
```
Operator    Argument 1  Argument 2  Result
+	        b           c           a
```

This quadruple represents the operation 'a = b + c', where:
* '+' is the operator (the operation to perform),
* 'b' is Argument 1,
* 'c' is Argument 2,
* 'a' is the Result of the operation.

Because quadruples are abstract representations, they are often used during optimisation.
- Constant folding: Replacing operations with known constant results (e.g. 3 + 4 becomes 7).
- Common subexpression elimination: If the same expression appears multiple times, it can be computed once and reused.
- Dead code elimination: Removing operations where the result is never used.

Consider the following simple code:

```
a = + b c
d = * a 2
```

In quadruples, it would be represented as:
1. '+ b c t1' (where t1 is a temporary variable for the result of b + c)
2. '* t1 2 d' (multiplying the temporary result t1 by 2 and storing it in d)

This representation breaks the code down into simpler steps, with temporary variables holding
intermediate results. The quadruples form a linear sequence of operations that can be optimised
and translated into machine code or further IR formats.


Sample2

TYPE:
..
