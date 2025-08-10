
## SMT Tools

Here we will present only a formal SMT solver, the Z3. 
It's purpose is to automatically decide satisfiability of
formulas in certain logics (often first-order logic with
theories like arithmetic, bit-vectors, arrays).

An SMT (Satisfiability Modulo Theories) solver is a program that
determines whether a logical formula is satisfiable, while also
reasoning about specialised domains. It extends SAT solving with
built-in "theory" knowledge, making it powerful for verification,
constraint solving, and symbolic reasoning.

SAT solving is the process of determining whether a Boolean
formula--built from variables that can be true or false and
connected with logic particulars (AND, OR, NOT)--can be made
true by some assignment of values to its variables.
A SAT solver automates this search efficiently, and is the
foundation upon which SMT solvers add richer reasoning about
numbers, data structures, and other theories.

Z3 is fully automated, you give it a formula, it tries to return sat/unsat/unknown.
Logical constraints is given in a standard language (SMT-LIB) or via an API.
It's fast, automation-friendly, great for model checking, program verification,
symbolic execution, but it also have limitations: it works in decidable fragments,
but doesn’t directly express higher-order logic or dependent types.
