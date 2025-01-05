
## A Simple Compiler: Static Checkers

A static checker is a tool used to analyze source code without executing it. Its goal is to detect errors
 enforce coding standards, and ensure the program adheres to certain constraints or rules.
 Static checkers operate at compile-time or during the development phase, offering early feedback to developers.

Typical responsibilities of static checkers include:
1. *Syntax Validation*: Ensuring the code conforms to the language's grammar.
2. *Type Checking*: Verifying type correctness (ensuring integers aren't used as arrays).
3. *Scope Resolution*: Ensuring variables, constants, or functions are declared and accessible within their intended scope.
4. *Semantic Analysis*: Checking higher-level rules, such as "constants cannot be assigned new values" or "functions must return a value".
5. *Error Reporting*: Providing meaningful feedback for detected issues to help the developer fix them.
6. *Code Optimisation*: Identifying unreachable code, redundant computations, or potential inefficiencies.


#### Static Checkers Using an Abstract Syntax Tree (AST)

An AST-based static checker uses the Abstract Syntax Tree (AST) as the foundation for analysis.
The AST is a hierarchical representation of the program's structure, capturing both the syntax
and semantics of the source code.

For example:
- A line like x := 5 + 3 might translate to an AST with nodes for assignment (:=), addition (+), and the identifiers/numbers (x, 5, 3).
- The structure of the AST allows systematic traversal for verifying rules.

Key aspects of AST-based static checking include:

1. AST Traversal
- The checker walks through the AST nodes, examining their relationships and properties.
- Different node types trigger different checks (assignments, function calls, conditions ..).

2. Context Tracking
- Maintains a symbol table to store information about declared variables, constants, functions, and their scopes.
- Tracks the current scope to ensure references are valid and adhere to rules like shadowing or re-declaration restrictions.

3. Rule Enforcement
- For each type of construct in the AST, specific rules are applied:
- Constants: Ensure they are only initialized once.
- Variables: Verify they are declared before use.
- Control Statements: Ensure constructs like if and while have valid conditions and blocks.
- Procedures: Check if they are called correctly and have consistent signatures.

4. Error Detection
- Errors detected during traversal are tied to specific AST nodes, which often map directly to lines of source code.
- The checker provides meaningful messages, like "Undeclared identifier" or "Assignment to constant not allowed."


#### How the Provided Static Checker Might Work

Given the code snippet 'static.py', static checker would:

1. Tokenize and Parse: Convert the source code into tokens and then into an AST.

2. Perform Static Checks:
- Scope and Declaration: Ensure variables/constants are declared before use.
- Type and Usage: Verify that assignments respect declared types and that constants are not reassigned.
- Control Flow: Ensure all branches of if, while, and similar constructs are valid.
- Semantics: Enforce the language's rules, such as const values not being reassigned.

3. Error Reporting:
- Map errors (undeclared variables, missing end etc.) to specific locations in the code for actionable feedback.


#### Example: AST-Based Check

Consider the program:

```pascal
const x = 10;
y := x + 1 .
```

1. AST Representation:
- Block node with:
- ConstDeclaration(x=10)
- AssignmentStatement(ident="y", expression="x+1")

2. Static Check:
- The x declaration is valid.
- The y assignment fails because y is undeclared.

```
Error reported: Undeclared identifier: y.
```

Benefits of AST-Based Static Checkers
- Precision: The AST provides a rich representation of the code, enabling deep and accurate analysis.
- Extensibility: New rules or checks can be added by extending node-specific behaviors.
- Feedback: Errors and warnings are precise, improving debugging efficiency.
