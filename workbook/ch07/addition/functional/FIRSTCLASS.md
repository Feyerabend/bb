

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


