
## Atomic Counter

Atomic counters are shared variables that guarantee thread-safe read-modify-write operations in *parallel*
(not just concurrent) systems. They are enforced by hardware/OS primitives, not just logical scheduling,
and are critical for performance-sensitive systems like databases, OS kernels, and game engines.

The code in the folder defines a modular virtual machine (ToyVM) that simulates *cooperative multithreading*
with synchronisation primitives, message passing, and stack-based instruction execution. It models OS-like concepts
(locks, semaphores, atomic counters, message queues) and supports configurable scheduling policies (round-robin,
priority-based). Threads execute in discrete *atomic steps*, managed by a non-preemptive scheduler, ensuring
operations like `acquire()` or `send()` are treated as indivisible within the VM’s concurrency model.

### Comparison to Real-World Counters

| Feature             | ToyVM AtomicCounter                   | Real-World Atomic (e.g., C++/Java)              |
|---------------------|---------------------------------------|-------------------------------------------------|
| Atomicity Guarantee | Cooperative scheduler steps           | Hardware instructions (e.g., x86 `LOCK` prefix) |
| Concurrency Model   | Simulated (single-threaded)           | Parallel (true multithreading)                  |
| Use Case            | Education/deterministic sim           | High-performance, thread-safe code              |
| Overhead            | None (logical abstraction)            | Low-level CPU/OS overhead                       |
| Operations          | `increment()`, `decrement()`, `get()` | `fetch_add()`, `compare_exchange_strong()`, etc.|
| Thread Safety       | VM-enforced via cooperative steps     | Hardware/OS-enforced                            |


### Atomicity in the ToyVM Context

"Atomic" here refers to *logical indivisibility*, not hardware-level guarantees. Operations are atomic
*within the VM’s cooperative scheduling model*: the scheduler ensures no thread is interrupted mid-operation,
enabling deterministic concurrency simulation.

1. *Thread (Execution Context)*  
   - Manages per-thread state: program counter (`pc`), stack, local variables, and status (`running`, `waiting`).  
   - *Atomic operation*: `step()` executes *one instruction* as an indivisible unit before yielding control.  

2. *Lock*  
   - Mutual exclusion primitive.  
   - *Atomic operations*:  
     - `acquire()`: Checks/updates `locked` and `owner` without interruption.  
     - `release()`: Clears ownership and unblocks a waiting thread (if any).  

3. *Semaphore*  
   - Counting-based synchronisation.  
   - *Atomic operations*:  
     - `acquire()`: Decrements `count` or blocks the thread.  
     - `release()`: Increments `count` and wakes one blocked thread.  

4. *MessageQueue*  
   - Thread communication channel.  
   - *Atomic operations*:  
     - `send()`: Transfers a message directly to a waiting receiver or enqueues it.  
     - `receive()`: Retrieves a message or blocks until one is available.  

5. *AtomicCounter*  
   - Shared integer with thread-safe semantics *within the VM*.  
   - *Atomic operations*: `increment()`, `decrement()`, and `get()` appear indivisible.  


*Core Behaviour*  
1. *Instruction Execution*  
   - Threads execute instructions sequentially via `step()`, with each step treated as atomic.  
   - Example instructions: `PUSH`, `ADD`, `ACQUIRE_LOCK`, `SEND_MSG`.  

2. *Scheduling*  
   - Cooperative: Threads run until they block, complete, or explicitly yield.  
   - Policies:  
     - *Round-robin*: Cycles through ready threads.  
     - *Priority*: Selects threads based on priority.  
   - Deadlock detection halts execution if all threads are blocked.  

3. *Synchronisation & Communication*  
   - Threads block on locks/semaphores/message queues, managed by the VM.  
   - `join()`: Blocks until a target thread terminates.  

4. *Debugging*  
   - Verbose logging tracks thread states, instruction flow, and synchronisation events.  



*Atomic Concept Summary*  
| Concept        | Atomic Operations            | Guarantee                               |  
|----------------|------------------------------|-----------------------------------------|  
| Thread         | `step()`                     | Single instruction execution            |  
| Lock           | `acquire()`, `release()`     | Uninterrupted ownership transition      |  
| Semaphore      | `acquire()`, `release()`     | Atomic count adjustment + thread wakeup |  
| MessageQueue   | `send()`, `receive()`        | Uninterrupted message transfer          |  
| AtomicCounter  | `increment()`, `decrement()` | Indivisible value update                |  
| VM Scheduler   | `select_thread()`            | Thread state transitions without race   |  


*Class Diagram Highlights*  
- *ToyVM*: Central coordinator managing threads, primitives, and scheduling.  
- *Primitives (Lock/Semaphore/MessageQueue)*: Decouple synchronisation logic from threads.  
- *Cooperative Design*: Threads rely on the scheduler to advance, enabling deterministic atomicity.  


*Key Clarifications*  
- *Simulated Concurrency*: No parallelism; atomicity is enforced via scheduling, not hardware.  
- *Non-Preemptive*: Threads yield control explicitly (e.g., via `WAIT` or `BLOCK` instructions).  
- *Determinism*: Atomic steps and cooperative scheduling enable reproducible behaviour.  

This version emphasises the VM’s *simulated* concurrency model, distinguishes logical vs. 
hardware atomicity, and aligns terminology with cooperative multithreading paradigms.



