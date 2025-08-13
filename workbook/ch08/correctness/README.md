
## Correctness as a Barrier

Hilbert’s programme, formulated in the early 20th century, sought to place all of mathematics
on an unshakeable formal foundation. Hilbert argued that any satisfactory formal system should
satisfy four conditions:

1. *Finiteness*: The system must be describable with a finite set of symbols, axioms,
   and rules of inference.
2. *Completeness*: Every well-formed statement expressible in the system must be either
   provable or disprovable within the system.
3. *Consistency*: No contradictions should be derivable; it must be impossible to prove
   both a statement and its negation.
4. *Decidability*: There must exist a mechanical procedure (an algorithm) that can,
   in finite time, determine whether any given statement is provable.

This vision was ambitious--and, for richer logics, unattainable. Gödel’s incompleteness theorems
and Church’s proof of the *Entscheidungsproblem* showed that completeness and decidability cannot
both be maintained beyond propositional logic. While the full programme collapsed, it left behind
a legacy that shaped logic, computability theory, and ultimately, the design of programming
languages and verification tools.

For computer programming, we must accept weaker properties. *Correctness* can still be preserved
as a guiding condition, provided we define it in attainable ways--typically as conformance to a
specification, not as universal mathematical truth. This gives us several working notions:

- *Partial correctness*: If the program produces a result, that result meets the specification.
  But no guarantee is made about whether the program halts.
- *Total correctness*: The program always halts and meets the specification.
- *Safety properties*: Nothing "bad" ever happens during execution (e.g., no invalid memory access).
- *Liveness properties*: Something "good" eventually happens (e.g., a request is eventually processed).

From LLMs we arrive naturally at automatically generated code. Such code, however, often lacks
rigour and may fail in subtle or obvious ways. To address this, we can introduce correctness as
a deliberate barrier--a checkpoint that every generated solution must pass before acceptance.
In this workflow:

1. Define the Specification: Clear, unambiguous requirements, invariants, or contracts.
2. Generate the Code: Let the LLM produce an implementation from the specification.
3. Verify Against the Barrier: Run the code through tests, static analysis, type systems,
   or formal proofs.
4. Refine Through Feedback: Feed any errors back into the LLM, adjusting prompts until
   the output satisfies the barrier.

In the context of LLM-generated code, different correctness techniques target different stages.
Dependent types and Presburger arithmetic can enforce constraints at compile time, giving static
guarantees. Tests validate behaviour at runtime, forming an empirical layer that catches violations
in finite cases. Tests do not prove correctness, but they complement formal methods where full
proofs are impractical--and they are often simple enough to implement or even generate automatically
with the help of the LLM itself.

By embedding these barriers into development, we transform the LLM from a suggestion tool into
a disciplined participant in software engineering--one where creative output is constrained by
uncompromising verification, and correctness becomes the gateway through which all code must pass.


### Craftsmanship

This approach fits naturally into the craftsmanship paradigm in programming. Craftsmanship is about
more than producing code that "works"; it is about creating software that is reliable, maintainable,
and elegant. The correctness barrier is the craftsperson’s measuring stick: the point where
creativity meets discipline. As in any skilled trade, tools serve the craftsperson, not the other
way around. The LLM becomes a powerful tool for exploration and speed, but the human developer
remains responsible for ensuring that each piece of software meets high standards. By embedding
correctness into the workflow, we preserve the idea that "working" is not the same as "good"--and
that pride in workmanship still matters in the age of machine-assisted programming.

- Deliberate Practice: Craftsmanship encourages constant refinement of one’s methods. Here,
  refinement is mirrored in the feedback loop: an LLM produces code, it is tested, analysed,
  and corrected until it meets the specification.

- Tools in Service of Skill: In craftsmanship, tools do not replace the craftsman; they extend
  skill. An LLM is a powerful tool, but correctness barriers ensure the human remains the arbiter of quality.

- Respect for Standards: Craftsmen work to high standards, often encoded in tests, coding
  styles, and best practices. Static guarantees and runtime checks serve as the formalisation
  of those standards in the LLM workflow.

- Layered Quality Assurance: Just as a master woodworker inspects joints, grain, and finish
  at different stages, the programmer-inspector uses static analysis, formal methods, and
  tests as successive layers of quality control.




### A Selection of Tools for Seeking Correctness

1. Foundational Logics & Formalisms (expressive power and verifiability of programs)

	- [Dependent Types](./logic/deptypes/) type system guarantees, proof-carrying code

	- [Presburger Arithmetic](./logic/presburger/) decidable fragments of logic useful
    for verification

	- [Model Checking](./logic/model/) automatic verification of finite-state systems


2. Verification in Practice (applying formal methods to code)

	- [Proof assistants](./assist/) like Coq, Lean, and Agda are interactive tools for
    writing machine-checked formal proofs, combining programming and logic in a single
    framework. They let you specify mathematical statements, construct proofs step
    by step, and have the system verify their correctness with complete rigour.

	- SMT solvers like [Z3](./smt/) automatically determine whether logical formulas
    (often with arithmetic, bit-vectors, or data structures) are satisfiable.
    They’re widely used for program analysis, verification, and synthesis by efficiently
    combining SAT solving with specialised theory reasoning.

3. Empirical Assurance (less formal but widely used)

	- [Property-based testing](./property/) checks that general invariants hold for a wide range of
    automatically generated inputs, sitting between hand-written example tests and
    full formal verification. It focuses on what must always be true, not just on
    specific input–output pairs (cf. "assert").



---
Additions

1. 	- Possible additions:
		- Refinement Types? maybe?
		- Hoare Logic (pre/postconditions), already, cross ref
		- Temporal Logic (reasoning about state over time), maybe

2. 	- Static analysis and contracts
    (Frama-C, Dafny, Eiffel-style contracts) -- sidelined, we already have static analyser! ..
