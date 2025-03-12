## P vs NP

The discussion surrounding P vs NP began in earnest in the 1970s, catalysed by
Stephen Cook's paper in 1971, "The Complexity of Theorem-Proving Procedures".
This paper introduced the P vs NP problem, which asks whether every problem
whose solution can be verified in polynomial time (the class NP) can also be
solved in polynomial time (the class P). This remains one of the most profound
open questions in computer science and mathematics today (part of the Millennium
Prize Problems with a $1 million reward for a solution).


### Developments in the 1970s

1. Cook's Theorem:
   Stephen Cook proved that SATISFIABILITY (SAT), the problem of determining
   whether there exists an assignment to variables that makes a Boolean formula
   true, is NP-complete. This means SAT is at least as hard as any problem in NP.
   If SAT can be solved in polynomial time, all NP problems can be solved in
   polynomial time.

2. Richard Karp's Work (1972):
   Building on Cook's theorem, Karp identified 21 problems as NP-complete, showing
   that these problems are equivalent in their computational difficulty. This
   reinforced the idea of NP-completeness as a framework for understanding
   computational complexity.

3. Leonid Levin (independently in the USSR):
   Levin's contributions mirrored Cook's results, though his work was less
   accessible to the broader community, until later.

4. Emergence of Computational Complexity Theory:
   The 1970s marked the development of theoretical frameworks for classifying
   computational problems, leading to broader questions about the nature of
   efficient computation and problem-solving.


Polynomial-time refers to problems that can be solved by an algorithm where the time
it takes to find the solution grows at a manageable rate as the size of the input
increases. Specifically, the growth is proportional to a power (or polynomial) of the
input size, such as $n^2$ or $n^3$, where n is the size of the input.

This is considered "efficient" in computational terms because even as inputs grow large,
the time remains feasible compared to algorithms that grow exponentially, where the time
can quickly become unworkable. In essence, if a problem can be solved in polynomial time,
it is generally viewed as computationally practical.


### Philosophical and practical implications in the 1970s

The P vs NP question struck a nerve because it was not just abstract but directly
tied to practical problems in fields like cryptography, scheduling, optimisation,
and artificial intelligence. If P = NP, tasks like cracking cryptographic codes or
optimising complex systems could become computationally trivial, with profound
societal consequences.

However, most computer scientists and mathematicians suspected (and still suspect)
that P <> NP, meaning that there are problems that are easy to verify but fundamentally
hard to solve.


### The modern perspective

Today, the P vs NP question is central to theoretical computer science, and its
importance has only grown:

1. Evidence and Beliefs:
   Despite decades of effort, no one has been able to prove or disprove P = NP.
   Most researchers believe that P <> NP, as no polynomial-time algorithms have
   been found for any NP-complete problem despite extensive study.

2. Implications for Cryptography:
   Modern cryptography, including public-key encryption, relies on the assumption
   that some problems (like factoring large integers or solving discrete logarithms)
   are computationally infeasible. If P = NP, these cryptographic systems would
   collapse.

3. Complexity Classes Beyond NP:
   The study of complexity classes has expanded, introducing concepts like NP-hard,
   co-NP, PSPACE, and EXP, deepening our understanding of the landscape of computational
   problems.

4. Applications of NP-completeness:
   NP-complete problems help guide practical approaches to problem-solving, as they
   often suggest using heuristics, approximation algorithms, or randomisation for
   problems that are unlikely to be solved exactly in polynomial time.


#### The philosophical take today

The P vs NP question remains one of the most compelling intellectual challenges of
our time. It forces us to confront the limits of computation and human ingenuity.
Philosophers and computer scientists alike ponder whether there are intrinsic
limitations to what can be computed efficiently--or if we simply haven't discovered
the right algorithms yet?



### Approximations?

AI has already demonstrated remarkable success in solving complex problems like protein
folding through approximation and predictive modelling. These are problems that can be
computationally overwhelming due to their combinatorial nature, similar to NP-complete problems,
where exact solutions may be infeasible in practice.


__1. AI in Protein Folding__

Protein folding involves predicting the three-dimensional structure of a protein based on
its amino acid sequence--a problem of staggering complexity. Until recently, it was considered
one of the "grand challenges" of biology. However, tools like *AlphaFold* from DeepMind have
achieved groundbreaking success. (Ultimately leading to the Nobel Prize.)

By training on large datasets of known protein structures, AlphaFold uses deep learning
to predict how a protein will fold. Its predictions are highly accurate, achieving
near-experimental precision for many proteins.

While not always perfect, AlphaFold provides solutions that are "good enough" for many
biological applications, such as drug discovery and understanding disease mechanisms.


__2. AI and approximation in *NP-like problems*__

For NP-complete and combinatorial problems (like protein folding), AI does not necessarily
guarantee exact solutions but excels at finding approximate solutions that are useful in
practice. This mirrors its success in protein folding.

AI uses techniques like reinforcement learning, genetic algorithms,
or Monte Carlo simulations to explore vast solution spaces efficiently.

By identifying recurring patterns and structures in the data,
AI bypasses brute-force methods and narrows the search to likely solutions.


__3. Why AI is effective in approximation__

* AI models can adapt to diverse problem types, from physics simulations to combinatorial optimisation.

* AI thrives on leveraging prior examples to make predictions or refine its search strategies, even in poorly understood systems.

* AI also scales well with computational resources, allowing it to tackle problems previously thought intractable.



__4. Other examples of "almost there" solutions__

In the Travelling Salesman Problem (TSP) finding the exact shortest path is computationally infeasible
for large instances, AI-powered methods often find near-optimal routes.

AI-driven approximations are widely used in airline scheduling, supply chain management, and delivery
routing, often saving significant time and resources.

In games like Go or Chess, AI approximates optimal strategies using reinforcement learning, achieving
"superhuman" performance, without brute-forcing every possible outcome.


__5. Applications beyond protein folding__

AI accelerates the search for potential drug candidates by predicting interactions between molecules and proteins.

Approximations in AI-driven simulations help model complex systems like weather patterns or climate change,
where exact computations are impossible.

AI predicts material properties and molecular interactions, enabling faster development of novel materials.


__6. Limitations of AI Approximations__

While AI excels in practical approximations, it has limitations:

- Lack of Guarantees: Unlike exact algorithms, AI approximations may lack mathematical guarantees of optimality or bounded error.

- Problem Dependency: AI solutions often rely on problem-specific data or assumptions, making them less generalisable than theoretical algorithms.

- Computational Cost: While AI avoids brute force, training and running models can still be resource-intensive.


__7. How It Relates to P vs NP__

The success of AI in approximating *NP-like problems*, such as protein folding,
illustrates a pragmatic approach to tackling problems we might never solve exactly.
Even if P <> NP, AI offers a way to address these challenges by:

* Finding useful, near-optimal solutions within practical timeframes.

* Providing insights into the structure of problems that can inform future algorithm design.


### Conclusion

AI's ability to solve problems like protein folding in an "almost there" way is a testament to
its power as an approximation tool. It demonstrates that even for problems beyond exact polynomial-time
solutions, AI can deliver results that are good enough for real-world applications. In this way,
AI transforms theoretical intractability into practical solvability, bridging the gap between
complexity theory and everyday challenges.

