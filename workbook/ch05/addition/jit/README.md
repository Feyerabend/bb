
## HotspotVM

An educational stack-based virtual machine that demonstrates
*Just-In-Time (JIT) compilation* through clear, understandable Python code.

This "HotspotVM" demonstrates the *fundamental workflow* of JIT compilation:

```
profile -> detect hotspots -> compile -> cache -> fast execution
```

While production JITs are vastly more complex (native code generation,
type specialisation, multiple compilation tiers, sophisticated optimisations),
this core loop remains the same.

The key insight: *Don't optimise everything, optimise what matters*.
JIT compilation makes that decision at runtime based on actual behaviour,
not static analysis.


### So What is JIT Compilation?

*Just-In-Time (JIT) compilation* is a runtime optimisation technique
that dramatically improves performance by:
1. *Running code initially as an interpreter* - fast startup, no compilation overhead
2. *Detecting "hot" code* - identifying frequently executed regions (especially loops)
3. *Compiling hot code on-the-fly* - translating it into faster executable form
4. *Switching to compiled code* - executing the optimized version instead of interpreting

This hybrid approach combines the best of both worlds:
interpreted code's flexibility with compiled code's speed.


### Why JIT Matters

Most performance-critical code follows the *90/10 rule*: 90% of execution time is
spent in 10% of the code (usually loops). JIT compilers focus optimisation effort
where it matters most, achieving near-native performance without requiring
ahead-of-time compilation.

*Real-world JIT compilers:*
- *Java* - HotSpot JVM (the original "HotSpot")
- *JavaScript* - V8 (Chrome), SpiderMonkey (Firefox)
- *Python* - PyPy
- *.NET* - CoreCLR/RyuJIT
- *Lua* - LuaJIT


### How HotspotVM Works

#### 1. Dual Execution Modes

Every instruction handler implements *two methods*:

```python
class ArithmeticHandler(InstructionHandler):
    def execute(self, vm, instr):
        ## Interpreter mode - runs immediately
        b, a = vm.stack.pop(), vm.stack.pop()
        vm.stack.append(a + b)
    
    def compile_to_python(self, vm, instr):
        ## JIT mode - generates optimized code
        return [
            "b = stack.pop()",
            "a = stack.pop()",
            "stack.append(a + b)"
        ]
```

#### 2. Hotspot Detection

The VM tracks execution counts per instruction:

```python
self.exec_count[self.pc] += 1
if self.exec_count[self.pc] >= self.hotspot_threshold:
    ## This code is "hot" - time to compile!
```

#### 3. Loop Detection (Key Innovation)

The VM tracks *control flow edges* to detect loops:

```python
## A backward jump indicates a loop
if jump_target < current_pc:
    loop_detected = (jump_target, current_pc)
```

Loops are the *most important target* for JIT compilation because:
- They execute many times (high iteration count)
- Small code size means low compilation overhead
- Huge performance gains when optimized

#### 4. Code Generation

When a hot loop is detected, HotspotVM generates Python code:

```python
# Original bytecode loop:
# LOAD_LOCAL 0
# PUSH 1
# SUB
# STORE_LOCAL 0
# JUMP 0

# Compiled to Python:
def jit_loop():
    stack = self.stack
    locals = self.locals
    while True:
        stack.append(locals[0])
        stack.append(1)
        b, a = stack.pop(), stack.pop()
        stack.append(a - b)
        locals[0] = stack.pop()
        if locals[0] == 0: return
```

This eliminates:
- Per-instruction dispatch overhead
- Instruction decoding
- PC manipulation
- Handler function calls

#### 5. Execution Statistics

HotspotVM tracks detailed metrics showing JIT impact:

```
JIT COMPILATION STATISTICS
=================================
Total compilations:       1
JIT executions:           9,990
Interpreter executions:   57
Avg JIT exec time:        1.23μs
Avg interp exec time:     5.67μs
Speedup factor:           4.61x
=================================
```

### Insights Demonstrated

#### 1. Warmup vs Peak Performance
- *Cold start:* Interpreter runs immediately (no compilation delay)
- *Warmup:* VM profiles execution, identifies hotspots
- *Peak:* Compiled code runs at full speed

This is why benchmarks should measure *sustained* performance, not just first execution.

#### 2. Compilation Threshold Tradeoff
- *Low threshold (3-5):* Compile quickly, but may waste effort on non-hot code
- *High threshold (50+):* Only compile genuinely hot code, but slower warmup
- *Production JITs* often use multiple tiers (quick compile -> optimized compile)

#### 3. What Gets Optimized
*Great for JIT:*
- Tight loops (99% of performance gain)
- Arithmetic-heavy code
- Predictable control flow

*Not worth JIT:*
- One-time initialization code
- I/O operations (already slow)
- Exception handling paths

#### 4. Compilation Overhead
JIT compilation takes time. The code must execute enough
times to *amortize* the compilation cost:

```
Total time = compilation_time + (iterations × execution_time)

Interpreter: 0 + (10000 × 5μs) = 50ms
JIT:         2ms + (10000 × 1μs) = 12ms
```

JIT wins when iterations are high.

### Obvious Limitations

HotspotVM demonstrates JIT *concepts* clearly but simplifies several production concerns:

#### 1. Compiles to Python, Not Native Code
- *Production JITs* generate x86/ARM machine code directly
- *HotspotVM* generates Python -> still interpreted by CPython
- Performance gain comes from eliminating dispatch overhead, not native execution

#### 2. No Type Specialisation
- *Production JITs* generate specialised code for observed types (e.g., integer-only addition)
- *HotspotVM* keeps dynamic typing -> misses major optimisation opportunity

#### 3. No Deoptimisation
- *Production JITs* can "bail out" if assumptions break (e.g., type changes)
- *HotspotVM* assumes compiled code is always valid

#### 4. No Inlining
- *Production JITs* inline function calls into hot code
- *HotspotVM* doesn't handle function boundaries

#### 5. Simple Loop Detection
- *Production JITs* use advanced trace-based compilation or graph-based IR
- *HotspotVM* uses simple backward-jump detection


### Architecture Diagram

```
┌--------------------┐
│    Program Start   │
└--------------------┘
          │
┌-------------------------------------┐
│     Interpreter Mode                │
│  - Execute instructions one-by-one  │
│  - Track execution counts           │
│  - Track control flow edges         │
└-------------------------------------┘
               │
        Hotspot detected?
               │
        Yes ------------- No
         │                │
         │                │
┌------------------┐      │
│  JIT Compiler    │      │
│  - Detect region │      │
│  - Generate code │      │
│  - Cache         │      │
└------------------┘      │
         │                │
         │                │
┌---------------------------------─┐
│     Compiled Code Mode           │
│  - Execute generated Python      │
│  - Direct stack/memory access    │
│  - No dispatch overhead          │
│  - 3-5x faster                   │
└----------------------------------┘
```

### Further Exploration

To deepen understanding:
1. *Add new opcodes* - implement both `execute()` and `compile_to_python()`
2. *Experiment with thresholds* - find optimal compilation trigger
3. *Create different programs* - nested loops, function calls, mixed code
4. *Profile with real tools* - use `cProfile` to see Python-level overhead
5. *Compare trace vs method JIT* - try recording execution paths instead

