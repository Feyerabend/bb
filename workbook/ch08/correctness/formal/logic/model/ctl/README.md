
## CTL and Kripke Structures

*Computational Tree Logic (CTL)* is a branching-time temporal logic used to specify and verify properties
of systems, particularly in model checking. Unlike Linear Temporal Logic (LTL), which considers a single
execution path, CTL allows reasoning about all possible computation paths in a system, making it suitable
for modeling systems with non-deterministic behavior. CTL formulas describe properties over states and
paths in a system's state-transition model, typically represented as a *Kripke structure*.

*Concepts in CTL:*
- *Atomic Propositions*: Basic properties that hold in specific states (e.g., "door_open" or "at_floor1").
- *Logical Operators*: Standard boolean operators like `AND (∧)`, `OR (∨)`, `NOT (¬)`, and `IMPLIES (→)`.
- *Temporal Operators*:
  - *Path Quantifiers*:
    - `A` (for All paths): A property must hold on all possible computation paths from a state.
    - `E` (there Exists a path): A property must hold on at least one computation path.
  - *State Operators*:
    - `X` (neXt): A property holds in the next state.
    - `F` (Future): A property holds in some future state.
    - `G` (Globally): A property holds in all future states.
    - `U` (Until): One property holds until another becomes true.
  - Examples:
    - `AG(p)`: Globally, for all paths, proposition `p` holds in all states.
    - `EF(p)`: There exists a path where `p` eventually holds.
    - `A[p U q]`: For all paths, `p` holds until `q` becomes true.

*Kripke Structures*:
A Kripke structure is a formal model used to represent the behavior of a system in CTL model checking.
It is defined as a tuple $(S, S_0, R, L)$, where:
- *S*: A finite set of states.
- *S_0 ⊆ S*: A set of initial states (though not always explicitly used in CTL).
- *R ⊆ S × S*: A total transition relation, where for every state $s \in S$, there is at least one
  state $s' \in S$ such that $(s, s') \in R$.
- *L: S → 2^{AP}*: A labeling function that maps each state to a set of atomic propositions
  (from a set $AP$) that hold in that state.

The Kripke structure represents the system's possible states and transitions, with labels indicating
properties true in each state. For example, in an elevator system, states might represent the elevator's
floor and door status, with transitions modeling movements or door operations.

*Model Checking with CTL*:
Model checking involves verifying whether a Kripke structure satisfies a given CTL formula. This is
done by computing the set of states where the formula holds, often using fixpoint algorithms for temporal
operators like `EU`, `AU`, `EG`, and `AF`. The process is automated and checks all possible paths to ensure
properties like safety (e.g., "doors never open while moving") or liveness
(e.g., "every request is eventually served").



### Overview of the CTL Program

The Python program implements a robust *CTL model checker* for verifying properties of a system modeled as
a Kripke structure, with an example application to a *3-floor elevator control system*.

#### 1. *Kripke Structure Implementation (`KripkeStructure` class)*:
- *Purpose*: Represents a Kripke structure with states, transitions, and labeled atomic propositions.
- *Features*:
  - *State Management*: States are stored as strings, with methods to add states (`add_state`) and transitions (`add_transition`).
  - *Labeling*: Each state is associated with a set of atomic propositions (e.g., `floor1`, `doors_open`).
  - *Validation*: Ensures the structure is valid (e.g., non-empty states, total transition relation)
    using `validate` and `ensure_total_relation`.
  - *Helper Methods*:
    - `get_successors`: Returns states reachable from a given state.
    - `get_predecessors`: Finds states that can reach a given set of states.
    - `get_universal_predecessors`: Finds states where all successors are in a given set (used for universal path quantifiers).
    - `get_strongly_connected_components`: Identifies strongly connected components using Tarjan's algorithm,
      useful for analysing system behaviour.
  - *Example Use*: In the elevator model, states encode the floor, direction, door status, and request status
    (e.g., `1_i_c_n` for floor 1, idle, doors closed, no request).

#### 2. *CTL Formula Representation (`CTLFormula` classes)*:
- *Purpose*: Defines an abstract syntax tree (AST) for CTL formulas, supporting logical and temporal operators.
- *Classes*:
  - *Base Class*: `CTLFormula` is an abstract base class with methods for validation (`validate`) and string representation (`__str__`).
  - *Atomic Propositions*: `Atom` represents basic propositions (e.g., `floor1`).
  - *Logical Operators*: `Not`, `And`, `Or`, `Implies` for boolean operations.
  - *Temporal Operators*: `EX`, `AX`, `EU`, `AU`, `EG`, `AG`, `EF`, `AF` for CTL-specific properties.
  - *Validation*: Ensures formulas use valid atomic propositions from the Kripke structure.
- *Example*: The formula `AG(Implies(Or(Atom('moving_up'), Atom('moving_down')), Atom('doors_closed')))`
  checks that doors are always closed when the elevator is moving.

#### 3. *Model Checker (`CTLModelChecker` class)*:
- *Purpose*: Verifies whether a CTL formula holds in the states of a Kripke structure.
- *Key Features*:
  - *Evaluation*: Recursively evaluates CTL formulas using fixpoint algorithms for temporal operators:
    - `EX`: States with at least one successor satisfying the operand.
    - `AX`: States where all successors satisfy the operand (implemented as `¬EX(¬φ)`).
    - `EU`: Least fixpoint for "exists until" using iterative predecessor computation.
    - `AU`: Least fixpoint for "all until" using universal predecessors.
    - `EG`: Greatest fixpoint for "exists globally."
    - `EF`: Implemented as `E[true U φ]`.
    - `AF`: Implemented as `A[true U φ]`.
    - `AG`: Implemented as `¬EF(¬φ)`.
  - *Caching*: Stores results of subformulas to avoid redundant computations (`cache` dictionary).
  - *Performance Tracking*: Returns a `ModelCheckingResult` with satisfying states, computation time,
    iterations, and formula size.
- *Optimisation*: Uses caching and efficient predecessor computations to improve performance.

#### 4. *Elevator Example (`build_elevator_model` and `run_elevator_analysis`)*:
- *Model*: A 3-floor elevator system with states encoding:
  - *Floor*: 1, 2, or 3.
  - *Direction*: Up, down, or idle.
  - *Door Status*: Open or closed.
  - *Request Status*: Pending or none.
  - Example state: `2_u_c_r` (floor 2, moving up, doors closed, request pending).
- *Transitions*: Model realistic elevator behavior, such as:
  - Moving between floors (e.g., `1_u_c_n → 2_i_c_n`).
  - Opening/closing doors (e.g., `2_i_c_r → 2_i_o_n`).
  - Handling requests (e.g., `1_i_c_n → 1_i_c_r`).
- *Properties Checked*:
  - *Safety*: Doors are closed when moving; the elevator cannot be on multiple floors simultaneously.
  - *Liveness*: Every request is eventually served; any floor can be reached from any other.
  - *Reachability*: Can reach floor 3 from floor 1.
  - *Fairness*: No infinite moving without serving pending requests.
- *Analysis*:
  - Verifies each property and reports satisfying states, computation time, and iterations.
  - Identifies counterexample states if a property does not hold universally.
  - Computes strongly connected components to analyze the model's structure.

#### 5. *Program Features*:
- *Robustness*: Includes validation for states, transitions, and formulas to prevent errors.
- *Optimization*: Uses caching to reduce redundant computations and efficient algorithms (e.g., Tarjan's for SCCs).
- *Extensibility*: The `KripkeStructure` and `CTLFormula` classes are general and can model other systems.
- *Diagnostics*: Provides detailed output, including model statistics, property verification results, and structural analysis.

#### 6. *How to Use*:
- Run the script to see the elevator example in action (`main()` calls `run_elevator_analysis()`).
- The output includes:
  - Model statistics (number of states, transitions, propositions).
  - Verification results for each property (status, satisfying states, computation time).
  - Structural analysis (strongly connected components).
- To extend the program:
  - Define a new Kripke structure for a different system.
  - Add new CTL formulas to check other properties.
  - Use the `CTLModelChecker` to verify properties on the new model.

#### 7. *Example Output*:
Running the program produces output like:
```
   CTL Model Checker - Elevator Control System Analysis
======================================================================
  Model Statistics:
   States: 17
   Transitions: 21
   Atomic Propositions: 8

  Property Verification Results:
----------------------------------------------------------------------
1. Safety: Never doors open while moving
   Formula: AG((moving_up ∨ moving_down) → doors_closed)
   Status: HOLDS
   Satisfying states: 17/17
   Computation time: 0.0023s
   Iterations: 4
...
  Total verification time: 0.0156s
  Cache entries: 12

  Structural Analysis:
   Strongly Connected Components: 3
   SCC 1: ['1_i_c_n', '1_i_c_r', '1_i_o_n', ...]
```


### Summary

- *CTL*: A logic for specifying properties over all possible paths in a system, using path
  quantifiers (`A`, `E`) and temporal operators (`X`, `F`, `G`, `U`).
- *Kripke Structures*: Formal models of system behavior with states, transitions, and labeled propositions.
- *Program*: Implements a CTL model checker with validation, caching, and performance tracking,
  demonstrated on a 3-floor elevator system. It verifies safety, liveness, reachability, and fairness
  properties, providing detailed diagnostics and structural analysis.

For further exploration, you can modify the elevator model (e.g., add floors or states) or define
new CTL formulas to check additional properties.


### Story

The story of "Kripke structures" and their place in modal logic has roots in a lively period of mid-20th
century philosophical logic. To understand it, we need to set the stage in the late 1950s and early 1960s,
when modal logic was undergoing a major transformation from an informal, philosophical tool to a fully
formal semantic theory.

In the early stages, the modern modal logic was primarily axiomatic, extending propositional logic with
operators like □ (“necessarily”) and ◇ (“possibly”). These were interpreted informally—metaphysically,
epistemically, or otherwise--depending on the philosopher. What was missing was a rigorous semantics
that explained what these modal operators meant in a way that paralleled truth tables for classical logic.

Enter Stig Kanger, a Swedish logician, who in the late 1950s began developing what we would now call
relational semantics for modal logic. His idea, still quite novel at the time, was to interpret modal
operators not in isolation, but relative to possible states of affairs and an accessibility relation
linking them. Around the same time, Jaakko Hintikka in Finland, independently, pursued a similar project,
especially with epistemic logic, introducing what we’d now call "possible worlds semantics" for
knowledge and belief.

Saul Kripke, then still a teenager in the United States, published a series of papers starting around
1959–1963 that systematised this approach, giving very general and precise definitions of what a "model"
for modal logic could be. His work was not merely a restatement of Kanger or Hintikka but provided a
particularly elegant and general framework that allowed for the classification of modal logics
(K, T, S4, S5, etc.) in terms of simple properties of the accessibility relation—reflexivity,
transitivity, symmetry.

The modern term "Kripke semantics" generally refers to this relational semantics framework: a set of
possible worlds, an accessibility relation, and a valuation function. A "Kripke structure" in the
computer science sense--especially in temporal logic and model checking--is essentially the same kind
of structure but adapted for discrete-state systems: a set of states, a transition relation, and a
labeling of states with atomic propositions.

The name itself can be somewhat misleading if taken at face value. The underlying ideas had already
appeared in the work of Kanger and Hintikka before Kripke's own contributions, and Kripke openly
acknowledged this--he had, in fact, visited Kanger as a student. Nevertheless, it was Kripke's
exposition that proved decisive: his formulations, especially in English, reached a far wider
audience and shaped how the approach was adopted in both philosophical logic and, later, theoretical
computer science. As a result, his name--rather than a more historically balanced pairing--became
attached to the formalism. For some time, Kanger's and Hintikka's roles remained more prominent
in Scandinavian philosophical circles, though they have since gained broader recognition.

As for "Kripke structures" specifically: these are *not* something Kripke introduced in the context
of computer science. The term was coined later, when model checking and temporal logic emerged in
the 1970s–1980s (Clarke, Emerson, Sifakis, and others). In that setting, the "possible worlds" of
Kripke semantics became the states of a system, and the "accessibility relation" became the system's
transition relation. The name was chosen to indicate the kinship with modal logic semantics,
even though Kripke himself did not define these as such.

