
## Two Different Approaches

We start with a more conceptual approach to the "machine",
rather than actual hardware.


### The State Machine VM: An Illustration of Microcoding Principles

This [State Machine VM](./state/) provides a high-level, clear example
of the logic that underlies the execution of instructions within a CPU,
a concept often implemented through *microcode*.

* *What:* This VM's architecture is built as a series of nested state machines.
  There is a top-level VM state machine that governs the overall fetch-decode-execute
  cycle, and a separate, smaller state machine for each individual instruction.
  This is a direct parallel to how a complex instruction in a real CPU is executed.

* *How:* When the VM is in the `VM_EXECUTING` state, it hands control to an `InstructionSM`
  (Instruction State Machine). This instruction state machine then progresses through
  its own states (e.g., `INST_INIT`, `INST_OPERAND`, `INST_EXECUTE`). The VM doesn't 
  just perform the entire operation at once. Instead, it breaks it down into fundamental,
  sequential steps. For instance, an `OP_LOAD` instruction isn't a single action;
  it's a sequence of states that first fetches the operand and then pushes it onto the stack.

* *Why:* This approach is a pedagogical tool for visualising a *microcoded CPU design*.
  In real hardware, a complex instruction like `ADD` might be implemented by a sequence
  of simple control signals (the microcode) that are fetched from a small, internal
  ROM or PLA (Programmable Logic Array) within the CPU. The State Machine VM illustrates
  this exact principle: a complex macro-instruction is reduced to a series of simpler,
  atomic, and observable *micro-operations*, each represented by a state transition.
  This makes the VM's internal workings highly transparent and easy to trace.


### The SAP VM: An Illustration of CPU-like Architecture and Addressing

This [SAP VM](./sap/) virtual machine illustrates the foundational design
of a classic Central Processing Unit (CPU), complete with registers and
various memory addressing modes.

* *What:* The SAP VM is a simplified model of a register-based computer. It features
  a central `cpu_t` struct with dedicated registers for the accumulator, program counter,
  stack pointer, and index register. Its instruction set is designed to work with
  different ways of accessing data in memory.

* *How:* The VM's instruction word is encoded to contain not only the operation to
  perform (`opcode_t`) but also a specific *addressing mode* (`addressing_mode_t`).
  This allows a single instruction like `OP_LDA` (Load Accumulator) to behave differently
  depending on how the operand is interpreted. For example, `LDA #42` (immediate mode)
  loads the number 42 directly, while `LDA $100` (direct mode) loads the value stored
  at memory address 100.

* *Why:* This design serves as a powerful illustration for understanding how real-world
  CPUs function. It demonstrates the importance of registers for fast, local data manipulation
  and the flexibility provided by different addressing modes to efficiently access data
  from various locations in memory (immediate values, direct locations, or calculated
  addresses via an index register).

