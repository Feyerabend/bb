

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


