
## Overview

This code implements a simple stack-based virtual machine (VM) in C, which can interpret and execute bytecode instructions, including arithmetic operations, function calls, and basic flow control. It supports recursive function calls, as illustrated with a factorial calculation.

### Key Components

1.	Definitions and Structures:
	•	STACK_SIZE and LOCALS_SIZE define the size limits of the stack and local variable space.
	•	Opcode enum defines the supported instructions (e.g., ADD, PUSH, CALL).
	•	Frame structure represents a function call’s execution context, including a stack, local variables, and return data.
	•	FrameStack and VM structures manage a stack of frames and the VM’s state, including the program counter (pc), code to execute, and a debug flag.

2.	VM Functions:
	•	Memory Management: pushFrame and popFrame manage stack frames for function calls and returns.
	•	Error Handling: error reports issues and terminates the VM if there’s an error (e.g., stack overflow).
	•	Stack Operations: push, pop, store, and load handle stack data and access local variables.
	•	Function Call Support: transferStackToLocals and transferStackToReturnValue transfer data between frames for argument passing and return values.

3.	Main Execution Loop (run function):
	•	The main loop executes instructions by fetching each opcode and performing the associated operation. Some highlights:
	•	CALL: Creates a new frame, stores the current pc as the return address, and optionally transfers arguments.
	•	RET: Ends the function call by transferring any return value to the calling frame and restoring the return address.
	•	CRET: Pushes the return value onto the stack.
	•	Arithmetic (e.g., ADD, SUB, MUL): Operate on stack data.
	•	Flow Control (e.g., JZ): Enables conditional branching.

4.	Main Program (Factorial Calculation):
	•	The main function initializes a code array containing bytecode to compute factorial(5) recursively:
	•	PUSH and CALL push arguments and initiate the recursive factorial function.
	•	The factorial function uses RET and CRET for recursion and return values.

The factorial bytecode computation illustrates the VM’s capability to handle recursion, local variables, and stack-based arithmetic, producing the factorial of 5 as the output (PRINT: 120).
