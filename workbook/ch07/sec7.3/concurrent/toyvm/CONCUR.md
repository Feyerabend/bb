
## Concur

Designing a high-level language for the *ToyVM* (Threaded Operations Yard Virtual Machine) should leverage
its strengths in concurrency, threading, synchronisation, and simplicity while abstracting away the low-level
stack-based instruction set. The language should be intuitive for users, especially those learning concurrent
programming or prototyping multithreaded algorithms. Below, is a proposed high-level language called *Concur*,
including its design rationale, features, syntax, and how it maps to ToyVM instructions.


### 1. Language Name: Concur

*Name*: *Concur*  
*Rationale*: Short for "Concurrent," it reflects the language's focus on concurrent programming with threads,
locks, semaphores, and message queues.

*Purpose*: Concur is a high-level, concurrent programming language built for the ToyVM, designed to:
- Simplify writing multithreaded programs.
- Provide intuitive constructs for synchronization and communication.
- Serve as an educational tool for learning concurrency concepts.
- Enable rapid prototyping of concurrent algorithms.


### 2. Design Principles

To fit the ToyVM, Concur adheres to these principles:
- *Concurrency-First*: Native support for threads, locks, semaphores, queues, and atomic operations, mirroring ToyVM’s features.
- *Simplicity*: Minimal syntax to reduce the learning curve, especially for beginners.
- *Expressiveness*: High-level constructs that abstract away stack manipulation and low-level instruction details.
- *Safety*: Encourage safe concurrency practices (e.g., structured locking) to avoid common pitfalls like deadlocks.
- *Educational*: Clear semantics to help users understand how concurrency primitives work under the hood.



### 3. Language Features

Concur includes features tailored to the ToyVM’s capabilities:

- *Thread Creation and Joining*: Easy syntax for spawning and synchronizing threads.
- *Synchronization Primitives*:
  - Locks for mutual exclusion.
  - Semaphores for resource control.
  - Atomic counters for thread-safe updates.
- *Message Passing*: Queues for asynchronous communication between threads.
- *Variables and Arithmetic*: Support for local/global variables and basic integer operations.
- *Control Flow*: Conditionals and loops for program logic.
- *Output*: Simple print statements for debugging and output.
- *Sleep*: Support for pausing threads to simulate real-world delays.



### 4. Syntax and Semantics

#### 4.1 Variables and Arithmetic
- *Syntax*: Variables are declared implicitly via assignment. Arithmetic uses standard operators (`+`, `-`, `*`, `%`, `/`).
- *Example*:
  ```concur
  x = 10
  y = 20
  z = x + y
  print("Sum: ", z)
  ```
- *Semantics*: Variables are stored in thread-local or global scope. Arithmetic operations manipulate the ToyVM stack.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 10),
      ("STORE", "x"),
      ("PUSH", 20),
      ("STORE", "y"),
      ("LOAD", "x"),
      ("LOAD", "y"),
      ("ADD",),
      ("STORE", "z"),
      ("LOAD", "z"),
      ("PRINT", "Sum: {}")
  ]
  ```

#### 4.2 Threads
- *Syntax*: `thread <name> { <body> }` spawns a thread; `join <name>` waits for it to finish.
- *Example*:
  ```concur
  thread worker {
      print("Worker running")
  }
  join worker
  print("Main done")
  ```
- *Semantics*: Threads are created with a named block of code. `join` ensures synchronization.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 0),
      ("THREAD_CREATE", [[("PRINT", "Worker running")]]),
      ("STORE", "worker"),
      ("LOAD", "worker"),
      ("THREAD_JOIN",),
      ("PRINT", "Main done")
  ]
  ```

#### 4.3 Locks
- *Syntax*: `lock <name> { <body> }` creates and acquires a lock, releasing it after the block.
- *Example*:
  ```concur
  global counter = 0
  lock mylock {
      counter = counter + 1
  }
  print("Counter: ", counter)
  ```
- *Semantics*: The `lock` block ensures mutual exclusion. The lock is automatically released at the end of the block.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 0),
      ("GLOBAL_STORE", "counter"),
      ("LOCK_CREATE",),
      ("STORE", "mylock"),
      ("LOAD", "mylock"),
      ("LOCK_ACQUIRE",),
      ("LOAD", "counter"),
      ("PUSH", 1),
      ("ADD",),
      ("GLOBAL_STORE", "counter"),
      ("LOAD", "mylock"),
      ("LOCK_RELEASE",),
      ("LOAD", "counter"),
      ("PRINT", "Counter: {}")
  ]
  ```

#### 4.4 Semaphores
- *Syntax*: `semaphore <name> = <count>` creates a semaphore; `acquire <name>` and `release <name>` manage it.
- *Example*:
  ```concur
  semaphore sem = 2
  acquire sem
  print("In critical section")
  release sem
  ```
- *Semantics*: Semaphores control access to resources with a count-based mechanism.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 2),
      ("SEMAPHORE_CREATE",),
      ("STORE", "sem"),
      ("LOAD", "sem"),
      ("SEMAPHORE_ACQUIRE",),
      ("PRINT", "In critical section"),
      ("LOAD", "sem"),
      ("SEMAPHORE_RELEASE",)
  ]
  ```

#### 4.5 Message Queues
- *Syntax*: `queue <name>` creates a queue; `send <name>, <value>` and `receive <name>` handle messages.
- *Example*:
  ```concur
  queue q
  thread producer {
      send q, "Hello"
  }
  thread consumer {
      msg = receive q
      print("Got: ", msg)
  }
  join producer
  join consumer
  ```
- *Semantics*: Queues enable asynchronous communication. `receive` blocks until a message is available.
- *ToyVM Mapping*:
  ```python
  [
      ("QUEUE_CREATE",),
      ("STORE", "q"),
      ("PUSH", 0),
      ("THREAD_CREATE", [[
          ("PUSH", "Hello"),
          ("LOAD", "q"),
          ("QUEUE_SEND",)
      ]]),
      ("STORE", "producer"),
      ("PUSH", 0),
      ("THREAD_CREATE", [[
          ("LOAD", "q"),
          ("QUEUE_RECEIVE",),
          ("STORE", "msg"),
          ("LOAD", "msg"),
          ("PRINT", "Got: {}")
      ]]),
      ("STORE", "consumer"),
      ("LOAD", "producer"),
      ("THREAD_JOIN",),
      ("LOAD", "consumer"),
      ("THREAD_JOIN",)
  ]
  ```

#### 4.6 Atomic Counters
- *Syntax*: `atomic <name> = <initial>` creates a counter; `increment <name>`, `decrement <name>`, `get <name>` manipulate it.
- *Example*:
  ```concur
  atomic counter = 0
  increment counter
  print("Counter: ", get counter)
  ```
- *Semantics*: Atomic counters ensure thread-safe updates.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 0),
      ("ATOMIC_CREATE",),
      ("STORE", "counter"),
      ("LOAD", "counter"),
      ("ATOMIC_INCREMENT",),
      ("POP",),
      ("LOAD", "counter"),
      ("ATOMIC_GET",),
      ("PRINT", "Counter: {}")
  ]
  ```

#### 4.7 Control Flow
- *Syntax*: `if <condition> { <body> }` for conditionals; `while <condition> { <body> }` for loops.
- *Example*:
  ```concur
  x = 0
  while x < 3 {
      print("x = ", x)
      x = x + 1
  }
  ```
- *Semantics*: Conditions use stack-based evaluation. Loops jump back to the condition check.
- *ToyVM Mapping*:
  ```python
  [
      ("PUSH", 0),
      ("STORE", "x"),
      ("LOAD", "x"),
      ("PUSH", 3),
      ("SUB",),
      ("JUMP_IF", 8),  # Jump to end if x >= 3
      ("LOAD", "x"),
      ("PRINT", "x = {}"),
      ("LOAD", "x"),
      ("PUSH", 1),
      ("ADD",),
      ("STORE", "x"),
      ("JUMP", 2)     # Jump back to condition
  ]
  ```

#### 4.8 Sleep
- *Syntax*: `sleep <milliseconds>` pauses execution.
- *Example*:
  ```concur
  print("Start")
  sleep 1000
  print("End")
  ```
- *ToyVM Mapping*:
  ```python
  [
      ("PRINT", "Start"),
      ("PUSH", 1000),
      ("SLEEP",),
      ("PRINT", "End")
  ]
  ```



### 5. Example Program: Producer-Consumer

Here’s a complete Concur program demonstrating a producer-consumer pattern with a queue and a lock-protected counter.

```concur
queue q
global counter = 0
lock counter_lock

thread producer {
    send q, "Message 1"
    send q, "Message 2"
    lock counter_lock {
        counter = counter + 1
    }
}

thread consumer {
    msg1 = receive q
    print("Consumer got: ", msg1)
    msg2 = receive q
    print("Consumer got: ", msg2)
    lock counter_lock {
        counter = counter + 1
    }
}

join producer
join consumer
print("Final counter: ", counter)
```

*Behavior*:
- The producer sends two messages to the queue and increments a shared counter.
- The consumer receives and prints the messages, then increments the counter.
- The main thread waits for both to finish and prints the final counter (should be 2).
- The lock ensures thread-safe counter updates.

*ToyVM Output* (with `debug=True`):
```
[DEBUG] Created thread main
[DEBUG] Created thread producer
[DEBUG] Created thread consumer
...
[consumer] Consumer got: Message 1
[consumer] Consumer got: Message 2
[main] Final counter: 2
All threads completed after X steps
```


### 6. Compilation to ToyVM

To compile Concur to ToyVM instructions, a compiler would:
1. *Parse the Syntax*: Use a parser (e.g., built with PLY or Lark) to create an abstract syntax tree (AST).
2. *Generate Instructions*: Traverse the AST, emitting ToyVM instructions for each construct:
   - Variables map to `PUSH`, `STORE`, `LOAD`, `GLOBAL_STORE`.
   - Arithmetic maps to `ADD`, `SUB`, `MUL`, `DIV`.
   - Threads map to `THREAD_CREATE`, `THREAD_JOIN`.
   - Synchronization maps to `LOCK_*`, `SEMAPHORE_*`, `ATOMIC_*`, `QUEUE_*`.
   - Control flow maps to `JUMP`, `JUMP_IF`.
3. *Optimise*: Optionally, eliminate redundant stack operations or inline small thread bodies.
4. *Output*: Produce a list of ToyVM instruction tuples.

For example, the compiler would translate the `lock` block into a sequence of `LOCK_ACQUIRE`, body instructions, and `LOCK_RELEASE`, ensuring the lock is always released (even on errors, via a try-finally-like mechanism in the compiler).


### 7. Why Concur Would Fit the ToyVM

Concur is a good fit for the ToyVM because:
- *Concurrency Focus*: It directly exposes ToyVM’s threading, synchronization, and message-passing features in a high-level way.
- *Abstraction*: It hides stack manipulation and low-level jumps, making programs easier to write and understand.
- *Educational Value*: Its simple syntax and clear semantics help learners grasp concurrency concepts like mutual exclusion and message passing.
- *Flexibility*: It supports a range of concurrent patterns (e.g., producer-consumer, critical sections) that map cleanly to ToyVM instructions.
- *Extensibility*: The language can be extended with new primitives (e.g., condition variables) by adding ToyVM instructions.


### 8. Comparison to Alternatives

Other high-level languages could be built for the ToyVM, but Concur stands out:
- *Versus a C-like Language*: A C-style language with explicit pointers and manual memory management would be too complex for the ToyVM’s simple stack model.
- *Versus a Functional Language*: A functional language (e.g., like Haskell) would struggle to map to the ToyVM’s imperative, stateful threading model.
- *Versus a Scripting Language*: A general-purpose scripting language (e.g., like Python) would be too broad, diluting the focus on concurrency.
Concur’s concurrency-first design ensures it leverages the ToyVM’s strengths without overcomplicating the language.


### 9. Potential Extensions

To enhance Concur, consider:
- *Condition Variables*: Add `wait` and `signal` for more flexible synchronization.
- *Arrays or Lists*: Support basic data structures via new ToyVM instructions.
- *Error Handling*: Introduce `try-catch` blocks for robust programs.
- *Standard Library*: Provide built-in functions for common tasks (e.g., random numbers).
- *Type System*: Add optional types for catching errors early (e.g., ensuring queue messages are strings).


### Conclusion

*Concur* is an ideal high-level language for the ToyVM, offering a concise, concurrency-focused
syntax that maps cleanly to the VM’s instruction set. Its Python-like structure makes it accessible,
while its thread, lock, semaphore, and queue primitives enable expressive concurrent programs. By
abstracting stack operations and providing structured control flow, Concur simplifies programming
on the ToyVM. I Concur.

