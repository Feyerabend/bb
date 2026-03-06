
I want in some part series, describe "functional patterns" in analogue
to design patterns, or other such patterns found in low-level coding and so on.
Below is a part of this as outlined. Can you help me extend this to both text as README
in markdown with the conceptual making, and code samples in C or Python as separate
files. Choose C if possible first, then Python if it is not suitable with C.
To make the series coherent, I want this to all be similar in a way that it 
is easy to a reader to follow the steps. Think you can do this?

----------------


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


