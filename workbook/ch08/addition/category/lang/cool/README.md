
## Project Suggestions: Design Programming Languages

These three files form a possible foundation for exploring category theory in programming language design:

- *cat_cool.py*: A basic interpreter for a Categorical Object-Oriented Language (COOL), emphasising
  category theory concepts like objects (classes/types), morphisms (subtyping/inheritance), and
  natural transformations (method dispatch).

- *cat_gen.py*: An extension of cat_cool.py that adds generics (modeled as endofunctors), variance
  (covariant/contravariant), and bounded polymorphism.

- *cat_parse.py*: A parser for COOL (with generics support) using categorical parser combinators,
  which can parse source code into ASTs for interpretation.

Here are some projects categorized by which files they primarily build upon. These range from
beginner-friendly extensions to more advanced integrations. They aim to deepen understanding of
category theory, language implementation, or parsing.


### 1. Projects Based Solely on cat_cool.py (Basic COOL Interpreter)

These focus on extending the core OOP language without generics or parsing, emphasising
categorical concepts like subtyping and composition.

- *Add Interface Implementation and Checks*
  - *Description*: Extend `ClassDef` and `Interface` to enforce that classes implementing
    interfaces must provide all required methods (already partially checked in `is_implemented_by`).
    Add runtime or type-checking enforcement during class registration. Introduce a new statement
    like `implements InterfaceName` in class definitions.
  - *Goals*: Demonstrate universal properties (interfaces as initial/terminal objects). Test with
    examples like a `Speakable` interface implemented by `Dog` and `Cat`.
  - *Difficulty*: Easy-Medium.
  - *Why?*: Builds on the existing interface system to show how category theory's universal
    constructions apply to OOP polymorphism.

- *Implement Method Overriding with Super Calls*
  - *Description*: Add support for `super` keyword in methods (e.g., in `Method` body, allow
    `super.speak()`). Modify `MethodCall` evaluation to handle super calls by traversing the
    inheritance chain (morphism composition).
  - *Goals*: Create a demo where a subclass overrides a method but calls the superclass version,
    showcasing morphism composition in inheritance.
  - *Difficulty*: Medium.
  - *Why?*: Highlights categorical composition (chaining subtyping morphisms) in method dispatch.

- *Add Basic Exception Handling*
  - *Description*: Introduce a `TryCatch` statement and an `Exception` class hierarchy. Use
    subtyping for catch blocks (e.g., catch a subtype exception).
    Model exceptions as special morphisms in the type category.
  - *Goals*: Handle runtime errors (e.g., division by zero in `BinaryOp`) and print stack traces
    using the environment chain.
  - *Difficulty*: Medium.
  - *Why?*: Extends the runtime to handle errors categorically, treating exceptions as
    "error arrows" in the category.


### 2. Projects Involving cat_gen.py (COOL with Generics)

These build on the generics extension, focusing on functors, variance, and polymorphic types.

- *Implement Generic Methods Inside Classes*
  - *Description*: Allow methods in `GenericClassDef` to have their own type parameters (e.g.,
    `def <U> map(U func): ...`). Extend `Method` to include type params and substitute them during
    calls. Update type checking in `MethodCall`.
  - *Goals*: Demo with a `Box<T>` method like `map<U>(func: T -> U): Box<U>`, showing functorial mapping.
  - *Difficulty*: Medium-Hard.
  - *Why?*: Reinforces generics as endofunctors, with method type params as higher-kinded types.

- *Add Collection Classes with Variance Enforcement*
  - *Description*: Implement built-in generics like `List<T>` (covariant) or `Set<T>` (invariant).
    Add methods like `add` and `get`, and test subtyping (e.g., `List<Dog> <: List<Animal>` for
    covariant). Extend `TypeEnvironment.is_subtype` to handle more variance cases.
  - *Goals*: Create a demo program that assigns a `List<Dog>` to a `List<Animal>` variable and iterates over it.
  - *Difficulty*: Medium.
  - *Why?*: Explores categorical variance properties in real data structures, building on the existing `Pair<T, U>` example.

- *Bounded Wildcards for Flexible Subtyping*
  - *Description*: Support wildcard types like `Box<? extends Animal>` in type declarations.
    Modify `TypeParameter` and `is_subtype` to handle upper/lower bounds dynamically (e.g.,
    producer-consumer principle with PECS).
  - *Goals*: Test with functions that accept `Box<? extends Animal>` but not `Box<Dog>` for
    writes (due to covariance restrictions).
  - *Difficulty*: Hard.
  - *Why?*: Advances bounded polymorphism as universal properties, mimicking Java generics
    but with explicit category theory ties.


### 3. Projects Involving cat_parse.py (Categorical Parser)

These extend the parser combinators or use them to parse more complex COOL code.

- *Extend Parser to Handle More Statements*
  - *Description*: Add parsing for new constructs like `if` statements (already in cat_cool.py's
    AST but not parsed), loops, or class definitions. Update `COOLParser._build_parsers` with new
    combinators using `bind`, `or_else`, etc.
  - *Goals*: Parse and build an AST for a full program like `{ if (x > 0) print("positive"); }`.
  - *Difficulty*: Easy-Medium.
  - *Why?*: Demonstrates parser combinators as categorical structures (monads/functors for parsing),
    testing mutual recursion with `Delayed`.

- *Error Reporting and Recovery in Parser*
  - *Description*: Enhance `ParseResult` to include position info (line/column). Implement error
    recovery (e.g., skip to semicolon on failure). Add pretty-printing for ASTs.
  - *Goals*: Run the parser on invalid input and output helpful errors, like "Expected ';' at line 2".
  - *Difficulty*: Medium.
  - *Why?*: Makes the parser more robust, showing how categorical combinators handle failure as
    part of the monadic structure.


### 4. Projects Combining Multiple Files (e.g., Full COOL Compiler/Interpreter)

These integrate parsing, generics, and interpretation for a more complete system.

- *Build a Full COOL Interpreter: Parse + Execute*
  - *Description*: Use cat_parse.py to parse source code into ASTs, then execute them using cat_cool.py's
    evaluator. Map parsed `Statement`s and `Expression`s to the interpreter's classes. Start with simple
    programs from the test_parser() function.
  - *Goals*: Write a main function that reads COOL source, parses it, type-checks, and runs it
    (e.g., "var x: Int = 42; print(x);").
  - *Difficulty*: Medium.
  - *Why?*: Combines parsing (categorical combinators) with execution (categorical OOP), creating
    a toy language interpreter.

- *Add Generics Parsing and Integration*
  - *Description*: Extend cat_parse.py to fully parse generic class definitions (e.g.,
    "class Box<T> { ... }"). Integrate with cat_gen.py by registering parsed generics
    in `TypeEnvironment`. Handle variance annotations like "+T" in parsing.
  - *Goals*: Parse and execute a program using generics, like the Box example in cat_gen.py's demo.
  - *Difficulty*: Hard.
  - *Why?*: Unites all three files: Parse generics (functors), register them categorically,
    and execute polymorphically.

- *COOL to Python Transpiler*
  - *Description*: After parsing with cat_parse.py, generate Python code from the AST
    (using cat_gen.py's type system for generics). Handle inheritance by generating Python
    classes with super calls.
  - *Goals*: Transpile a COOL program to runnable Python, preserving categorical structures
    (e.g., subtyping as inheritance).
  - *Difficulty*: Hard.
  - *Why?*: Applies the system to code generation, showing how category theory can inform
    language translation.

These projects can be scaled: Start small (e.g., add one feature) and iterate. If you're implementing them,
focus on testing with the existing demos/tests. For more theory depth, document how each extension embodies
a category theory concept (e.g., functors for generics).


