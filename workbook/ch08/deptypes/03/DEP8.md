
## A Type Checker and Proof Assistant

This code implements a dependent type system and proof assistant in Python.
The implementation combines aspects of typed lambda calculus with elements
of intuitionistic logic, allowing for formal verification of logical proofs
and type-safe programming.


### 1. Type System

The code defines several fundamental types:

- *Basic Types*: `Nat` (natural numbers), `Bool` (booleans), and `Unit` (singleton type)
- *Dependent Types*: 
  - `Pi` (dependent function types) - Generalizes function types where the return type can depend on the input value
  - `Sigma` (dependent pair types) - Generalizes pair types where the second component can depend on the first
- *Identity Types*: `Id` - Represents the proposition that two terms are equal
- *Logical Types*:
  - `Proposition` - Base type for logical statements
  - `Implies` - Represents logical implication (P → Q)
  - `And` - Represents logical conjunction (P ∧ Q)


### 2. Term Language

Terms represent expressions in the language:

- *Variables*: `Var` - Represents variable references
- *Functions*: `Lam` (lambda abstraction) and `App` (function application)
- *Constants*: `TrueTerm`, `FalseTerm`, `UnitTerm`
- *Identity Proofs*: `Refl` (reflexivity), `Sym` (symmetry), `Trans` (transitivity)
- *Pairs*: `Pair`, `Fst` (first projection), `Snd` (second projection)
- *Logical Proofs*:
  - `Assume` - Assumes a proposition to prove another
  - `ImpliesIntro` - Introduces an implication (→I rule in natural deduction)
  - `ImpliesElim` - Eliminates an implication (→E rule, modus ponens)
  - `AndIntro` - Introduces a conjunction (∧I rule)
  - `AndElim` - Eliminates a conjunction (∧E rule)


### 3. Type Checking

The `type_check` function is the core algorithm that verifies term correctness
according to the typing rules. For each kind of term, it:

1. Checks if the term is well-formed
2. Determines its type
3. Ensures that logical rules are correctly applied

For example, with function application (`App`):
- It checks that the function term has a function type (`Pi`)
- Verifies that the argument type matches the function's expected input type
- Returns the result type (possibly with substitutions)


### 4. Beta Reduction

The `beta_reduce` function implements the computational aspect of the system,
reducing terms to their simplest form:

- For function application, it substitutes arguments into function bodies
- For logical operations, it applies corresponding reductions
- For pair projections, it extracts the appropriate component


### 5. Substitution

The `substitute` function replaces variables with terms throughout an expression,
handling variable binding correctly to avoid name capture.



### Type Checking Process

1. Maintain a typing context (`ctx`) mapping variable names to their types
2. Recursively traverse the term structure
3. Apply typing rules specific to each term constructor
4. Return the resulting type or raise a type error

### Example: Proving P → (Q → P)

The example at the end demonstrates the proof of a simple tautology in propositional logic:

```python
# Define propositions P and Q
P = Proposition("P")
Q = Proposition("Q")

# Build the term for the proof of P → (Q → P)
# This corresponds to: λp:P. λq:Q. p
proof_term = ImpliesIntro(
    "p", P, ImpliesIntro("q", Q, Var("p"))
)
```

This constructs a proof term representing "if I have P, then given Q, I can still provide P."

When type checked, this term produces the type `(P → (Q → P))`, verifying the proof's correctness.


## Connection to Logic and Type Theory

This implementation demonstrates the Curry-Howard correspondence, which establishes a deep connection between:

- Types and logical propositions
- Programs and proofs
- Normalization (computation) and proof simplification

Aspects illustrated:

- Function types (`→`) correspond to logical implication
- Product types (`∧`) correspond to logical conjunction
- The type checker acts as a proof checker
- Beta reduction corresponds to proof normalization

The system provides a computational foundation for constructive logic, where
*proofs* are represented as *executable* programs.
