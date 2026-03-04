

# 1. First-Class Functions

Concept
Functions are values. They can be passed, returned, stored.

Why it exists
To enable abstraction over behavior instead of abstraction over data only.

Use Python for the main exposition.

Example:

```python
def apply(f, x):
    return f(x)

def square(x):
    return x * x

print(apply(square, 5))
```

Key discussion points:
* Functions are objects
* Late binding
* Dynamic dispatch through function objects

Under the hood (C side)

Show:

```c
typedef int (*func)(int);

int apply(func f, int x) {
    return f(x);
}
```

Explain:
* Function pointers
* Indirection cost
* Call stack mechanics
* No environment capture yet

Concurrency link:
Passing behavior instead of shared mutable state reduces coupling.



# 2. Closures

We already have had some.

Concept
Functions capturing surrounding variables.

Why it exists
To encapsulate local state without global mutation.

Use Python for conceptual clarity.

```python
def make_adder(n):
    def adder(x):
        return x + n
    return adder

add5 = make_adder(5)
print(add5(10))
```

Explain:

* Lexical scoping
* Environment capture
* Lifetime extension

Under the hood (C implementation)

Simulate closure:

```c
typedef struct {
    int n;
} context;

int adder(void* ctx, int x) {
    context* c = ctx;
    return x + c->n;
}
```

Explain:

* Environment struct
* Heap allocation requirement
* Explicit lifetime management
* Why GC languages simplify this

Concurrency link:

Captured immutable values are thread-safe.
Captured mutable shared state is not.

This bridges to memory model discussion.



# 3. Immutability

Concept
Data that never changes after construction.

Why it exists

* Simplifies reasoning
* Avoids data races
* Eliminates need for locks in many cases

Primary language: Python (for demonstration)

But emphasise: Python objects are not deeply immutable unless designed so.

Show contrast:

Mutable shared list vs creating new list on update.

Then explain in C:

* const correctness
* Copy vs shared pointer
* Structural sharing requires custom allocator or persistent data structure

Concurrency connection:

Immutability eliminates write-write conflicts.
Memory barriers become less critical when no mutation occurs.

This ties directly to the low-level chapter. More?



# 4. Higher-Order Functions (map, filter, reduce)

Concept
Functions that operate on other functions.

Why it exists

To separate iteration mechanics from transformation logic.

Use Python:

```python
nums = [1,2,3,4]
squared = list(map(lambda x: x*x, nums))
```

Discuss:

* Declarative style
* Reduced surface for mutation
* Pipeline reasoning

Under the hood in C:

Manual loop with function pointer.

Explain:

* No implicit closure
* No lazy iterator
* Manual allocation

Concurrency link:

Stateless transformations are embarrassingly parallel.
Can connect to data-parallel execution model. More..



# 5. Function Composition

Concept
Combining small functions into larger ones.

Why it exists

Compositional reasoning.
Local correctness implies global correctness.

Use Python:

```python
def compose(f, g):
    return lambda x: f(g(x))
```

Explain:

* Associativity
* Small units of reasoning
* No inheritance needed

Under the hood in C:

Show nested function pointer dispatch and context stacking.

Explain cost model!

Concurrency link:

Composition + immutability enables deterministic pipelines.



# 6. Lazy Evaluation and Generators

Concept
Deferred computation.

Why it exists

* Memory efficiency
* Pipeline streaming
* Infinite sequences

Use Python generators:

```python
def count():
    i = 0
    while True:
        yield i
        i += 1
```

Explain:

* Suspension points
* Frame preservation

Under the hood explanation (no need for full C implementation):

Explain that a generator is:

* A state machine (or skip to ref instead?)
* Heap-allocated frame
* Program counter stored explicitly

Tie this to:

Coroutine mechanisms
Thread scheduling differences

Strong connection to concurrency.



# 7. Functors (Mapped Contexts)

Concept
Mapping over values inside a context.

Why it exists

To abstract over container-like structures.

Use Python with simple container wrapper.

Avoid category theory heavy formalism.

Explain:

* map over list
* map over Maybe-like structure

Do not implement in C.

Explain conceptually that in C this becomes boilerplate-heavy.
No impl. in C.



# 8. Monads (Effect Management)

Concept
Structured composition of computations with context.

Why it exists

To control:

* Errors
* State
* IO
* Async flow

Use Python:

Implement Maybe or Result.

Show:

* bind
* propagation without explicit branching

Connect to:

Error handling in C via return codes.

Show contrast:

C style:

```c
if (error) return error;
```

or other sample?

vs monadic bind chain.

Concurrency link:

Monads serialize effect flow.
Make side effects explicit.
Improves reasoning in async systems.



# 9. Referential Transparency

Concept
Same input -> same output.

Why it exists

Enables:

* Equational reasoning
* Safe caching
* Parallel execution

Primary exposition in Python.

Then connect to C:

Show how hidden global state breaks this property.

Tie directly to:

Data races
Undefined behavior
Compiler optimizations

This is a bridge.



# 10. Persistent Data Structures (Optional Advanced Section)

Concept
Structural sharing instead of mutation.

Why it exists

Efficient immutability.

Use Python conceptually.
No need to implement fully.

In C:

Explain why manual implementation is complex:

* Reference counting
* Copy-on-write
* Memory allocator concerns

Tie to:

Lock-free read sharing.



# 11. Cost Model Section

Very important for your book.

Compare:

Python functional style:

* Allocation cost
* Object overhead
* Dynamic dispatch

C:

* Stack allocation
* Inline expansion
* Branch prediction

This section connects abstraction to hardware reality.



# 12. Final Integrative Section

Title suggestion:

Functional Style as Concurrency Discipline

Explain:

* Shared mutable state causes races
* Functional purity removes synchronisation needs
* Immutability simplifies memory ordering
* Composition localises reasoning

Earlier low-level relevant again.



# Language Allocation Summary

Python for:

* First-class functions
* Closures
* Composition
* Generators
* Monads
* Higher-order functions
* Declarative pipelines

C for:

* Function pointer mechanics
* Closure simulation
* Memory layout of environments
* Lifetime management
* Cost model discussion
* Referential transparency violations
* const correctness and immutability limits

Avoid in C!
* Full monadic abstractions
* Deep functional DSLs
* Artificial category constructs



# Structural Flow

1. Behavioral abstraction (Python)
2. Captured state (Python -> C mechanics)
3. Immutability and concurrency
4. Composition and reasoning
5. Effect management (monads)
6. Under-the-hood implementation cost (C)
7. Concurrency implications

This creates intellectual progression:
Mechanics -> Problems -> Abstractions -> Implementation reality -> Concurrency benefits

