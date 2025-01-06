
## A Simple Compiler

__Basic Grammar__

The parser assumes an input format similar to a simplified programming language,
or could be considered as the very common expression part. The general grammar is:

```ebnf
    expression  ::= term (( "+" | "-" ) term)* 
    term        ::= factor (( "*" | "/" ) factor)*
    factor      ::= NUMBER | IDENTIFIER | "(" expression ")"
    statement   ::= IDENTIFIER "=" expression ";"
    program     ::= statement+
```

- *Expressions*: Mathematical operations with precedence ('x + y * z', or '5 * (2 + 3)').
- *Statements*: Assignments where an identifier ('x', 'y') is set to an expression,
  ending with a semicolon.
- *Programs*: A sequence of statements (in this case expressions) separated by semicolons.

__Scripts for a Compiler__

We will process the scripts in the following sequence:

```
token.py -> parser.py -> comp.py -> vm.py
```

Each step produces an output that serves as input for the next stage. To keep things simple,
no files are saved during the process, though you can easily modify the scripts to add file
handling if needed to experiment with more expressions.

__Expressions to Tokens or Lexical Analysis__

The first step is converting the raw mathematical expression (or program code) into
tokens that the parser can work with. This process is called lexical analysis or tokenisation
(tokenization).

For example, consider the expression:

```
x = 345; y = 345; z = x + y - 5 * (7 + 9) / 2;
```

A token is a small meaningful unit in the code, such as keywords (=), operators (+, -, *, /),
identifiers (like x, y, z), numbers (like 345, 7, 9), and punctuation (like ; or parentheses ()).
A lexer might tokenise it:

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

The lexer takes the input code and breaks it into these tokens, which represent the
different parts of the code in a structured format.

__Token Parsing: Creating an AST__

The parser takes the list of tokens and builds an Abstract Syntax Tree (AST). The AST
is a tree representation of the code's structure, where each node represents an operation
or expression.

For example, when parsing the expression 'x = 345;', the parser will generate a tree
like this:

```python
ASTNode(kind='ASSIGN', value=None, children=[
    ASTNode(kind='IDENTIFIER', value='x', children=[]),
    ASTNode(kind='NUMBER', value='345', children=[])
])
```

The AST for the entire expression would be much larger, representing the entire structure,
including the mathematical expressions, assignments, and variables.

Outline of the types of AST nodes:
- ASSIGN: For assignment statements like x = 345.
- IDENTIFIER: For variables like x, y, z.
- NUMBER: For numeric constants like 345, 5, 7.
- PLUS, MINUS, TIMES, DIVIDE: For operations like +, -, *, /.
- LPAREN, RPAREN: For parentheses ( and ).


__Building the Symbol Table__

The symbol table is a mapping from variable names (identifiers) to their values or
references. During parsing, the compiler records the variables being used and assigns
their values as they are encountered.

For example, in the line 'x = 345', the symbol table will look like this:

```python
symbol_table = {'x': 345}
```

If a variable is not yet assigned a value, the symbol table may initially contain
'None' or be left empty. This symbol table will be updated as the program parses
further expressions and encounters assignments.


__Optimisations: Example Constant Folding__

After building the symbol table, you might apply optimisations to improve performance
or simplify the code. One such optimisation is constant folding, where expressions
involving only constants are evaluated at compile time rather than runtime.

For example, consider the expression:

```python
z = 5 + (7 + 9) * 2
```

You can fold the constants '7 + 9' and '5 + 2' at compile time, which would result in:

```python
z = 5 + 16
```

This optimisation simplifies the expression, which can then be directly evaluated as
'z = 21'. In the AST, constant folding will reduce the number of nodes and make the code
more efficient.

This step is here optional, and the decision to apply it depends on whether you want to
optimise for runtime performance or keep the code as-is.


__Code Generation for the Virtual Machine__

After parsing the expression and building the symbol table, the next step is to generate
code that a virtual machine can execute. This code is typically a list of instructions that
represent the operations described in the AST.

For example, consider the AST for the statement 'x = 345;'. The corresponding VM code
might look like:

```assembly
PUSH 345
STORE x
```

For a more complex expression like 'z = x + y - 5 * (7 + 9) / 2;', the corresponding VM code
might look like:

```assembly
LOAD x
LOAD y
ADD
PUSH 5
PUSH 7
PUSH 9
ADD
MUL
PUSH 2
DIV
SUB
STORE z
```

This list of VM instructions represents the sequence of operations that the VM will execute.
The process of code generation essentially walks through the AST, visiting each node and
emitting the corresponding VM instruction.

__Execution in the Virtual Machine__

Finally, the virtual machine (VM) executes the generated code. The VM interprets each
instruction and updates its state accordingly. Here's an example of how the VM might work:
- PUSH 345: Pushes the value 345 onto the stack.
- STORE x: Pops the top value from the stack and stores it in the variable x.
- LOAD x: Loads the value of x onto the stack.
- ADD: Pops the top two values from the stack, adds them, and pushes the result back onto the stack.
- And so on .. for other operations like SUB, MUL, DIV.

The VM has a stack for holding intermediate values, and it operates by manipulating that stack based on the instructions it receives.


#### Summary

1. *Tokenisation*: Convert the raw source code into a series of tokens.
2. *Parsing*: Build an Abstract Syntax Tree (AST) that represents the structure of the code.
3. *Symbol Table*: Track variable assignments and values during parsing.
4. *Optimisation*: Optionally apply optimisations like constant folding to simplify expressions.
5. *Code Generation*: Generate a list of VM instructions from the AST.
6. *Execution*: Execute the generated code in a virtual machine that interprets the instructions
   and manages the program's state.



### Projects

__1. Basic Arithmetic Expression Evaluator__

- *Extend the simple interpreter for arithmetic expressions for floating points and more mathematical operators.*
    - Challenge: Start by tokenising the expressions and building an Abstract Syntax Tree (AST).
    - Enhancement: Implement a symbol table to handle variables and apply operations in the correct order.
    - Optimisation: Implement constant folding to simplify constant expressions during compilation.
    - Extension: Create a basic Virtual Machine (VM) that can execute the generated instructions.

__2. Basic Compiler for a Custom Language__

- *Design and implement a compiler for a simple, custom programming language with basic arithmetic and variable assignments.*
    - Challenge: Start with parsing expressions and assignments, then generate intermediate code (like bytecode).
    - Enhancement: Include error handling for invalid syntax, unsupported operations, or undeclared variables.
    - Extension: Add optimisations such as constant propagation and dead code elimination to improve efficiency.
    - Bonus: Create a simple runtime environment or VM that executes the compiled code.

__3. Extend to a Toy Programming Language with Control Flow (If/Else, Loops)__

- *Expand your simple language to include control flow statements like if, else, and while loops.*
    - Challenge: Implement a parser that can handle conditional expressions and loops.
    - Enhancement: Implement AST nodes that represent control flow structures and handle their evaluation.
    - Extension: Extend your VM to interpret control flow instructions, and add jump/branch functionality.
    - Bonus: Add debugging features (e.g. breakpoints or step-through execution).

__4. Interpreter for a Simple Object-Oriented Language__

- *Implement an interpreter for a simple object-oriented language, supporting classes, objects, and methods.*
    - Challenge: Design a class system in the language, where you can define classes, instantiate objects, and call methods.
    - Enhancement: Implement inheritance and method overloading.
    - Extension: Add memory management (e.g. garbage collection) and handle dynamic method dispatch.
    - Bonus: Build an interactive shell or REPL for users to input and evaluate expressions.

__5. Bytecode Virtual Machine__

- *Create a virtual machine that can execute bytecode instructions generated by a custom compiler or interpreter.*
	- Challenge: Design a simple set of bytecode instructions (e.g. PUSH, ADD, LOAD, STORE) and implement a stack-based execution model.
	- Enhancement: Support a range of data types (e.g. integers, strings, arrays) and implement operations on them.
	- Extension: Add support for function calls and recursion, including managing the call stack.
	- Bonus: Optimise the bytecode for performance (e.g. by adding inline optimisations or simplifying common operations).

__6. Code Optimisation Pass for a Compiler__

- *Implement an optimisation pass for your existing compiler or interpreter.*
	- Challenge: Implement simple optimisations like constant folding, constant propagation, and dead code elimination.
	- Enhancement: Explore more advanced optimisations, such as loop unrolling or strength reduction.
	- Extension: Compare the performance of the optimised code versus non-optimised code using a simple benchmark.
	- Bonus: Implement a debug mode that shows the before-and-after effects of optimisation.

__7. A Memory-Safe Language (with a Garbage Collector)__

- *Create a language that includes garbage collection to automatically manage memory.*
	- Challenge: Implement reference counting or mark-and-sweep garbage collection to automatically reclaim unused memory.
	- Enhancement: Implement features like memory leaks detection and weak references.
	- Extension: Add support for object finalisation (clean-up code before garbage collection).
	- Bonus: Integrate your garbage collector with an existing runtime or VM that supports a basic language.

__8. Language for Logic Programming (Mini Prolog)__

- *Build a simple logic programming language, similar to Prolog, which supports basic facts and rules.*
	- Challenge: Implement a system for defining facts and rules, and query the database using a simple backward-chaining approach.
	- Enhancement: Implement recursion in rules and queries.
	- Extension: Add constraints and logic operators to enhance expressiveness.
	- Bonus: Create an interactive prompt where users can define facts, rules, and query the system.

__9. Simple Static Analysis Tool for Code__

- *Develop a static code analysis tool that can find bugs, inefficiencies, or security vulnerabilities in code.*
	- Challenge: Build a parser for a subset of a programming language, and design static analysis rules
      (e.g. unused variables, division by zero, unreachable code).
	- Enhancement: Allow users to define their own analysis rules (e.g. detect deadlocks or infinite loops).
	- Extension: Generate warnings or suggestions for code improvements, and integrate this tool with popular IDEs or code editors.
	- Bonus: Implement a reporting system that generates a detailed analysis report with issue severity levels.

__10. Interpreter for a Domain-Specific Language (DSL)__

- *Design and implement an interpreter for a domain-specific language tailored to a particular problem, like
  a data manipulation language or a configuration language.*
	- Challenge: Design the syntax and semantics of the DSL. Parse the language and generate an appropriate AST.
	- Enhancement: Build an execution model that evaluates the DSL code and produces meaningful output for the domain.
	- Extension: Optimise the execution of the DSL by introducing caching, memoization, or other techniques.
	- Bonus: Provide a visual representation or a web-based interface for users to interact with the DSL.

__11. A Simple JavaScript Engine__

- *Create an interpreter or VM that can execute a subset of JavaScript, focusing on basic features like variable
  assignment, arithmetic operations, and control flow.*
	- Challenge: Parse JavaScript-like syntax, manage variables, and implement basic operations like addition,
      subtraction, loops, and conditionals.
	- Enhancement: Implement support for functions, scopes, and closures.
	- Extension: Implement asynchronous behaviour (callbacks, promises) and basic error handling (try/catch).
	- Bonus: Add support for simple DOM manipulation if you plan to extend it for web-based execution.

__12. Reverse Engineering a Simple Bytecode__

- *Reverse-engineer a simple bytecode (like a compiled language or VM bytecode) and implement an interpreter to execute it.*
	- Challenge: Design a bytecode format and create a parser for it.
	- Enhancement: Implement an interpreter that can execute the bytecode, simulating how a VM would process it.
	- Extension: Implement a disassembler to convert bytecode back into a more human-readable form.
	- Bonus: Add debugging features like step-by-step execution, breakpoints, and a stack trace.

Each of these projects can be adjusted to fit the scope you're comfortable with. You can also choose to
combine multiple ideas into a single project, like implementing an interpreter that includes optimisation
passes and garbage collection.
