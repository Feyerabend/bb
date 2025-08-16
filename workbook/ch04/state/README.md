
## State Machines and VMs 

A state machine-based virtual machine (VM) is an abstract model of a computer that operates by
transitioning between a finite number of states. This approach is conceptually similar to how
a physical computer processes instructions, making a state machine VM a good low-level representation
of a real machine.

A state machine VM, like the one in `new_vm.c`, mirrors the fundamental components and execution
cycle of a physical CPU. This is because both systems are driven by a continuous cycle of fetching,
decoding, and executing instructions.

* *Fetch-Decode-Execute Cycle*: A physical CPU continuously performs the fetch-decode-execute cycle.
  The VM orchestrates this same cycle using its primary state machine. The VM transitions from a
  *`VM_READY`* state to *`VM_FETCHING`* to load an instruction from memory, then to *`VM_DECODING`*
  to identify the instruction, and finally to *`VM_EXECUTING`* to carry it out. This sequential,
  state-driven process is a direct abstraction of the real hardware's operation.

* *Instruction-Level State Machines*: In the `new_vm.c` and `vm_sm.c` examples, each individual
  instruction is also implemented as its own state machine. For instance, the *`OP_LOAD`* instruction
  has states like *`INST_INIT`*, *`INST_OPERAND`*, and *`INST_EXECUTE`*. This multi-state approach
  for a single instruction, especially one with an operand, mimics a microprogrammed CPU design,
  where complex instructions are broken down into a series of simpler micro-operations. A real
  processor might take multiple clock cycles to complete a single instruction, which is analogous
  to how an instruction state machine might need several *`INST_EV_STEP`* events to transition to
  the *`INST_COMPLETE`* state.

* *Explicit State Management*: The VM's explicit state variables (`VMState` and `InstState`) and
  event-driven transitions (`VMEvent`, `InstEvent`) make the entire process transparent and
  deterministic. This contrasts with a traditional, more procedural VM implementation where the
  program counter and other registers are just incremented or modified in a linear flow. The state
  machine approach forces a clear, well-defined progression, which is how a hardware circuit
  operates at its core--each logical gate's output is a function of its current state and input.


### Abstractions in a Simple Programming Language VM

A simple programming language virtual machine, such as the *Python VM* or the *Java Virtual Machine (JVM)*,
is a higher-level abstraction than a state machine VM. While still built on the principles of a
virtual machine, they are intentionally designed to hide the low-level details of the underlying
hardware to provide a more convenient environment for developers.

* *Opcode Complexity*: Instructions in a high-level VM are often much more complex and abstract than
  those in the provided C examples. For instance, a JVM instruction might be something like
  `invokevirtual` to call a method, which involves complex operations like looking up the method
  in a class table and managing the call stack. The state machine VM's opcodes like *`OP_ADD`* and
  *`OP_SUB`* are much closer to the single, atomic operations a CPU performs, like integer addition
  or subtraction.

* *Memory and Stack Management*: High-level VMs include sophisticated features like automatic garbage
  collection and dedicated heap memory for objects, which are completely absent in the state machine
  VM examples. The provided VMs only manage a simple, fixed-size stack and an array for memory.

* *Turing Completeness*: The `new_vm.c` example introduces instructions like `OP_JMP`, `OP_BEZ`, and
  `OP_CALL`. These instructions for branching and function calls are what make the VM "more Turing
  complete," allowing it to perform any computable task. While a high-level VM is also Turing complete,
  it achieves this through more abstract, high-level constructs (e.g., `if-then-else` statements, loops,
  and function calls) that are compiled down to its bytecode, which is then interpreted by the VM.

In summary, a state machine VM's explicit state transitions and multi-step instructions align closely
with the low-level, sequential nature of hardware operation. In contrast, a simple programming language
VM abstracts away these details, providing a higher-level, more user-friendly execution environment that
is further removed from the physical machine's core logic.

