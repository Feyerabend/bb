
### Concurrency & Threading

| Mechanism | Description | Use Cases | Related Pattern(s) |
|--|--|--|--|
| [Re-entrant](./reentrant/) | Function safe to be re-entered concurrently | Multithreading, interrupt-safe routines | Thread-safe design, Stateless design |
| [Context Switch](./context/) | Save/restore execution context between tasks | Thread scheduling, green threads, RTOS | Scheduler design |
| [Memory Barrier](./barrier/) | Prevent CPU from reordering memory operations | Lock-free concurrency, shared memory | Happens-before relations |

[Threads](./THREADS.md) represent an execution context that runs independently yet shares memory with other threads
within the same process. They serve as a concrete mechanism beneath higher-level concurrency constructs, enabling
multitasking at the granularity of individual flows of control. Threads provide the substrate upon which re-entrancy,
context switching, and memory barriers operate--each ensuring safe and efficient coordination between threads. Without
threads (or their equivalents), these concurrency techniques would lack an execution model to act upon.

.. to be continued ..

