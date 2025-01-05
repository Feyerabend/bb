
## Type Systems

A type system is a formal system used in programming languages to categorize and define
the behavior of values and expressions. It specifies how values and variables are classified
into types (i.e. integer, string, boolean ..) and how operations are applied to these types.
The primary goal of a type system is to ensure that a program behaves as expected by catching
errors at compile time (in statically typed languages) or at runtime (in dynamically typed
languages).


1. Types: A type represents a classification of data. Types describe properties of values
   such as the kind of data they hold, the types. Examples of types include:
	- Primitive types: Basic types like int, char, boolean, etc.
	- Composite types: More complex structures like arrays, lists, tuples, or user-defined
      types such as classes or structs.
	- Function types: These define the types of inputs and outputs of a function
      (wich could be a function that takes two integers and returns a boolean might have the
      type '(int, int) -> bool').

2. Type Checking: Type checking is the process of verifying and enforcing the constraints of
   types in a program. There are two primary forms of type checking:
	- Static Type Checking: Performed at compile-time. The compiler checks that values and operations
      are consistent with their declared types before generating machine code. Examples of statically
      typed languages include Java, C, and Rust.
	- Dynamic Type Checking: Performed at runtime. In dynamically typed languages, such as Python,
      JavaScript, or Ruby, the types of values are determined during execution.

3. Type Inference: Some programming languages have type inference, which allows the compiler or
   interpreter to automatically deduce the type of an expression based on the context. This feature
   is common in languages like Haskell and modern versions of TypeScript.

4. Type Safety: A type system aims to provide type safety, which prevents type errors (e.g.,
   trying to add a string and a number) by ensuring that operations are only performed on
   compatible types. Type safety helps to prevent common bugs and makes code more predictable.

5. Subtyping and Polymorphism: In object-oriented languages and certain functional languages,
   types can have a hierarchy. For example, in many object-oriented languages, a Dog class might
   inherit from an Animal class. This creates a subtype relationship, where a Dog is a type of Animal.
   This allows for polymorphism, where functions or methods can operate on objects of different
   types that share a common superclass.

6. Type Systems in Functional Programming: Functional languages like Haskell, OCaml, and Scala often
   use advanced type systems that include parametric polymorphism (generics), higher-order types,
   and dependent types. These systems allow for highly flexible and reusable code while still
   providing strong guarantees about correctness.


### How Type Systems Work

1. Declarations and Assignments: In most programming languages, variables must be declared with a
   type or inferred from context. For example, in C, a variable is declared with a specific type,
   and the compiler checks that the variable’s value matches that type.

```c
int x = 5;  // x is an integer
```

In a dynamically typed language like Python:

```python
x = 5  # x is inferred to be an integer
```

2. Operations on Types: A type system ensures that operations are performed on compatible types.
   For example, adding two integers is allowed, but adding an integer to a string might not be,
   depending on the type system:
	- In C (statically typed), the compiler will generate an error if you try to add incompatible types.
	- In Python (dynamically typed), this check happens at runtime and raises an exception if the types are incompatible.

3. Type Constraints: Some type systems allow for more complex type constraints to express relationships
   between types. For example, in Haskell, you can define functions that work with multiple types through type classes:

```haskell
class Eq a where
  (==) :: a -> a -> Bool
```

4. Type Systems in Compilation: In a compiled language, type systems are usually checked by the compiler.
   The compiler generates an abstract syntax tree (AST) and performs type checking to ensure that the
   program adheres to the constraints of its type system. After that, the program can be transformed
   into machine code or bytecode.

5. Type Systems in Interpretation: In interpreted languages, type checking can be deferred to runtime,
   where the interpreter checks types as the code executes. This is seen in languages like Python,
   where variables can change type during execution.


### Types of Type Systems

1. Static vs Dynamic Typing:
	- Static Typing: Types are determined at compile time, and the type of every variable is known before
      the program runs. Examples: Java, C++, Rust.
	- Dynamic Typing: Types are determined at runtime, and variables do not have fixed types until execution.
      Examples: Python, JavaScript, Ruby.

2. Strong vs Weak Typing:
	- Strong Typing: The type system strictly enforces type constraints, meaning that operations between
      mismatched types will result in errors or exceptions. Examples: Python, Java, Rust.
	- Weak Typing: The type system is more flexible and may perform implicit type conversions. For example,
      adding an integer to a string might automatically convert the integer to a string. Examples: JavaScript, PHP.

3. Nominal vs Structural Typing:
	- Nominal Typing: The type is determined by its name or declaration rather than its structure. This means
      that two types with the same structure but different names are considered distinct types. Examples: Java, C++.
	- Structural Typing: The type is determined by its structure (e.g., the fields or methods it has) rather
      than its name. Types with the same structure are considered compatible. Examples: TypeScript, Go.

4. Polymorphic vs Non-Polymorphic Typing:
	- Polymorphism: A language supports polymorphism when a function or method can operate on different types
      through a shared interface. For example, a function in C++ or Java that operates on a base class but can
      accept instances of derived classes.
	- Non-Polymorphic Typing: A language or type system that does not support polymorphism requires functions
      or methods to operate on specific types.

5. Dependent Types:
	- In dependent types, the type of a value can depend on the value itself. This is a feature seen in some
      advanced functional programming languages like Agda and Coq, where types can be constructed depending
      on the actual data (for example, a type that defines a vector of a specific length).


#### How Type Systems Are Implemented

1. Type Checking Algorithms: The implementation of type systems in compilers or interpreters typically involves
   algorithms that traverse the program’s abstract syntax tree (AST) or intermediate representations (IR).
   The type checker will verify that expressions and variables are used correctly according to their types.

2. Type Inference: Many modern languages use type inference algorithms to automatically deduce types for variables
   and expressions based on context. This makes the language more flexible while retaining type safety. Type
   inference algorithms, such as Hindley-Milner (used in languages like Haskell), can often infer types without
   explicit annotations.

3. Type Representation: Types are typically represented in a compiler or runtime as data structures such as:
	- Type Trees: Representing hierarchical relationships between types.
	- Symbol Tables: Storing type information for variables and functions.
	- Abstract Syntax Tree (AST): Type checking is often done by traversing the AST, with each node representing
      a syntactic construct and its associated type.

4. Runtime Systems for Dynamic Languages: In dynamically typed languages, the runtime system plays a significant
   role in checking types. When an operation is executed, the runtime system checks the types of operands and
   ensures the operation is valid. This is why dynamically typed languages tend to have slower execution than
   statically typed ones.


### Conclusion

A type system serves to ensure correctness, consistency, and safety in programming languages by enforcing rules
about how values and variables are used. It can help catch many types of errors before execution (static typing)
or during execution (dynamic typing). The structure and complexity of a type system vary greatly between programming
languages, with some providing simple checks and others offering powerful features like type inference, polymorphism,
and dependent types.
