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

