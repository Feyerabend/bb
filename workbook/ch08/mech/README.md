
## Low-Level Control-Flow and Execution Mechanisms

### Concurrency & Threading
| Mechanism       | Description                                                            | Use Cases                                            | Related Pattern(s)                     |
|-----------------|------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------|
| Re-entrant      | Function safe to be re-entered concurrently                            | Multithreading, interrupt-safe routines              | Thread-safe design, Stateless design    |
| Context Switch  | Save/restore execution context between tasks                           | Thread scheduling, green threads, RTOS               | Scheduler design                        |
| Memory Barrier  | Prevent CPU from reordering memory operations                          | Lock-free concurrency, shared memory                 | Happens-before relations                |

### Control Flow & Dispatch
| Mechanism       | Description                                                            | Use Cases                                            | Related Pattern(s)                     |
|-----------------|------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------|
| Dispatch        | Choose code to run based on input/state                                | Message dispatch, interpreters, drivers              | Command, Strategy                        |
| Jump Table      | Array of code addresses for fast branching                             | Opcode dispatch, switch-case replacement             | Direct dispatch idiom                   |
| Trampoline      | Loop-based control flow instead of recursion                           | Tail-call optimisation, interpreter loops            | Interpreter pattern                     |
| State Machine   | Explicit modelling of transitions and states                            | Embedded control, protocols, parsing                 | State pattern                           |
| Continuation    | Representation of "what to do next" in execution                       | Functional languages, backtracking                   | CPS (Continuation-passing style)        |

### Memory & State Management
| Mechanism       | Description                                                            | Use Cases                                            | Related Pattern(s)                     |
|-----------------|------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------|
| Checkpoint      | Save program state to resume from that point                           | Backtracking, recovery systems, interpreters         | Memento, Recovery                       |
| Stack Frame     | Local storage for function calls                                        | Recursion, coroutines, nested procedures             | Call stack convention                   |
| Backtracking    | Reverting to previous states on failure                                | Logic programming, constraint solving                | Search tree, trail stack                |

### Event-Driven & Reactive
| Mechanism       | Description                                                            | Use Cases                                            | Related Pattern(s)                     |
|-----------------|------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------|
| Callback        | Function invoked at a later point, usually by a framework              | Event handling, async operations, sorting hooks      | Observer, Inversion of Control          |
| Signal Handler  | Async routine called in response to OS or hardware signals             | Interrupt handling, Unix signals, exceptions         | Observer, Interrupt Vector Table        |
| Event Loop      | Central loop dispatching async events                                  | GUIs, servers, JavaScript runtimes                   | Reactor, Proactor                       |

### Computation Models
| Mechanism       | Description                                                            | Use Cases                                            | Related Pattern(s)                     |
|-----------------|------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------|
| Coroutine       | Generalised subroutine with suspend/resume semantics                   | Generators, cooperative multitasking, simulations    | Actor model, State Machine              |
