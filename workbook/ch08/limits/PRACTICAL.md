
## Practical Limits

Even when a problem is theoretically solvable in polynomial time, real-world constraints--such as
memory limitations, energy consumption, and parallelisation bottlenecks--often make computation
infeasible. These practical limits arise from the physical and architectural realities of computing
systems, regardless of theoretical complexity classifications.


### Memory Constraints: The Problem of Scale

Many computational problems, particularly in areas like artificial intelligence, cryptography, and
combinatorial optimisation, require an exponential or even super-polynomial amount of memory. A key
example is the combinatorial explosion in AI search spaces. Consider a chess-playing algorithm: the
number of possible board positions grows exponentially with the number of moves, making exhaustive
search infeasible even with vast amounts of RAM. Similarly, in deep learning, large language models
require hundreds of gigabytes of memory just for storing parameters and intermediate states, leading
to practical limitations in deployment.

This issue extends to storage capacity as well. Some problems generate immense datasets that are
impractical to store or process efficiently. Even if an algorithm runs in polynomial time, if the
memory requirement grows beyond physical hardware capabilities, it becomes computationally intractable
in practice.


### Energy and Heat: The Cost of Computation

Computation requires energy, and as transistor densities increase, power consumption and heat dissipation
become major bottlenecks. Supercomputers, such as those used for weather prediction, AI training, or
nuclear simulations, consume megawatts of power, often requiring dedicated cooling infrastructure.
Modern data centres struggle with energy efficiency, as they must balance performance per watt while
minimising thermal waste.

The problem worsens as Moore's Law slows down. Traditional performance improvements relied on increasing
clock speeds, but higher frequencies lead to greater energy dissipation (since power scales roughly
with frequency squared). This has led to a shift toward multi-core architectures, low-power processors,
and specialised accelerators like TPUs (Tensor Processing Units) and neuromorphic chips, designed to
compute efficiently while reducing energy costs.

At a fundamental level, the Landauer Limit (discussed previously) places a theoretical bound on the
minimum energy required for computation. However, in practice, today's computers operate orders of
magnitude above this limit due to inefficiencies in circuit design, data movement, and cooling
mechanisms.


### Parallelisation Limits: The Bottleneck of Coordination

One way to mitigate performance issues is parallelisation, distributing computational tasks across
multiple processors. However, this approach has its own limits, most notably captured by Amdahl's
Law. This principle states that the speedup from adding more processors is limited by the sequential
portion of a program. If 90% of a task can be parallelised but 10% must be executed sequentially,
then even with an infinite number of processors, the maximum speedup is only 10x.

Certain problems--such as matrix multiplication, graphics processing, and deep learning
inference--parallels well, benefiting from GPU acceleration. However, many tasks involve inherent
dependencies, making parallelisation inefficient. Examples include:
- Graph algorithms, where traversal depends on previous computations.
- Recursively defined problems, such as those in symbolic AI and formal verification.
- I/O-bound tasks, where data fetching from memory or disk creates bottlenecks.

Additionally, parallelization introduces communication overhead. Distributing a computation across
thousands of processors requires synchronization, and delays in communication (latency) can outweigh
the benefits of parallel execution.


### Conclusion

Even if an algorithm is theoretically efficient in terms of asymptotic complexity, real-world
constraints often dominate feasibility. Memory limitations, energy consumption, and parallelization
bottlenecks define the practical limits of computation. As a result, algorithm design must account
for hardware realities, leading to optimizations such as:
- Memory-efficient data structures (e.g., bloom filters, compressed representations).
- Low-power computing architectures (e.g., edge AI, neuromorphic computing).
- Hybrid approaches, where parallelization is applied selectively based on Amdahl's Law.

These constraints shape modern computing paradigms and explain why some theoretically solvable
problems remain infeasible in practice.
