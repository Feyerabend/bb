
## Correctness in Computer Programming

Correctness in computer programming ensures that a program adheres to a well-defined
*specification*, which describes its intended behaviour across *all possible executions*,
encompassing both functional (e.g., correct outputs) and non-functional (e.g., safety,
performance) properties. Unlike universal mathematical truth, which is often unattainable
due to theoretical limits like undecidability (e.g., Peano arithmetic with multiplication
is undecidable, unlike Presburger arithmetic), correctness relies on practical, verifiable
properties such as partial/total correctness, safety, and liveness, often enhanced by
advanced techniques like dependent types and tools like Z3, Lean, and Agda. This
explanation details what correctness expects, how it is achieved, and connects these
concepts to the provided documents and additional tools.


### What Correctness Expects

Correctness expects a program to conform to a *specification*, which can be formal
(e.g., mathematical formulas in temporal logic or arithmetic) or informal (e.g.,
natural language requirements like "the elevator stops at requested floors").

Specifications define:

- *Functional Properties*: Correct input-output behaviour (e.g., a sorting algorithm
  returns a sorted list).

- *Non-Functional Properties*: Safety (e.g., no crashes), liveness (e.g., progress),
  performance, or resource constraints.

- *Dependent Type Properties*: In advanced systems, specifications may include dependent
  types, where types depend on values (e.g., a list type indexed by its length, ensuring
  operations like indexing are safe at compile-time).

The original explanation's reference to "weaker properties" reflects the need to focus
on attainable goals due to:

- *Undecidability*: Full correctness for arbitrary programs (e.g., with multiplication)
  is undecidable, pushing us toward decidable fragments like Presburger arithmetic.

- *Complexity*: Exhaustive verification can be computationally infeasible (e.g., state
  explosion in model checking).

- *Practical Constraints*: Real-world systems prioritise critical properties like
  safety over universal correctness.

Let's review the previous points mentioned in the README.

1. *Partial Correctness*: If a program produces a result, it meets the specification,
   but termination is not guaranteed. For example, in `vmmodel.c`, a virtual machine
   (VM) might produce correct register values when halting, but the model checker
   doesn't ensure termination.

2. *Total Correctness*: The program always halts and meets the specification. In `ctlmodel.py`,
   the liveness property `AG(Implies(Atom('request_pending'), AF(Atom('doors_open'))))`
   ensures an elevator eventually serves requests, implying termination of request-handling.

3. *Safety Properties*: Nothing "bad" happens (e.g., no invalid memory access). In `ctlmodel.py`,
   `AG(Implies(Or(Atom('moving_up'), Atom('moving_down')), Atom('doors_closed')))` ensures
   the elevator never moves with open doors. In `vmmodel.c`, the checker verifies the program
   counter (PC) stays within bounds.

4. *Liveness Properties*: Something "good" eventually happens (e.g., progress). In `ctlmodel.py`,
   `And(AG(EF(Atom('floor2'))), And(AG(EF(Atom('floor1'))), AG(EF(Atom('floor3')))))` ensures
   the elevator can reach any floor.

5. *Dependent Type Properties*: Using dependent types, specifications can embed correctness
   constraints in the type system (e.g., in Agda or Lean, a function's type might guarantee
   that an array index is within bounds, as in `a : Vector ℕ n → Fin n → ℕ`, where `Fin n`
   ensures the index is less than `n`). This reduces runtime checks by proving properties
   at compile-time.


## How Correctness Works

Achieving correctness involves verifying that a program satisfies its specification
using techniques like testing, model checking, theorem proving, static analysis, and
dependent types, supported by tools like Z3, Lean, and Agda. The provided documents
illustrate several approaches, which we detail below.


### 1. Specification Definition

Specifications articulate expected behavior:

- *In `ctlmodel.py`*: The elevator's specification uses CTL formulas for safety (e.g.,
  doors closed while moving) and liveness (e.g., requests served).

- *In `vmmodel.c`*: The implicit specification ensures no invalid instructions or
  out-of-bounds PC values in the VM.

- *In `presburger.py` and `cooper.py`*: Specifications are Presburger arithmetic
  formulas (e.g., `∃x. 2x = 6`) for numerical constraints like array bounds.

- *With Dependent Types*: Specifications are encoded in types (e.g., in Lean, a
  type `List ℕ` with a length parameter ensures safe operations, reducing the
  need for separate verification).


### 2. Verification Techniques

#### a. Testing
- *Description*: Execute the program on selected inputs to check specification conformance.
- *How It Works*: Run test cases and compare outputs to expected results. For example,
  testing the elevator in `ctlmodel.py` might simulate requests to verify door behavior.
- *Limitations*: Incomplete coverage misses edge cases, unlike exhaustive methods in
  `ctlmodel.py` or `vmmodel.c`.
- *Relevance*: Testing is a practical first step but less rigorous than formal methods.

#### b. Model Checking
- *Description*: Exhaustively explore all possible system states to verify properties,
  as in `ctlmodel.py` and `vmmodel.c`.
- *How It Works*:
  - *System Model*: Represent the system as a finite-state structure, like a Kripke
    structure in `ctlmodel.py` (states, transitions, labels) or a state space in
    `vmmodel.c` (PC, register, halted).
  - *Property Specification*: Use temporal logic e.g., CTL in `ctlmodel.py`:
    `AG(Implies(Or(Atom('moving_up'), Atom('moving_down')), Atom('doors_closed')))`
    or invariants in `vmmodel.c` (valid PC).
  - *Exploration*: Employ algorithms like depth-first search (`vmmodel.c`) or
    fixpoint computations (`ctlmodel.py`) to check properties across all reachable states.
  - *Counterexamples*: Provide traces to violating states (e.g., counterexample states
    in `ctlmodel.py` or error states in `vmmodel.c`).
- *Examples*:
  - In `ctlmodel.py`, the `CTLModelChecker` verifies elevator properties using fixpoint
    algorithms for CTL operators (`EU`, `AU`, `EG`), reporting satisfying states and
    counterexamples.
  - In `vmmodel.c`, the checker explores VM states to ensure no invalid instructions,
    using a hash set for efficiency.
- *Optimisations*: Caching (`ctlmodel.py`) and hash-based state storage (`vmmodel.c`)
  mitigate state explosion.
- *Relevance*: Ideal for safety-critical systems like elevators or VMs, ensuring
  exhaustive verification.

#### c. Theorem Proving
- *Description*: Use logical deduction to prove specification conformance, as in
  `presburger.py` and `cooper.py`.
- *How It Works*:
  - *Formal System*: Define axioms and inference rules (e.g., Presburger axioms in
    `presburger.py`: `∀x. x + 0 = x`).
  - *Proof Construction*: Derive the specification using rules like modus ponens or
    universal instantiation (tested in `test_presburger.py`).
  - *Automated Decision Procedures*: Use algorithms like Cooper's quantifier elimination
    (`cooper.py`) to decide formulas (e.g., `Exists('x', Eq(Mult(2, var('x')), const(6)))`).
- *Examples*:
  - In `presburger.py`, the `ProofSystem` proves formulas like
    `ForAll('x', Eq(Add(var('x'), Zero()), var('x')))` using axioms.
  - In `cooper.py`, Cooper's algorithm decides numerical constraints
    by eliminating quantifiers.
- *Relevance*: Suited for numerical properties (e.g., array bounds) or
  logical invariants in decidable theories.

#### d. Static Analysis
- *Description*: Analyze code without execution to infer properties, often using
  abstract interpretation or symbolic execution.
- *How It Works*: Tools detect errors (e.g., null pointer dereferences) or prove
  properties (e.g., bounds safety using Presburger arithmetic in `cooper.py`).
- *Relevance*: Complements model checking and theorem proving for large codebases.

#### e. Dependent Types
- *Description*: Encode specifications in the type system to ensure correctness
  at compile-time, as used in languages like Lean and Agda.
- *How It Works*:
  - Types depend on values, allowing specifications to be embedded in the program's
    structure. For example, in Agda, a type `Vector ℕ n` represents a list of natural
    numbers with length `n`, and a function `head : Vector A (suc n) → A` ensures
    the vector is non-empty, preventing runtime errors.
  - Proofs of correctness (e.g., bounds safety) are checked by the type system,
    reducing the need for separate verification.
- *Examples*:
  - In a dependently typed language, a specification like `∃x. 2x = 6` (from `cooper.py`)
    could be encoded as a type ensuring a function returns a value satisfying the constraint.
  - The elevator's safety property (`doors_closed` when moving) could be encoded as
    a type invariant, ensuring only valid states are constructed.
- *Relevance*: Dependent types shift correctness checks to compile-time, enhancing
  reliability for critical systems, though they require significant programmer effort.

### 3. Tools and Libraries
Correctness is supported by specialised tools:
- *Model Checkers*: SPIN, NuSMV, or custom checkers in `ctlmodel.py` and `vmmodel.c`
  for state-based verification.
- *SMT Solvers*: Z3, mentioned in the Presburger README, automates decision procedures
  for Presburger arithmetic (e.g., `∃x. 2x = 6` in `cooper.py`) and other theories,
  widely used in program verification.
- *Theorem Provers*: Lean and Agda support dependent types and interactive proof
  construction. Lean is used for formalising mathematics and verifying software,
  while Agda focuses on type-theoretic proofs, both enabling compile-time correctness
  guarantees.
- *Static Analysers*: Frama-C, Infer, or tools using Presburger arithmetic
  (`presburger.py`) for bounds checking.

### 4. Practical Examples
- *Elevator System (`ctlmodel.py`)*:
  - *Specification*: Safety (doors closed while moving), liveness (requests served),
    reachability (all floors accessible).
  - *Verification*: The `CTLModelChecker` uses CTL formulas and fixpoint algorithms,
    reporting counterexamples if properties fail.
- *Virtual Machine (`vmmodel.c`)*:
  - *Specification*: No invalid instructions or out-of-bounds PC.
  - *Verification*: Depth-first state exploration with hash-based optimisation ensures
    safety.
- *Numerical Constraints (`presburger.py`, `cooper.py`)*:
  - *Specification*: Formulas like `∀x. x + 0 = x` or `∃x. 2x = 6`.
  - *Verification*: Proof systems and Cooper's algorithm decide truth, supporting
    program verification tasks.
- *Dependent Types*: In Lean or Agda, the elevator's safety property could be
  encoded as a dependent type ensuring `doors_closed` when `moving_up` or `moving_down`,
  verified at compile-time.

### 5. Challenges
- *State Explosion*: Model checking (`ctlmodel.py`, `vmmodel.c`) faces exponential
  state growth, mitigated by caching or symbolic methods.
- *Complexity*: Presburger arithmetic decision procedures (`cooper.py`) have double
  exponential complexity, though practical fragments are tractable.
- *Specification Errors*: Incorrect specifications lead to false positives or negatives.
- *Dependent Types*: Require significant expertise and annotation effort, though
  tools like Lean and Agda ease this through interactive proving.
- *Scalability*: Large systems need abstraction or partial verification.

### 6. Connection to Provided Documents
- *CTL Model Checking (`ctlmodel.py`)*: Verifies elevator properties using Kripke
  structures and CTL, ensuring safety and liveness.
- *VM Model Checking (`vmmodel.c`)*: Checks VM safety through state exploration,
  preventing invalid states.
- *Presburger Arithmetic (`presburger.py`, `cooper.py`)*: Supports numerical
  correctness (e.g., bounds checking) via decidable proof systems and quantifier
  elimination.
- *Dependent Types*: While not in the documents, Lean and Agda could encode the
  elevator's or VM's specifications as types, ensuring correctness at compile-time.

## Conclusion
Correctness in programming ensures conformance to a specification, using properties like
partial/total correctness, safety, liveness, and dependent type guarantees, necessitated
by undecidability and complexity constraints. It is achieved through testing, model checking,
theorem proving, static analysis, and dependent types, with tools like Z3, Lean, and Agda
enhancing automation and rigor, as exemplified by the provided elevator, VM, and
Presburger arithmetic implementations.


