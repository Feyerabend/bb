
## PL/0

PL/0 is a minimalistic teaching language designed by Niklaus Wirth to illustrate
fundamental concepts of compilers and programming language implementation. It serves
as a simplified model of Pascal, focusing on essential control structures, arithmetic,
and variable handling while omitting complex features like floating-point numbers,
complex data structures, or extensive I/O.

PL/0 is a procedural language with the following characteristics:
- Variable Declarations: Local variables can be declared within a procedure.
- Arithmetic Operations: Supports basic arithmetic (+, -, *, /).
- Control Structures: Includes if, while, and begin-end blocks.
- Procedures: Supports simple procedures with local scope.
- Symbolic Execution Model: Designed to be compiled into a stack-based intermediate language.


PL/0 programs are compiled into a stack-based virtual machine (P-Code machine) with instructions such as:
- LIT – Push a constant onto the stack.
- LOD – Load a variable from memory.
- STO – Store a value into a variable.
- JMP – Unconditional jump.
- JPC – Conditional jump (if top of stack is false).
- CAL – Call a procedure.
- RET – Return from a procedure.
- OPR – Perform an arithmetic or logical operation.


A simple factorial program in PL/0:
```pascal
const n = 5;
var result;

procedure factorial;
var i;
begin
    result := 1;
    i := n;
    while i > 1 do
    begin
        result := result * i;
        i := i - 1;
    end;
end;

begin
    call factorial;
end.
```
This program computes 5! = 120 using a loop.

Why PL/0?
- Educational Purpose: It introduces core compiler concepts such as lexical analysis,
  parsing, code generation, and virtual machine execution.
- Minimal but Functional: Despite its simplicity, PL/0 supports structured programming.
- Compiler Construction: Many textbooks and courses use PL/0 to teach how to write a
  compiler from scratch.


### Project: Experimentation and Progression

In the included folders there are different experiments with primarily an interpreter
of PL/0. The first folder ([01](./01/)) also contains a compiler. Your task is to enhance
the compiler so it can compile (and parse) more of the actual PL/0 language.
