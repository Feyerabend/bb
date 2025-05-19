
## The Threaded Operations Yard VM (ToyVM)

The *ToyVM* is a Python-based virtual machine designed to simulate a multithreaded environment with
support for concurrent programming constructs such as threads, locks, semaphores, message queues, and
atomic counters. It provides a stack-based instruction set for executing programs, with a focus on
demonstrating thread scheduling, synchronisation, and inter-thread communication. The VM is intended
for educational purposes, prototyping concurrent algorithms, or experimenting with thread-based
programming in a controlled environment.


### 1. Purpose of the ToyVM

The ToyVM is designed to:
- *Simulate Multithreading*: Execute multiple threads with different scheduling strategies (e.g., round-robin, priority-based).
- *Support Synchronization*: Provide mechanisms like locks, semaphores, and atomic counters to manage shared resources.
- *Facilitate Communication*: Enable inter-thread communication through message queues.
- *Demonstrate Concurrency Concepts*: Serve as a teaching tool for understanding thread states, deadlocks, and synchronisation primitives.
- *Allow Experimentation*: Offer a flexible environment for testing concurrent algorithms without the complexity of real-world operating systems.

The VM is clearly not optimised for performance but prioritises clarity and ease of use for learning and prototyping.



### 2. Architecture Overview

The ToyVM consists of several key components:

- *Thread*: Represents a single thread of execution with its own program counter (PC), stack, and variables.
- *Lock*: A mutual exclusion mechanism to ensure only one thread accesses a critical section at a time.
- *Semaphore*: A synchronisation primitive for controlling access to resources with a specified count.
- *MessageQueue*: A queue for asynchronous communication between threads.
- *AtomicCounter*: A thread-safe counter for atomic operations like increment and decrement.
- *ToyVM*: The main virtual machine that manages threads, resources, and scheduling.

#### Features

- *Stack-Based Execution*: Instructions operate on a per-thread stack, similar to a stack machine like the JVM.
- *Thread Scheduling*: Supports round-robin (default), priority-based, or random thread selection.
- *Deadlock Detection*: Detects when all threads are waiting and cannot proceed.
- *Debug Mode*: Provides detailed output of thread states, stacks, and instructions during execution.
- *Flexible Instruction Set*: Includes arithmetic, control flow, threading, and synchronization instructions.



### 3. Instruction Set

The ToyVM uses a tuple-based instruction format: `(opcode, *args)`, where `opcode` is a string identifying
the operation, and `args` are optional arguments.


#### Stack Operations

- *PUSH value*: Pushes `value` (integer, string, etc.) onto the thread's stack.
- *POP*: Removes the top value from the stack.
- *DUP*: Duplicates the top value on the stack.


#### Arithmetic Operations

- *ADD*: Pops two values, adds them, and pushes the result (`a + b`).
- *SUB*: Pops two values, subtracts them, and pushes the result (`a - b`).
- *MUL [mod]*: Pops two values, multiplies them, and pushes the result (`a * b`). If `mod` is specified, computes the modulo (`a % b`).
- *DIV*: Pops two values, performs integer division, and pushes the result (`a // b`). Assumes `b != 0`.


#### Variable Operations

- *LOAD var_name*: Pushes the value of `var_name` from thread-local variables or globals onto the stack.
- *STORE var_name*: Pops the top value and stores it in thread-local `var_name`.
- *GLOBAL_STORE var_name*: Pops the top value and stores it in the VM's global variables.


#### Control Flow

- *JUMP address*: Sets the program counter to `address` (0-based index).
- *JUMP_IF address*: Pops a value; if it's non-negative (`>= 0`), jumps to `address`.


#### Output

- *PRINT [message]*: Prints a message or the top stack value. If `message` contains `{}`, it formats the message with the top stack value.

#### Thread Management

- *THREAD_CREATE instruction_list*: Pops an index, selects a set of instructions from `instruction_list`,
  creates a new thread with those instructions, and pushes the thread's name.
- *THREAD_JOIN*: Pops a thread name, waits until that thread terminates, then continues.


#### Synchronization

- *LOCK_CREATE*: Creates a new lock and pushes its name.
- *LOCK_ACQUIRE*: Acquires the lock named at the top of the stack. If the lock is taken, the thread waits.
- *LOCK_RELEASE*: Releases the lock named at the top of the stack, waking the next waiting thread.
- *SEMAPHORE_CREATE*: Pops a count, creates a semaphore with that count, and pushes its name.
- *SEMAPHORE_ACQUIRE*: Acquires the semaphore named at the top of the stack. If the count is zero, the thread waits.
- *SEMAPHORE_RELEASE*: Releases the semaphore named at the top of the stack, waking a waiting thread or incrementing the count.
- *ATOMIC_CREATE*: Pops an initial value, creates an atomic counter, and pushes its name.
- *ATOMIC_INCREMENT*: Increments the counter named at the top of the stack and pushes the new value.
- *ATOMIC_DECREMENT*: Decrements the counter named at the top of the stack and pushes the new value.
- *ATOMIC_GET*: Pushes the current value of the counter named at the top of the stack.


### Message Passing

- *QUEUE_CREATE*: Creates a message queue and pushes its name.
- *QUEUE_SEND*: Pops a message and queue name, sends the message to the queue. If a receiver is waiting, delivers directly.
- *QUEUE_RECEIVE*: Receives a message from the queue named at the top of the stack. If no message is available, the thread waits.


### Miscellaneous

- *SLEEP duration*: Pops a duration (in milliseconds), pauses the thread for that time.
- *NOP*: No operation; does nothing.



### 4. How to Use

#### Step 1: Initialize the VM
Create an instance of the `ToyVM` class:
```python
vm = ToyVM()
```

#### Step 2: Define Instructions
Create a list of instruction tuples for a thread. For example:
```python
instructions = [
    ("PUSH", 42),
    ("PRINT", "Value: {}"),
    ("POP",),
]
```

#### Step 3: Create a Thread
Register a thread with the VM:
```python
vm.create_thread(instructions, name="main")
```

#### Step 4: Run the VM
Execute the VM with optional debug output and a maximum step limit:
```python
vm.run(max_steps=1000, debug=True)
```

#### Step 5: Use Synchronization and Communication
For concurrent programs, create locks, semaphores, or queues, and use
corresponding instructions. (See examples below.)


### 5. Example Programs

#### Example 1: Simple Arithmetic
This program pushes two numbers, adds them, and prints the result.

```python
instructions = [
    ("PUSH", 10),
    ("PUSH", 20),
    ("ADD",),
    ("PRINT", "Sum: {}"),
]

vm = ToyVM()
vm.create_thread(instructions, name="main")
vm.run(debug=True)
```

*Output*:
```
[DEBUG] Created thread main
[DEBUG] Selected thread main
Step 1: Running thread main (priority 0) at PC 0
  Instruction: ('PUSH', 10)
  Stack: []
  Variables: {}
  State: runnable
[DEBUG] Selected thread main
Step 2: Running thread main (priority 0) at PC 1
  Instruction: ('PUSH', 20)
  Stack: [10]
  Variables: {}
  State: runnable
[DEBUG] Selected thread main
Step 3: Running thread main (priority 0) at PC 2
  Instruction: ('ADD',)
  Stack: [10, 20]
  Variables: {}
  State: runnable
[DEBUG] Selected thread main
Step 4: Running thread main (priority 0) at PC 3
  Instruction: ('PRINT', 'Sum: {}')
  Stack: [30]
  Variables: {}
  State: runnable
[main] Sum: 30
All threads completed after 4 steps
```

#### Example 2: Producer-Consumer with Message Queue
This program demonstrates a producer thread sending messages to a consumer
thread via a message queue.

```python
producer_instructions = [
    ("QUEUE_CREATE",),
    ("DUP",),
    ("GLOBAL_STORE", "queue"),
    ("PUSH", "Hello"),
    ("PUSH", "queue"),
    ("QUEUE_SEND",),
    ("PUSH", "World"),
    ("PUSH", "queue"),
    ("QUEUE_SEND",),
]

consumer_instructions = [
    ("LOAD", "queue"),
    ("QUEUE_RECEIVE",),
    ("PRINT", "Received: {}"),
    ("LOAD", "queue"),
    ("QUEUE_RECEIVE",),
    ("PRINT", "Received: {}"),
]

vm = ToyVM()
vm.create_thread(producer_instructions, name="producer")
vm.create_thread(consumer_instructions, name="consumer")
vm.run(debug=True)
```

*Output* (highly abridged):
```
[DEBUG] Created thread producer
[DEBUG] Created thread consumer
...
[producer] Created queue queue-0
[consumer] Received: Hello
[consumer] Received: World
All threads completed after X steps
```

#### Example 3: Critical Section with Lock
This program uses a lock to protect a shared counter, incremented by two threads.

```python
counter_instructions = [
    ("LOCK_CREATE",),
    ("GLOBAL_STORE", "lock"),
    ("ATOMIC_CREATE", 0),
    ("GLOBAL_STORE", "counter"),
    ("PUSH", 0),
    ("THREAD_CREATE", [worker_instructions]),
    ("PUSH", 0),
    ("THREAD_CREATE", [worker_instructions]),
    ("THREAD_JOIN",),
    ("THREAD_JOIN",),
    ("LOAD", "counter"),
    ("PRINT", "Final counter: {}"),
]

worker_instructions = [
    ("LOAD", "lock"),
    ("LOCK_ACQUIRE",),
    ("LOAD", "counter"),
    ("ATOMIC_INCREMENT",),
    ("GLOBAL_STORE", "counter"),
    ("LOAD", "lock"),
    ("LOCK_RELEASE",),
]

vm = ToyVM()
vm.create_thread(counter_instructions, name="main")
vm.run(debug=True)
```

*Output* (abridged):
```
[DEBUG] Created thread main
[DEBUG] Created thread thread-0
[DEBUG] Created thread thread-1
...
[main] Final counter: 2
All threads completed after X steps
```



### 6. Scheduling and Thread States

The VM supports three scheduling modes (set via `vm.scheduler_type`):
- *round_robin* (default): Cycles through active threads in order.
- *priority*: Selects the thread with the highest priority (ties broken by least recent execution).
- *random*: Chooses a thread randomly.

Threads can be in one of three states:
- *runnable*: Ready to execute.
- *waiting*: Blocked on a lock, semaphore, queue, or join operation.
- *terminated*: Completed execution or out of instructions.

The `print_thread_states` method (in debug mode) shows each thread's state, PC, stack, and variables.



### 7. Deadlock Detection

The VM detects deadlocks when all threads are waiting (or terminated) and no thread can proceed.
For example, if two threads each hold a lock and wait for the other's lock, the VM will stop and report
a deadlock in debug mode.



### 8. Best Practices and Limitations

#### Best Practices
- *Use Debug Mode*: Enable `debug=True` to trace execution and diagnose issues.
- *Name Resources Explicitly*: Assign meaningful names to threads, locks, and queues for clarity.
- *Avoid Infinite Loops*: Ensure threads terminate to prevent the VM from hitting `max_steps`.
- *Test Synchronization*: Use locks or semaphores for shared resources to avoid race conditions.

#### Limitations
- *No Floating-Point Support*: Arithmetic is integer-based.
- *Simplified Error Handling*: Division by zero or invalid opcodes may produce warnings but not halt cleanly.
- *No Preemption*: Threads run one instruction at a time, with no true parallelism.
- *Max Steps Limit*: Long-running programs may be cut off unless `max_steps` is increased.
- *No Advanced Data Types*: The VM supports basic values (integers, strings) but not complex objects.



### 9. Extending the ToyVM

To extend the VM, you can:
- *Add New Instructions*: Modify `execute_instruction` to support custom opcodes (e.g., bitwise operations).
- *Enhance Scheduling*: Implement a more sophisticated scheduler (e.g., based on thread runtime).
- *Add Data Types*: Extend the stack to support lists, dictionaries, or custom objects.
- *Improve Error Handling*: Add validation for stack underflows, invalid jumps, etc.



### Conclusion

The ToyVM is a versatile tool for learning and experimenting with concurrent programming. Its instruction
set covers basic computation, thread management, synchronisation, and communication, making it suitable for
simulating scenarios like producer-consumer problems, critical sections, or message-passing systems.
By writing programs and running them with debug mode, you can gain a deeper understanding of how threads
interact and how synchronisation primitives prevent conflicts.

For further exploration, try e.g. creating a custom scheduler. The VM's simplicity and transparency make
it an suitable platform for such experiments.
