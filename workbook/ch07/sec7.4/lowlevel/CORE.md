
## Core System Mechanisms

It is not possible to cover all kinds of systems programming and lower-level constructs in this exposition.
But it can be fruitful to have some knowledge of them, if only by the name. These mechanisms, while diverse
in purpose and implementation, share a common role: *they enable control over the fundamental resources and
behaviours of a computing system*. Even without deep implementation expertise, understanding their existence
and conceptual function sharpens one's ability to design reliable software and reason about system behaviour.

Awareness of execution contexts, memory management, I/O handling, synchronisation, scheduling, communication,
interrupts, and timing mechanisms equips a developer with a mental model of how computation, data, and control
flow are orchestrated beneath higher-level abstractions. For example, appreciating how a scheduler selects
among threads, or how a memory barrier enforces ordering in shared memory, can inform better decisions in
program structure, performance optimisation, and debugging.

Moreover, the vocabulary of these mechanisms provides a bridge to explore more advanced topics. Discussions
of lock-free programming, real-time constraints, resource contention, and system scalability are grounded
in these foundational concepts. Even in application-level programming, seemingly distant from operating
systems or hardware, these mechanisms shape the capabilities and constraints of the runtime environment.
Thus, a working familiarity with them strengthens both practical competence and architectural insight.

| Mechanism Class | Examples | Purpose |
|---|---|---|
| *Execution Contexts* | Threads, Processes, Coroutines, Tasks, Interrupt Handlers     | Units of execution that run code concurrently or asynchronously |
| *Memory Management*  | Virtual Memory, Memory Protection, Allocation, Garbage Collection | Control access, isolation, and allocation of memory resources |
| *I/O Handling*       | Blocking I/O, Non-blocking I/O, DMA, Interrupt-driven I/O     | Manage communication and data transfer with external devices |
| *Synchronisation Primitives* | Locks, Semaphores, Condition Variables, Atomics       | Coordinate safe access to shared resources between contexts |
| *Scheduling*         | Preemptive Scheduling, Cooperative Scheduling, Real-time Scheduling | Decide when and which execution context is run |
| *Communication Mechanisms* | Signals, Message Queues, Pipes, Shared Memory          | Enable data exchange between execution contexts or devices |
| *Interrupt & Exception Handling* | Hardware Interrupts, Software Interrupts, Exceptions | Respond to asynchronous events, errors, and hardware signals |
| *Timing & Clocks*    | Timers, Time Slicing, High-resolution Clocks                  | Measure time, schedule delays, and coordinate timed events |

Core system mechanisms form the foundation upon which reliable and efficient computing systems are built. At the
centre are execution contexts, such as threads, processes, coroutines, tasks, and interrupt handlers. These are the
entities that actively execute code, enabling concurrent and asynchronous operations. To support them, memory management
mechanisms--including virtual memory, memory protection, allocation strategies, and garbage collection--govern how memory
is allocated, isolated, and safely accessed across these contexts.

I/O handling mechanisms, such as blocking and non-blocking I/O, direct memory access (DMA), and interrupt-driven I/O,
manage communication with external devices and peripherals, ensuring data can move efficiently between hardware and
software. To safely coordinate access to shared resources, synchronisation primitives like locks, semaphores, condition
variables, and atomic operations enforce orderly interaction between concurrent execution contexts.

Determining when and which execution context is allowed to run falls to scheduling mechanisms. These include preemptive,
cooperative, and real-time scheduling strategies that balance responsiveness and fairness. For explicit data exchange
between contexts or devices, communication mechanisms such as signals, message queues, pipes, and shared memory offer
structured pathways for interaction.

In handling unforeseen or asynchronous events, interrupt and exception handling mechanisms--like hardware interrupts,
software interrupts, and exceptions--enable the system to react promptly to hardware signals or runtime errors. Finally,
timing and clock facilities, such as timers, time slicing, and high-resolution clocks, provide accurate time measurement
and control, supporting operations that depend on precise delays, deadlines, or temporal coordination.

Together, these classes of mechanisms define the essential substrate of concurrency, resource management, and interaction
in any modern computing environment.

While we will not delve into the implementation details of these mechanisms, recognising their roles allows us to better
understand how higher-level abstractions are supported and constrained by the underlying system. With this conceptual
foundation in place, we can now return to the constructs and patterns that are directly relevant to our primary subject,
applying this broader systems perspective where appropriate.

CF. ch04! (timing .. and some constructs!)
