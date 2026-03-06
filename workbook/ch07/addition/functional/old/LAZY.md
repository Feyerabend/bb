

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


