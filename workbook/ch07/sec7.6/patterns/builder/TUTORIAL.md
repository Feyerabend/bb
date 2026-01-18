
## PL/0 Interpreter Tutorial

This tutorial provides an overview of the PL/0 interpreter implemented in Python,
guiding you through its components, usage, and how to write and run PL/0 programs.
PL/0 is a simple programming language designed for educational purposes, featuring
variables, procedures, conditionals, loops, and basic arithmetic operations.

## Table of Contents
1. [Overview](#overview)
2. [PL/0 Language Syntax](#pl0-language-syntax)
3. [Components of the Interpreter](#components-of-the-interpreter)
4. [Running the Interpreter](#running-the-interpreter)
5. [Writing a PL/0 Program](#writing-a-pl0-program)
6. [Example Program](#example-program)
7. [Extending the Interpreter](#extending-the-interpreter)
8. [Common Errors and Debugging](#common-errors-and-debugging)


### Overview

The PL/0 interpreter is a Python program that processes PL/0 code by performing lexical
analysis, parsing, building an Abstract Syntax Tree (AST), and interpreting the AST to
execute the program.
- Variable declarations and assignments
- Procedure definitions and calls
- Input/output operations
- Conditional statements (`if-then`)
- Loops (`while-do`)
- Basic arithmetic and comparison operations

The interpreter follows a modular design with classes for lexical analysis, parsing,
AST construction, and interpretation, using the Visitor pattern for AST traversal.



### PL/0 Language Syntax

PL/0 has a simple syntax with the following constructs:

- *Keywords*: `var`, `procedure`, `begin`, `end`, `if`, `then`, `while`, `do`, `call`, `?` (input), `!` (output)
- *Operators*: `+`, `-`, `*`, `/`, `<`, `>`, `=`, `:=` (assignment)
- *Identifiers*: Alphanumeric names for variables and procedures (e.g., `x`, `counter`)
- *Numbers*: Integer literals (e.g., `42`)
- *Punctuation*: `;`, `,`, `(`, `)`
- *Program Structure*:
  - A program starts with optional variable declarations (`var x, y;`)
  - Followed by optional procedure declarations (`procedure p; ...`)
  - Ends with a main statement block, terminated by `end.`


#### Example Syntax

```pascal
var x, y;
procedure add;
  x := x + y;
begin
  x := 5;
  y := 3;
  call add;
  !x
end.
```

This program declares variables `x` and `y`, defines a procedure `add`, assigns values,
calls the procedure, and outputs the result.



### Components of the Interpreter

The interpreter is divided into several key components:

#### 1. Lexer (`PL0Lexer`, `TokenMatchStrategy`, `TokenIterator`)
- *Purpose*: Converts the input PL/0 code into a stream of tokens (e.g., keywords, identifiers, operators).
- *Key Classes*:
  - `RegexTokenMatchStrategy`: Uses regular expressions to match tokens like numbers, operators, and keywords.
  - `TokenIterator`: Manages the token stream, allowing the parser to iterate over tokens.
  - `PL0Lexer`: Coordinates tokenization, appending a semicolon to ensure proper termination.

#### 2. Parser and AST Builder (`ASTBuilder`, `ASTNode` subclasses)
- *Purpose*: Parses the token stream to build an AST representing the program's structure.
- *Key Classes*:
  - `ASTBuilder`: Recursively constructs the AST by recognizing syntactic constructs (e.g., blocks, statements, expressions).
  - `ASTNode` subclasses (e.g., `BlockNode`, `AssignNode`, `IfNode`): Represent different program elements in the AST.

#### 3. Interpreter (`Interpreter`, `Visitor`, `Scope`)
- *Purpose*: Executes the program by traversing the AST and performing the corresponding actions.
- *Key Classes*:
  - `Interpreter`: Implements the Visitor pattern to evaluate AST nodes.
  - `Scope`: Manages variable and procedure bindings, supporting nested scopes for procedures.
  - `OperatorFactory`: Maps operator symbols to Python functions (e.g., `+` to `operator.add`).

#### 4. Main Program (`PL0Interpreter`, `main`)
- *Purpose*: Provides the entry point to read a PL/0 file and run the interpreter.
- *Key Function*: `PL0Interpreter.run_file` orchestrates the lexer, parser, and interpreter.



### Writing a PL/0 Program

Follow these guidelines to write a PL/0 program:
- *Variable Declarations*: Use `var` followed by a comma-separated list of identifiers, ending with `;`.
  ```pascal
  var x, y, z;
  ```
- *Procedure Declarations*: Define procedures with `procedure <name>;` followed by a block, ending with `;`.
  ```pascal
  procedure sum; x := x + y;
  ```
- *Statements*:
  - Assignment: `<id> := <expression>`
  - Procedure call: `call <id>`
  - Input: `? <id>`
  - Output: `! <expression>`
  - Compound: `begin <statements> end`
  - Conditional: `if <expression> <op> <expression> then <statement>`
  - Loop: `while <expression> <op> <expression> do <statement>`
- *Expressions*: Support arithmetic (`+`, `-`, `*`, `/`) and comparisons (`<`, `>`, `=`), with parentheses for grouping.
- *Termination*: End the program with `end.`.



### Example Program

Here’s a sample PL/0 program that calculates the factorial of a number input by the user:

```pascal
var n, result;
begin
  ?n;              (* Read input *)
  result := 1;
  while n > 0 do
    begin
      result := result * n;
      n := n - 1
    end;
  !result          (* Output result *)
end.
```

#### Explanation
- Declares variables `n` and `result`.
- Reads `n` from the user.
- Computes the factorial by multiplying `result` by `n` and decrementing `n` until it reaches 0.
- Outputs the final `result`.

### Running the Example
1. Save the program as `factorial.pl0`.
2. Run:
   ```
   python3 pl0.py factorial.pl0
   ```
3. Enter a number (e.g., `5`) when prompted.
4. The program outputs `120` (5! = 5 × 4 × 3 × 2 × 1).



### Extending the Interpreter

You can extend the interpreter to add features like:
- *New Operators*: Add operators (e.g., `mod`) to `RegexTokenMatchStrategy` and `OperatorFactory`.
- *Data Types*: Extend `Scope` to support non-integer types.
- *Error Handling*: Enhance `SyntaxError` messages with line numbers by tracking positions in `PL0Lexer`.
- *New Statements*: Add new AST nodes and parsing rules in `ASTBuilder` (e.g., `for` loops).

#### Example: Adding a Modulo Operator
1. Update `RegexTokenMatchStrategy` to recognize `%`:
   ```python
   r"(?P<op>[-+*/%()<>=])|"
   ```
2. Add modulo to `OperatorFactory`:
   ```python
   "%": operator.mod
   ```
3. Test with a program like `x := 10 % 3; !x` (outputs `1`).



### Common Errors and Debugging

#### Syntax Errors
- *Unexpected Character*: Check for invalid tokens (e.g., `@`, `#`). Ensure proper keywords and operators.
- *Expected <token> but got <token>*: Verify statement syntax, such as missing `;` or `then`.
- *Fix*: Review the program against the PL/0 syntax rules.

#### Semantic Errors
- *Variable/Procedure Not Found*: Ensure variables and procedures are declared before use.
- *Fix*: Check `var` and `procedure` declarations.

#### Debugging Tips
- Print the token stream in `PL0Lexer` to verify tokenization.
- Add debug output in `ASTBuilder` to inspect the AST structure.
- Trace variable values in `Interpreter` to diagnose runtime issues.



### Conclusion

The PL/0 interpreter is a powerful tool for learning about compilers and interpreters.
By understanding its components and experimenting with PL/0 programs, you can gain insights
into lexical analysis, parsing, and program execution. Try writing your own PL/0 programs
or extending the interpreter to explore its capabilities further.
