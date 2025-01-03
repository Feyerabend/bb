
## A Simple Compiler

The process of compiling code involves several steps, each transforming the program's representation
toward executable form.

### 1. Tokenisation (Lexical Analysis)

- *Goal*: Convert the raw source code into a series of tokens matching the grammar.

- Grammar:
    ```ebnf
    expression  ::= term (( "+" | "-" ) term)* 
    term        ::= factor (( "*" | "/" ) factor)*
    factor      ::= NUMBER | IDENTIFIER | "(" expression ")"
    statement   ::= IDENTIFIER "=" expression ";"
    program     ::= statement+
    ```
- Process:
  - Identify elements such as `IDENTIFIER`, `NUMBER`, `+`, `-`, `*`, `/`, `=`, `;`, and parentheses.
  - Ignore whitespace and comments.

- Example:
  - *Input*: `x = 42 + 8 * (y - 3);`  
  - *Output Tokens*: `[ID(x), EQ, NUM(42), PLUS, NUM(8), MUL, LPAREN, ID(y), MINUS, NUM(3), RPAREN, SEMI]`


### 2. Parsing

- *Goal*: Use the tokens to create a tree structure that represents the code according to the grammar.

- Process:
  - Recognise hierarchical groupings, such as `term` within `expression` or `statement` within `program`.
  - Build an Abstract Syntax Tree (AST).

- Example:
  - *Input Tokens*: `[ID(x), EQ, NUM(42), PLUS, NUM(8), MUL, LPAREN, ID(y), MINUS, NUM(3), RPAREN, SEMI]`  
  - *AST*:
    ```
    statement
    ├── ID(x)
    └── expression
        ├── term
        │   ├── NUM(42)
        │   ├── PLUS
        │   └── term
        │       ├── NUM(8)
        │       ├── MUL
        │       └── factor
        │           └── expression
        │               ├── ID(y)
        │               ├── MINUS
        │               └── NUM(3)
    ```

### 3. Tree Transformations

- *Goal*: Optimise or transform the AST.

- Examples:
  - *Constant Folding*: Simplify `42 + 8` to `50`.
  - *..*:  ..

- Example:
  - Original Tree:
    ```
    expression
    ├── NUM(42)
    ├── PLUS
    └── NUM(8)
    ```
  - Optimized Tree:
    ```
    expression
    └── NUM(50)
    ```


### 4. Code Generation

- *Goal*: Convert the AST into target instructions, such as bytecode or machine code.

- Grammar Mapping:
    - `IDENTIFIER` maps to variable storage/access.
    - Arithmetic operations (`+`, `-`, `*`, `/`) map to corresponding machine instructions.
    - `=` assigns a value to an identifier.

- Example:
  - *AST*:
    ```
    statement
    ├── ID(x)
    └── expression
        ├── NUM(50)
    ```
  - *Generated Code*: 
    ```
    LOAD 50
    STORE x
    ```

### 5. Execution

- *Goal*: Execute the generated instructions.

- Process:
  - For an interpreter: Evaluate the AST or instructions step-by-step.
  - For a compiler: Combine the generated code with other modules or libraries into an executable binary.


### Summary

The compilation pipeline involves transforming a program through stages aligned with its grammar:

1. *Tokenization*: Recognize grammar constructs as tokens.

2. *Parsing*: Build an AST matching the grammar structure.

3. *Transformations*: Optimize the AST.

4. *Code Generation*: Map grammar constructs to executable instructions.

5. *Execution*: Run the final code.


..
