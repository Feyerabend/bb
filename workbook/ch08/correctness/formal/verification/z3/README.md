
## Symbolic Register-Based Virtual Machine

The code implements a *symbolic register-based virtual machine (SymRegVM)* that
leverages the *Z3 theorem prover* to perform *symbolic execution* and verify
properties of programs.

To be able to run this, you have to install the additional package of Z3 with
Python.

1. *Symbolic Execution*:
   - Symbolic execution is a program analysis technique where programs are executed
     with *symbolic variables* (representing arbitrary values) instead of concrete inputs.
   - This enables reasoning about *all possible execution paths*, rather than a
     single execution with specific inputs.
   - In the provided code, the VM tracks its state (program counter, registers
     `A` and `B`, and flags `Z` and `N`) symbolically using Z3’s integer and boolean variables.

2. *Register-Based Virtual Machine*:
   - The VM models a simple computer with:
     - *Registers*: `A` (accumulator), `B` (auxiliary register), `Z` (zero flag, true if the
       last operation resulted in 0), and `N` (negative flag, true if the last operation resulted
       in a negative value).
     - *Program Counter (pc)*: Tracks the current instruction being executed.
     - *Instruction Set*: Includes `LOAD_A`, `LOAD_B`, `ADD`, `SUB`, `MUL`, `DIV`, `JNZ`
       (jump if `B` is not zero), and `HALT`.
   - Programs are lists of tuples `(instruction, operand)`, where the operand is used by
     instructions like `LOAD_A`, `LOAD_B`, or `JNZ`.

3. *Property Verification*:
   - The VM verifies whether a program satisfies a specific property, such as the accumulator
     `A` holding a particular value upon halting.
   - This is achieved by encoding the program’s execution as a set of constraints and using Z3
     to check if the property holds for all possible executions.

4. *Trace Generation*:
   - If a property does not hold, the VM generates an *execution trace*—a sequence of states
     showing a counterexample to aid debugging.

5. *Z3 Theorem Prover*:
   - Z3 is a *Satisfiability Modulo Theories (SMT)* solver developed by Microsoft Research.
   - It solves logical formulas involving constraints over theories like integers, booleans, and arrays.
   - In this code, Z3 encodes the VM’s state transitions, checks properties, and generates execution traces.


### Description of the Two Programs

#### `simple.py`
- *Purpose*: Implements a basic SymRegVM with a simple program that computes `A = B * 5 + 0`
  (resulting in `A = 0`) and verifies if `A == 0` when the program halts.
- *Program*:
  ```python
  program = [
      (LOAD_B, 5),  # B = 5
      (LOAD_A, 0),  # A = 0
      (MUL, 0),     # A = A * B = 0 * 5 = 0
      (HALT, 0)     # Halt
  ]
  ```
- *Execution*:
  - Loads 5 into register `B`.
  - Loads 0 into register `A`.
  - Multiplies `A` by `B`, resulting in `A = 0`.
  - Halts and checks if `A == 0`.
- *Key Features*:
  - Simple constraint encoding for state transitions.
  - Basic property checking to ensure `A == 0` at halt.
  - Trace generation if the property fails.
- *Limitations*:
  - Fixed `max_steps=20`, limiting execution steps.
  - No explicit handling of out-of-bounds program counter values.
  - Basic example program that doesn’t fully showcase the VM’s capabilities (e.g., no loops or jumps).


#### `sym_regvm.py`
- *Purpose*: An enhanced SymRegVM with improved constraint handling, a utility function for boolean
  conversion (`z3_bool_to_python`), and multiple example programs for factorial computation.
- *Key Improvements*:
  - *Increased `max_steps`*: Default is 50, supporting longer programs.
  - *Out-of-Bounds Handling*: Explicitly halts on invalid program counter values:
    ```python
    out_of_bounds = Or(pc_t < 0, pc_t >= len(self.program))
    ```
  - *Improved Property Checking*: Uses a fresh solver to check if *any* step reaches a halt
    state with the expected `A` value.
  - *Boolean Conversion*: Converts Z3 boolean expressions to Python booleans for cleaner trace output.
- *Example Programs*:
  1. *Factorial Program (5! = 120)*:
     ```python
     factorial_program_v2 = [
         (LOAD_A, 1),  # A = 1
         (LOAD_B, 2),  # B = 2
         (MUL, 0),     # A = 1 * 2 = 2
         (LOAD_B, 3),  # B = 3
         (MUL, 0),     # A = 2 * 3 = 6
         (LOAD_B, 4),  # B = 4
         (MUL, 0),     # A = 6 * 4 = 24
         (LOAD_B, 5),  # B = 5
         (MUL, 0),     # A = 24 * 5 = 120
         (HALT, 0)     # Halt
     ]
     ```
     - Computes 5! by multiplying `A` by 2, 3, 4, and 5.
     - Verifies `A == 120` at halt.
  2. *Factorial Program (3! = 6)*:
     ```python
     factorial_3_program = [
         (LOAD_A, 1),  # A = 1
         (LOAD_B, 2),  # B = 2
         (MUL, 0),     # A = 1 * 2 = 2
         (LOAD_B, 3),  # B = 3
         (MUL, 0),     # A = 2 * 3 = 6
         (HALT, 0)     # Halt
     ]
     ```
     - Computes 3! by multiplying `A` by 2 and 3.
     - Verifies `A == 6` at halt.
  3. *Factorial Program (4! = 24)*:
     ```python
     loop_factorial_4 = [
         (LOAD_A, 4),  # A = 4
         (LOAD_B, 3),  # B = 3
         (MUL, 0),     # A = 4 * 3 = 12
         (LOAD_B, 2),  # B = 2
         (MUL, 0),     # A = 12 * 2 = 24
         (LOAD_B, 1),  # B = 1
         (MUL, 0),     # A = 24 * 1 = 24
         (HALT, 0)     # Halt
     ]
     ```
     - Computes 4! by multiplying `A` by 3, 2, and 1.
     - Verifies `A == 24` at halt.
  4. *Incomplete Loop-Based Factorial*:
     - Attempts a loop-based factorial using `JNZ` but is incomplete due to the
       lack of a decrement operation for `B`.
- *Execution*:
  - Programs are executed symbolically, with traces showing step-by-step states.
  - Property checks verify expected factorial values.
- *Key Features*:
  - Robust constraint handling with out-of-bounds checks.
  - Multiple factorial programs demonstrate arithmetic capabilities.
  - Attempted loop-based factorial highlights instruction set limitations.


#### Differences Between the Two Programs
- *`simple.py`*:
  - Simpler implementation with fewer features.
  - Single trivial program (`A = 0`).
  - Limited to 20 steps, no out-of-bounds handling.
- *`sym_regvm.py`*:
  - Enhanced with higher `max_steps` (50) and out-of-bounds handling.
  - Multiple factorial programs, including loop attempts.
  - Improved trace output and property checking.


### What is Z3 and How Does It Work?

- *Z3* is an SMT solver that checks the satisfiability of logical formulas
  over theories like integers, booleans, and arrays.
- Developed by Microsoft Research, it’s used for program verification,
  testing, and constraint solving.

#### How Z3 Works
1. *Input*: Logical formulas with constraints (e.g., `x + y = 10`, `x > 0`).
2. *Theories*: Supports arithmetic, booleans, arrays, etc.
3. *Satisfiability Checking*:
   - Determines if there’s an assignment of values satisfying all constraints
     (`sat`) or if none exists (`unsat`).
   - If `sat`, provides a *model* (concrete values for variables).
4. *Applications*:
   - Encodes VM state transitions as constraints.
   - Checks properties by proving the negation is unsatisfiable.
   - Generates traces using models.

#### Example in Context
- *Constraint Encoding*:
  - State variables (`pc[t]`, `A[t]`, `B[t]`, `Z[t]`, `N[t]`) are Z3 integers.
  - Instructions like `MUL` are encoded as `A[t+1] == A[t] * B[t]`.
  - `JNZ` uses conditional constraints: `If(B_t != 0, pc[t+1] == operand, pc[t+1] == pc_t + 1)`.
- *Property Checking*:
  - Verifies `A == 120` at halt by checking if `Not(And(pc[max_steps] == -1, A[max_steps] == 120))` is `unsat`.
- *Trace Generation*:
  - Uses Z3’s model to provide concrete values for each step.


### Mathematical Background

Z3 relies on formal logic and decision procedures:

1. *First-Order Logic*:
   - Handles formulas with variables and predicates (e.g., `x > y`).
   - VM constraints are expressed as first-order logical formulas.

2. *Satisfiability Modulo Theories (SMT)*:
   - Extends SAT with theories like integer arithmetic.
   - Handles constraints like `x + y > 5 AND x * y == 10`.

3. *Decision Procedures*:
   - Uses specialized algorithms for each theory, combined with the *DPLL(T)* framework.

4. *Symbolic Execution*:
   - Models all execution paths as constraints, handling branches like `JNZ`.

5. *Model Generation*:
   - Produces concrete values satisfying constraints for traces.


### Benefits of This Approach

1. *Formal Verification*:
   - Proves correctness for all inputs, ideal for safety-critical systems.
2. *Path Coverage*:
   - Explores all execution paths, catching edge cases.
3. *Counterexample Generation*:
   - Provides traces for debugging when properties fail.
4. *Flexibility*:
   - Extensible to new instructions or properties.
   - Z3 supports complex operations.
5. *Automation*:
   - Z3 automates constraint solving, reducing manual effort.


### Limitations and Challenges

1. *Scalability*:
   - Symbolic execution is computationally expensive for large programs.
   - Fixed `max_steps` limits long-running programs.
2. *Instruction Set Limitations*:
   - No decrement instruction complicates loop-based programs.
3. *Constraint Solving Complexity*:
   - Non-linear constraints can slow Z3 or cause timeouts.
   - Simplistic division-by-zero handling may not reflect real-world behavior.
4. *Loop Handling*:
   - Fixed step limits and lack of loop invariants restrict loop verification.
5. *Manual Program Design*:
   - Requires manual instruction sequences, lacking a high-level language.


### Projects: Potential Improvements

1. *Add Decrement Instruction*:
   - Introduce `DEC_B` for easier loops.
2. *Loop Invariants*:
   - Encode invariants for arbitrary loop verification.
3. *Dynamic Step Limits*:
   - Adjust `max_steps` or use termination analysis.
4. *High-Level Language*:
   - Develop a compiler for VM instructions.
5. *Performance Optimization*:
   - Use incremental solving or constraint simplification.


### Conclusion

The `SymRegVM` demonstrates an approach to program verification using symbolic execution and Z3.
`simple.py` provides a basic proof-of-concept, while `sym_regvm.py` extends it with robust features
and factorial examples. Z3’s ability to reason about all execution paths makes this ideal for formal
verification, but scalability and instruction set limitations suggest areas for improvement. This
framework is valuable for verifying small, critical programs in domains like embedded systems or
algorithmic proofs.

