
## JIT Compilation in a "HotspotVM"

Just-In-Time (JIT) compilation is a runtime optimisation technique that improves the performance
of interpreted code by compiling frequently executed parts into faster code (usually native machine code)
during program execution. Unlike ahead-of-time (AOT) compilation, JIT compilers can make optimisation
decisions based on actual runtime behavior.

### Core Concepts

1. *Dynamic Compilation*  
   Code is translated at runtime, often from bytecode or another intermediate representation into
   native code (or in simpler systems--into another higher-performance representation).

2. *Hotspot Detection*  
   The system identifies frequently executed code regions ("hotspots")--typically loops, inner
   functions or repeatedly called basic blocks--and prioritises them for compilation.

3. *Common Optimisation Techniques*  
   - Inlining  
   - Loop unrolling / loop invariant code motion  
   - Constant folding & propagation  
   - Dead code elimination  
   - Type specialization (especially important in dynamically typed languages)  
   - Profile-guided optimizations (branch prediction hints, etc.)

4. *Trade-offs*  
   *Advantages*  
   - Much better peak performance than pure interpretation  
   - Runtime profiling allows better optimization decisions than static compilation  
   - Same portable code can be specialized for the current hardware/OS

   *Disadvantages*  
   - Initial compilation overhead (warm-up time)  
   - Increased memory consumption (code cache + profiling data)  
   - Significant implementation complexity

5. *Well-known Production JITs*  
   - Java -> HotSpot JVM (the original "HotSpot")  
   - JavaScript -> V8 (TurboFan), SpiderMonkey (IonMonkey)  
   - Python -> PyPy  
   - .NET -> RyuJIT / CoreCLR  
   - Lua -> LuaJIT (very successful trace-based JIT)

6. *Main JIT Strategies*  
   - *Method-based JIT* — whole functions/methods (most common: HotSpot, .NET, V8 non-optimized tier)  
   - *Trace-based JIT* — records and compiles hot execution paths (LuaJIT, some JavaScript engines, older Dalvik)  
   - *Region-based / loop JIT* — focuses on compiling natural loop bodies or other hot linear regions (used in HotspotVM, some research VMs, parts of GraalVM)


### "HotspotVM" Implementation

The "HotspotVM" is an educational stack-based virtual machine that implements a
*very simple region-based JIT compiler* written in Python.

It executes instructions defined in the `OpCode` enum using a classic interpreter
loop and a handler-based architecture.

Each instruction group is handled by a dedicated handler class that implements two methods:
- `execute(vm, instr)` — normal interpreter execution  
- `compile_to_python(vm, instr)` — generates equivalent Python source code lines

*How the JIT works in HotspotVM:*

1. Counts executions per instruction address (`exec_count`)
2. When any instruction reaches the `hotspot_threshold` (default: 3)
3. Tries to find a straight-line code region forward from current PC  
   (stops at control-flow instructions or after ~30 instructions)
4. If region is considered long enough (≥5 instructions),  
   generates Python code for all instructions in that region
5. Wraps the generated code into a function using `exec()`
6. Caches the function
7. On next visits to the region start -> directly calls the compiled function

The compiled function works directly on `vm.stack`, `vm.memory` and `vm.locals`
and returns the PC value after the region.

*Example:* tight counting/summing loops become significantly faster after compilation.


### Current Limitations

- *Very naive region selection* — only straight-line code without any control flow  
- *Control-flow instructions (JUMP, CALL/RET, conditional branches)* are *not* compiled  
  -> JIT regions always end before any branch  
- *Generates Python bytecode* — not native machine code  
  -> performance gain is limited compared to real native JITs  
- *No deoptimization* — once compiled, region is never invalidated  
- *No type specialization* — no runtime type profiling or polymorphic inline caches  
- *I/O and some complex instructions* are deliberately not compiled  
- *No on-stack replacement* (OSR) — loops are not switched mid-execution


### Summary

HotspotVM demonstrates the basic idea of *region-based JIT compilation* in a very simple,
understandable way. It trades off realism for clarity and is best understood as an *educational prototype*
rather than a production-grade JIT system, naturally.

The current implementation shows the fundamental workflow of:
```
hotspot detection -> region selection -> code generation -> caching -> fast-path execution
```
while clearly showing the difficulties that arise when trying to handle control flow, dynamic types, and native code generation.
It serves well as a teaching tool and as a foundation for experimenting with more advanced JIT concepts.
