
## Dispatch

Dispatch, at its core, is a mechanism for selecting and invoking a specific function
or behaviour based on some criteria, such as input values, types, patterns, or runtime
conditions. It’s about routing a request to the appropriate handler, enabling flexibility
and modularity in code. Conceptually, dispatch is like a switchboard operator in an old
telephone exchange: given an incoming call (input), the operator connects it to the
right line (function) based on predefined rules or identifiers.

Dispatch is central to many programming paradigms:
- *Polymorphism* in object-oriented programming (OOP) dispatches method calls based
  on object types.
- *Event handling* dispatches actions based on events (e.g., user clicks).
- *Command processing* dispatches operations based on input strings or tokens.

The criteria for dispatch can vary widely—types, values, patterns, or even external
states—making it a versatile concept. Dispatching techniques differ in how they map
inputs to handlers, their flexibility, and their performance characteristics.

We have already made ourselves acquainted with a very simple dispatch in the
virtual machines, where either in Python we use `if-then-else`, or in C often
the `switch-case`.

In Python, a typical dispatch might look like this:

```python
if opcode == "ADD":
    do_add()
elif opcode == "SUB":
    do_sub()
elif opcode == "MUL":
    do_mul()
else:
    unknown_opcode()
```

Each branch corresponds to a different operation depending on the value of opcode.

In C, a similar dispatch is typically done using a switch-case:

```c
switch (opcode) {
    case OP_ADD:
        do_add();
        break;
    case OP_SUB:
        do_sub();
        break;
    case OP_MUL:
        do_mul();
        break;
    default:
        unknown_opcode();
        break;
}
```

But there are actually many ways of handling even such simple cases, and these
might be very beneficial to know by the programmer.

For example, in Python, instead of using multiple `if-elif-else` branches, we can use
a dictionary that maps opcodes to functions:

```python
dispatch_table = {
    "ADD": do_add,
    "SUB": do_sub,
    "MUL": do_mul,
}

# perform dispatch
operation = dispatch_table.get(opcode, unknown_opcode)
operation()
```

This technique avoids the growing cost of many if-elif-else comparisons, making
the code cleaner and faster, especially when the number of cases grows.

Similarly, in C, we can replace switch-case with an array of function pointers:

```c
typedef void (*operation_func)();

operation_func dispatch_table[] = {
    [OP_ADD] = do_add,
    [OP_SUB] = do_sub,
    [OP_MUL] = do_mul,
};

if (opcode >= 0 && opcode < sizeof(dispatch_table)/sizeof(dispatch_table[0])
       && dispatch_table[opcode]) {
    dispatch_table[opcode]();
} else {
    unknown_opcode();
}
```

Here, the opcode directly indexes into a table of function pointers. This is much faster
than a large switch-case if there are many operations, and the cost becomes essentially
constant time.

Thus, even for very simple dispatch mechanisms, it is useful for the programmer
to know alternative techniques, as different methods may offer better performance,
better readability, or better flexibility depending on the situation.


#### 1. Continuation-Passing Style (CPS) Dispatch

- *Concept*: Instead of directly invoking a function, [CPS](./../continue/) dispatch
  passes control to a continuation--a function that represents "what to do next."
  Dispatch occurs by selecting the appropriate continuation based on input, enabling
  asynchronous or chained execution. This is common in functional programming and
  event-driven systems.

- *How It Differs*: Unlike direct function calls, CPS defers execution and explicitly
  manages control flow, making it ideal for non-blocking or stateful dispatching.
  It’s less about immediate resolution and more about orchestrating a sequence of operations.

- *Python Example*:
     ```python
     def dispatch_operation(op, a, b, continuation):
         if op == "add":
             continuation(a + b)
         elif op == "subtract":
             continuation(a - b)
         else:
             continuation(None)

     def print_result(result):
         print(f"Result: {result}")

     # with continuation
     dispatch_operation("add", 2, 3, print_result)  # Output: Result: 5
     dispatch_operation("subtract", 5, 2, lambda x: print(f"Doubled: {x * 2}"))  # Output: Doubled: 6
     ```
- *C Equivalent*: Use function pointers as continuations, passing them as arguments to a
  dispatcher function. Common in asynchronous C libraries (e.g., libuv).

- *Pros*: Flexible for asynchronous systems, composable, decouples caller from result handling.

- *Cons*: Complex to reason about, overhead from function passing, less intuitive for simple tasks.

- *Use Case*: Event loops, asynchronous programming, or functional pipelines.


#### 2. Rule-Based Dispatch (Expert System Style)

- *Concept*: Dispatch is driven by a set of declarative rules, often stored in a knowledge base,
  where conditions are evaluated to select a handler. This mimics expert systems, where rules are
  matched against input data to determine the action.

- *How It Differs*: Unlike fixed mappings (e.g., dictionaries), rule-based dispatch evaluates dynamic
  conditions, often involving logical inference or prioritisation. It’s more declarative than procedural,
  focusing on "what" rather than "how."

- *Python Example*:
     ```python
     from dataclasses import dataclass
     from typing import Callable

     @dataclass
     class Rule:
         condition: Callable[[dict], bool]
         action: Callable[[dict], str]

     def evaluate_rules(input_data: dict, rules: list[Rule]) -> str:
         for rule in rules:
             if rule.condition(input_data):
                 return rule.action(input_data)
         return "No matching rule"

     rules = [
         Rule(
             condition=lambda d: d["op"] == "add" and d["x"] > 0,
             action=lambda d: f"Sum: {d['x'] + d['y']}"
         ),
         Rule(
             condition=lambda d: d["op"] == "subtract",
             action=lambda d: f"Difference: {d['x'] - d['y']}"
         )
     ]

     data = {"op": "add", "x": 2, "y": 3}
     print(evaluate_rules(data, rules))  # Output: Sum: 5
     data = {"op": "subtract", "x": 5, "y": 2}
     print(evaluate_rules(data, rules))  # Output: Difference: 3
     ```

- *C Equivalent*: Implement a rule table with function pointers for conditions
  and actions, iterating over rules in a loop. Used in embedded systems or
  decision engines.

- *Pros*: Highly flexible, supports complex logic, easy to extend with new rules.

- *Cons*: Slower due to condition evaluation, harder to optimise, rule conflicts
  need resolution.

- *Use Case*: Business rule engines, diagnostic systems, or configuration-driven
  applications.


#### 3. Aspect-Oriented Dispatch

- *Concept*: Dispatch is triggered by cross-cutting concerns (aspects) like logging,
  validation, or error handling, which are applied before or after the main function.
  The dispatcher selects and applies these aspects based on metadata or context.

- *How It Differs*: Instead of dispatching to a single handler, it composes multiple
  behaviours around a core function, focusing on separation of concerns. It’s less about
  choosing a function and more about augmenting execution.

- *Python Example*:
     ```python
     from functools import wraps
     from typing import Callable, Dict

     def aspect_dispatch(aspects: Dict[str, Callable]):
         def decorator(func: Callable):
             @wraps(func)
             def wrapper(*args, *kwargs):
                 context = {"args": args, "kwargs": kwargs}
                 for aspect_name, aspect_func in aspects.items():
                     aspect_func(context, "before")
                 result = func(*args, *kwargs)
                 for aspect_name, aspect_func in aspects.items():
                     aspect_func(context, "after", result)
                 return result
             return wrapper
         return decorator

     def logging_aspect(context, stage, result=None):
         if stage == "before":
             print(f"Logging: Calling with {context['args']}")
         else:
             print(f"Logging: Result = {result}")

     def validation_aspect(context, stage, result=None):
         if stage == "before" and any(x < 0 for x in context["args"]):
             raise ValueError("Negative numbers not allowed")

     @aspect_dispatch({"log": logging_aspect, "validate": validation_aspect})
     def add(a, b):
         return a + b

     print(add(2, 3))  # Output: Logging: Calling with (2, 3), Logging: Result = 5, 5
     ```

- *C Equivalent*: Use function pointers for aspects, manually calling them
  before/after the main function. Common in middleware or embedded systems with hooks.

- *Pros*: Modularises cross-cutting concerns, reusable aspects, clean core logic.

- *Cons*: Overhead from multiple calls, complex debugging, requires careful design.

- *Use Case*: Middleware in web frameworks, logging/tracing systems, or transaction management.


#### 4. Probabilistic Dispatch

- *Concept*: Dispatch is based on probabilities or random selection, where handlers
  are chosen according to weights or distributions. This is used in systems requiring
  stochastic behaviour, like simulations or load balancing.

- *How It Differs*: Unlike deterministic dispatch, it introduces randomness, making
  outcomes non-predictable. It’s less about exact matches and more about statistical
  selection.

- *Python Example*:
     ```python
     import random
     from typing import Callable, Dict

     def probabilistic_dispatch(handlers: Dict[Callable, float]):
         total_weight = sum(handlers.values())
         normalized = {func: weight / total_weight for func, weight in handlers.items()}
         return random.choices(list(normalized.keys()), list(normalized.values()), k=1)[0]

     def fast_add(a, b): return a + b  # 80% chance
     def slow_add(a, b): return a + b + 0.001  # 20% chance

     handlers = {fast_add: 0.8, slow_add: 0.2}
     for _ in range(3):
         func = probabilistic_dispatch(handlers)
         print(func(2, 3))  # Output: e.g., 5, 5.001, 5 (varies randomly)
     ```

- *C Equivalent*: Use `rand()` with a weighted selection algorithm (e.g.,
  cumulative probability table). Common in game development or randomised algorithms.

- *Pros*: Enables stochastic behaviour, useful for testing or simulations.

- *Cons*: Non-deterministic, harder to debug, requires careful weight tuning.

- *Use Case*: A/B testing, randomised algorithms, or load balancing.


#### 5. Introspective Dispatch

- *Concept*: Dispatch is driven by inspecting the runtime properties of objects,
  such as their attributes, methods, or metadata, rather than predefined mappings
  or types. This leverages reflection or introspection.

- *How It Differs*: It’s dynamic and adaptive, relying on the structure or state of
  inputs at runtime, unlike static type-based or value-based dispatch. It's more
  exploratory, suited for loosely coupled systems.

- *Python Example*:
     ```python
     class Processor:
         def process_add(self, a, b): return a + b
         def process_subtract(self, a, b): return a - b

     def introspective_dispatch(obj, operation: str, *args):
         method_name = f"process_{operation}"
         if hasattr(obj, method_name):
             return getattr(obj, method_name)(*args)
         raise AttributeError(f"No method for {operation}")

     processor = Processor()
     print(introspective_dispatch(processor, "add", 2, 3))  # Output: 5
     print(introspective_dispatch(processor, "subtract", 5, 2))  # Output: 3
     ```

- *C Equivalent*: Limited in C due to lack of reflection, but can be approximated with
  a naming convention and a function pointer table searched by string. Rare, but used
  in plugin systems.

- *Pros*: Highly dynamic, supports extensible systems, reduces explicit registration.

- *Cons*: Slower due to introspection, error-prone if naming conventions are inconsistent.

- *Use Case*: Plugin architectures, dynamic APIs, or scripting engines.



### Why These Flavours Are Distinct
- *CPS Dispatch*: Focuses on control flow and deferred execution,
  unlike direct function invocation in traditional dispatch.
- *Rule-Based Dispatch*: Emphasises declarative logic and inference,
  contrasting with procedural mappings like dictionaries.
- *Aspect-Oriented Dispatch*: Augments functions with orthogonal
  behaviours, rather than selecting a single handler.
- *Probabilistic Dispatch*: Introduces randomness, breaking from
  deterministic routing.
- *Introspective Dispatch*: Relies on runtime object inspection,
  avoiding predefined mappings or types.

### Notes on C

In C, these flavours are less common due to the language’s static
nature and lack of introspection or dynamic typing.
However:
- *CPS*: Implemented with function pointers and explicit state passing (e.g., in event-driven libraries).
- *Rule-Based*: Uses arrays of structs with condition/action pointers, common in embedded systems.
- *Aspect-Oriented*: Simulated with middleware-like function chains or hooks.
- *Probabilistic*: Achieved with `rand()` and weighted tables, used in simulations.
- *Introspective*: Rare, approximated with string-based lookups or plugin systems.

