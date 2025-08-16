
## Simulate a CPU with Logic Gates and Microcode


### 1. Logic Gates

*Concept Description*:
Logic gates are the fundamental building blocks of digital circuits, performing
basic boolean operations on binary inputs (0 or 1). The code implements basic gates
(AND, OR, XOR, NOT, NAND, NOR) which are used to construct more complex circuits
like adders and ALUs (Arithmetic Logic Units).

- *AND Gate*: Outputs true only if both inputs are true.
- *OR Gate*: Outputs true if at least one input is true.
- *XOR Gate*: Outputs true if exactly one input is true.
- *NOT Gate*: Inverts the input (true to false, false to true).
- *NAND Gate*: Inverts the AND gate output.
- *NOR Gate*: Inverts the OR gate output.

*Where to Follow in the Code*:
- File: `cpu.c`
- Functions: `and_gate`, `or_gate`, `xor_gate`, `not_gate`, `nand_gate`, `nor_gate`
- Example Code:
  ```c
  bool and_gate(bool a, bool b) {
      return a && b;
  }
  bool xor_gate(bool a, bool b) {
      return a != b;
  }
  ```
  These functions implement the boolean logic directly using C's logical operators.

- Test Cases: In `test_cpu.c`, the `test_basic_gates` function verifies the behavior:
  ```c
  TEST_ASSERT(and_gate(true, true) == true, "AND: 1,1 = 1");
  TEST_ASSERT(xor_gate(true, false) == true, "XOR: 1,0 = 1");
  ```

*Example*:
- AND Gate: `and_gate(true, false)` → `false` (1 AND 0 = 0).
- XOR Gate: `xor_gate(true, true)` → `false` (1 XOR 1 = 0).
- NOT Gate: `not_gate(true)` → `false` (NOT 1 = 0).

*Follow-Up Projects*:
1. *Build a Logic Gate Simulator*: Create a program that allows users to input binary
   values and select a gate to see the output. Extend it to combine gates (e.g., AND
   followed by OR).
2. *Logic Gate Visualiser*: Use a graphics library (e.g., SDL or SFML) to visually
   represent logic gates and their connections, showing real-time output changes.
3. *Truth Table Generator*: Write a program that generates truth tables for all basic
   gates and allows users to define custom gate combinations.



### 2. Microcode

*Concept Description*:
Microcode is a low-level set of instructions that controls the CPU's internal operations
to execute higher-level machine instructions (opcodes). It acts as a bridge between
hardware and software, defining how each instruction (e.g., ADD, SUB) is broken down into
micro-operations like fetching data, performing ALU operations, or updating registers.

In this code, microcode is implemented as a lookup table (`microcode_rom`) where each
opcode maps to a sequence of `MicroInstruction`s, each containing `ControlSignals` to
manage CPU components (e.g., ALU, registers, memory).

*Where to Follow in the Code*:
- File: `cpu.h`
  - Struct: `ControlSignals` defines signals like `alu_enable`, `reg_write_enable`, `pc_increment`.
  - Struct: `MicroInstruction` pairs control signals with a description.
  ```c
  typedef struct {
      bool reg_write_enable;
      uint8_t reg_write_select;
      uint8_t alu_operation;
      bool pc_increment;
      // .. other signals
  } ControlSignals;

  typedef struct {
      ControlSignals signals;
      const char* description;
  } MicroInstruction;
  ```

- File: `cpu.c`
  - Function: `init_microcode` initializes the `microcode_rom` array with microinstructions
    for each opcode.
  - Example for ADD (opcode 0x00):
    ```c
    microcode_rom[0x00][0] = (MicroInstruction){
        .signals = {
            .alu_enable = true,
            .alu_operation = 0,
            .reg_read_a_select = 0,
            .reg_read_b_select = 1,
            .pc_increment = true,
            .use_alu_result = true
        },
        .description = "ADD: Compute R0 + R1"
    };
    microcode_rom[0x00][1] = (MicroInstruction){
        .signals = {
            .reg_write_enable = true,
            .reg_write_select = 0,
            .end_instruction = true,
            .use_alu_result = true
        },
        .description = "ADD: Store result in R0"
    };
    ```
    This defines a two-step process:
    (1) Compute R0 + R1 using the ALU,
    (2) Store the result in R0.

- File: `test_cpu.c`
  - Function: `test_microcode_initialization` tests microcode execution for
    ADD, LOAD, and HALT instructions.
    ```c
    vm.registers[0] = 15;
    vm.registers[1] = 7;
    vm.memory[0] = OP_ADD;
    vm.memory[1] = OP_HALT;
    run_vm(&vm);
    TEST_ASSERT(vm.registers[0] == 22, "Microcode: ADD instruction (R0 = 15 + 7 = 22)");
    ```

*Example*:
- ADD Instruction:
  - Step 1: ALU computes `R0 + R1`, sets flags, increments PC.
  - Step 2: Stores ALU result in `R0`, ends instruction.
  - If `R0 = 15`, `R1 = 7`, then after execution, `R0 = 22`.

*Follow-Up Projects*:
1. *Extend Microcode for New Instructions*: Add support for new opcodes (e.g., multiplication
   or division) by defining new microcode sequences in `microcode_rom`.
2. *Microcode Debugger*: Build a tool that prints the control signals and state changes for
   each microinstruction during execution, enhancing the debugging output in `execute_microinstruction`.
3. *Microcode Optimiser*: Analyze the microcode sequences and propose optimizations
   (e.g., combining steps to reduce cycles for certain instructions).



### 3. Virtual Machine (VM)

*Concept Description*:
The virtual machine (VM) emulates a simple CPU with registers, memory, a program counter (PC)
and an ALU. It executes instructions by fetching opcodes from memory, decoding them via microcode,
and executing the corresponding microinstructions. The VM supports operations like arithmetic
(ADD, SUB), bitwise operations (AND, OR, XOR, NOT), shifts (SHL, SHR), and memory operations
(LOAD, STORE).

*Where to Follow in the Code*:
- File: `cpu.h`
  - Struct: `VM` defines the CPU state:
    ```c
    typedef struct {
        uint8_t registers[4];
        uint8_t memory[256];
        uint8_t pc;
        ALUFlags flags;
        bool running;
        uint8_t current_instruction;
        uint8_t micro_step;
        uint8_t fetched_byte;
        ALUResult alu_result;
        uint8_t memory_data;
    } VM;
    ```

- File: `cpu.c`
  - Function: `init_vm` initializes the VM with zeroed registers, memory, and flags.
    ```c
    void init_vm(VM *vm) {
        memset(vm->registers, 0, sizeof(vm->registers));
        memset(vm->memory, 0, sizeof(vm->memory));
        vm->pc = 0;
        vm->flags = (ALUFlags){0};
        vm->running = true;
        // ...
    }
    ```
  - Function: `fetch` retrieves the next instruction from memory and increments the PC.
    ```c
    uint8_t fetch(VM *vm) {
        return vm->memory[vm->pc++];
    }
    ```
  - Function: `execute_microinstruction` handles the execution of a single microinstruction,
    updating registers, memory, or flags based on control signals.
  - Function: `run_vm` runs the VM, fetching instructions and executing microcode until
    halted or a cycle limit is reached.
    ```c
    void run_vm(VM *vm) {
        int cycle = 0;
        while (vm->running && cycle < 1000) {
            if (vm->micro_step == 0) {
                vm->current_instruction = fetch(vm);
                // ...
            }
            uint8_t opcode_index = (vm->current_instruction == 0xFF) ? 0x0F : vm->current_instruction;
            const MicroInstruction *micro = &microcode_rom[opcode_index][vm->micro_step];
            execute_microinstruction(vm, micro);
            // ...
        }
    }
    ```

- File: `test_cpu.c`
  - Functions like `test_vm_add_instruction`, `test_vm_sub_instruction`, and
    `test_vm_load_instruction` test specific VM instructions.
    ```c
    void test_vm_add_instruction() {
        VM vm;
        init_vm(&vm);
        vm.registers[0] = 15;
        vm.registers[1] = 7;
        vm.memory[0] = OP_ADD;
        vm.memory[1] = OP_HALT;
        run_vm(&vm);
        TEST_ASSERT(vm.registers[0] == 22, "VM ADD: R0 = 15 + 7 = 22");
    }
    ```

*Example*:
- ADD Instruction Execution:
  - Initialize VM: `R0 = 15`, `R1 = 7`, `memory[0] = OP_ADD`, `memory[1] = OP_HALT`.
  - Run VM: Fetches `OP_ADD`, executes microcode (ALU computes 15 + 7 = 22, stores in `R0`), then halts.
  - Result: `R0 = 22`, flags updated (e.g., zero = false, carry = false).

*Follow-Up Projects*:
1. *Instruction Set Expansion*: Add new instructions like multiplication or conditional
   jumps (already defined as `OP_JMP`, `OP_JZ`, `OP_JC` but not fully implemented).
   Implement their microcode and test cases.
2. *Assembler for VM*: Write a simple assembler that converts mnemonic instructions
   (e.g., "ADD R0, R1") into binary opcodes and loads them into VM memory.
3. *VM Debugger*: Create a debugger that allows stepping through instructions, inspecting
   registers, memory, and flags, and setting breakpoints.
4. *Extend Memory and Registers*: Increase the VM's memory size or number of registers and
   update the microcode to handle them, testing scalability.
5. *Simulate a Real Program*: Write a program for the VM that performs a complex task
   (e.g., calculating Fibonacci numbers) and verify its correctness.



### Additional Notes

- *Integration of Concepts*: The code demonstrates how logic gates build adders
  (`half_adder`, `full_adder`, `ripple_carry_adder_8bit`), which are used in the
  ALU (`enhanced_alu`), which is controlled by microcode to execute VM instructions
  (`run_vm`).
- *Testing Rigor*: The `test_cpu.c` file provides comprehensive tests for each layer
  (gates, adders, ALU, VM), ensuring correctness. Students can study the `TEST_ASSERT`
  macro and test functions to learn unit testing.
- *Cycle Limit*: The VM includes a cycle limit (`cycle < 1000`) to prevent infinite
  loops, tested in `test_edge_cases`.



### Suggested Learning Path for Students

1. *Start with Logic Gates*:
   - Understand boolean logic and implement additional gates (e.g., XNOR).
   - Project: Build a truth table generator or a gate simulator.

2. *Explore Adders and ALU*:
   - Study how `half_adder` and `full_adder` combine to form `ripple_carry_adder_8bit`.
   - Extend the ALU to support new operations (e.g., multiplication).

3. *Dive into Microcode*:
   - Trace the microcode for `OP_ADD` and `OP_LOAD` in `init_microcode`.
   - Add microcode for unimplemented instructions like `OP_JMP` or `OP_STORE`.

4. *Master the VM*:
   - Run the VM with simple programs (e.g., add two numbers, load from memory).
   - Implement a debugger or assembler to interact with the VM.

5. *Advanced Projects*:
   - Simulate a stack-based VM or implement interrupts.
   - Port the VM to a real microcontroller or FPGA for hardware execution.
