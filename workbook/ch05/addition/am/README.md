
## Exploring Abstract Machines

- *[The SECD Machine](./secd/)*:
  The SECD machine, introduced by Peter Landin, is an abstract stack-based virtual machine for evaluating
  functional languages like Lisp, based on lambda calculus. Its state comprises Stack, Environment, Control,
  and Dump, handling operations like function application, conditionals, and recursion via instructions
  (e.g., `LDC`, `LDF`, `AP`). It supports closures and lexical scoping, serving as a compiler target or
  teaching tool. While simple and expressive, it's not optimised for hardware and lacks robust error handling.

- *[WAM (Warren Abstract Machine)](./wam/)*:
  The WAM is a virtual machine tailored for executing Prolog programs, acting as a compiler back-end
  and runtime environment. It translates Prolog code into an intermediate representation (WAM code)
  for efficient execution, supporting features like backtracking and unification. As an abstract machine,
  it ensures portability across platforms but is specific to Prolog's logical execution model,
  distinguishing it from general-purpose VMs like the JVM.


