
## Programming Language Models / Programming Paradigms

Programming paradigms define the fundamental approaches to structuring and executing computation.
As we have emphasised in the context of programming languages, *they shape the way we think about
coding*. Therefore it is also beneficial to learn several different paradigms. They influence not
only how programmers write code but also how they approach problem-solving, data manipulation,
and control flow. Paradigms emerge from different ways of modelling computation, each offering
distinct advantages and trade-offs in terms of expressiveness, maintainability, efficiency, and
correctness.

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
|*[Imperative Programming](./imp/)* |Mutable state, explicit control flow, sequences of statements, loops, conditionals, function calls, procedural abstraction, side effects|
|*[Functional Programming](./fp/)*	|First-class functions, immutability, higher-order functions, recursion, lazy evaluation, pure functions, generics|
|*[Object-Oriented Programming](./oo/)*	|Encapsulation, inheritance, polymorphism, abstraction, method overloading/overriding, interfaces/abstract classes, generics|
|*[Event-Driven Programming](./event/)*	|Event loops, callbacks, asynchronous execution, event handlers, observer pattern, state machines|
|*[Concurrent Programming](./concurrent/)*	|Threads, locks, mutexes, semaphores, atomic operations, message passing, parallelism, condition variables|
|*[Concatenative Programming](./concat/)*   |Stack-based execution, function composition, point-free style, implicit data flow, postfix notation, small reusable functions, lack of named variables|
|*[Logic Programming](../../ch05/code/wam/)* ([ch05](../../ch05/code/))	|Facts, rules, queries, backtracking, unification|
|*[Procedural Programming](../../ch05/code/pl0/)* ([ch05](../../ch05/code/))	|Procedures, functions, control structures (loops, conditionals), modularity, call stack|
|*Declarative Programming*	|SQL, pattern matching, rules, constraints|
|*Reactive Programming*	|Data streams, observers/subscribers, backpressure, push-based updates|
|*Aspect-Oriented Programming* (AOP)  |Aspects, join points, advice (before/after/around), weaving, cross-cutting concerns, separation of concerns|


### Paradigms, Models, Techniques and Styles

If one stretches the definition of a paradigm to include computational styles that significantly
impact code structure and execution, then *[Array Programming](./array/)* could be considered a
specialised paradigm, much like *Dataflow Programming*, indeed *Reactive Programming*,
or *Parallel Programming*.

The latter you might find interesting. A key reason why *Concurrent Programming* is considered
more of a paradigm while *Parallel Programming* is not is that concurrency changes how we think
about program structure, state, and communication, whereas parallelism is primarily about how
efficiently computations are performed. Parallelism often emerges as an implementation detail
of concurrent programs when mapped onto hardware that can execute tasks simultaneously.

There are no hard boundaries that definitively classify a concept as a programming paradigm
or something else like a computational model, style, or technique. These classifications exist
on a spectrum rather than as rigid categories. The reason for this is that programming paradigms 
evolve over time, often borrowing ideas from each other, and many techniques exist at multiple
levels of abstraction.

For example, *Functional Programming* is a well-defined paradigm with core principles like
*immutability and first-class functions*, but elements of functional programming (e.g. higher-order
functions, pure functions) are often used in object-oriented languages like Java or Python.
Similarly, *Aspect-Oriented Programming (AOP)* is sometimes considered an *extension of
object-oriented programming* rather than an independent paradigm.

Furthermore, concepts like *Concurrent Programming* and *Reactive Programming* demonstrate
how blurry these distinctions can be. *Concurrency* is often called a paradigm because it
fundamentally influences program structure, yet it is also an execution model.
*Reactive Programming* could be seen as a paradigm, but it is more accurately a computational
style that can be applied in different paradigms.

If we go back, even *Parallel Programming*, which is often seen as a hardware-related
execution model, influences how software is structured and written, making it closer to a
paradigm in some contexts. *Declarative Programming*, on the other hand, is sometimes
described as a paradigm but is more of a broad *umbrella term* that encompasses multiple
paradigms (functional, logic, database query languages like SQL).

In short, classifications like "paradigm" or "style" are *human-made distinctions* that
help us reason about programming but are not absolute. Many concepts exist at the intersection
of multiple classifications, making it difficult to draw strict boundaries. Instead of
thinking in rigid categories, it's often more useful to see programming concepts as
*interconnected ideas* that influence each other in various ways.
