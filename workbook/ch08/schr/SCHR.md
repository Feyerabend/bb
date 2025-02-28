
## Minimal Scheme: Schr

This code implements a simple Lisp-like interpreter in C. It includes fundamental Lisp structures, an evaluator, an environment for symbol lookup, support for functions (both built-in and user-defined), and basic test cases. Below are the key aspects worth noting:

1. Data Structures
	•	LispObject: Represents a Lisp value, which can be a number, symbol, list, or function.
	•	LispList: Represents a linked list (similar to cons cells in Lisp).
	•	LispFunction: Encapsulates functions, supporting both built-in functions and user-defined lambdas.
	•	Environment: Implements a symbol table (scoped environment) where symbols are mapped to values.

2. Memory Management and Object Creation
	•	Functions like make_number(), make_symbol(), and make_list() allocate memory dynamically.
	•	strdup() is used for copying strings to avoid modifying original literals.

3. Evaluation (eval function)
	•	Evaluates different types of Lisp expressions:
	•	Numbers return themselves.
	•	Symbols are looked up in the environment.
	•	Lists are evaluated as function applications or special forms.
	•	Handles special forms like:
	•	quote to return unevaluated expressions.
	•	define to define new variables.
	•	lambda to create functions.
	•	Implements tail call optimisation by using a loop instead of recursion when evaluating functions.

4. Function Application (apply_function function)
	•	Evaluates function arguments before calling the function.
	•	Distinguishes between built-in and user-defined functions.

5. Built-in Functions
	•	Arithmetic: +, -, *
	•	Conditional evaluation: if
	•	Equality check: eq?
	•	Recursive factorial function (builtin_fact), using memoization to store previously computed values.

6. Environment (env_lookup, env_define)
	•	Supports a hierarchical scope system where variables are looked up in enclosing environments.

7. Testing and Debugging
	•	The DEBUG macro is used to print evaluation steps.
	•	The run_tests function contains various test cases for numbers, symbols, addition, quoting, lambda expressions, and factorial.

Key Takeaways
	•	This interpreter captures essential Lisp semantics while keeping the implementation compact.
	•	Tail call optimisation allows efficient recursion handling.
	•	Symbol resolution follows a simple lexical scoping rule.
	•	Memoization optimises recursive computations like factorial.
	•	Error handling is minimal (e.g., missing memory management for garbage collection).

