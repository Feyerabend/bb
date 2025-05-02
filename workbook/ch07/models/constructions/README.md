
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
| Imperative                | Mutable variables (1)                           |
|                           | Assignment statements (2)                       |
|                           | Sequence of statements (3)                      |
|                           | Loops (4)                                       |
|                           | Conditionals (5)                                |
|                           | Function/procedure calls (6)                    |
|                           | Explicit control flow* (3, 7)                   |
|                           | Side effects (8)                                |
|                           | Procedure abstraction (9)                       |
| Functional                | First-class functions* (10)                     |
|                           | Higher-order functions* (10)                    |
|                           | Pure functions* (11)                            |
|                           | Immutability* (12)                              |
|                           | Recursion* (13)                                 |
|                           | Lazy evaluation (14)                            |
|                           | Closures* (10)                                  |
|                           | Currying (15)                                   |
|                           | Partial application (16)                        |
|                           | Algebraic data types (ADTs)* (17)               |
|                           | Pattern matching* (17)                          |
|                           | Type inference (18)                             |
|                           | Parametric polymorphism (generics)* (19)        |
|                           | Monads (20)                                     |
|                           | Functors (21)                                   |
|                           | Applicatives (22)                               |
|                           | Tail call optimisation (23)                     |
| Object-Oriented           | Classes and objects (24)                        |
|                           | Encapsulation* (25)                             |
|                           | Inheritance (26)                                |
|                           | Polymorphism (subtype) (27)                     |
|                           | Method overriding (28)                          |
|                           | Method overloading (29)                         |
|                           | Constructors/destructors (30)                   |
|                           | Interfaces / Abstract classes (31)              |
|                           | Access modifiers (32)                           |
|                           | Composition (33)                                |
|                           | Generics* (19)                                  |
|                           | Static methods / Static variables (34)          |
|                           | Mixins / Traits (35)                            |
| Event-Driven              | Event loops (36)                                |
|                           | Event handlers (37)                             |
|                           | Callbacks* (38)                                 |
|                           | Asynchronous execution* (39)                    |
|                           | Observer pattern* (40)                          |
|                           | Signals and slots (41)                          |
|                           | Publish/subscribe pattern* (40)                 |
|                           | State machines* (42)                            |
| Concurrent                | Threads (43)                                    |
|                           | Processes (44)                                  |
|                           | Locks (45)                                      |
|                           | Semaphores (46)                                 |
|                           | Monitors (47)                                   |
|                           | Atomic operations (48)                          |
|                           | Message passing* (49)                           |
|                           | Futures / Promises* (50)                        |
|                           | Parallelism (51)                                |
|                           | Barriers (52)                                   |
|                           | Condition variables (53)                        |
|                           | Thread pools (54)                               |
|                           | Software transactional memory (55)              |
| Concatenative             | Stack-based execution (56)                      |
|                           | Postfix notation (57)                           |
|                           | Function composition* (10)                      |
|                           | Point-free style (58)                           |
|                           | Implicit argument passing (59)                  |
|                           | Small reusable combinators (60)                 |
|                           | Lack of named variables (61)                    |
| Logic                     | Facts (62)                                      |
|                           | Rules* (63)                                     |
|                           | Queries (64)                                    |
|                           | Unification (65)                                |
|                           | Backtracking (66)                               |
|                           | Cut operator (67)                               |
|                           | Definite clause grammars (68)                   |
|                           | Meta-programming (69)                           |
| Procedural                | Procedures (9)                                  |
|                           | Control structures (loops, conditionals)* (4,5) |
|                           | Modularisation (70)                             |
|                           | Call stack (71)                                 |
|                           | Pass-by-value / Pass-by-reference (72)          |
|                           | Static/global variables (73)                    |
|                           | Explicit sequencing* (3,7)                      |
| Declarative               | Pattern matching* (17)                          |
|                           | Constraints (74)                                |
|                           | Rules* (63)                                     |
|                           | SQL-style queries (75)                          |
|                           | Functional relations* (76)                      |
|                           | Property declarations (77)                      |
|                           | Comprehensions (78)                             |
| Reactive                  | Data streams (79)                               |
|                           | Observers/subscribers* (40)                     |
|                           | Push-based updates (80)                         |
|                           | Backpressure (81)                               |
|                           | Observable sequences (82)                       |
|                           | Operators (map, filter, merge, zip)* (83)       |
|                           | Hot vs cold observables (84)                    |
|                           | Reactive extensions (Rx) (85)                   |
|                           | Event emitters (86)                             |
| Aspect-Oriented           | Aspects (87)                                    |
|                           | Join points (88)                                |
|                           | Pointcuts (89)                                  |
|                           | Advice (before, after, around) (90)             |
|                           | Weaving (91)                                    |
|                           | Cross-cutting concerns (92)                     |
|                           | Interceptors / Decorators* (93)                 |

#### Common constructions

Features appearing across multiple paradigms:

- *(10)* First-class functions, higher-order functions, closures, function composition:  
  FP, Concatenative, Event-driven, Reactive → Encourages abstraction and reuse

- *(13, 17)* Recursion, pattern matching, ADT (Algebraic data types):  
  FP, Declarative, Logic → Strengthens declarative & structural expression

- *(38, 39, 40)* Callbacks, asynchronous execution, observers/subscribers:  
  Event-driven, Reactive, Concurrent → Drives concurrency and reactive data flow

- *(3, 4, 5, 7)* Explicit control flow, procedures, control structures (loops/conditionals):  
  Imperative, Procedural → Enables low-level control

- *(19)* Generics / Parametric polymorphism:  
  FP, OO → Boosts type abstraction and reusable code

- *(40)* Observer pattern, publish/subscribe pattern:  
  Event-driven, Reactive → Enables decoupled event propagation

- *(49, 50)* Message passing, futures/promises:  
  Concurrent, Event-driven → Supports safe concurrency models

- *(93)* Interceptors / Decorators:  
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

