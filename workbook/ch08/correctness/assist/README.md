
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

