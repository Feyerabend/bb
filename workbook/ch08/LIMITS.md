
## Limits

The limits of computers can be categorised into several fundamental areas: *logical
limits* (Gödel, Church-Turing), *computational complexity* (P vs. NP), *physical limits*
(thermodynamics, quantum mechanics), and *practical limits* (energy consumption, memory
constraints). Each of these imposes constraints on what computers can and cannot do.


__1. Logical Limits: Gödel’s Incompleteness Theorems and the Halting Problem__

Gödel's incompleteness theorems (1931) show that in any sufficiently powerful formal
system (such as arithmetic), there exist true statements that cannot be proven within
the system. This has direct implications for computation, since formal systems underlie
programming languages and mathematical logic.

Turing (1936) extended this idea with the Halting Problem, proving that there is no
general algorithm that can determine whether an arbitrary program will halt or run
forever. This establishes an absolute limit on computation: some problems are undecidable,
meaning no computer can solve them in finite time.

Church-Turing thesis (1936) posits that any "effectively computable" function can be
computed by a Turing machine. This defines the fundamental scope of computability,
showing that some problems (like the Entscheidungsproblem) have no algorithmic solution.


__2. Computational Complexity: P vs. NP and Beyond__

Even for problems that are theoretically computable, the time required to solve them
varies drastically. The P vs. NP problem is one of the biggest open questions in computer
science. It asks whether every problem whose solution can be verified in polynomial time
(NP) can also be solved in polynomial time ($\`P\`$). If $\`P = NP$\`, it would mean that problems
like integer factorisation and the traveling salesman problem could be solved efficiently,
revolutionising cryptography and optimisation.

Other complexity classes, such as EXPTIME (exponential time), PSPACE (problems solvable
with polynomial space), and BQP (quantum polynomial time), further classify problems
based on computational resources.


__3. Physical Limits: Energy, Heat, and Quantum Mechanics__

Computation is bound by physical laws. The Landauer Limit states that erasing one bit
of information requires a minimum amount of energy (about $\`kT \ln 2\`$ Joules at temperature $\`T\`$).
This imposes thermodynamic constraints on computation.

The speed of light and minimum transistor size also impose limits. As transistors shrink
toward the atomic scale, quantum effects (uncertainty, tunnelling) make classical computation
unreliable, leading to the development of quantum computing.


__4. Practical Limits: Memory, Energy, and Real-World Constraints__

Even if a problem is theoretically solvable in polynomial time, practical issues arise:
- Memory: Some problems require impractical amounts of RAM (e.g., combinatorial explosion
  in AI search spaces).
- Energy and heat: Supercomputers require enormous power; as transistor densities increase,
  heat dissipation becomes a bottleneck.
- Parallelisation limits: Some problems do not scale well with more processors due to
  Amdahl's Law.

### Summary
- Gödel and Turing showed that some problems are undecidable.
- P vs. NP concerns problems that may be solvable in theory but not efficiently.
- Physical constraints like energy and quantum mechanics impose practical limitations.
- Even solvable problems can be infeasible due to memory, energy, and real-world constraints.

