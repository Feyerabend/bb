

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


