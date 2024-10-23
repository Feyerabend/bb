
### *VM4 Overview*

VM4 is a simple stack-based virtual machine (VM) that simulates a processor capable of executing basic arithmetic and control-flow operations. It operates on a *stack* to perform operations and uses *frames* for managing local variables and return addresses in a function call.

Key components of VM4:

1. *Opcodes*: 
   - The VM recognizes several opcodes (operation codes) like `ADD`, `MUL`, `PUSH`, `POP`, `CALL`, `RET`, etc. Each of these opcodes corresponds to a specific action, such as pushing a value onto the stack, adding numbers, or calling a function.
   
2. *Stack*:
   - Each frame has a stack (`frame->stack`) where operands are stored temporarily while performing calculations.
   - Operations like `PUSH`, `POP`, `ADD`, and `MUL` work directly with values on the stack.

3. *Frames*:
   - Each frame (`Frame` struct) represents a function context, holding a stack, local variables, the return address, and a return value.
   - A *FrameStack* manages these frames and allows the VM to handle function calls and returns.

4. *Program Counter (PC)*:
   - The VM has a program counter (`pc`) that points to the current instruction in the code.
   - Instructions are fetched, and the program counter increments to the next one, allowing sequential execution.

5. *Basic Flow*:
   - The main execution loop in `run()` fetches opcodes from the `code` array, decodes them, and executes the corresponding operation.
   - When an opcode like `HALT` is encountered, execution stops.
   - The VM can also call functions (`CALLV`, `CALL`), return from them (`RET`, `RETV`), and handle local variables via the stack.

6. *Memory Layout*:
   - `stack[]`: Holds temporary values for arithmetic or function arguments.
   - `locals[]`: Holds local variables in the current frame, accessed by the `LD` (load) and `ST` (store) instructions.
