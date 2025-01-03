
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
  - *Input*:
    ```
    x = 345;
    y = 345;
    z = x + y - 5 * (7 + 9) / 2;
    ```
  - *Output Tokens*:
  ```python
  tokens = [
    ('IDENTIFIER', 'x'), 
    ('ASSIGN', '='), 
    ('NUMBER', '345'),
    ('SEMICOLON', ';'),
    ('IDENTIFIER', 'y'),
    ('ASSIGN', '='),
    ('NUMBER', '345'),
    ('SEMICOLON', ';'),
    ('IDENTIFIER', 'z'),
    ('ASSIGN', '='),
    ('IDENTIFIER', 'x'),
    ('PLUS', '+'),
    ('IDENTIFIER', 'y'),
    ('MINUS', '-'),
    ('NUMBER', '5'),
    ('TIMES', '*'),
    ('LPAREN', '('),
    ('NUMBER', '7'),
    ('PLUS', '+'),
    ('NUMBER', '9'),
    ('RPAREN', ')'),
    ('DIVIDE', '/'),
    ('NUMBER', '2'),
    ('SEMICOLON', ';')
    ]
  ```


### 2. Parsing

- *Goal*: Use the tokens to create a tree structure that represents the code according to the grammar.

- Process:
  - Recognise hierarchical groupings, such as `term` within `expression` or `statement` within `program`.
  - Build an Abstract Syntax Tree (AST).

- Example:
  - *Input Tokens*:
    ```
    tokens
    ``` 
  - *AST*:
    ```
    program
    ├── statement
    │   ├── IDENTIFIER(x)
    │   └── expression
    │       └── NUMBER(345)
    ├── statement
    │   ├── IDENTIFIER(y)
    │   └── expression
    │       └── NUMBER(345)
    └── statement
        ├── IDENTIFIER(z)
        └── expression
            ├── term
            │   ├── IDENTIFIER(x)
            │   ├── PLUS
            │   ├── IDENTIFIER(y)
            │   ├── MINUS
            │   ├── term
            │   │   ├── factor
            │   │   │   ├── NUMBER(5)
            │   │   │   ├── TIMES
            │   │   │   └── factor
            │   │   │       ├── LPAREN
            │   │   │       ├── expression
            │   │   │       │   ├── NUMBER(7)
            │   │   │       │   ├── PLUS
            │   │   │       │   └── NUMBER(9)
            │   │   │       ├── RPAREN
            │   │   │       ├── DIVIDE
            │   │   │       └── NUMBER(2)
    ```

### 3. Tree Transformations

- *Goal*: Optimise or transform the AST. Here in [2](./2) we ignore the earlier parsing
  to make it simple to read code, and build a new representation in TAC, Three-Address Code.

- Examples:
  - *Constant Folding*: Simplify `7 + 9` to `16`.

  - *Common Subexpression Elimination (CSE)*: Expressions like x + y that are computed
    multiple times in a program and replaces them with a single computation.

  - *Dead Code Elimination*: Code that is not reached, or not making any alternations can
    be considered "dead" and thus can be eliminated from the executable.

- Example in case AST constant folding:
  - Original Tree:
    ```
    expression
    ├── NUMBER(7)
    ├── PLUS
    └── NUMBER(9)
    ```
  - Optimised Tree:
    ```
    expression
    └── NUMBEr(16)
    ```

- Example CSE in a TAC:
  - Original TAC:
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
  - Optimised TAC:
    ```
    x = 2025
    y = 1477
    t1 = x + y  # only calculation here
    t2 = 7 + 9
    t3 = 5 * t2
    t4 = t3 / 2
    t5 = t1 - t4
    z = t5
    t6 = t1 # replaced
    t7 = 0
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
    ├── IDENTIFIER(z)
    └── expression
        └── term
            ├── IDENTIFIER(x)
            ├── PLUS
            ├── IDENTIFIER(y)
            ├── MINUS
            ├── factor
                └── NUMBER(5)
    ```
  - *Generated Code*: 
    ```
    LOAD x
    ADD y
    SUB 5
    MUL 16
    DIV 2
    STORE z
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
