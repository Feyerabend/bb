
## Gödel's incompleteness theorems, Turing and Church

Gödel's incompleteness theorems (1931) are a fundamental result in mathematical logic that reveal intrinsic limitations
in formal mathematical systems. Gödel showed that for any sufficiently expressive formal system--such as Peano arithmetic--there
exist statements that are true but unprovable within the system itself. This means that no formal system can ever be
both complete (capable of proving all true statements) and consistent (free from contradictions). If a system is consistent,
there will always be true statements it cannot prove. Gödel's proof method involved constructing a self-referential mathematical
statement (akin to the "This statement is unprovable" paradox), which, if provable, would create a contradiction, and if
unprovable, would be a true statement that the system fails to prove.

This result has deep implications for computation because formal systems underlie programming languages and mathematical logic,
which are used to define what computers can and cannot do. It suggests that there will always be limits to what a computational
system, based on formal rules, can determine.

Alan Turing (1936) extended this line of thought with the Halting Problem, proving that there is no general algorithm that can
decide whether an arbitrary program will halt or run indefinitely. He formalized computation through the concept of a Turing
machine, a mathematical model that captures the essence of algorithmic processing. Turing's proof used a diagonalization
argument, similar to Gödel's self-referential trick, by constructing a program that takes another program as input and
determines whether it halts. If such an algorithm existed, one could construct a paradoxical program that contradicts
itself, proving that no universal "halt-checking" algorithm can exist.

This result establishes an absolute boundary on computation: some problems are undecidable, meaning that no finite mechanical
process can solve them in general. While some specific cases of the halting problem can be decided, the general case cannot.
This affects areas such as software verification, where determining whether a given program has bugs, loops forever, or
behaves as expected is often undecidable.

The Church-Turing thesis (1936), independently formulated by Alonzo Church and Alan Turing, asserts that any function that
can be computed by an "effective procedure" (a well-defined mechanical method) can also be computed by a Turing machine.
This does not mean all functions are computable, but rather that Turing machines capture the full extent of what is
algorithmically possible. The thesis is not a formal theorem but rather a guiding principle in theoretical computer
science. It implies that any computational model--whether lambda calculus (Church's approach), register machines, or
modern programming languages--is ultimately no more powerful than a Turing machine.

One of the most significant consequences of the Church-Turing thesis is the realization that certain problems are
inherently non-algorithmic. This was demonstrated with Hilbert's *Entscheidungsproblem* (the "decision problem"), which
sought a general algorithm to determine whether a given logical statement is provable. Turing's and Church's work showed
that no such algorithm exists, meaning mathematical truth goes beyond what can be mechanically computed.

These foundational results have shaped modern computer science, artificial intelligence, and mathematical logic by
highlighting the fundamental limits of formal reasoning and computation. They underscore the reality that while computers
are immensely powerful, there exist problems that are forever beyond their reach.
