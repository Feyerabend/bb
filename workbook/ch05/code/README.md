
## Exploring Virtual Machines and Compilers

- *[Bootstrapping](./bootstrap/)*:
  Bootstrapping is the process of developing a programming language or system using the language
  itself. It typically begins with a minimal prototype compiler or interpreter, often written in
  a different, well-established language (e.g., C). Once this initial version exists, it is used
  to compile or run a more complete implementation written in the target language. Through successive
  iterations, the system “pulls itself up by its own bootstraps” until it becomes fully self-hosting.

- *[JIT Compilation in HotspotVM](./jit/)*:
  HotspotVM is a stack-based virtual machine that uses Just-In-Time (JIT) compilation to optimise
  frequently executed code (hotspots) by translating them into Python code. It employs a region-based
  JIT approach, compiling sequences of instructions (e.g., `PUSH`, `ADD`) when their execution
  count exceeds a threshold (default: 3). Key features include dynamic compilation, hotspot detection,
  and optimisations like inlining and loop unrolling. While it improves performance over interpretation,
  it’s limited to Python code generation, not native machine code, and excludes complex operations
  like jumps and I/O from compilation. The VMProfiler aids debugging by tracking execution metrics.

- *[PL/0](./pl0/)*:
  PL/0, designed by Niklaus Wirth, is a minimalistic teaching language resembling Pascal, used to teach
  compiler concepts. It supports variable declarations, basic arithmetic, control structures (if, while,
  begin-end), and procedures. PL/0 programs compile to stack-based P-Code instructions (e.g., `LIT`,
  `LOD`, `OPR`) for execution on a virtual machine. Its simplicity makes it ideal for learning lexical
  analysis, parsing, and code generation. The project includes an interpreter and a basic compiler, with
  a task to enhance the compiler to support more PL/0 features.

- *[Minimal Lisp Interpreters in C](./sch/)*:
  These documents detail the evolution of minimal Lisp (Scheme-like) interpreters in C, focusing on core
  data structures (S-expressions, lists, atoms) and components like evaluation (`eval`), environments,
  and special forms (`quote`, `define`, `lambda`). Initial versions use manual memory allocation, while
  later ones introduce object pools and mark-and-sweep garbage collection. Tail recursion optimisation
  is attempted via `eval_tail_recursive`. The interpreters support basic arithmetic, conditionals, and
  list operations, with suggestions for enhancements like better error handling and compilation.

- *[The SECD Machine](./secd/)*:
  The SECD machine, introduced by Peter Landin, is an abstract stack-based virtual machine for evaluating
  functional languages like Lisp, based on lambda calculus. Its state comprises Stack, Environment, Control,
  and Dump, handling operations like function application, conditionals, and recursion via instructions
  (e.g., `LDC`, `LDF`, `AP`). It supports closures and lexical scoping, serving as a compiler target or
  teaching tool. While simple and expressive, it’s not optimised for hardware and lacks robust error handling.

- *[Tail Recursion](./tail/)*:
  Tail recursion occurs when a recursive call is the final operation in a function, enabling tail call
  optimisation (TCO) to reuse stack frames and prevent stack overflow. This makes tail-recursive functions
  as space-efficient as loops. The document references a Scheme-like interpreter implementation in the
  `sch` folder, emphasising TCO’s role in supporting deep recursion in functional programming.

- *[Vtable and Projects](./vtable/)*:
  Vtables enable dynamic polymorphism in object-oriented programming by mapping method calls to their
  implementations at runtime. The document outlines projects to enhance a basic compiler, ranging from
  easy tasks (e.g., adding integer arithmetic, multiple print statements) to advanced ones (e.g., supporting
  multiple classes, virtual method overriding, exception handling). These projects teach concepts like
  parsing, code generation, inheritance, and file I/O, with open-ended options like designing a DSL
  or building a REPL.

- *[WAM (Warren Abstract Machine)](./wam/)*:
  The WAM is a virtual machine tailored for executing Prolog programs, acting as a compiler back-end
  and runtime environment. It translates Prolog code into an intermediate representation (WAM code)
  for efficient execution, supporting features like backtracking and unification. As an abstract machine,
  it ensures portability across platforms but is specific to Prolog’s logical execution model,
  distinguishing it from general-purpose VMs like the JVM.


