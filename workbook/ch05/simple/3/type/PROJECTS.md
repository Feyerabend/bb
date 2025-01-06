
## Project Title: Building and Extending a TAC Interpreter

### Goal

The goal of this project is to develop a deeper understanding of Three-Address Code (TAC),
intermediate representations, dynamic and static typing, and how parsers interact with runtime
environments. By working on this project, you will expand and refine the provided TACParser
into a fully functional interpreter capable of handling more complex programs, including
type safety, custom data structures, and advanced control flow mechanisms.


### Exercises and Extensions

__1. Implement Type Coercion__

*Modify the interpreter to handle implicit type coercion where appropriate.*

Task: Extend the parser and symbol table to allow mixed-type arithmetic operations, such as int + float, with results conforming to a standard type (e.g., float). Update the symbol table to reflect these coerced types.

Expected Outcome:
- Enhanced type system with explicit rules for type coercion.
- Ability to handle mixed-type expressions like x = 5 + 3.14 with x inferred as float.


__2. Add Support for Strings__

*Extend the TAC language and interpreter to support string types and operations.*

Task:
- Define a string type in the symbol table.
- Allow string assignment (e.g., greeting = "Hello").
- Support concatenation (full = first + " " + last).
- Extend the print command to output strings.

Expected Outcome:
- Programs can declare and manipulate strings.
- Strings integrate seamlessly with the existing type system.


__3. Introduce Function Support__

*Add the ability to define and call functions in the TAC language.*

Task:
-	Extend the syntax to include function definitions and calls, e.g.,

```
func add(a, b):
t1 = a + b
return t1
x = add(10, 20)
```

- Implement a function table and a call stack for managing function calls and returns.

Expected Outcome:
- Support for reusable logic encapsulated in functions.
- The runtime environment handles function calls, arguments, and return values.


__4. Add Static Type Checking__

*Introduce static type checking to the TAC language.*

Task:
- Implement a static analyzer that checks for type mismatches before runtime.
- Report errors for invalid operations, such as x = "text" + 10.
- Ensure type declarations (e.g., int x, float y) align with usage.

Expected Outcome:
- Programs with type mismatches are rejected with clear error messages.
- A static type-checking phase runs before execution.


__5. Visualize Control Flow__

*Build a tool to visualize the control flow of TAC programs, including labels, jumps, and branches.*

Task:
- Parse the TAC program into a control flow graph (CFG).
- Represent the CFG as a graph using a visualization library (e.g. Graphviz or Matplotlib, or use JavaScript).
- Highlight control flow paths dynamically based on execution.

Expected Outcome:
- Visual representations of the control flow, aiding debugging and analysis.
- Ability to step through execution paths interactively.


__6. Extend Arrays with Dynamic Sizing__

*Modify the TAC interpreter to allow dynamically sized arrays.*

Task:
- Introduce dynamic array initialization (e.g., int_array = int[x], where x is a runtime value).
- Implement bounds checking to ensure safe access and assignments.

Expected Outcome:
- Arrays can be initialized with sizes determined at runtime.
- Access beyond declared sizes results in meaningful runtime errors.


__7. Build a Debugger for the Interpreter__

*Create a debugging tool for TAC programs.*

Task:
- Add commands like break, step, and inspect.
- Allow the user to set breakpoints and inspect the symbol table and current execution state.

Expected Outcome:
- A simple command-line debugger for TAC programs, improving usability for complex debugging.


### Project Deliverables

By completing these exercises, you will have:
1. A fully functional TAC interpreter with enhanced features like type coercion, string support, and function handling.
2. Tools for static type checking and debugging.
3. Visualization capabilities to represent the structure and flow of TAC programs.
4. Extended language support for real-world use cases.

Conclusion

Through this project, you will not only refine your knowledge of intermediate representations and dynamic/static type systems but also enhance your problem-solving skills by extending a functional parser. The expected outcome is a versatile TAC interpreter capable of handling diverse scenarios, complete with robust debugging and analysis tools.
