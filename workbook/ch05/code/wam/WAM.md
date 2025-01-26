
## WAM

The Warren Abstract Machine (WAM) is a highly influential virtual machine designed specifically for
implementing the logic programming language Prolog. David H. D. Warren developed it in the early 1980s
as a way to efficiently execute Prolog programs by transforming the high-level logic of Prolog into
lower-level operations tailored to a virtual machine architecture.



### High-Level Purpose

The WAM provides an efficient execution model for Horn clause logic. Prolog programs are compiled
into a sequence of low-level WAM instructions, which the WAM interprets or executes. This design
takes into account Prolog's unique features, such as unification, backtracking, and logical variables.

*Core Features of WAM*

1. Unification
Unification is central to Prolog and involves matching terms with variables, constants, or structures.
The WAM includes efficient instructions for performing unification, supporting variable bindings and
logical constraints.

2. Backtracking
Prolog relies on backtracking to explore alternative solutions when a computation path fails. The WAM
achieves this using a stack-based control structure that stores choice points, enabling efficient
return to earlier states.

3. Efficient Term Representation
The WAM represents Prolog terms (variables, constants, lists, and structures) compactly in memory,
using tagged cells to distinguish between term types.


### Components of the WAM


__1. Registers__

The WAM uses registers to manage the execution state:
- The Instruction Pointer (IP) controls the flow of execution, pointing to the next instruction in the program.
- The Heap Pointer (HP) tracks the dynamic allocation of terms.
- Other auxiliary registers may track choice points or environment frames.

In the code:

```python
self.registers = {
    'IP': 0,    # instruction pointer
    'CP': 0,    # current predicate (not always used directly)
    'HP': 0,    # heap pointer
}
```

These registers perform the same roles, ensuring that the execution progresses correctly and
that terms are allocated properly during unification.


__2. Memory Areas__

The WAM divides memory into structured areas for storing terms, execution state, and control flow.
- Heap: Stores terms such as variables, constants, and compound structures.

```python
self.heap = []
```

In the provided implementation, the heap is dynamically allocated to store data like references
to variables or constants.

- Stack: Temporarily stores intermediate values, such as variable bindings or unification states.

```python
self.stack = []
```

- Call Stack: Tracks procedure return addresses to enable nested predicate calls.

```python
self.call_stack = []
```

- Choice Points: Maintains snapshots of the execution state to enable backtracking.

```python
self.choice_points = []
```


These memory areas work together to enable unification, recursive calls, and nondeterministic Prolog execution.

__3. Instructions__

The WAM operates on a specialized set of instructions tailored to Prolog. These instructions handle term manipulation,
predicate calls, unification, and control flow.

In the Python implementation, the instructions list holds the compiled program:

```python
self.instructions = []
```

Each instruction is represented as a tuple:

```python
('CALL', ('child', 1), 0)  # Example of a CALL instruction
```

The fetch_execute method simulates the execution cycle of the WAM:
1. Fetch the current instruction using IP.
2. Decode the operation and its arguments.
3. Execute the operation, updating memory or control flow as needed.

Examples of supported instructions include:
- CALL: Invokes a predicate.
- GET_VARIABLE: Allocates a reference for a variable.
- PUT_CONSTANT: Places a constant into the heap.
- PROCEED: Completes the current predicate and returns to the caller.
- CUT: Discards choice points, pruning alternative execution paths.

__4. Compilation__

Prolog programs are compiled into a sequence of WAM instructions. The Compiler class in the provided code
transforms high-level Prolog facts, rules, and queries into these low-level instructions.

For instance, a Prolog fact like:

```prolog
parent(zeb, john).
```

is compiled into:

```python
[
    ('PUT_CONSTANT', 0, 0),  # 'zeb' -> argument 0
    ('PUT_CONSTANT', 1, 1),  # 'john' -> argument 1
    ('PROCEED', 0, 0)        # Return to caller
]
```

A query like:

```python
?- child(X).
```

is compiled into:

```python
[
    ('GET_VARIABLE', 0, 0),  # Allocate variable 'X'
    ('CALL', ('child', 1), 0)  # Call the 'child/1' predicate
]
```

The compiler registers variables and constants, assigns indices, and maps predicates to their
instruction addresses. The final instructions are stored in self.instructions for execution.

__5. Execution__

The execution phase starts by loading the compiled program into the WAM:

```python
vm.load(compiler)
```

The machine begins execution at the starting point of the query:

```python
vm.registers['IP'] = vm.predicates[('child', 1)]
```

The fetch_execute method cycles through instructions:
- Unification: Matches variables and constants using instructions like GET_VARIABLE and PUT_CONSTANT.
- Predicate Calls: Executes predicates using CALL and PROCEED.
- Backtracking: Restores choice points when a branch fails, enabling exploration of alternative solutions.

For example:
- A query '?- child(X)' succeeds if the child/1 predicate matches a fact or rule. Backtracking (choice_points)
allows exploration of all possible bindings for X.

WAM Workflow
1. Compilation: The Compiler translates Prolog code into WAM instructions.
2. Loading: The WAM instance loads the compiled instructions, constants, and variables.
3. Execution:
	- The machine begins execution at the query’s entry point.
	- Unification matches terms, predicates are invoked, and results are produced.
	- Backtracking explores alternative solutions where necessary.


### Conclusion

This Python implementation provides a very simplified, Pythonic abstraction of the WAM. It replicates
the WAM's core components—registers, memory areas, and instructions—while focusing on unification,
predicate execution, and backtracking. By integrating the Compiler and WAM classes, the system compiles
Prolog programs into executable instructions, simulating the WAM's execution model and enabling
Prolog-like functionality in a structured manner.

The WAM is considered one of the most significant advancements in logic programming implementation.
Its design influenced Prolog compilers, interpreters, and other virtual machines for logic programming
languages. Many modern Prolog implementations, such as SWI-Prolog and SICStus Prolog, still use or
build upon the WAM.

The WAM also served as a foundational idea for other abstract machines in related domains, including
constraint logic programming and theorem proving systems.
