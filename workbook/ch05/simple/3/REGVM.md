
## REGVM overview

The `REGVM` Python class defines a simple register-based virtual machine (VM) capable
of executing a set of instructions and supporting program control with labels, arithmetic
operations, and stack-based function calls.


### Structure

The `REGVM` class contains:
- *Program Counter (`pc`)*: Tracks the next instruction to execute.
- *Registers (`registers`)*: A dictionary representing dynamically initialized registers.
- *Flags (`flags`)*: A dictionary with:
  - `Z` (Zero flag): Set if the result of an operation is zero.
  - `N` (Negative flag): Set if the result of an operation is negative.
- *Memory (`memory`)*: Stores the program's instructions.
- *Stack (`stack`)*: Supports function calls and returns.
- *Label Map (`label_map`)*: Maps labels to corresponding instruction indices.
- *Program Lines (`program_lines`)*: Stores the raw instructions for program execution.

### Functions

1. `load_program(program)`
   Loads a program (list of instructions) into `program_lines` and maps labels to instruction indices for control flow.

2. `fetch()`
   Retrieves the next instruction to execute. Skips label definitions.

3. `decode_and_execute(instruction)`
   Decodes and executes an instruction, supporting:
   - *Arithmetic Operations*: `MOV`, `ADD`, `SUB`, `MUL`, `DIV`.
   - *Comparison and Branching*: `CMP`, `JMP`, `JL`, `JG`, `JZ`.
   - *Stack Operations*: `CALL`, `RETURN`.
   - *Output*: `PRINT`.
   - *Program Control*: `HALT`.

   Dynamically initializes registers and ensures safe operation handling (e.g., checks for division by zero).

4. `update_flags(result)`
   Updates `Z` and `N` flags based on the result of an operation. Optionally updates an overflow flag for signed arithmetic.

5. `run()`
   Executes instructions in a loop until the program completes or encounters a `HALT` instruction.

6. `_build_label_map()`
   Prepares the `label_map` by associating labels in the program with their corresponding instruction indices.


### Ideas of the REGVM Class

- *Dynamic Register Initialization*: Any named register (e.g., `R1`, `R2`) is created on-the-fly with an initial value of 0 when referenced.
- *Error Handling*: Some safeguards against errors such as division by zero or accessing undefined labels.
- *Extendable Instruction Set*: New operations can be added easily within `decode_and_execute`.
- *Stack for Function Calls*: Supports subroutine calls (`CALL`) and returns (`RETURN`), making it suitable for recursive programs.


### REGVM Mnemonics Overview


#### Data Movement
- `MOV dst src`  
  Moves a value from `src` (register or immediate value) to `dst` (register).  
  Example: `MOV A 5` sets register `A` to `5`.


#### Arithmetic Operations
- `ADD dst src`  
  Adds the value of `src` (register or immediate) to `dst` (register). Updates flags.  
  Example: `ADD A 10` adds `10` to register `A`.

- `SUB dst src`  
  Subtracts the value of `src` (register or immediate) from `dst` (register). Updates flags.  
  Example: `SUB A B` subtracts the value in `B` from `A`.

- `MUL dst src`  
  Multiplies `dst` (register) by `src` (register or immediate). Updates flags.  
  Example: `MUL A B` multiplies the value in `A` by the value in `B`.

- `DIV dst src`  
  Divides `dst` (register) by `src` (register or immediate). Updates flags.  
  Example: `DIV A 2` divides the value in `A` by `2`.  
  Note: Division by zero triggers an error, and the result is set to `0`.


#### Comparison
- `CMP reg1 reg2|val`  
  Compares the value in `reg1` to `reg2` (or immediate value `val`).  
  - Sets `Z` (Zero flag) to `1` if the values are equal, otherwise `0`.  
  Example: `CMP A 0` compares the value in `A` with `0`.


#### Conditional and Unconditional Jumps
- `JMP label`  
  Unconditionally jumps to the instruction at `label`.  
  Example: `JMP loop` transfers execution to the `loop` label.

- `JL label reg1 reg2`  
  Jumps to `label` if the value in `reg1` is less than the value in `reg2`.  
  Example: `JL loop A B` jumps to `loop` if `A < B`.

- `JG label reg1 reg2`  
  Jumps to `label` if the value in `reg1` is greater than the value in `reg2`.  
  Example: `JG loop A B` jumps to `loop` if `A > B`.

- `JZ label`  
  Jumps to `label` if the `Z` (Zero flag) is set to `1`.  
  Example: `JZ end` jumps to `end` if the last comparison was equal.


#### Function Calls and Stack Operations
- `CALL label`  
  Saves the current program counter to the stack and jumps to the instruction at `label`.  
  Example: `CALL subroutine` calls the function at `subroutine`.

- `RETURN`  
  Pops the last program counter from the stack and resumes execution there.  
  Example: `RETURN` exits a function and continues from the caller.


#### Output
- `PRINT reg`  
  Prints the value of `reg` to the console.  
  Example: `PRINT A` displays the value in register `A`.


#### Program Termination
- `HALT`  
  Stops program execution immediately.  
  Example: `HALT` terminates the program.


### Labels
- `label:`  
  Defines a label for program control. Labels act as markers for jumps or calls.  
  Example:  

```assembly
LOOP:
    ADD A 1
    JMP LOOP
```


#### Flags
- Zero Flag (`Z`)  
Set to `1` if the result of the last operation or comparison is zero, otherwise `0`.

- Negative Flag (`N`)  
Set to `1` if the result of the last operation is negative, otherwise `0`.


#### Example: Summing Numbers

```assembly
    MOV A 0       # Initialize sum in A
    MOV B 1       # Initialize counter in B
LOOP:
    ADD A B       # Add B to A
    ADD B 1       # Increment B
    CMP B 6       # Compare B with 6
    JZ END        # If B == 6, exit loop
    JMP LOOP      # Repeat the loop
END:
    PRINT A       # Output the sum
    HALT          # Terminate program
```

This example sums numbers from 1 to 5, storing the result in A and printing it.
