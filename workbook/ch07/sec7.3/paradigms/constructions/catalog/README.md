
### Constructions in Relation to Models / Paradigms

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

