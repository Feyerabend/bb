
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


