
## Limits

The limits of computers can be categorised into several fundamental areas:
[*logical limits*](./GODEL.md) (Gödel, Church-Turing),
[*computational complexity*](./PvsNP.md) (P vs. NP),
[*physical limits*](./PHYSICAL.md) (thermodynamics, quantum mechanics), and
[*practical limits*](./PRACTICAL.md) (energy consumption, memory constraints).
Each of these imposes constraints on what computers can and cannot do.


__1. Logical Limits: Gödel's Incompleteness Theorems and the Halting Problem__

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
showing that some problems (like the *Entscheidungsproblem*) have no algorithmic solution.


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
of information requires a minimum amount of energy (about $\`kT \ln 2\`$ Joules
at temperature $\`T\`$). This imposes thermodynamic constraints on computation.

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


### Conventional and Compatibility Limits in Computing: The Weight of Legacy

Computing is not just constrained by fundamental limits like P vs NP or physical laws as
above--it is also shaped by historical decisions, entrenched standards, and the necessity
of backward compatibility. These constraints are not inherent to computation itself but
emerge from the practical realities of how technology evolves. Unlike the absolute barriers
imposed by mathematics or physics, these limitations are often accidents of history, yet
they exert a powerful influence on what computers can do today.  

One of the most pervasive forces holding back computing progress is *legacy hardware and
backward compatibility*. Modern processors, for instance, still bear the architectural
imprint of designs from the 1970s and 1980s. The x86 instruction set, originally developed
for Intel’s early chips, persists today not because it is optimal, but because the entire
software ecosystem—from operating systems to applications—depends on it. Even though RISC 
rchitectures (like ARM) are more efficient, the inertia of x86 means that CPUs must include
complex translation layers to maintain compatibility, wasting energy and transistor space.
Similarly, the transition from BIOS to UEFI firmware took decades, not because UEFI wasn't
superior, but because changing low-level system firmware risked breaking decades of hardware
and software dependencies.  

Software and protocol inertia further compound the problem. Many of the foundational technologies
of the internet, for example, were designed under assumptions that no longer hold true.
IPv4, with its limited address space, should have been replaced by IPv6 long ago, yet the
transition remains incomplete because of the sheer scale of re-engineering required. File
systems like FAT32, originally designed for floppy disks, persist in embedded systems and
removable media, limiting file sizes and security features. Even programming languages suffer
from this: COBOL, a language from the 1950s, still runs critical financial systems, creating
a shortage of expertise and making modernisation risky.  

Another layer of constraint comes from *industry standards and interoperability requirements*.
While open standards are generally beneficial, they can also freeze technology in suboptimal
states. USB, for instance, has gone through multiple revisions, but each new version must
remain compatible with the previous ones, leading to a tangled mess of cables, adapters,
and power delivery quirks. Similarly, the QWERTY keyboard layout persists not because it is
efficient, but because retraining billions of users and redesigning input systems would be
impractical.  

Perhaps the most frustrating aspect of these conventional limits is that they are *not
insurmountable in theory*--only in practice. Unlike the speed of light or the laws of
thermodynamics, which impose hard boundaries, these constraints exist because the cost of
change (economic, logistical, or cultural) is deemed too high. The result is a computing
landscape where progress is often incremental, where layers of legacy systems accumulate
like geological strata, and where truly radical innovations must either find a way to
coexist with the past or face an uphill battle for adoption.  

In this sense, the limits of computing are not just about what is fundamentally
possible--they are also about what we, as a technological society, are willing to endure
to move forward.

