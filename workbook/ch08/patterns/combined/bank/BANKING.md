
## Banking

Bank switching originated in the early days of computing when memory was limited. Systems could not
store large amounts of data or programs in RAM due to hardware constraints. To overcome this, developers
used bank switching to split available memory into banks or chunks. By switching between banks, the
system could access more memory than what was physically available at one time. This was crucial in
early microprocessors and embedded systems, where hardware limitations meant that running large
applications required manual memory management.

Bank switching refers to the ability to selectively map different blocks of memory into a system’s
address space at different times. This allows more memory to be effectively utilized than the system
can access in a single operation. In this context, "bank" means a segment of memory, and switching
means choosing which memory block (bank) is currently active. The Program Counter (PC) management
was critical because, when switching banks, the system had to remember where it was in the program,
hence the need for mechanisms like call stacks and context switching. Otherwise we got a
"jeopardized" corrupted memory ..

Then why was bank switching necessary? Early computers had very small RAM capacities (often just a
few kilobytes). Developers had to make the most out of limited memory. Instead of increasing physical
memory (which was expensive and hard to upgrade), systems used bank switching to simulate larger
memory. This made it possible to run larger programs than the hardware could directly support.
Bank switching also allowed for multi-programming where different parts of a program or different
programs could run at the same time by switching between memory banks.

Today, bank switching is rarely used in general-purpose computing but remains important in embedded
systems, microcontrollers, and the revival of game consoles (especially older ones like the Commodore
64 or early arcade machines). It has evolved into memory management techniques like paging and
segmentation in modern operating systems, which allow systems to handle much larger memory spaces
by dynamically managing which part of memory is active.

Solutions Over Time:
- Memory Paging: Modern operating systems use paging (or virtual memory) to dynamically allocate
  memory from a larger pool, rather than manually switching banks.
- Virtual Memory: Systems employ virtual memory to map memory addresses to different physical
  locations, providing the illusion of more memory than the system physically has.
- Bank Switching in Embedded Systems: Bank switching is still used in embedded systems and
  microcontrollers to simulate large memory areas, enabling complex programs on small, constrained
  devices.

In summary, bank switching was a critical solution to memory limitations in early computing, and
although it’s less relevant in modern high-memory systems, it remains a key concept in memory
management for embedded and resource-constrained systems.


#### Components

1. Shared RAM Communication Area:
   Reserve a fixed block in RAM for inter-bank communication. This holds:  
   - Function ID: Index or identifier of the target function.  
   - Parameters: Input data for the function.  
   - Return Address: Address to resume execution after returning.  
   - Return Bank: Original bank number to restore after processing.  

2. Dispatcher Routine in Each Bank:  
   Each ROM bank includes a dispatcher at a fixed entry point (e.g., `0xFFFE`). Its tasks:  
   - Read the Function ID from shared RAM.  
   - Jump to the corresponding function via a Jump Table (mapping IDs to addresses).  
   - Handle bank switching back using the Return Bank and Return Address.  

3. Bank Switching Protocol:  
   - Calling Bank (A):  
     1. Disable interrupts to prevent race conditions.  
     2. Populate the shared RAM with parameters, Function ID, Return Address, and Return Bank.  
     3. Switch to the target bank (B) by writing its ID to the bank-switching address (e.g., `0x0000`).  
     4. Jump to the dispatcher entry point in Bank B.  

   - Target Bank (B):  
     1. Dispatcher reads the Function ID and parameters.  
     2. Executes the target function via its Jump Table.  
     3. Writes results to shared RAM (if needed).  
     4. Restores the original bank (A) and jumps to the Return Address.  


#### Example Flow

```assembly
; Bank A: Prepare and call a function in Bank B
LDA #FUNC_ID       ; Function identifier
STA SHARED_FUNC_ID
LDA #RETURN_BANK   ; Bank A's ID
STA SHARED_RET_BANK
LDA #<RETURN_ADDR  ; Low byte of return address
STA SHARED_RET_ADDR
LDA #>RETURN_ADDR  ; High byte
STA SHARED_RET_ADDR+1
LDA #BANK_B_ID     ; Switch to Bank B
STA BANK_SWITCH_ADDR
JMP DISPATCHER     ; Jump to Bank B's dispatcher

; Bank B's Dispatcher:
LDX SHARED_FUNC_ID
JMP (JUMP_TABLE,X) ; Jump to function via table

; After processing, Bank B switches back:
LDA SHARED_RET_BANK
STA BANK_SWITCH_ADDR
JMP (SHARED_RET_ADDR) ; Return to Bank A
```


#### Considerations

- Reentrancy/Interrupts: Disable interrupts during setup to protect shared data.  
- Jump Tables: Each bank has a static table mapping IDs to function addresses.  
- Nested Calls: Use a stack-like structure in RAM for multiple pending calls.  
- Efficiency: Overhead from copying data and switching banks is acceptable given hardware limits.  


#### Alternatives

- Mailbox System: Banks poll shared RAM mailboxes for requests (simpler but less efficient).  
- Fixed Common Area: A small, unbanked ROM section with shared switching code (if hardware allows).  

This approach ensures safe cross-bank communication without stack corruption,
leveraging shared RAM for parameters and return context.


### Simulation

This Python program simulates a system that handles multiple "banks" of code, each bank containing
a set of functions. The goal is to model the behavior of a system that switches between different
banks (such as in a hardware system with memory banks) and executes functions from those banks while
sharing data between them. The program is designed to mimic a simple execution model of functions
interacting across banks, where each function can read and write shared parameters and log its actions.

#### Components

1. SharedRAM (Shared Memory Simulation):
- This class simulates the shared memory space that is used by the different banks to store parameters,
  function call results, and logs.
- Memory: The shared memory (self.memory) stores values that are used across banks.
- Call Stack: The self.call_stack keeps track of function calls, storing the return context (such as
  the current bank and a simulated return address).
- Parameter Stack: The self.param_stack is used to push and pop function arguments.
- Log Output: The self.output_buffer collects log messages generated during the execution of functions.

2. Bank:
- Represents a bank of functions (like a ROM bank in older hardware systems).
- Functions: The self.functions dictionary maps function IDs to the actual function implementations.
- Registration: Functions are registered with unique IDs using the register decorator. This decorator
  allows functions to be added to the bank’s functions dictionary by their function ID.

3. BankManager (Bank Switching and Execution):
- The BankManager handles the execution flow of the system, including switching between banks and
  managing the shared memory.
- Adding Banks: The add_bank method adds a bank to the system. Each bank is an instance of the Bank class.
- Calling Functions: The call method simulates switching from the current bank to a target bank,
  executing a function in the target bank, and returning control to the original bank. It also handles
  pushing and popping function parameters in the shared memory.
- Returning from Functions: The ret method handles returning control to the calling bank after a
  function has executed.
- Logging: During execution, logs are written to the SharedRAM to capture function execution details.

4. Simulation Function:
- The run_simulation function simulates the execution of a program across multiple banks. It sets up
  the banks, calls the functions in the MAIN bank, and prints out logs of the execution.
- It starts by calling the main function in the MAIN bank. This function in turn calls functions in
  other banks, such as math operations in the MATH bank and string operations in the STRINGS bank.
- After the program finishes execution, the log output and the final state of the shared memory
  (including the current bank, parameter stack, and call stack depth) are printed.


__Example Execution Flow__

1. The run_simulation function is called, which first creates and adds three banks: MAIN, MATH, and STRINGS.
2. The program starts execution in the MAIN bank. The main function within the MAIN bank logs the start of the program.
3. The main function calls the add function from the MATH bank, passing two parameters (5 and 3). The add
   function computes the sum (8) and returns the result to the MAIN bank.
4. Similarly, the main function calls the multiply function from the MATH bank with parameters 4 and 6,
   computing the product (24) and returning the result to the MAIN bank.
5. The main function also calls the concat function from the STRINGS bank, passing two strings
   ("Hello" and "World"). The concat function concatenates the strings and returns the result ("HelloWorld").
6. Lastly, the main function calls the reverse function from the STRINGS bank with the string "Python",
   which is reversed to "nohtyP".
7. The execution completes, and the log of all operations is printed out, showing the results of the function calls.

Logs:
- The program logs messages each time a function is called or completed, capturing the parameters,
  operations performed, and results. These logs are stored in the SharedRAM and printed at the end
  of the simulation.

Final State:
- After the simulation completes, the program prints the current state of the system, including:
- The current bank being executed (MAIN in this case).
- The contents of the parameter stack (which holds results from the executed functions).
- The depth of the call stack (indicating how many function calls were made and returned from).

Example Output:

```
MAIN: Starting program
ADD: 5 + 3 = 8
MULT: 4 * 6 = 24
CONCAT: 'Hello' + 'World' = 'HelloWorld'
REVERSE: 'Python' -> 'nohtyP'
MAIN: Program complete

Execution Log:
MAIN: Starting program
ADD: 5 + 3 = 8
MULT: 4 * 6 = 24
CONCAT: 'Hello' + 'World' = 'HelloWorld'
REVERSE: 'Python' -> 'nohtyP'
MAIN: Program complete

Final State:
Current Bank: MAIN
Param Stack: [8, 24, 'HelloWorld', 'nohtyP']
Call Stack Depth: 0
```

#### Summary

This program simulates a system where different banks contain functions, and function
calls are handled by switching between these banks while maintaining a shared memory
space for data transfer. It mimics a bank-switched ROM system, where each bank has its
own set of functions, and the manager coordinates the execution across these banks.

