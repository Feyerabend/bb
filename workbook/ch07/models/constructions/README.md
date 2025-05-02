
## Programming Language Constructions

Programming languages are not neutral tools; they reflect underlying theories of computation and
design philosophies. The constructions that a language emphasises--such as recursion, monads,
inheritance, or pattern matching--are deliberate choices that guide how programmers conceptualise
and solve problems.

For example, Haskell encourages recursion and pure functions, reflecting a foundation in lambda
calculus and category theory, where functions are transformations without mutable state. In
contrast, imperative languages like C prioritise explicit loops and mutable variables, aligning
with the von Neumann architecture and a view of programs as sequences of state changes.

Similarly, Haskell enforces explicit handling of side effects via monads, making the boundary
between pure and impure computations clear. In languages like Python or Java, side effects can
appear anywhere without explicit markers, placing the responsibility on the programmer to manage
them carefully.

These contrasts illustrate that programming languages encode theoretical commitments, influencing
the patterns of reasoning they support and the constructions they make convenient. Awareness of
these commitments helps programmers understand not just how to use a language,
but why it works the way it does.


| Language     | Constructions                                                            |
|--------------|----------------------------------------------------------------------------|
| C            | Mutable vars, loops, conditionals, explicit control flow, procedures      |
| C++          | Classes, inheritance, generics, composition, threads, locks, functions    |
| Java         | Classes, inheritance, interfaces, polymorphism, threads, futures, generics|
| C#           | Classes, inheritance, LINQ (map/filter), events, delegates, async/await   |
| Python       | First-class funcs, OO (classes), dynamic typing, list comprehensions, decorators |
| Haskell      | Pure functions, ADTs, pattern matching, lazy evaluation, monads, type inference |
| Scala        | Pure functions, pattern matching, traits (mixins), monads, generics       |
| JavaScript   | First-class funcs, closures, event loop, callbacks, promises, async/await |
| Erlang       | Message passing, recursion, immutable state, pattern matching, processes  |
| Go           | Goroutines, channels, static typing, explicit control flow                |
| Rust         | Ownership, pattern matching, ADTs, threads, generics, safe concurrency    |
| Prolog       | Facts, rules, queries, unification, backtracking                          |
| SQL          | Queries, constraints, rules, declarative relations                        |
| Forth        | Stack-based execution, postfix notation, small reusable combinators       |
| Elm          | Pure functions, pattern matching, ADTs, subscriptions, signals            |
| AspectJ      | Aspects, join points, advice, weaving, cross-cutting concerns             |


### Constructions in Relation to Models


| Paradigm / Model          | Construction                                    |
|---------------------------|-------------------------------------------------|
| Imperative                | Mutable variables                               |
|                           | Assignment statements                           |
|                           | Sequence of statements                          |
|                           | Loops                                           |
|                           | Conditionals                                    |
|                           | Function/procedure calls                        |
|                           | Explicit control flow*                          |
|                           | Side effects                                    |
|                           | Procedure abstraction                           |
| Functional                | First-class functions*                          |
|                           | Higher-order functions*                         |
|                           | Pure functions*                                 |
|                           | Immutability*                                   |
|                           | Recursion*                                      |
|                           | Lazy evaluation                                 |
|                           | Closures*                                       |
|                           | Currying                                        |
|                           | Partial application                             |
|                           | Algebraic data types (ADTs)*                    |
|                           | Pattern matching*                               |
|                           | Type inference                                  |
|                           | Parametric polymorphism (generics)*             |
|                           | Monads                                          |
|                           | Functors                                        |
|                           | Applicatives                                    |
|                           | Tail call optimisation                          |
| Object-Oriented           | Classes and objects                             |
|                           | Encapsulation*                                  |
|                           | Inheritance                                     |
|                           | Polymorphism (subtype)                          |
|                           | Method overriding                               |
|                           | Method overloading                              |
|                           | Constructors/destructors                        |
|                           | Interfaces / Abstract classes                   |
|                           | Access modifiers                                |
|                           | Composition                                     |
|                           | Generics*                                       |
|                           | Static methods / Static variables               |
|                           | Mixins / Traits                                 |
| Event-Driven              | Event loops                                     |
|                           | Event handlers                                  |
|                           | Callbacks*                                      |
|                           | Asynchronous execution*                         |
|                           | Observer pattern*                               |
|                           | Signals and slots                               |
|                           | Publish/subscribe pattern*                      |
|                           | State machines*                                 |
| Concurrent                | Threads                                         |
|                           | Processes                                       |
|                           | Locks                                           |
|                           | Semaphores                                      |
|                           | Monitors                                        |
|                           | Atomic operations                               |
|                           | Message passing*                                |
|                           | Futures / Promises*                             |
|                           | Parallelism                                     |
|                           | Barriers                                        |
|                           | Condition variables                             |
|                           | Thread pools                                    |
|                           | Software transactional memory                   |
| Concatenative             | Stack-based execution                           |
|                           | Postfix notation                                |
|                           | Function composition*                           |
|                           | Point-free style                                |
|                           | Implicit argument passing                       |
|                           | Small reusable combinators                      |
|                           | Lack of named variables                         |
| Logic                     | Facts                                           |
|                           | Rules                                           |
|                           | Queries                                         |
|                           | Unification                                     |
|                           | Backtracking                                    |
|                           | Cut operator                                    |
|                           | Definite clause grammars                        |
|                           | Meta-programming                                |
| Procedural                | Procedures                                      |
|                           | Control structures (loops, conditionals)*       |
|                           | Modularisation                                  |
|                           | Call stack                                      |
|                           | Pass-by-value / Pass-by-reference               |
|                           | Static/global variables                         |
|                           | Explicit sequencing*                            |
| Declarative               | Pattern matching*                               |
|                           | Constraints                                     |
|                           | Rules*                                          |
|                           | SQL-style queries                               |
|                           | Functional relations*                           |
|                           | Property declarations                           |
|                           | Comprehensions                                  |
| Reactive                  | Data streams                                    |
|                           | Observers/subscribers*                          |
|                           | Push-based updates                              |
|                           | Backpressure                                    |
|                           | Observable sequences                            |
|                           | Operators (map, filter, merge, zip)*            |
|                           | Hot vs cold observables                         |
|                           | Reactive extensions (Rx)                        |
|                           | Event emitters                                  |
| Aspect-Oriented           | Aspects                                         |
|                           | Join points                                     |
|                           | Pointcuts                                       |
|                           | Advice (before, after, around)                  |
|                           | Weaving                                         |
|                           | Cross-cutting concerns                          |
|                           | Interceptors / Decorators*                      |


#### Common constructions (*)

Features that appear across multiple paradigms:
- First-class functions, higher-order functions, closures, function composition:
  Found in FP, Concatenative, Event-driven, Reactive → Encourages abstraction and reuse
- Recursion, pattern matching, ADT (Algebraic data types):
  Found in FP, Declarative, Logic → Strengthens declarative & structural expression
- Callbacks, asynchronous execution, observers/subscribers:
  Event-driven, Reactive, Concurrent → Drives concurrency and reactive data flow
- Explicit control flow, procedures, control structures (loops/conditionals):
  Imperative, Procedural → Enables low-level control
- Generics / Parametric polymorphism:
  FP, OO → Boosts type abstraction and reusable code
- Observer pattern, publish/subscribe pattern:
  Event-driven, Reactive → Enables decoupled event propagation
- Message passing, futures/promises:
  Concurrent, Event-driven → Supports safe concurrency models
- Interceptors / Decorators:
  AOP, OO, FP → Allows cross-cutting or extensible behavior injection

Implications
- Functional + Declarative + Logic share many data-centric and structural abstractions → good for reasoning and correctness
- Event-driven + Reactive + Concurrent share many asynchronous and event-based mechanisms → good for scalability and responsiveness
- OO + FP increasingly blend via generics, higher-order functions, immutability → modern multiparadigm languages exploit both
- Procedural + Imperative is often the "baseline" for control flow, extended by most paradigms


### Projects

If you want to engage directly with how theoretical commitments shape programming languages,
there are several practical projects you can undertake. Each project forces you to make explicit
choices about which constructions you favour and why.


- *Design and implement a small programming language*  

  Building your own language naturally leads you to decide whether to emphasize constructions
  like recursion, mutable state, pattern matching, or message passing. You will make concrete
  design choices that reflect your theoretical preferences.


- *Implement a minimalist interpreter or virtual machine*  

  Even a simple interpreter for arithmetic expressions or stack-based operations will highlight
  how different control flow models (e.g. explicit loops vs recursion) shape language behavior.


- *Transpile code between paradigms*  

  Write a tool that translates between two languages or paradigms (e.g. from imperative to
  functional style). This will expose where constructions align or conflict and force you to
  understand their theoretical underpinnings.


- *Extend an existing language with a new feature*  

  Adding pattern matching, coroutines, or a type system extension to an existing interpreter
  (like a Lisp or Python subset) will show how constructions integrate into a broader system.


- *Compare idiomatic solutions across languages*  

  Choose one problem (such as file I/O, tree traversal, concurrency) and solve it idiomatically
  in different languages and paradigms. This reveals how constructions shape thinking and code
  organization.


- *Implement a language feature from theory*  

  Build concrete implementations of constructs like monads, continuations, backtracking, or
  actor models in a general-purpose language. This gives hands-on understanding of theoretical
  concepts.


These projects are manageable: if scoped carefully. They not only develop technical skill but
also deepen your understanding of how language design shapes program structure and reasoning.

