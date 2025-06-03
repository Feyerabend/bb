
## An Extensible Arithmetical Parser and Evaluator

Project Layout:
```
arithmetic_parser/
├── __init__.py               # Package initialization
├── api/                      # API Layer (Public Contract)
│   ├── __init__.py
│   └── parser_api.py         # Main public interface
├── core/                     # Library Layer (Core Implementation)
│   ├── __init__.py
│   ├── tokenizer.py          # String to tokens conversion
│   ├── evaluator.py          # Expression evaluation engine
│   └── exceptions.py         # Custom exception classes
├── components/               # Module/Component Layer
│   ├── __init__.py
│   ├── tokens.py             # Token definitions and types
│   ├── validators.py         # Expression validation logic
│   ├── operators/            # Operator handling (extensible)
│   │   ├── __init__.py
│   │   ├── base.py           # Base operator classes
│   │   ├── arithmetic.py     # +, -, *, / operators
│   │   └── advanced.py       # Power, modulo, etc. (future)
│   └── functions/            # Mathematical functions (extensible)
│       ├── __init__.py
│       ├── base.py           # Base function classes
│       ├── basic.py          # sqrt, abs, etc.
│       └── trigonometric.py  # sin, cos, tan, etc. (future)
├── extensions/               # Extension points for new features
│   ├── __init__.py
│   ├── variables.py          # Variable support (future)
│   ├── constants.py          # Mathematical constants (future)
│   └── custom_operators.py   # User-defined operators (future)
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── helpers.py            # Common helper functions
│   └── formatters.py         # Output formatting utilities
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_tokenizer.py
│   ├── test_evaluator.py
│   └── test_operators.py
├── examples/                   # Usage examples
│   ├── __init__.py
│   ├── basic_usage.py
│   ├── advanced_features.py
│   └── extension_examples.py
└── main.py                     # Entry point / demonstration
```

This structure demonstrates:
1. Clear separation of architectural layers
2. Extensibility through plugin-like structure
3. Proper Python package organization
4. Separation of concerns
5. Easy testing and maintenance


This set of Python files constitutes an *Extensible Arithmetic Parser*, designed to evaluate mathematical
expressions. Its core strength lies in its modular and extensible architecture, allowing for easy addition
of new operators and functions without modifying the core parsing logic.


### Architectural Overview

If we focus at the main features: The parser follows a clear separation of concerns, broken
down into several key components.

1.  *`ArithmeticParserAPI` (parser_api.py)*:
    * This is the main public interface for the parser.
    * It orchestrates the entire parsing and evaluation process, acting as a facade to the internal components.
    * It initializes the `Tokenizer` and `Evaluator` with registries for operators and functions.
    * Crucially, it provides methods to `add_operator` and `add_function`, enabling the extension of the parser's
      capabilities at runtime.
    * It also includes `parse` for evaluation and `validate` for checking expression validity.

2.  *`Tokenizer` (tokenizer.py)*:
    * Responsible for converting a raw string arithmetic expression into a sequence of meaningful `Token` objects.
    * It identifies numbers, operators, parentheses, commas, and function names.
    * It handles potential unary minus and validates basic number formats.
    * It relies on the `OperatorRegistry` and `FunctionRegistry` to identify known operators and functions.

3.  *`Evaluator` (evaluator.py)*:
    * Takes the list of tokens from the `Tokenizer` and computes the final numerical result.
    * It employs the *Shunting-Yard algorithm* to convert infix expressions (standard mathematical notation)
      into postfix (Reverse Polish Notation).
    * It then evaluates the postfix expression using a stack-based approach.
    * It interacts with the `OperatorRegistry` and `FunctionRegistry` to apply the correct logic for each operator
      and function.

4.  *Components (components/operators and components/functions directories)*:
    * This is where the extensibility shines.
    * *`BaseFunction` (base.py)*: An abstract base class for all functions, defining a `name`, `arity`
      (number of arguments), and an abstract `apply` method.
    * *`FunctionRegistry` (base.py)*: A central repository for registering and retrieving `BaseFunction`
      instances.
    * *`basic.py` (components/functions)*: Provides concrete implementations of common mathematical
      functions like `sqrt`, `abs`, `pow`, `max`, and `min`, and populates a `FunctionRegistry` with them.
    * *`BinaryOperator` and `UnaryOperator` (base.py)*: Abstract base classes for operators, defining
      properties like `symbol`, `precedence`, and `associativity`, and an `apply` method.
    * *`OperatorRegistry` (base.py)*: A central repository for registering and retrieving `BaseOperator`
      instances.
    * *`arithmetic.py` (components/operators)*: Provides concrete implementations of standard arithmetic
      operators (`+`, `-`, `*`, `/`) and populates an `OperatorRegistry`.

5.  *`exceptions.py`*:
    * Defines a hierarchy of custom exceptions (e.g., `ParserError`, `TokenizationError`, `EvaluationError`)
      for robust error handling throughout the parsing process.


### How to Use

The `main.py` file demonstrates the usage and extensibility of the parser.

1.  *Basic Usage*:
    * First, import `ArithmeticParserAPI`.
    * Create an instance of `ArithmeticParserAPI`: `parser = ArithmeticParserAPI()`.
    * Then, use the `parse()` method to evaluate an expression: `result = parser.parse("2 + 3 * 4")`.

    ```python
    from arithmetic_parser import ArithmeticParserAPI

    parser = ArithmeticParserAPI()
    expression = "2 + 3 * 4"
    result = parser.parse(expression)
    print(f"'{expression}' = {result}") # Output: '2 + 3 * 4' = 14.0
    ```

2.  *Extending with New Operators*:
    * To add a new operator, create a class that inherits from `BinaryOperator` (for two operands)
      or `UnaryOperator` (for one operand).
    * Define its `symbol`, `precedence`, and `associativity` in the constructor.
    * Implement the `apply` method with the desired logic.
    * Add the new operator to the parser instance using `parser.add_operator()`.

    ```python
    from arithmetic_parser.components.operators.base import BinaryOperator
    import math

    class PowerOperator(BinaryOperator): #
        def __init__(self): #
            super().__init__("*", precedence=3, associativity="right") #
        
        def apply(self, base: float, exponent: float) -> float: #
            return math.pow(base, exponent) #

    parser = ArithmeticParserAPI()
    parser.add_operator(PowerOperator()) #
    result = parser.parse("2 * 3")
    print(f"'2 * 3' = {result}") # Output: '2 * 3' = 8.0
    ```

3.  *Extending with New Functions*:
    * To add a new function, create a class that inherits from `BaseFunction`.
    * Define its `name` and `arity` (number of arguments) in the constructor.
    * Implement the `apply` method with the function's logic.
    * Add the new function to the parser instance using `parser.add_function()`.

    ```python
    from arithmetic_parser.components.functions.base import BaseFunction
    import math

    class SinFunction(BaseFunction): #
        def __init__(self): #
            super().__init__("sin", arity=1) #
        
        def apply(self, x: float) -> float: #
            return math.sin(x) #

    parser = ArithmeticParserAPI()
    parser.add_function(SinFunction()) #
    result = parser.parse("sin(1.5708)")
    print(f"'sin(1.5708)' = {result:.4f}") # Output: 'sin(1.5708)' = 1.0000
    ```

This modular and plugin-like architecture ensures that the parser is not only functional but
also highly adaptable to evolving requirements for mathematical expression evaluation.

