
## Semantic Analysis

__Build__

```shell
make clean
make
make samples
make table
```

The provided code fragments illustrate the basic structure for a simple symbol table build in a
language close to PL/0. The symbol table relies on an *Abstract Syntax Tree* (AST) for the extraction
of information, and thus the AST has to be built *before* extraction of the symbol table.

__Execute__

In the directory of 'tools' you'll find a Python file: ast_interpreter.
Run the file to see a preliminary execution of the programs.


..