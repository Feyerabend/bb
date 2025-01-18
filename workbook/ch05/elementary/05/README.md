
## Semantic Analysis

__Build__

```shell
make clean
make
make samples
make table
```

We go back to the *Abstract Syntax Tree* (AST) for use in a preliminary *interpreter*. This gives us
more confidence in the compiler proceeds as expected. It also shows how the meaning and validity of
code. Another part of sematic analysis are error checks. Here they are simplified as print to the console.

__Execute__

In the directory of 'tools' you'll find a Python file: ast_interpreter. Run the file to see an execution
of the programs.



### Analysis

Semantic analysis ensures logical correctness and adherence to program rules:

1. *Scope Management*: Each block or procedure maintains its own environment. Variables declared in one
   scope are isolated from others unless explicitly propagated.

2. *Type Checking*: Expressions are evaluated to ensure correct types (e.g. numeric operations). (Only one type here: integers)

3. *Consistency*: Constants and procedures cannot be re-declared. Assignments check for variable existence.

4. *Control Flow*: Ensures proper structure for blocks, calls, and recursion. Detects unreachable or malformed code.


#### Error Messages

1. *Syntax Errors*: Errors in JSON structure (e.g. invalid node types or unexpected formats).

2. *Semantic Errors*: Logical issues during interpretation, like undefined variables or unsupported operations.

3. *Runtime Errors*: Issues encountered while executing the interpreted program, such as division by zero or recursive depth limits.

