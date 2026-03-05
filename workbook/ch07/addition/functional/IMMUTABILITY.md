

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


