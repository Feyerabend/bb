
## Alternative Routes: Functional and Structural Foundations

Although this chapter follows the imperative route, two other major perspectives on
programming foundations are worth understanding: the *functional* route and the *structural*
route. Both provide their own logic, their own way of thinking about computation,
and their own historical motivations. These routes are not merely stylistic choices;
they represent different answers to the question “What is computation?”


### The Functional Perspective

The functional perspective approaches computation as the evaluation of expressions rather
than the manipulation of changing state. In this view, a program is a collection of
definitions--functions that accept values and return new values. The key principle is
immutability: once a value is created, it does not change. Instead of updating variables,
new values are produced from old ones, much like in algebra.

This approach works because it eliminates a whole class of complications. If nothing
changes, then the meaning of an expression depends solely on the meaning of its parts.
This property, called *referential transparency*, makes reasoning about programs far easier.
A function call can be replaced by its result without altering the program’s behaviour.
Many optimisations, such as memoisation and lazy evaluation, rely on this stability.

Historically, the functional perspective arises from mathematical logic and the lambda
calculus, which was created to formalise the idea of functions and substitution long
before computers existed. Early researchers saw computation as a form of symbolic
reduction--expressions simplifying into other expressions--and functional programming
languages grew directly out of that tradition. Languages such as Lisp, ML, and Haskell
preserve this lineage.

In a functional system, the "flow" of computation is not described by commands but by
expressions nestingly applied to one another. A functional program therefore expresses
*what* something is, not *how* to update some state to achieve it. This difference sets
the functional route apart from the imperative foundations of state, memory, and sequential
steps.


### The Structural Perspective

The structural route focuses on the shape of both data and computation. Instead of loops
and mutable counters, it relies heavily on recursion: defining a problem in terms of smaller
instances of itself. Instead of manual branching, it uses pattern-matching to express how
different cases of a data structure should be handled.

This perspective works particularly well when dealing with rich, nested data--lists, trees,
syntax structures, and decomposable patterns. A structural program follows the form of the
data being processed: the structure of the argument determines which branch of the computation
is used. This leads to programs that are often clearer, shorter, and more directly aligned
with the problem itself.

Structurally oriented languages or styles were influenced by mathematical induction, logic,
and the desire to describe algorithms in a way that naturally mirrors the problem's conceptual
form. In this setting, "control flow" is handled not by jumps or mutable indices, but by
systematically breaking data apart and defining rules for each case. The programmer describes
the structure of the computation as a set of well-formed transformations.

Structurally oriented computation remains close to mathematical reasoning: one proves a
property about a program the same way one proves a property about inductively defined
objects--by analysing each structural case. This transparency is one of its major strengths.


#### Then Why?

These routes exist because *computation* is not only a machine-level phenomenon but also
a conceptual one. Different models of programming emphasise different aspects of reasoning:

- The imperative route reflects how hardware actually executes instructions.
  It introduces programming as state changes and control flow, mapping naturally
  to the underlying architecture.
- The functional route emphasises mathematical purity, simplicity of reasoning,
  and expressions as the central unit of computation.
- The structural route emphasises decomposition, recursion, and pattern-directed
  computation, mirroring the shape of data.

Each route answers a different question.
Imperative programming asks: *How do we tell the machine what to do?*
Functional programming asks: *How do we describe computations cleanly and predictably?*
Structural programming asks: *How can computation follow the form of the data itself?*

Understanding these alternative routes provides valuable context. Even if this chapter
focuses on the imperative foundations--largely because they map directly onto the machine-level
concepts explored in the following VM chapter--the functional and structural routes show
that computation is broader and more varied than any single model. They offer powerful
abstractions and insights that become increasingly important as students progress beyond
the machine-level view.

