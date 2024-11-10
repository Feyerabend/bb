
## TDD

For a more advanced TDD-driven virtual machine, let's expand the concept to include features like registers,
stack frames for function calls, basic I/O, and more advanced control flow (e.g., conditionals, loops).
This will result in a richer, more realistic virtual machine while still keeping it manageable.

Let's design a Register-Based Virtual Machine (RVM) with a small instruction set that can run more complex programs.


### Advanced Features Outline

1.	Registers: A fixed number of general-purpose registers (R0, R1, etc.) for storing values and intermediate results.
2.	Stack Frame: Support for function calls, with local variables and a return address, managed in a stack frame.
3.	Conditionals and Control Flow: JMP_IF, CMP (comparison), and branching instructions to allow conditional execution and loops.
4.	Basic I/O: Simple print or store operations to observe output.
5.	Additional Instructions: Support for additional operations, such as MUL, DIV, MOD, and others as needed.


### Expanded Instruction Set

1.	MOV Rx, N: Move value N to register Rx.
2.	ADD Rx, Ry: Add values in registers Rx and Ry and store the result in Rx.
3.	SUB Rx, Ry: Subtract value in Ry from Rx and store the result in Rx.
4.	MUL, DIV, MOD: Multiplication, division, and modulus.
5.	PUSH Rx: Push the value in Rx onto the stack.
6.	POP Rx: Pop the top of the stack into register Rx.
7.	CALL addr: Call function at address addr, saving the return address.
8.	RET: Return from a function.
9.	JMP addr: Unconditional jump to address addr.
10.	CMP Rx, Ry: Compare values in Rx and Ry, setting status flags (e.g., ZERO, LESS, GREATER).
11.	JMP_IF flag, addr: Jump to addr if flag is true.
12.	PRINT Rx: Print the value in Rx.


### TDD Test Suite

Each of these features will have associated tests, which will grow the complexity and functionality of the VM gradually.
Below are example tests in Python and C.

#### Test 1: Register and MOV Instruction

1.	Description: Check if values can be stored and retrieved in registers using MOV.
2.	Python Test:

```python
def test_mov_register():
    vm = VirtualMachine()
    vm.mov("R0", 42)
    assert vm.get_register("R0") == 42
```

3.	C Test:

```c
void test_mov_register() {
    VM vm;
    vm_init(&vm);
    vm_mov(&vm, R0, 42);
    assert(vm_get_register(&vm, R0) == 42);
}
```


#### Test 2: Arithmetic (ADD, SUB, MUL) on Registers

1.	Description: Test that arithmetic instructions correctly update register values.
2.	Python Test:

```python
def test_arithmetic_registers():
    vm = VirtualMachine()
    vm.mov("R0", 5)
    vm.mov("R1", 10)
    vm.add("R0", "R1")
    assert vm.get_register("R0") == 15  # 5 + 10
    vm.sub("R0", "R1")
    assert vm.get_register("R0") == 5   # 15 - 10
```

3.	C Test:

```c
void test_arithmetic_registers() {
    VM vm;
    vm_init(&vm);
    vm_mov(&vm, R0, 5);
    vm_mov(&vm, R1, 10);
    vm_add(&vm, R0, R1);
    assert(vm_get_register(&vm, R0) == 15);
    vm_sub(&vm, R0, R1);
    assert(vm_get_register(&vm, R0) == 5);
}
```


Test 3: Stack Frame and Function Call (CALL/RET)

1.	Description: Verify that CALL and RET correctly handle function calls and return.
2.	Python Test:

```python
def test_call_ret():
    vm = VirtualMachine()
    program = [
        ("MOV", "R0", 5),
        ("CALL", 5),           # Call function at address 5
        ("MOV", "R1", 10),     # This should execute after RET
        ("HALT",),             # Stops the program
        ("ADD", "R0", "R0"),   # Function doubles R0's value
        ("RET",)               # Return to main program
    ]
    vm.load_program(program)
    vm.execute()
    assert vm.get_register("R0") == 10  # R0 is doubled to 10
    assert vm.get_register("R1") == 10  # R1 is set after the return
```

3.	C Test:

```c
void test_call_ret() {
    VM vm;
    vm_init(&vm);
    Instruction program[] = {
        {MOV, R0, 5},
        {CALL, 5},
        {MOV, R1, 10},
        {HALT},
        {ADD, R0, R0},
        {RET}
    };
    vm_load_program(&vm, program, sizeof(program) / sizeof(Instruction));
    vm_execute(&vm);
    assert(vm_get_register(&vm, R0) == 10);
    assert(vm_get_register(&vm, R1) == 10);
}
```


#### Test 4: Conditional Jump and Comparison (CMP, JMP_IF)

1.	Description: Test CMP and conditional jumps, like JMP_IF, for control flow.
2.	Python Test:

```python
def test_conditional_jump():
    vm = VirtualMachine()
    program = [
        ("MOV", "R0", 5),
        ("MOV", "R1", 10),
        ("CMP", "R0", "R1"),
        ("JMP_IF", "LESS", 6),
        ("MOV", "R0", 0),  # This should be skipped
        ("HALT",),
        ("MOV", "R0", 1)   # This should execute if R0 < R1
    ]
    vm.load_program(program)
    vm.execute()
    assert vm.get_register("R0") == 1  # Ensures conditional jump
```

3.	C Test:

```c
void test_conditional_jump() {
    VM vm;
    vm_init(&vm);
    Instruction program[] = {
        {MOV, R0, 5},
        {MOV, R1, 10},
        {CMP, R0, R1},
        {JMP_IF, LESS, 6},
        {MOV, R0, 0},
        {HALT},
        {MOV, R0, 1}
    };
    vm_load_program(&vm, program, sizeof(program) / sizeof(Instruction));
    vm_execute(&vm);
    assert(vm_get_register(&vm, R0) == 1);
}
```


#### Test 5: Complete Program with Basic I/O (PRINT)

1.	Description: Test a program that performs computations and prints values.
2.	Python Test:

```python
def test_program_with_print():
    vm = VirtualMachine()
    program = [
        ("MOV", "R0", 6),
        ("PUSH", "R0"),
        ("MUL", "R0", "R0"),
        ("PRINT", "R0")
    ]
    vm.load_program(program)
    output = vm.execute()
    assert output == [36]  # Output should contain printed value 36
```

3.	C Test:

```c
void test_program_with_print() {
    VM vm;
    vm_init(&vm);
    Instruction program[] = {
        {MOV, R0, 6},
        {PUSH, R0},
        {MUL, R0, R0},
        {PRINT, R0}
    };
    vm_load_program(&vm, program, sizeof(program) / sizeof(Instruction));
    int output[10];
    int output_len = vm_execute(&vm, output);
    assert(output_len == 1);
    assert(output[0] == 36);
}
```

This set of TDD tests guides you through building an advanced, register-based VM. Each test expands the
functionality and allows for richer programs, demonstrating how TDD can incrementally build a complex virtual machine.
