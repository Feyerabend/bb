
 ## Low-Level Control-Flow and Execution Mechanisms


| Mechanism      | Description                                                                 | Typical Use Cases                                      | Related Pattern(s) / Idiom(s)                |
|----------------|-----------------------------------------------------------------------------|--------------------------------------------------------|----------------------------------------------|
| Checkpoint     | Save program state to resume execution later                                | Backtracking, crash recovery, VM snapshotting          | Memento, Recovery Pattern                    |
| Coroutine      | Generalized subroutine with multiple entry/exit points                      | Cooperative multitasking, generators, pipelines        | State Machine, Actor Model                   |
| Dispatch       | Determine function/handler to execute based on input/state                  | Virtual tables, interpreters, event loops              | Command, Strategy                            |
| Re-entrant     | Function safe to be interrupted or called simultaneously                    | Signal handlers, interrupt-safe code, multithreading   | Thread-safe functions, Stateless Design      |
| Callback       | Function passed to be called at a later time                                | Event handling, async operations, GUI, sorting hooks   | Observer, Inversion of Control               |
| Trampoline     | Loop-based dispatching instead of recursion                                 | Interpreter loops, tail-call optimization              | Interpreter Pattern                          |
| Continuation   | Abstract representation of the rest of computation                          | Functional languages, backtracking, coroutines         | CPS (Continuation-Passing Style)             |
| State Machine  | Explicit states and transitions                                              | Protocol parsers, control logic, embedded systems      | State Pattern                                |
| Jump Table     | Table of code addresses for fast dispatch                                   | Interpreters, switch optimization, VM opcode dispatch  | Direct Dispatch Idiom                        |
| Stack Frame    | Structure for maintaining call state                                        | Function calls, recursion, coroutines                  | Call Stack Convention                        |
| Context Switch | Save/restore execution context between tasks                                | Threads, green threads, multitasking                   | Scheduler Design                             |
| Event Loop     | Central loop dispatching incoming events to handlers                        | GUIs, servers, async runtimes                          | Reactor, Proactor                            |
| Signal Handler | Function triggered by async external events                                 | Interrupts, OS signals                                 | Observer, Interrupt Vector Table             |
| Backtracking   | Reverting to previous state on failure                                      | Logic programming, parsers                            | Search Tree, Trail Stack                     |
| Memory Barrier | Instruction ordering constraint for concurrency                            | Multithreaded code, lock-free algorithms               | Happens-before Relations                     |

