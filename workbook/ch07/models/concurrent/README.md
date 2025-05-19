# From Basics To Bytecode: A guide to computers and programming
# Workbook


- proco ?

- mutex ?


## Concurrency

Concurrency, as a concept in computing, has evolved through a rich interplay between hardware capabilities,
theoretical breakthroughs, and the development of programming languages. Its roots stretch back to the earliest
days of computing, yet its meaning and implementation have changed profoundly over time. To understand concurrency
in a historical sense is to trace the gradual realisation that computers can—and often must—do more than one
thing at a time, or at least appear to.

In the earliest digital computers of the 1940s and 1950s, programs were executed sequentially, in a single stream
of instructions. These machines ran one task at a time, and control remained firmly in the hands of the program's
step-by-step execution. As computing systems became more powerful and more users needed to share them, the idea
of multiprogramming began to emerge. This involved the system switching between multiple programs, keeping them
resident in memory and giving each a slice of time on the CPU. This was not true concurrency in the modern sense,
but it was a foundational shift: the machine could now maintain the illusion that multiple tasks were progressing
simultaneously.

By the 1960s, with the advent of time-sharing systems, this illusion became more refined. Operating systems like
Multics allowed multiple users to interact with a central computer as if they had it to themselves. This required
the operating system to interleave computations carefully and manage concurrent access to resources like memory
and disk. These early efforts brought forth the first serious efforts to formalise concepts like processes, critical
sections, and mutual exclusion. Dijkstra, Hoare, and others developed theoretical models that became central to
understanding concurrency, such as semaphores and monitors.

The challenge at this stage was not just how to run concurrent processes, but how to reason about them. Theoretical
computer science developed a rich body of work on process calculi (like CSP and π-calculus), synchronization, and
deadlock avoidance. These abstractions had a major influence on both operating system design and the emerging field
of concurrent programming languages.

High-level language support for concurrency began to appear in the 1970s. Languages like Concurrent Pascal and Modula-2
(by Niklaus Wirth) introduced structured ways of managing concurrent processes, but they remained niche. The Ada
programming language, developed by the U.S. Department of Defense, took a more ambitious step in the early 1980s by
incorporating built-in support for tasking, rendezvous (a form of synchronous message passing), and protected types.
These features brought concurrency to the forefront as a language-level construct.

In the 1980s and 1990s, as personal computing expanded and multi-processor systems became more common, concurrency began
to shift from large mainframes to the desktop and eventually the server room. Threads became the dominant model, supported
by libraries (like POSIX threads) and gradually incorporated into languages such as Java and C#. Java, in particular,
made multithreading a first-class citizen with its Thread class and synchronisation primitives, although it inherited
many of the complexities and pitfalls of low-level thread programming.

By the 2000s, the rise of multi-core processors made concurrent programming not just an option but a necessity. Languages
like Erlang, which had long championed lightweight, message-passing processes for telecom systems, gained new attention.
Erlang's actor model, where processes communicate only through message passing and do not share state, offered a radical
and safer alternative to shared-memory concurrency.

The actor model also inspired newer languages and frameworks. Scala, with its Akka library, became popular in distributed
system development. Functional languages such as Haskell began to offer advanced concurrency models like software
transactional memory, which allowed for composable, declarative management of state changes in a concurrent context.

In the past two decades, the programming world has seen a shift toward more abstract and safer concurrency models. Go,
released by Google in 2009, made concurrency a language design feature through goroutines and channels, reflecting a philosophy
of "don't communicate by sharing memory; share memory by communicating." Rust, with its strict ownership model, approaches
concurrency from a safety-first perspective, catching many concurrency errors at compile time that would otherwise lead
to runtime crashes or data races.

Today, concurrency is deeply embedded in every layer of computing, from web servers handling millions of connections
simultaneously, to GPUs executing thousands of threads, to reactive user interfaces responding to human actions in
real time. High-level language development continues to evolve to meet the challenge: asynchronous programming with
promises and async/await syntax has become standard in JavaScript, Python, and C#, making event-driven concurrency
easier to write and understand.

Yet despite these developments, concurrency remains one of the hardest areas of programming. Its difficulty lies not
just in syntax, but in reasoning: understanding how independent flows of execution interact, how to prevent subtle
timing bugs, and how to maintain consistency without sacrificing performance. As such, the history of concurrency is
not only a story of languages and hardware, but of an evolving attempt to make the invisible world of simultaneous
computation intelligible and manageable to human beings.

