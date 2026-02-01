
## Code Generation: RISC VM Simulation

The RISC-V-like virtual machine in this example executes *assembly-like instructions*,
manipulating registers and control flow to simulate a CPU's behavior.

- Registers: The virtual machine has 32 registers (x0 to x31), with the first register
  (x0) being hardcoded to always hold the value 0 (this is a typical feature in many
  CPU architectures, like RISC-V).
- Program Counter (PC): The program counter keeps track of the current instruction that
  is being executed. It is incremented after each instruction, unless modified by a jump
  instruction (like BEQ or J).
- Running Flag: The running flag indicates whether the virtual machine is still executing.
  If set to False, the VM halts.
- Labels: The labels dictionary maps instruction labels (used for jumps and branches) to
  (implicit) line numbers in the program, enabling the VM to handle jumps and branches correctly.


#### Execution of the Program

The method execute() runs the program line by line, using a loop to fetch and execute
instructions until the program ends or the HALT instruction is encountered.
- The program consists of a list of strings representing assembly instructions.
- Each instruction is parsed and executed by calling the appropriate handler based on the
  opcode (ADDI, MUL, BEQ, etc.).

#### Opcode Handlers

Each type of instruction (opcode) is mapped to a handler function. The get_opcode_handler()
method retrieves the appropriate handler based on the opcode. The following instructions
are implemented:
- ADDI: Adds an immediate value (constant) to a register's value. For example,
  ADDI x1, x0, 5 adds 5 to register x0 (which is 0), storing the result in x1.
- SLE: Performs a comparison check to see if a value in a register is greater
  than 0. It stores 1 in the destination register if true, otherwise 0. For
  example, SLE x4, x1, x0 checks if x1 > 0 and stores the result in x4.
- BEQ: Compares two registers and, if they are equal, jumps to a label. The
  program counter (pc) is set to the label's position. For example, BEQ x4, x0,
  end checks if x4 == x0 and, if so, jumps to the end label.
- MUL: Multiplies the values in two registers and stores the result in a destination
  register. For example, MUL x2, x2, x1 multiplies x2 and x1, storing the result in x2.
- SUB: Subtracts an immediate value (constant) from the value in a register.
  For example, SUB x1, x1, 1 subtracts 1 from the value in register x1.
- J: Performs an unconditional jump to a label. For example, J loop jumps to the
  loop label, updating the program counter to the corresponding instruction.
- PRINT: Prints the value of a register. For example, PRINT x2 prints the value
  stored in register x2.
- HALT: Stops the execution of the program.

#### Print Registers (Debugging)

For debugging purposes, the print_registers() method prints the contents of all registers,
which can help track the VM's state during execution.


### Concepts Connected to the VM

*Instruction Set Architecture (ISA)*: This virtual machine simulates a subset of the
RISC-V ISA, which is a reduced instruction set architecture (RISA) focusing on simple
instructions that are efficient to execute.

*Registers*: The VM uses registers (x0 to x31) to store intermediate and final results
during the execution of instructions. Registers are the fastest storage locations available
to the CPU (or VM in this case).

*Control Flow*: The VM handles conditional jumps (BEQ, SLE) and unconditional jumps (J),
allowing for complex program logic like loops and conditional branching, which is fundamental
in control flow management.

*Program Counter (PC)*: The program counter (pc) controls the flow of execution, keeping
track of the next instruction to be executed. It is updated sequentially unless a jump
instruction alters its value.

*Label Handling*: The preprocessing of labels allows the VM to map human-readable labels
to memory locations (or instruction indices), which is essential for handling jumps and
branches.

*Memory Model*: While this VM does not explicitly use memory (aside from the registers),
in more complex VMs, memory management would be a key component to store variables, arrays,
and objects.


### Conclusion

This simple RISC-V-like virtual machine is a simple model for understanding how low-level
code execution works. It demonstrates some basic principles such as instruction decoding,
register manipulation, program flow control, and label-based jumps.

