
## Symbol Tables and Programming Languages

Symbol tables are a concept in the implementation of programming languages, particularly
in the process of parsing and interpreting or compiling a program. A symbol table is a data
structure that holds information about the variables, functions, and other identifiers used
in a program. This information typically includes the name of the symbol, its type, and,
in the case of variables, its value or memory location.

The way symbol tables are structured and used varies significantly between e.g. procedural and
functional programming languages due to the different paradigms they follow.


### Symbol Tables in Procedural Languages

In procedural languages, the symbol table's primary role is to manage variables and functions.
These can be thought of as the "state" of the program (variables) and the "actions" (functions).

- *Variables and Functions as First-Class Citizens*: In procedural languages, variables and
  functions are treated as first-class entities, meaning both can be declared, assigned, and manipulated.

- *Mutable State*: Variables are often mutable, meaning their values can change over time during
  the execution of the program. Functions are typically defined once and called multiple times,
  but they don't change in terms of their structure.

- *Scopes and Lifetime*: Procedural languages use scopes to manage the lifetime of variables and
  function definitions. For example, a variable defined inside a function will only be available
  within that function's scope. This allows for local and global variables, with different
  lifetimes and visibility.


#### Symbol Table

- *Global and Local Scopes*: At the global level, we define variables and functions that are
  accessible across the program. Inside functions, a local scope is often created where local
  variables are stored.

- *Function Definitions and Parameter Bindings*: When a function is defined, it is added to the
  symbol table. When the function is called, the symbol table is updated to bind its parameters
  to the actual arguments passed in the function call.



### Symbol Tables in Functional Languages

Functional languages, on the other hand, place a much greater emphasis on functions as first-class
citizens and immutability. In functional programming, variables are often treated as bindings rather
than mutable states, and functions can be passed around like any other value.

- *Immutability*: In functional languages, once a variable is bound to a value, it cannot be changed.
  This is in contrast to procedural languages, where variables can be reassigned.

- *Functions as First-Class Citizens*: Functions can be assigned to variables, passed as arguments,
  and returned from other functions. They are not just blocks of code, but values in the language.

- *Scopes and Closures*: Functions in functional languages may also *close* over variables. This
  means that a function can remember the environment in which it was created and continue to access
  those variables even after the function has been returned.


#### Symbol Table

- *Bindings*: The symbol table handles bindings rather than assignments. For instance, in functional
  programming, when a function is created, it is stored as a binding in the symbol table, often in a
  manner similar to how variables are stored in procedural languages.

- *Nested Scopes for Function Parameters*: When a function is invoked, its parameters are treated as
  new bindings within a local scope. However, functions can also close over variables in their defining
  scope, allowing for things like lexical scoping and closures.

- *Function Definitions and Higher-Order Functions*: Functions themselves are added to the symbol table
  as values. Higher-order functions (functions that take other functions as parameters or return them)
  are common in functional programming, and symbol tables need to manage these functions as they would
  other values.


###  Core Differences Between Procedural and Functional Symbol Tables

1. Mutability vs. Immutability:
	- *Procedural*: Variables are mutable and can be updated over time. The symbol table reflects this
      with the ability to overwrite values.
	- *Functional*: Variables are immutable. Once a binding is created, it cannot change. The symbol
      table reflects this with a fixed set of bindings for each scope.

2. Function Handling:
	- *Procedural*: Functions are typically defined once and called multiple times. The symbol table
      stores the function definition as a reference, and when a function is called, its parameters
      are bound to the arguments.
	- *Functional*: Functions are first-class citizens and are treated as values. They can be passed
      around like any other value, stored in variables, or returned from other functions. The symbol
      table stores the function itself and manages its parameters as bindings in the scope.

3. Scope Management:
	- *Procedural*: Local scopes are created for each function call. Variables within a function are
      only accessible within that scope.
	- *Functional*: Scopes are also used, but functions may close over variables from outer scopes.
      The symbol table tracks these closures, managing how functions capture their lexical environment.

4. Function Calls:
	- *Procedural*: When a function is called, the symbol table is updated to reflect the local bindings
      for the parameters, and the function body executes within this local scope.
	- *Functional*: Function calls are similar, but there is often the added complexity of handling
      closures and higher-order functions. Functions can be passed around as arguments or returned
      from other functions, meaning the symbol table must handle this dynamism.


The difference lies in how state is managed:
- *Procedural programs* often focus on managing mutable states (variables) across function calls,
  with symbol tables reflecting changes in those states.
- *Functional programs*, on the other hand, focus on immutable bindings and higher-order functions,
  with symbol tables capturing these immutable relationships, closures, and function environments.

Ultimately, the symbol table serves as a bridge between the source code and the runtime, allowing
the interpreter or compiler to track and manage the various entities (variables, functions, etc.)
as the program executes.


### Adding Logical Languages: Similarities and Differences

While there are fundamental similarities in how symbol tables are used in procedural, functional,
and logical languages (i.e., they manage names, values, and scopes), each language paradigm introduces
unique aspects of state management and variable binding.


__Procedural Languages__

In procedural languages like C, Java, or Python, the symbol table maps variables to memory locations
where their values are stored. The symbol table also tracks function names, parameters, and local
variables within different scopes (global, local, etc.).
- *Mutable state*: Variables are mutable, meaning their values can change during execution.
- *Procedural flow*: The program executes in a sequence of steps, and the symbol table must reflect these changes.

__Functional Languages__

Functional languages like Haskell or Lisp emphasize immutability and function closures. The symbol table in functional languages often focuses on managing function bindings, immutable variable bindings, and higher-order functions.
- *Immutability*: Once a variable is bound to a value, it cannot change. The symbol table reflects
  this by holding fixed bindings throughout the scope.
- *Higher-order functions*: Functions are first-class citizens and can be passed as arguments
  or returned as values. The symbol table handles the environment of these functions, ensuring the correct values are available.

__Logical Languages__

In logical languages like *Prolog*, the symbol table manages logical variables, predicates, and facts/rules.
The role of the symbol table is to support unification and backtracking as the logic engine attempts to find
solutions to queries.
- *Unification*: The process of binding variables to values (or other variables) to satisfy a logical predicate.
  The symbol table stores the current set of bindings that result from the unification process.
- *Declarative relationships*: The program defines relationships and rules, and the symbol table tracks these
  definitions to answer queries based on logical inference.



## Suggested Projects

The projects cover everything from simple interpreters to advanced optimisations, helping you to build
a deeper understanding of how symbol tables are used across various paradigms. By working on these
projects, you will get a hands-on understanding of variable binding, scope management, and the distinctive
features of each language's approach to symbol management.



### 1. Procedural Language Projects

#### Simple Interpreter for a Procedural Language

- Goal: Implement a small interpreter for a basic procedural language
  (like a subset of C or Python) that manages variable declarations,
  assignments, function calls, and control flow.

- Tasks:
    - Create a symbol table to manage variable bindings and function scopes.
	- Implement basic arithmetic expressions, loops, and conditional statements.
	- Manage scopes for functions and local/global variables.
	- Implement a simple debugger that allows students to inspect the symbol
      table and step through variable changes.

- Learning Objectives:
	- Understanding how variables are mapped to memory locations.
	- Managing function calls and their local variables.
	- Using the symbol table to track program execution.

#### Variable Tracking Tool for a Procedural Language

- Goal: Build a tool that allows to track variable values
  across a program's execution using a symbol table.

- Tasks:
	- Track changes to variable values during program execution
      (such as within loops or after function calls).
	- Generate a log or visualisation of variable values over time.

- Learning Objectives:
	- Building and managing symbol tables dynamically during runtime.
	- Using the symbol table to optimise variable tracking in programs.


### 2. Functional Language Projects


#### Functional Language Evaluator (Lambda Calculus or Lisp Subset)
	
- Goal: Implement an evaluator for a small functional language (a subset of Lisp or Lambda Calculus).

- Tasks:
	- Create a symbol table to manage variable bindings (as environments) for function applications.
	- Implement basic operations for handling immutable variables and closures.
	- Extend the evaluator to support higher-order functions, such as map, filter, and reduce.
	- Implement tail-call optimisation or closure capture to demonstrate practical uses of environments in a functional setting.

- Learning Objectives:
	- Understanding environments and closures in functional languages.
	- Managing function scopes and variable bindings in a purely functional context.
	- Exploring optimization techniques like tail-call optimization.


#### Debugging Tool for Functional Programs

- Goal: Build a tool that helps students debug functional programs by inspecting their environments.

- Tasks:
	- Implement an environment visualizer that shows function parameters, variable bindings, and closures at each point in the program.
	- Allow users to trace function calls and view the environment at different points in the program.
	- Extend the tool to support stepping through recursive functions and observing changes in function environments.

- Learning Objectives:
	- Understanding how function environments and closures work in a functional language.
    - Debug recursive and higher-order functions.


### 3. Logical Language Projects

If you have a particular interest in logical languages (such as Prolog), as I did in the early '80s,
working on tasks related to symbol tables can be highly rewarding.


#### Prolog-like Interpreter with Symbol Table Management

- Goal: Implement an interpreter for a simple logical language like Prolog, which uses symbol tables
  to manage predicates, facts, and logical variables.

- Tasks:
	- Build a system to store and query facts and rules using a symbol table.
	- Implement unification and backtracking, tracking variable bindings during the search for solutions.
	- Implement a mechanism to check for variable bindings and to display the state of the symbol table as queries are evaluated.
	- Extend the interpreter with features like cut (!) for pruning search space and assert/retract for dynamically adding or removing facts.

- Learning Objectives:
	- Understand how logical variables and predicates are managed using a symbol table.
	- Learn how unification and backtracking work in logical languages.
	- Explore how the symbol table evolves through the process of logical inference and querying.

#### Visualizing Unification and Backtracking

- Goal: Build a tool that visualizes the process of unification and backtracking in a Prolog-like system.

- Tasks:
	- Implement the unification algorithm that binds variables and matches terms.
	- Use the symbol table to manage variable bindings and visualize the current state after each unification step.
	- Allow users to input queries and visually step through the backtracking process as different bindings are tried.

- Learning Objectives:
	- Visualize the relationship between variables and terms during unification.
	- Understand how Prolog resolves queries and performs backtracking.
	- Examine the impact of backtracking on variable bindings and the symbol table.

#### Implementing Constraints in a Logic-based System

- Goal: Create a logic programming environment where students can implement and query
  constraints (such as CSPs - Constraint Satisfaction Problems).

- Tasks:
	- Implement a constraint solver using a logic-based language with symbolic representations of variables.
	- Use the symbol table to manage variable domains and their constraints.
	- Implement a basic constraint propagation algorithm that updates the symbol table as constraints are enforced.
	- Allow students to query the system with a set of constraints and examine the symbol table to see how the domains of variables are updated.

- Learning Objectives:
	- Learn how logical variables can be constrained.
	- Explore how the symbol table is used to manage the relationships and domains of variables in constraint problems.
	- Implement basic constraint propagation techniques.


### 4. Cross-Paradigm Project: Symbol Table Comparison

#### Multi-Paradigm Language Interpreter

- Goal: Create a small language that supports procedural, functional, and logical paradigms,
  and implement a unified symbol table that works across all three paradigms.

- Tasks:
	- Design a simple language that includes basic constructs from all three paradigms
      (e.g. variables, functions, rules, predicates).
	- Implement a symbol table that supports each paradigm’s variable and function management.
	- Allow for programs that combine constructs from procedural, functional, and logical
      paradigms and see how the symbol table changes as the program runs.
	- Compare and contrast how the symbol table is used in each paradigm (e.g. mutable vs.
      immutable variables, unification, scoping rules).

- Learning Objectives:
	- Understand how different paradigms interact with the symbol table.
	- Compare the differences and similarities in symbol table management across procedural,
      functional, and logical programming.
	- Get hands-on experience in building an interpreter for a multi-paradigm language.

### 5. Advanced Logical Language Projects

#### Optimizing Symbol Table for Logic-based Reasoning

- Goal: Implement an optimisation layer over the Prolog-style system where the symbol table
  is used to minimise redundant variable bindings and reduce search space.

- Tasks:
	- Implement a cache system for variable bindings (memoization) to avoid redundant unification attempts.
	- Optimise the backtracking search by pruning irrelevant paths based on the state of the symbol table.
	- Test the optimized system with complex queries and large knowledge bases.

- Learning Objectives:
	- Explore optimization strategies for logical programming languages.
	- Learn how the symbol table can be used to enhance performance in logic-based systems.
	- Study the tradeoffs between memory usage and computational efficiency in backtracking systems.
