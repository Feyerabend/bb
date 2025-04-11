
## Dependent Type Checker & Proof Assistant

This repository implements a Python-based proof assistant with dependent types, combining typed
lambda calculus with intuitionistic logic for formal verification.


### Core System Architecture

- *Type Foundation*: Combines basic types, dependent types (Pi/Sigma), identity types, and logical types
- *Expression Language*: Full term language supporting variables, lambdas, pairs, logical constants and proof terms
- *Verification Engine*: Implements rigorous type checking according to typing rules
- *Computational Model*: Beta reduction for execution semantics
- *Proof Normalisation*: Cut elimination for simplifying logical proofs

### Theoretical Foundations

- Implements the *Curry-Howard correspondence* (propositions-as-types)
- Provides computational foundation for *constructive logic*
- Supports *dependent types* where types depend on values

### Verification Capabilities

- *Type Safety*: Ensures program correctness via typing rules
- *Proof Checking*: Verifies logical proofs within the system
- *Normalisation*: Simplifies proofs to canonical forms

### Implementation Highlights

- Clean separation between type system, term language, and checking algorithm
- Proper handling of variable binding and substitution
- Support for both computational features and logical reasoning


### Example

The system allows encoding and verifying logical theorems like:

```python
# Proving P → (Q → P)
P = Proposition("P")
Q = Proposition("Q")

proof = ImpliesIntro("p", P, ImpliesIntro("q", Q, Var("p")))

# Type checking verifies this has type P → (Q → P)
```

### Applications

- *Formal Verification*: Prove properties of programs
- *Theorem Proving*: Encode and verify mathematical theorems
- *Program Extraction*: Derive correct-by-construction programs from proofs
- *Type-Level Programming*: Express complex invariants at the type level

Potential extensions could include:
- Inductive types and recursion principles
- Universe hierarchies for more expressive typing
- Tactics for semi-automated proof construction
- Interactive proof development environment


### Project Suggestions

- Propositional Logic Library: Implement standard theorems of propositional logic
  (e.g., De Morgan's laws, distributivity)
- Natural Number Arithmetic: Define addition, multiplication and their properties
- Simple Data Structures: Define and verify properties of lists or binary trees

- Program Verification: Extract verified algorithms (e.g., sorting with correctness proof)
- Modal Logic Extension: Add operators for necessity and possibility
- Type-Level Programming: Implement type-level functions (e.g., vector operations with length constraints)
- Bidirectional Type Checking: Enhance the type checker with bidirectional inference

- Unification Algorithm: Implement higher-order unification for proof automation
- Effect System: Add a layer for tracking computational effects
- Homotopy Features: Extend with basic homotopy type theory concepts
- Compiler Backend: Generate executable code from verified programs
- Interactive Theorem Prover: Build a simple UI for interactive proof development

Each project builds on the core implementation while exploring different dimensions
of type theory, logic, and verification methodologies.
