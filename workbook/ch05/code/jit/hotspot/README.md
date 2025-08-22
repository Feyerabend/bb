
## JITs

JIT (Just-In-Time) compilation is a runtime optimisation technique. Instead of
interpreting every instruction, the VM monitors which parts of the program are
executed frequently (hot spots). When a section is executed often, the VM generates
more efficient code for it on the fly. Future executions of that section then
run the compiled code, bypassing the interpreter.


### How HotspotVM implements JIT

HotspotVM is a stack-based virtual machine. Instructions are executed by handler
classes, each providing:
- `execute(vm, operands)`: runs the instruction in the interpreter.
- `compile(vm, operands)`: produces Python code for that instruction.

During execution, the VM counts how often each instruction runs. When an instruction
exceeds `hotspot_threshold`, the VM tries to detect a region of instructions
suitable for compilation. Non-compilable instructions (like jumps or I/O) terminate
the region. If a region is long enough, Python code is generated for it, wrapped
into a function, and stored in `jit_cache`.

When the program counter reaches a compiled region, the VM calls the function
instead of interpreting. The function manipulates the VM’s stack, memory, and
locals directly and returns the next program counter.


### Hotspot compilation example

In a loop like “sum 1..10,” the first few iterations are interpreted. After the
threshold, the VM generates a function that performs the loop’s operations directly
on the stack and locals. Subsequent iterations execute the compiled function,
which is faster than interpreting each instruction.

The VM is stack-based, which makes instruction compilation straightforward. Each
handler knows how to interpret an instruction and how to emit Python code. Hotspot
detection ensures only frequently executed regions are compiled. Rarely executed
instructions remain interpreted, avoiding unnecessary compilation overhead.

