
## Low-Level Control-Flow and Execution Mechanisms

### Concurrency & Threading

Concurrency and threading mechanisms manage safe and predictable execution when multiple tasks operate simultaneously,
ensuring isolation, coordination, and ordering. Re-entrancy guarantees that functions behave correctly under concurrent
calls; context switching enables multitasking by preserving and restoring task states; memory barriers enforce visibility
and ordering of shared memory operations. Together, these techniques build the foundation for reliable thread scheduling,
interrupt handling, lock-free programming, and real-time systems where timing and correctness are critical.

| Mechanism | Description | Use Cases | Related Pattern(s) |
|--|--|--|--|
| [Re-entrant](./reentrant/) | Function safe to be re-entered concurrently | Multithreading, interrupt-safe routines | Thread-safe design, Stateless design |
| Context Switch  | Save/restore execution context between tasks                           | Thread scheduling, green threads, RTOS               | Scheduler design                        |
| [Memory Barrier](./barrier/) | Prevent CPU from reordering memory operations | Lock-free concurrency, shared memory | Happens-before relations |

[Threads](./THREADS.md) represent an execution context that runs independently yet shares memory with other threads
within the same process. They serve as a concrete mechanism beneath higher-level concurrency constructs, enabling
multitasking at the granularity of individual flows of control. Threads provide the substrate upon which re-entrancy,
context switching, and memory barriers operate--each ensuring safe and efficient coordination between threads. Without
threads (or their equivalents), these concurrency techniques would lack an execution model to act upon.


### Control Flow & Dispatch

[Control flow and dispatch mechanisms](./CONTROL.md) provide structured ways to manage "what happens next"
during program execution, whether by selecting actions, organising states, or deferring computation. Despite
differing in form--dispatch tables, state models, trampolines, or continuations--all aim to decouple control
decisions from rigid call structures, enabling flexibility, efficiency, and modularity. These techniques
are foundational for building interpreters, managing embedded protocols, optimising recursion, and handling
complex execution paths in functional and system-level programming.


### Memory & State Management

[State management mechanisms](./MEMORY.md) control how a program preserves, restores, and navigates its
execution history, especially in complex or failure-prone scenarios. Checkpoints capture program state
for resumption or recovery, stack frames organise local data during nested or recursive calls, and backtracking
systematically reverts to earlier states when encountering dead ends. These techniques are central to building
interpreters, recovery systems, logic solvers, and any software requiring controlled exploration or structured
undo capability.


### Event-Driven & Reactive

Event-driven mechanisms organise program control around external stimuli, allowing systems to react
dynamically rather than following a rigid sequence. Callbacks are scheduled by frameworks to execute
later during normal program flow, typically in response to events like user input or asynchronous
operations. Signal handlers, by contrast, respond spontaneously to low-level hardware or OS signals,
often interrupting normal execution unpredictably. Event loops provide the structural foundation,
continuously polling or waiting for events and dispatching control to appropriate callbacks or handlers.

Together, these techniques enable reactive, responsive systems in domains such as GUIs, servers,
embedded systems, and asynchronous programming environments.

| Mechanism | Description | Use Cases | Related Pattern(s) |
|---|---|---|---|
| [Callback](./callback/) | Function invoked at a later point, usually by a framework | Event handling, async operations, sorting hooks | Observer, Inversion of Control |
| Signal Handler  | Async routine called in response to OS or hardware signals             | Interrupt handling, Unix signals, exceptions         | Observer, Interrupt Vector Table        |
| Event Loop      | Central loop dispatching async events                                  | GUIs, servers, JavaScript runtimes                   | Reactor, Proactor                       |


### Computation Models

[Coroutines](./COROUTINE.md) are generalised subroutines that allow suspension and resumption of
execution, enabling cooperative multitasking, generators, and simulations. They are often used
in the Actor model and State Machine patterns to manage concurrency and control flow in a structured,
non-preemptive way.


### Conclusion

*I became interested in low-level programming patterns in 1981 after reading two articles that described
some of these techniques.[^modern] I thought, "Why not apply them in higher-level contexts?" At the time,
I had just started learning BASIC and machine/assembly programming, but had no experience or knowledge
of computer science. Although I have saved copies of the articles all this time.*

[^modern]: The magazine was *Modern elektronik: med branschnyheter - teknik och ekonomi*. (1970-1992).
Solna: Nordpress. Specifically by: Hans Beckman and Johan Finnved (1981) "Metodöversikt för mikrodatorprogrammerare",
*Modern elektronik: med branschnyheter - teknik och ekonomi*, nr. 8:1-2, pp. 35-38


Modern programs rely on a set of *fundamental mechanisms* to manage execution control, concurrency, state, and
event handling. Control flow techniques such as dispatch, jump tables, trampolines, state machines, and continuations
structure "what happens next," enabling flexible branching, recursion optimisation, and dynamic behaviour modelling.
Concurrency mechanisms, including re-entrancy, context switching, and memory barriers, coordinate multiple threads
or tasks safely, ensuring isolation, synchronisation, and ordering in multithreaded and real-time environments.
State management strategies like checkpoints, stack frames, and backtracking preserve and restore program execution
history, supporting recovery, logic inference, and deep recursive calls. Event-driven models built from callbacks,
signal handlers, and event loops allow programs to react to asynchronous stimuli, shifting control flow based on
external inputs or hardware signals. Together, these interconnected techniques form the backbone of reliable,
scalable software systems, from embedded controllers and interpreters to servers, GUI frameworks, and functional
runtimes.
