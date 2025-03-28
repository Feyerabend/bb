
## Imperative Programming

You should already be well aware of the imperative programming style from the working examples and code from the book.
In short *imperative programming* focuses on *how* a program should achieve its goal, using constructs like variables,
assignments, loops, and conditionals to control program flow. The includede BASIC interpreter follows a command-driven
execution model, where commands (PRINT, INPUT, GOTO, etc.) operate by mutating the global state (Interpreter.vars,
Interpreter.code, etc.). This approach aligns well with traditional BASIC-style interpreters, which are typically written
imperatively.

Some aspects of imperative programming in this code:
- Sequential execution: The interpreter reads and executes instructions in a strict order, following numbered program lines.
- Mutable state: The Interpreter class maintains global dictionaries (vars, code, loops) that store the program state and
  are updated as commands execute.
- Explicit control flow: GOTO, IF-THEN, FOR-NEXT, and subroutine handling (GOSUB and RETURN) dictate execution order,
  similar to classic imperative languages like Fortran or Pascal.
- Procedural decomposition: The *interpreter* breaks down functionality into classes and methods (execute(), expr(),
  term(), etc.), reinforcing procedural programming principles.

Even though the code employs object-oriented techniques (such as the Command hierarchy for executing statements), its
execution model remains imperative—commands mutate state step by step, and control flow is directed explicitly via
conditions and jumps. This is different from declarative programming, where you describe *what* should be done rather
than *how*.


### Suggested Projects

If you're a student looking to deepen your understanding of imperative programming using this interpreter, you have plenty
of opportunities to explore fundamental and advanced concepts. Here are a few ideas to help you extend the interpreter and
write interesting programs:


__1. Learn the Basics of Imperative Programming__

This interpreter already follows an imperative paradigm, meaning that programs consist of explicit sequences of commands
that modify state. 
- Writing small programs that manipulate numbers, strings, or simple data structures using variables and loops.
- Exploring how control structures (like conditionals and loops) work inside the interpreter.
- Understanding the execution model: how the program counter moves, how values are stored, and how function calls work.


__2. Extend the Interpreter__

Once you’re comfortable with how the interpreter works, you can modify it to support additional features.
- Local Variables & Scopes: If your interpreter doesn’t already support local variables, implement a scoping mechanism.
- Function Definitions: Allow defining functions within the interpreted language.
- Error Handling: Add a simple mechanism for catching runtime errors, like division by zero or undefined variables.
- Structured Data: Implement arrays, dictionaries, or even simple object-oriented features.
- Concurrency: Introduce parallel execution or coroutines.


__3. Write Example Programs__

You can write various small programs to test and demonstrate how imperative programming works in your interpreter.
- Math Computations: Write programs that calculate prime numbers, factorials, or Fibonacci sequences.
- Stateful Graphics: If your interpreter has a graphics component (like PostScript), create simple animations or shape-based visualisations.
- Sorting Algorithms: Implement and compare different sorting techniques (Bubble Sort, QuickSort, MergeSort) in your language.
- Text Processing: Create a simple text-based search tool that finds words in a string.


__4. Build Projects__

For a deeper challenge, try one of these projects:
- A Mini Game Engine: Implement a way to define simple game logic, such as moving characters or basic physics.
- A Small Shell or REPL: Allow users to type commands interactively, making your interpreter behave like a command-line shell.
- A Micro Database: Implement an in-memory key-value store with basic query operations.
- A Tiny Assembler or Compiler: Write a small compiler that translates a subset of your interpreted language into another format, like TAC or LLVM IR.

Each of these projects will push your understanding of imperative programming while giving you something fun and useful to build.
