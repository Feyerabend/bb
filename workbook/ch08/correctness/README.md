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




1. Foundational Logics & Formalisms (expressive power and verifiability of programs)
	- Dependent Types (type system guarantees, proof-carrying code)
	- Presburger Arithmetic (decidable fragments of logic useful for verification)
	- Possible additions:
		- Refinement Types?
		- Hoare Logic (pre/postconditions), already, cross ref
		- Temporal Logic (reasoning about state over time), maybe
		- Model Checking (automatic verification of finite-state systems) should be!

2. Verification in Practice (applying formal methods to code)
	- Proof assistants (Coq, Lean, Agda) -- mention!
	- SMT solvers (Z3, CVC5) --ok
	- Static analysis and contracts (Frama-C, Dafny, Eiffel-style contracts) -- sidelined

ch03!!!!
3. Empirical Assurance (less formal but widely used!)
	- Traditional tests (unit, integration, property-based)
	- Fuzz testing
	- Mutation testing





Agda

A dependently typed functional programming language where types can express
logical propositions and programs are proofs.
Proofs are built by writing programs that type-check against these propositions.
Minimal automation; focuses on human-guided, type-driven proof development.

Coq

An interactive theorem prover based on the Calculus of Inductive Constructions.
Users build proofs interactively using tactics.
Supports both constructive proofs and extraction of verified functional programs.
Used in large verification projects (e.g., CompCert verified C compiler, formalised mathematics).

Lean

Similar in core logic to Coq but with a modern language design and tooling.
Combines interactive proof development with strong automation support.
Well-known for mathlib, a rapidly growing formal mathematics library.



| Tool  | Type | Automation Level | Logic / Foundation | Typical Use Cases |
|—–|——|——|––|——|
| Z3    | SMT solver | Fully automated | First-order logic + background theories (arithmetic, arrays, bit-vectors, etc.) | Constraint solving, program verification, model checking |
| Agda  | Dependently typed language | Manual (type-driven) | Intuitionistic type theory | Verified programming, type-level proofs, teaching logic |
| Coq   | Interactive theorem prover | Semi-automated (tactics) | Calculus of Inductive Constructions | Large formal proofs, verified software, formalised mathematics |
| Lean  | Interactive theorem prover | Semi-automated + good automation tools | Similar to Coq (dependent type theory) | Formal mathematics (mathlib), verified algorithms, teaching |

