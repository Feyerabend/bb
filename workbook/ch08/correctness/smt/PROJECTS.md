
## Projects on Z, SMT, and Symbolic Reasoning

#### Introductory Tasks

1. *Define a Simple Z Schema*

You write down a Z schema for a basic counter system: it has a state variable
count : ℤ and two operations: Increment and Reset. Try to formally specify
preconditions and postconditions.

2. *Check Consistency with an SMT Solver*

You encode your Z schema into constraints for an SMT solver (e.g., Z3).
You then ask:
- Is the schema consistent (has at least one model)?
- Can you find a state where count < 0 after some operations?

3. *Experiment with Symbolic Execution*

Using your simple.py interpreter, you make a program that updates a variable.
You symbolically execute it with your sym_regvm.py system, and then feed the
resulting constraints into an SMT solver to see if certain conditions can ever hold.



### Intermediate Projects

4. *Translate Z Operations into SMT Constraints*

You choose a slightly larger Z specification, e.g., a bank account system with
balance : ℤ and operations Deposit and Withdraw. You encode preconditions
(like Withdraw requires balance ≥ amount) and use an SMT solver to verify properties:
- "You can never withdraw more than you deposited."
- "Balance is always non-negative."

5. *Extend Your Symbolic VM*

You modify sym_regvm.py so that it not only tracks symbolic states but also
automatically generates SMT constraints. You then let the solver check reachability
of error states (e.g., division by zero).

6. *Path Condition Exploration*

You implement branching in your VM where symbolic execution collects different path
conditions. You then hand these to an SMT solver to check which paths are feasible
and generate concrete input examples.



### Advanced Projects

7. *Link Z Specifications with Your VM*

You take a Z schema (like the counter or bank account) and translate
it into operations in your VM. Then you symbolically execute a sequence
of operations and use the solver to check whether the Z-invariant holds
in all reachable states.

8. *Invariant Discovery with SMT*

You try to automatically discover invariants. For example, run symbolic
execution on your VM, dump the constraints into the solver, and try to
generalise patterns like “balance ≥ 0”. You don’t need a full theorem
prover, but you can aim at automating simple checks.

9. *Model Checking Small Protocols*

You specify a small protocol in Z (e.g., a handshake or token ring).
You then simulate it in your symbolic VM and check safety properties
with SMT, such as "at most one process holds the token."

10. *Integration of Z, Symbolic VM, and SMT in One Workflow*

You aim to create a pipeline where:

- A Z schema is parsed or represented,
- It is mapped to your VM instructions,
- Symbolic execution runs and produces constraints,
- An SMT solver verifies invariants or finds counterexamples.

This becomes a miniature verification framework.
