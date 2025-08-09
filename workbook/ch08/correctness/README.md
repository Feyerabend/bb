# From Basics To Bytecode: A guide to computers and programming
# Workbook

In the context of counteracting LLM-generated code errors:
- Dependent types and Presburger arithmetic --> enforce constraints at *compile time*.
- Tests --> validate behaviour at *runtime*.
Together, they form a layered safety net: static guarantees + dynamic checks.

---
EXPAND

In contrast to logical, the empirical part move to ch03?
Reasoning in general here?

- RUNTIME
	* unit -- integration -- property -- more reasoning? not so much code?

- EXPLORATORY
	* Fuzz
	* Mutation

Tests belong to the empirical layer:
They don't prove correctness but detect violations in finite cases.
They complement formal methods by catching issues in parts of the system where full formal verification is impractical.


---

1. Foundational Logics & Formalisms (expressive power and verifiability of programs)
	- Dependent Types (type system guarantees, proof-carrying code)
	- Presburger Arithmetic (decidable fragments of logic useful for verification)
	- Possible additions:
		- Refinement Types?
		- Hoare Logic (pre/postconditions), already, cross ref
		- Temporal Logic (reasoning about state over time), maybe
		- Model Checking (automatic verification of finite-state systems) should be!

2. Verification in Practice (applying formal methods to code)
	- Proof assistants (Coq, Lean, Agda)
	- SMT solvers (Z3, CVC5)
	- Static analysis and contracts (Frama-C, Dafny, Eiffel-style contracts)

3. Empirical Assurance (less formal but widely used!)
	- Traditional tests (unit, integration, property-based)
	- Fuzz testing
	- Mutation testing
