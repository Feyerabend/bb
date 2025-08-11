# From Basics To Bytecode: A guide to computers and programming
# Workbook

From LLMs we arrive naturally at automatically generated code. Such code, however, often lacks
rigour and may fail in subtle or obvious ways. To address this, we can introduce *correctness* as
a deliberate barrier--a constraint that every generated solution must pass before it can be
accepted. In this model, correctness is not merely an aspiration; it is an enforced checkpoint.

This barrier can take many forms: automated unit tests, type systems, static analysis,
property-based testing, or even formal verification techniques. Regardless of the method,
the aim is the same--to ensure that generated code does not simply appear plausible but
demonstrably satisfies a clearly defined specification.

A typical process might look like this:

1. *Define the Specification*
Describe the expected behaviour in precise terms, using requirements, invariants, or formal contracts.

2. *Generate the Code*
Provide the LLM with the specification and let it produce an implementation.

3. *Verify Against the Barrier*
Subject the generated code to tests, linters, static analysers, or proof tools.

4. *Refine Through Feedback*
Feed any errors or failures back into the LLM, adjusting the prompt to guide it towards a correct solution.

By embedding this barrier into the workflow, we shift from a "generate and hope" (like Google
once hade the search option: "I feel lucky") approach to a closed-loop system where *correctness
is continuously enforced*. The LLM becomes part of a disciplined development process--producing
not just functional code, but code that can survive deliberate and systematic scrutiny.

In effect, the AI's creativity is constrained by the same uncompromising standards we apply to
human-written software, making correctness not an optional extra but the very gateway through
which all code must pass.

In the context of counteracting LLM-generated code errors:
- E.g. dependent types and Presburger arithmetic --> enforce constraints at *compile time*.
- Tests --> validate behaviour at *runtime*.
Together, they form a layered safety net: static guarantees + dynamic checks.

Tests belong to the empirical layer:
They don't prove correctness but detect violations in finite cases.
They complement formal methods by catching issues in parts of the system where full formal verification is impractical.
They are however often easy to implement and can often be automatically (LLM) generated.

---



1. Foundational Logics & Formalisms (expressive power and verifiability of programs)
	- Dependent Types (type system guarantees, proof-carrying code)
	- Presburger Arithmetic (decidable fragments of logic useful for verification)
	- Possible additions:
		- Refinement Types? maybe?
		- Hoare Logic (pre/postconditions), already, cross ref
		- Temporal Logic (reasoning about state over time), maybe
		- Model Checking (automatic verification of finite-state systems) should be!m ok

2. Verification in Practice (applying formal methods to code)
	- Proof assistants (Coq, Lean, Agda) -- mention!
	- SMT solvers (Z3, CVC5) --ok
	- Static analysis and contracts (Frama-C, Dafny, Eiffel-style contracts) -- sidelined, we already have static analyser ..


ch03!!!!
3. Empirical Assurance (less formal but widely used!)
	- Traditional tests (unit, integration, property-based .. also here! complementary?)
	- Fuzz testing
	- Mutation testing


