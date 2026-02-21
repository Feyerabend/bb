
## The Producer-Consumer Problem

The *producer-consumer problem* is a classic synchronisation problem in computer science that models
how multiple processes or threads share a fixed-size buffer. Producers generate data (e.g., messages,
tasks, or items) and place it into the buffer, while consumers retrieve and process that data. The
challenge is to ensure thread-safe access to the shared buffer, prevent race conditions, and handle
cases where the buffer is full (producers must wait) or empty (consumers must wait). This problem
illustrates core concurrency concepts like mutual exclusion, condition synchronisation, and inter-thread
communication.

*Key Components*:
- *Producers*: Threads or processes that create data and add it to the buffer.
- *Consumers*: Threads or processes that remove and process data from the buffer.
- *Bounded Buffer*: A finite queue or storage that holds data, requiring synchronisation
  to avoid overflows (buffer full) or underflows (buffer empty).
- *Synchronisation Primitives*: Tools like locks (for mutual exclusion), semaphores (for
  signalling), or monitors (for condition variables) to coordinate access and ensure correctness.

The problem is foundational in operating systems, parallel programming, and distributed systems,
as it mirrors real-world scenarios like task queues in web servers, data pipelines, or
message-passing systems.


### Short History

The producer-consumer problem emerged in the 1960s during the development of early operating systems,
as researchers tackled the challenges of concurrent programming. It was formalised by *Edsger Dijkstra*,
a pioneer in concurrency, who introduced semaphores in 1965 as a general-purpose synchronisation mechanism.
Dijkstra’s work, including his seminal paper *"Cooperating Sequential Processes"* (1968), provided a
framework for solving problems like producer-consumer by using semaphores to manage shared resources.

In the 1970s, the problem became a standard example in operating system design, appearing in texts like
*Operating Systems Concepts* by Silberschatz and Galvin. It was used to teach synchronisation in systems
like UNIX and Multics, where processes needed to share resources safely. The introduction of *monitors*
by *C.A.R. Hoare* (1974) offered an alternative high-level construct for solving the problem, influencing
languages like Java and Ada.

By the 1980s and 1990s, the producer-consumer pattern was integral to concurrent programming models in
threading libraries (e.g., POSIX threads) and parallel computing frameworks. It remains relevant today
in modern systems, such as message queues (e.g., RabbitMQ, Kafka), thread pools in application servers,
and GPU programming, where data production and consumption must be carefully coordinated.


### ToyVM

A standout feature of the ToyVM is its implementation of the *producer-consumer problem*. In this problem,
producer threads generate data and place it into a fixed-size buffer, while consumer threads retrieve and
process that data. Synchronisation is critical to prevent buffer overflows (when full) or underflows (when
empty), and to ensure thread-safe access. The ToyVM’s `producer_consumer_example` demonstrates this
with two producers and three consumers sharing a buffer of size 5. Producers generate 8 items each (total
16 items), using an atomic counter for unique IDs, and send them to a message queue (`buffer_queue`).
Consumers retrieve items, with a shared atomic counter tracking total consumption to ensure termination
once all items are processed. Synchronisation is achieved using:
- A lock (`buffer_lock`) for mutual exclusion during buffer access.
- Two semaphores: `empty_sem` (initially 5) to track available slots,
  and `filled_sem` (initially 0) to track filled slots.
- A message queue to transfer items between producers and consumers.

The example showcases proper use of synchronisation primitives to avoid race conditions and ensure correct
coordination, with producers waiting when the buffer is full and consumers waiting when it’s empty. Sleep
instructions introduce randomness to simulate varying processing speeds, testing the robustness of the
synchronisation.

The ToyVM’s design reflects historical computing challenges, drawing inspiration from early operating system
schedulers and virtual machines like Green Threads or early Java threading models, simplified for pedagogical
clarity. Its roots trace back to the 1960s and 1970s, when pioneers like Dijkstra and Hoare developed semaphores
and monitors to address concurrency issues like the producer-consumer problem, which became a cornerstone
of operating system education. The ToyVM’s instruction set and threading model echo these concepts, providing
a hands-on way to explore thread lifecycle management, synchronisation pitfalls, and the mechanics of
concurrency primitives.

Programs are defined as lists of instruction tuples, with the main thread spawning worker threads that execute
parallel task sequences. The system supports dynamic thread creation (`THREAD_CREATE`) and joining (`THREAD_JOIN`),
allowing complex workflows. An additional example (`example_mutex`) demonstrates two threads safely incrementing
a shared counter using locks, illustrating race condition prevention. The producer-consumer example extends
this by combining multiple synchronisation mechanisms, making it an ideal case study for understanding
real-world concurrency patterns, such as those in message queues (e.g., Kafka) or thread pools.
