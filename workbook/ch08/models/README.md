
## Programming Language Models or Programming Paradigms

Programming paradigms define the fundamental approaches to structuring and executing computation.
As we have emphasised in the context of programming languages, they shape the way we think about
coding. They influence not only how programmers write code but also how they approach problem-solving,
data manipulation, and control flow. Paradigms emerge from different ways of modelling computation,
each offering distinct advantages and trade-offs in terms of expressiveness, maintainability,
efficiency, and correctness.

At their core, paradigms dictate how computations are expressed and executed. Some emphasise state
changes and execution order, others focus on declarative logic, and some are based on abstracting
operations into high-level transformations. The distinctions between paradigms often stem from how
they handle state management, control flow, concurrency, and abstraction.


### State and Mutation: Imperative vs. Declarative Thinking

One of the fundamental distinctions in programming paradigms is whether computation is based on
explicit state changes or on describing results without detailing the steps to achieve them.

- State-driven paradigms rely on sequences of instructions that modify memory. This reflects
  the way physical computers operate, making it intuitive but also prone to side effects,
  where one change in state may unpredictably affect another part of the program.

- Declarative paradigms shift the focus away from explicit control over execution and state
  changes. Instead of specifying how to compute a result, they describe what the result should
  be, relying on an underlying execution model to determine the best way to derive it.


### Control Flow: Sequential Execution vs. Rules and Constraints

Control flow determines how instructions or expressions are evaluated and in what order.

- Some paradigms assume an explicit, linear sequence of operations where one step follows
  another in a clearly defined order. This approach often aligns with stateful execution,
  requiring detailed management of how data flows through a program.

- Others adopt a rule-based or constraint-driven approach, where computations occur whenever
  certain logical conditions are met, or where the system searches for solutions dynamically.
  Such models allow for greater abstraction, often shifting the burden of control flow from
  the programmer to the underlying system.

 
### Concurrency and Parallelism: How Programs Handle Multiple Executions

Different paradigms also shape how programs handle simultaneous execution of tasks. Some
naturally facilitate parallel computation, while others assume a fundamentally sequential
model that must be explicitly adapted for concurrency.

- Certain paradigms encourage a shared-state model, where multiple execution threads
  operate on the same data. This approach is powerful but requires synchronisation
  mechanisms to prevent conflicts.

- Others favour isolated execution units that communicate indirectly, reducing the
  complexity of coordinating multiple computations but often requiring different
  problem-solving techniques.


### Abstraction: The Role of Encapsulation and Composition

The level of abstraction a paradigm encourages affects how reusable, scalable, and
maintainable a program is.

- Some paradigms emphasise encapsulation, where data and behaviour are tightly bound
  together, ensuring controlled interactions.

- Others promote composition, where programs are built by assembling independent,
  stateless transformations, allowing greater modularity.

- The balance between encapsulation and composition shapes the reusability and
  complexity of software, influencing how different parts of a program interact.


### Trade-offs and Blurred Boundaries

No paradigm is universally superior. Instead, each has trade-offs, making it better suited for
certain types of problems and less effective for others. Some paradigms emphasise clarity and
correctness, while others prioritise performance and low-level control. Additionally, modern
programming often blends paradigms, allowing developers to leverage the strengths of multiple
approaches within the same system.

### Table over Distinguishing Features in Types of Languages

We will not delve into every paradigm, we will leave some, but will examine others in slightly
more detail.

|Programming Model / Paradigm	|Important Features|
|--|--|
|*[Functional Programming](./fp/)*	|First-class functions, immutability, higher-order functions, recursion, lazy evaluation, pure functions, generics|
|*[Object-Oriented Programming](./oo/)*	|Encapsulation, inheritance, polymorphism, abstraction, method overloading/overriding, interfaces/abstract classes, generics|
|*[Event-Driven Programming](./event/)*	|Event loops, callbacks, asynchronous execution, event handlers, observer pattern, state machines|
|*[Concurrent Programming](./concurrent/)*	|Threads, locks, mutexes, semaphores, atomic operations, message passing, parallelism, condition variables|
|*Logic Programming*	|Facts, rules, queries, backtracking, unification|
|*Declarative Programming*	|SQL, pattern matching, rules, constraints|
|*Procedural Programming*	|Procedures, functions, control structures (loops, conditionals), modularity, call stack|
|*Reactive Programming*	|Data streams, observers/subscribers, backpressure, push-based updates|

