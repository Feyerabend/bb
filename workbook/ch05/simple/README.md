
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
            └── term
                ├── IDENTIFIER(x)
                ├── PLUS
                ├── IDENTIFIER(y)
                ├── MINUS
                └── term
                    └── factor
                        ├── NUMBER(5)
                        ├── TIMES
                        └── factor
                            ├── LPAREN
                            ├── expression
                            │   ├── NUMBER(7)
                            │   ├── PLUS
                            │   └── NUMBER(9)
                            ├── RPAREN
                            ├── DIVIDE
                            └── NUMBER(2)
    ```

### 3. Static Checking

- *Goal*: Identify and report errors or inconsistencies in the source code without executing it.
  This process ensures code correctness by catching issues early in the compilation pipeline.

- *Examples*:
	- *Type Checking*: Verify that operations are performed on compatible types
      (e.g. adding a number to a string raises an error).

	- *Scope Validation*: Ensure variables are declared before use and are within accessible scope.

	- *Control Flow Analysis*: Detect unreachable code or improperly formed loops and conditionals.

	- *Rule Enforcement*: Validate adherence to specific language rules,
      such as const correctness or naming conventions.


### 4. Tree Transformations

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
    └── NUMBER(16)
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

  
### 5. Code Generation

- *Goal*: Convert the AST into target instructions, such as bytecode or machine code.

- Grammar Mapping:
    - `IDENTIFIER` maps to variable storage/access.
    - Arithmetic operations (`+`, `-`, `*`, `/`) map to corresponding machine instructions.
    - `=` assigns a value to an identifier.

- Example:
  - *AST*:
    ```
        PROGRAM(None)
        ├── ASSIGN(None)
        │   ├── IDENTIFIER(x)
        │   └── NUMBER(345)
        ├── ASSIGN(None)
        │   ├── IDENTIFIER(y)
        │   └── NUMBER(345)
        └── ASSIGN(None)
            ├── IDENTIFIER(z)
            └── MINUS(None)
                ├── PLUS(None)
                │   ├── IDENTIFIER(x)
                │   └── IDENTIFIER(y)
                └── DIVIDE(None)
                    ├── TIMES(None)
                    │   ├── NUMBER(5)
                    │   └── PLUS(None)
                    │       ├── NUMBER(7)
                    │       └── NUMBER(9)
                    └── NUMBER(2)
    ```
  - *Generated Code*: 
    ```
    PUSH 345
    STORE x
    PUSH 345
    STORE y
    LOAD x
    LOAD y
    ADD
    PUSH 5
    PUSH 7
    PUSH 9
    ADD
    MUL
    SUB
    STORE z
    ```


### 6. Execution

- *Goal*: Execute the generated instructions.

- Process:
  - For an interpreter: Evaluate the AST or instructions step-by-step.
  - For a compiler: Combine the generated code with other modules or libraries into an executable binary.


### Summary

The compilation pipeline involves transforming a program through stages aligned with its grammar:

1. *Tokenisation*: Recognize grammar constructs as tokens.

2. *Parsing*: Build an AST matching the grammar structure.

3. *Static Checking*: Enforce language rules, validate variable scopes, type correctness, semantic consistency.

4. *Transformations*: Optimise the AST.

5. *Code Generation*: Map grammar constructs to executable instructions.

6. *Execution*: Run the final code.

See [folder 1](./1) for a simple compiler overview, and step 1, 2, and 3.
For details in 4 see [folder 2](./2/).
And, for step 5 and 6, see [folder 3](./3/).
