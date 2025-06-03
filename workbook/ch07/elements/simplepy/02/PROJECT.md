
## Project Instructions: Extending the Arithmetic Parser Architecture

#### Overview

In this project, you will extend a modular Python-based arithmetic parser system that evaluates
mathematical expressions using a tokeniser, evaluator, and registries for operators and functions.
The system, implemented in files like `tokenizer.py`, `evaluator.py`, `arithmetic.py`, and `basic.py`,
uses a Shunting Yard algorithm for parsing and supports extensibility through registries.
Your mission, should you choose to accept it, is to enhance the *architecture* by adding new features,
improving robustness, and applying software engineering principles like separation of concerns,
modularity, and error handling. This project emphasizes *extensibility*, allowing you to add new
components, refine existing ones, and explore advanced parsing techniques.


#### Learning Objectives

By completing this project, you will:
1. *Master Software Architecture*: Design modular, extensible systems using principles like separation
   of concerns and dependency inversion.
2. *Extend a Parsing System*: Add new operators, functions, or advanced features like variables or new
   token types, integrating with `OperatorRegistry` and `FunctionRegistry`.
3. *Enhance Robustness*: Improve error handling in `Tokenizer`, `Evaluator`, and `ExpressionValidator`
  for edge cases.
4. *Develop Project Management Skills*: Plan and execute a software project with clear milestones and
   deliverables.
5. *Practice Collaboration and Communication*: Produce clear documentation and optionally work in teams.
6. *Apply Testing Practices*: Write automated tests to ensure functionality.
7. *Explore Advanced Concepts*: Experiment with parsing algorithms, plugin systems, or domain-specific
   languages.


#### Project Requirements

1. *Core System*: Start with the provided arithmetic parser code in `arithmetic_parser/`, including:
   - `components/tokens.py`: Defines `Token` and `TokenType`.
   - `components/operators/arithmetic.py`: Defines operators (`+`, `-`, `*`, `/`) and `OperatorRegistry`.
   - `components/functions/basic.py`: Defines functions (`sqrt`, `abs`, `pow`, `max`, `min`) and `FunctionRegistry`.
   - `core/tokenizer.py`: Implements `Tokenizer` for converting strings to tokens.
   - `core/evaluator.py`: Implements `Evaluator` using Shunting Yard.
   - `core/validators.py`: Implements `ExpressionValidator` (incomplete, needs extension).
2. *Architectural Focus*: Extend the architecture with at least *two significant enhancements* (see suggestions below).
3. *Minimum Features*:
   - Add at least *one new operator* (e.g., modulo `%`) to `arithmetic.py`.
   - Add at least *one new function* (e.g., `cos`) to `basic.py`.
   - Implement *one major architectural improvement* (e.g., variable support, enhanced validation).
4. *Deliverables*:
   - *Source Code*: Extended, commented Python code in the `arithmetic_parser/` directory.
   - *Makefile*: With targets for running (`run`), cleaning (`clean`), testing (`test`), and documentation (`docs`).
   - *Documentation*:
     - `README.md`: Guide on features, architecture, setup, and usage.
     - API documentation: Generated using `pdoc3` or docstrings.
   - *Test Suite*: Unit tests (using `pytest`) in `tests/` covering new and existing features.
   - *Report*: A 2-3 page PDF/Markdown document on design decisions, challenges, and lessons learned.
   - *Presentation (Optional)*: A 5-minute demo or slide deck (if required).
5. *Constraints*:
   - Use Python 3.8+.
   - Preserve method signatures in `Tokenizer`, `Evaluator`, and other core classes.
   - Ensure backward compatibility (e.g., `(10 - 5) / 2 = 2.5`, `sqrt(16) + abs(-3) = 7.0`).
   - Follow PEP 8 style guidelines.


#### Suggested Architectural Extensions

Choose at least *two* significant extensions to enhance the architecture, leveraging the provided files:
- *Basic Extensions* (1-2 hours each):
  - Add a new operator (e.g., modulo `%`) to `arithmetic.py` with appropriate precedence.
  - Add a new function (e.g., `cos`, `tan`) to `basic.py`, using Python’s `math` module.
  - Enhance `validators.py` to complete `_check_token_sequence` for rules like preventing consecutive
    operators (e.g., `1 ++ 2`).
  - Improve error messages in `Tokenizer` or `Evaluator` with token position from `Token.position`.
- *Intermediate Extensions* (3-5 hours each):
  - Support variables (e.g., `x * 2` where `x` is defined):
    - Use `TokenType.VARIABLE` (already in `tokens.py`).
    - Create a `VariableRegistry` in `components/variables/`.
    - Update `Tokenizer` and `Evaluator` to handle variables.
  - Implement dynamic configuration for operators/functions via JSON/YAML in `arithmetic.py` or `basic.py`.
  - Add constant support (e.g., `PI = 3.14159`) using `TokenType.CONSTANT` in `tokens.py`.
- *Advanced Extensions* (6-10 hours each):
  - Support new expression types:
    - *Boolean expressions*: Add operators (`<`, `>`, `AND`) with `TokenType.BOOLEAN`.
    - *String operations*: Use `TokenType.STRING` for concatenation (e.g., `"a" + "b"`).
  - Create a plugin system for loading operators/functions from external modules.
  - Implement a recursive descent parser in a new `core/parser.py` as an alternative to Shunting Yard.
  - Support multi-line expressions (e.g., `x = 5; x + 3`) with a new `ScriptParser` class.


#### Additional Features (Optional)

- *REPL*: Build an interactive interface in `repl.py` for real-time evaluation.
- *AST Visualisation*: Use `graphviz` to visualise the expression’s parse tree
  (or use JavaScript, and add upload locally files).
- *Performance Optimisation*: Profile `Evaluator` with `cProfile` and optimise.
- *Logging*: Add logging in `Evaluator` and `Tokenizer` using `logging`.


#### Time Planning (6 Weeks)

Total effort: ~30-40 hours (~5-7 hours/week).
- *Week 1: Setup and Learning (5-7 hours)*
  - Understand files (`tokenizer.py`, `evaluator.py`, `arithmetic.py`, `basic.py`).
  - Set up environment: Python 3.8+, Git, `pytest`, `pdoc3`.
  - Run `make run` to verify `(10 - 5) / 2 = 2.5`.
  - Research Shunting Yard and tokenization.
  - Write project plan: Select extensions, sketch architecture.
  - Milestone: Project plan, initial Git commit.
- *Week 2: Basic Extensions (6-8 hours)*
  - Add modulo operator and `cos` function.
  - Write tests in `tests/`.
  - Update `README.md` draft.
  - Milestone: Basic extensions with tests.
- *Week 3: Major Extension Part 1 (6-8 hours)*
  - Start major extension (e.g., variables).
  - Design new components (e.g., `VariableRegistry`).
  - Write tests and update `README.md`.
  - Milestone: Partial major extension.
- *Week 4: Major Extension Part 2 (6-8 hours)*
  - Complete major extension.
  - Enhance error handling in `validators.py`.
  - Expand tests and refactor code.
  - Milestone: Major extension complete.
- *Week 5: Optional Features and Testing (5-7 hours)*
  - Add optional feature (e.g., REPL).
  - Achieve >80% test coverage (`pytest-cov`).
  - Finalize `README.md` and generate API docs.
  - Milestone: Polished code and docs.
- *Week 6: Report and Presentation (5-6 hours)*
  - Write report on design, challenges, lessons.
  - Prepare demo or slides (if required).
  - Submit zip file with code, tests, docs.
  - Milestone: Project submitted.


#### Tips

- Start with small extensions (e.g., `%` in `arithmetic.py`).
- Test incrementally with `make test`.
- Commit regularly with Git Bash.
- Seek help for complex issues (e.g., `Tokenizer` regex).
- Propose creative extensions (e.g., `sin`, constants).

#### Collaboration Guidelines

- *Teams*: 2-3 students.
- *Roles*: Lead Developer, Tester, Documenter.
- *Workflow*: Use Git branches, pull requests.
- *Communication*: Weekly meetings via Discord/Slack.

#### Evaluation Criteria

- *Functionality (40%)*: Extensions work, tests pass.
- *Architecture (30%)*: Modular, extensible design.
- *Documentation (20%)*: Clear `README.md`, report.
- *Testing (10%)*: >80% coverage, edge cases tested.


#### Resources
- [Python Docs](https://docs.python.org/3/)
- [Shunting Yard](https://en.wikipedia.org/wiki/Shunting_yard_algorithm)
- [Pytest](https://docs.pytest.org/)
- [Pdoc](https://pdoc3.github.io/pdoc/)

#### Example Deliverable Structure (in the main)
```
project/
├── main.py
├── repl.py
├── arithmetic_parser/
│   ├── core/
│   │   ├── tokenizer.py
│   │   ├── evaluator.py
│   │   ├── validators.py
│   ├── components/
│   │   ├── tokens.py
│   │   ├── operators/
│   │   │   ├── arithmetic.py
│   │   ├── functions/
│   │   │   ├── basic.py
│   │   ├── variables/
│   │       ├── base.py
├── tests/
│   ├── test_parser.py
├── docs/
├── Makefile
├── README.md
├── report.pdf
```


#### Step-by-Step Instructions

1. *Setup*:
   - Clone the provided code.
   - Install dependencies:
     ```bash
     pip install pytest pytest-cov pdoc3 graphviz
     ```
   - Init Git: `git init`.
   - Test base system: `make run` for `(10 - 5) / 2 = 2.5`.
2. *Plan Extensions*:
   - Choose two extensions (e.g., modulo, `cos`, variables).
   - Sketch architecture (e.g., new `VariableRegistry`).
   - Update Makefile:

```makefile
     .PHONY: all
     all: run

     .PHONY: clean
     clean:
     	find . -type d -name "__pycache__" -exec rm -r {} +
     	find . -type f -name "*.pyc" -delete
     	@echo "All __pycache__ folders and .pyc files removed."

     .PHONY: run
     run:
     	@test -f main.py || (echo "Error: main.py not found"; exit 1)
     	python3 main.py

     .PHONY: test
     test:
     	python3 -m pytest tests -v --cov=arithmetic_parser

     .PHONY: docs
     docs:
     	pdoc3 --html -o docs arithmetic_parser
     	@echo "Documentation generated in docs/"

     .PHONY: help
     help:
     	@echo "Usage:"
     	@echo "  make          - Run main.py (default)"
     	@echo "  make clean    - Remove __pycache__ and .pyc files"
     	@echo "  make run      - Run main.py with python3"
     	@echo "  make test     - Run unit tests with coverage"
     	@echo "  make docs     - Generate API documentation"
```

3. *Implement Extensions*:
   - *Modulo Operator*:
     - Update `arithmetic_parser/components/operators/arithmetic.py`:
       ```python
       from .base import BinaryOperator, UnaryOperator, OperatorRegistry
       from ...core.exceptions import OperatorError

       # Existing operators...

       class ModuloOperator(BinaryOperator):
           """Modulo operator (%)."""
           def __init__(self):
               super().__init__("%", precedence=2)
           def apply(self, a: float, b: float) -> float:
               if b == 0:
                   raise OperatorError("Modulo by zero")
               return a % b

       def create_arithmetic_registry() -> OperatorRegistry:
           registry = OperatorRegistry()
           registry.register(AdditionOperator())
           registry.register(SubtractionOperator())
           registry.register(MultiplicationOperator())
           registry.register(DivisionOperator())
           registry.register(ModuloOperator())  # New
           return registry
       ```
     - Test: `7 % 3 = 1.0`.
   - *Cosine Function*:
     - Update `arithmetic_parser/components/functions/basic.py`:
       ```python
       import math
       from .base import BaseFunction, FunctionRegistry

       # Existing functions...

       class CosFunction(BaseFunction):
           """Cosine function."""
           def __init__(self):
               super().__init__("cos", arity=1)
           def apply(self, x: float) -> float:
               return math.cos(x)

       def create_basic_function_registry() -> FunctionRegistry:
           registry = FunctionRegistry()
           registry.register(SqrtFunction())
           registry.register(AbsFunction())
           registry.register(PowFunction())
           registry.register(MaxFunction())
           registry.register(MinFunction())
           registry.register(CosFunction())  # New
           return registry
       ```
     - Test: `cos(0) = 1.0`.
   - *Variable Support*:
     - Create `arithmetic_parser/components/variables/base.py`:
       ```python
       from typing import Dict
       from ...core.exceptions import EvaluationError

       class VariableRegistry:
           """Registry for storing variable names and values."""
           def __init__(self):
               self.variables: Dict[str, float] = {}

           def register(self, name: str, value: float):
               if not isinstance(value, (int, float)):
                   raise ValueError(f"Variable '{name}' must have a numeric value")
               self.variables[name] = float(value)

           def get(self, name: str) -> float:
               if name not in self.variables:
                   raise EvaluationError(f"Undefined variable: {name}")
               return self.variables[name]
       ```
     - Update `tokens.py` to include `is_variable`:
       ```python
       from enum import Enum
       from typing import Union
       from dataclasses import dataclass

       class TokenType(Enum):
           NUMBER = "NUMBER"
           OPERATOR = "OPERATOR"
           FUNCTION = "FUNCTION"
           PARENTHESIS = "PARENTHESIS"
           VARIABLE = "VARIABLE"
           CONSTANT = "CONSTANT"
           COMMA = "COMMA"

       @dataclass
       class Token:
           type: TokenType
           value: Union[float, str]
           position: int = 0

           def __str__(self):
               return f"{self.type.value}({self.value})"

           def is_number(self) -> bool:
               return self.type == TokenType.NUMBER

           def is_operator(self) -> bool:
               return self.type == TokenType.OPERATOR

           def is_function(self) -> bool:
               return self.type == TokenType.FUNCTION

           def is_variable(self) -> bool:
               return self.type == TokenType.VARIABLE
       ```
     - Update `tokenizer.py`:
       ```python
       import re
       from typing import List, Optional
       from ..components.tokens import Token, TokenType
       from ..components.operators.base import OperatorRegistry
       from ..components.functions.base import FunctionRegistry
       from .exceptions import TokenizationError

       class Tokenizer:
           def __init__(self, operator_registry: OperatorRegistry, function_registry: Optional[FunctionRegistry] = None):
               self.operator_registry = operator_registry
               self.function_registry = function_registry
               self.number_pattern = re.compile(r'-?\d*\.?\d*')
               self.identifier_pattern = re.compile(r'[a-zA-Z_]\w*')

           def tokenize(self, expression: str) -> List[Token]:
               tokens = []
               if not expression or expression.isspace():
                   raise TokenizationError("Empty or whitespace-only expression")

               expression = expression.replace(' ', '')
               i = 0
               orig_i = 0

               while i < len(expression):
                   char = expression[i]

                   if char.isdigit() or char == '.' or char == '-':
                       if char == '-' and i > 0:
                           prev_char = expression[i - 1]
                           if prev_char.isdigit() or prev_char == ')':
                               tokens.append(Token(TokenType.OPERATOR, '-', orig_i))
                               i += 1
                               orig_i += 1
                               continue

                       number_match = self.number_pattern.match(expression, i)
                       if number_match:
                           value_str = number_match.group()
                           if value_str in ('-', '.', '-.'):
                               raise TokenizationError(f"Invalid number format: '{value_str}' at position {orig_i}")
                           if value_str.count('.') > 1:
                               raise TokenizationError(f"Multiple decimal points in number: '{value_str}' at position {orig_i}")
                           value = float(value_str)
                           tokens.append(Token(TokenType.NUMBER, value, orig_i))
                           i += len(value_str)
                           orig_i += len(value_str)
                           continue

                   matched_operator = None
                   for symbol in self.operator_registry.get_all_symbols():
                       if expression[i:].startswith(symbol):
                           if matched_operator is None or len(symbol) > len(matched_operator):
                               matched_operator = symbol
                   if matched_operator:
                       tokens.append(Token(TokenType.OPERATOR, matched_operator, orig_i))
                       i += len(matched_operator)
                       orig_i += len(matched_operator)
                       continue

                   if char in '()':
                       tokens.append(Token(TokenType.PARENTHESIS, char, orig_i))
                       i += 1
                       orig_i += 1
                       continue

                   if char == ',':
                       tokens.append(Token(TokenType.COMMA, char, orig_i))
                       i += 1
                       orig_i += 1
                       continue

                   if char.isalpha() or char == '_':
                       identifier_match = self.identifier_pattern.match(expression, i)
                       if identifier_match:
                           name = identifier_match.group()
                           if self.function_registry and self.function_registry.is_registered(name):
                               tokens.append(Token(TokenType.FUNCTION, name, orig_i))
                           else:
                               tokens.append(Token(TokenType.VARIABLE, name, orig_i))
                           i += len(name)
                           orig_i += len(name)
                           continue

                   raise TokenizationError(f"Unexpected character: '{char}' at position {orig_i}")

               return tokens
       ```
     - Update `evaluator.py`:
       ```python
       from typing import List, Optional
       from ..components.tokens import Token, TokenType
       from ..components.operators.base import OperatorRegistry
       from ..components.functions.base import FunctionRegistry
       from ..components.variables.base import VariableRegistry
       from .exceptions import EvaluationError

       class Evaluator:
           def __init__(self, operator_registry: OperatorRegistry, function_registry: Optional[FunctionRegistry] = None, variable_registry: Optional[VariableRegistry] = None):
               self.operator_registry = operator_registry
               self.function_registry = function_registry
               self.variable_registry = variable_registry or VariableRegistry()

           def evaluate(self, tokens: List[Token]) -> float:
               if not tokens:
                   raise EvaluationError("Empty expression")
               postfix = self._to_postfix(tokens)
               return self._evaluate_postfix(postfix)

           def _to_postfix(self, tokens: List[Token]) -> List[Token]:
               output = []
               operator_stack = []

               for token in tokens:
                   if token.is_number() or token.is_variable():
                       output.append(token)
                   elif token.is_function():
                       operator_stack.append(token)
                   elif token.value == ',':
                       while operator_stack and operator_stack[-1].value != '(':
                           output.append(operator_stack.pop())
                   elif token.is_operator():
                       while (operator_stack and 
                              operator_stack[-1].is_operator() and
                              self._should_pop_operator(token, operator_stack[-1])):
                           output.append(operator_stack.pop())
                       operator_stack.append(token)
                   elif token.value == '(':
                       operator_stack.append(token)
                   elif token.value == ')':
                       while operator_stack and operator_stack[-1].value != '(':
                           output.append(operator_stack.pop())
                       if not operator_stack:
                           raise EvaluationError("Mismatched parentheses")
                       operator_stack.pop()
                       if operator_stack and operator_stack[-1].is_function():
                           output.append(operator_stack.pop())

               while operator_stack:
                   if operator_stack[-1].value in '()':
                       raise EvaluationError("Mismatched parentheses")
                   output.append(operator_stack.pop())

               return output

           def _should_pop_operator(self, current: Token, stack_top: Token) -> bool:
               current_op = self.operator_registry.get(current.value)
               stack_op = self.operator_registry.get(stack_top.value)
               if current_op is None or stack_op is None:
                   raise EvaluationError(f"Unknown operator: {current.value if current_op is None else stack_top.value}")
               if current_op.associativity == "left":
                   return current_op.precedence <= stack_op.precedence
               else:
                   return current_op.precedence < stack_op.precedence

           def _evaluate_postfix(self, tokens: List[Token]) -> float:
               stack = []

               for token in tokens:
                   print(f"Stack before {token.value}: {stack}")

                   if token.is_number():
                       stack.append(token.value)
                   elif token.is_variable():
                       if not self.variable_registry:
                           raise EvaluationError("Variables not enabled")
                       value = self.variable_registry.get(token.value)
                       stack.append(value)
                       print(f"Resolved variable {token.value} -> {value}")
                   elif token.is_operator():
                       operator = self.operator_registry.get(token.value)
                       if operator is None:
                           raise EvaluationError(f"Unknown operator: {token.value}")
                       if len(stack) < operator.arity:
                           raise EvaluationError(f"Not enough operands for operator {token.value}")
                       operands = []
                       for _ in range(operator.arity):
                           operands.append(stack.pop())
                       operands.reverse()
                       try:
                           result = operator.apply(*operands)
                           stack.append(result)
                           print(f"Applied {token.value} to {operands} -> {result}")
                       except Exception as e:
                           raise EvaluationError(f"Error applying operator {token.value} to {operands}: {e}")
                   elif token.is_function():
                       if not self.function_registry:
                           raise EvaluationError("Functions not enabled")
                       function = self.function_registry.get(token.value)
                       if function is None:
                           raise EvaluationError(f"Unknown function: {token.value}")
                       if len(stack) < function.arity:
                           raise EvaluationError(f"Not enough arguments for function {token.value}")
                       args = []
                       for _ in range(function.arity):
                           args.append(stack.pop())
                       args.reverse()
                       try:
                           result = function.apply(*args)
                           stack.append(result)
                           print(f"Applied {token.value} to {args} -> {result}")
                       except Exception as e:
                           raise EvaluationError(f"Error applying function {token.value} to {args}: {e}")

               print(f"Final stack: {stack}")

               if not stack:
                   raise EvaluationError("No result after evaluation")
               if len(stack) > 1:
                   raise EvaluationError(f"Invalid expression: too many values left on stack {stack}")

               return stack[0]
       ```
     - Test: `x + 5` with `x = 3` → `8.0`.
4. *Test Thoroughly*:
   - Create `tests/test_parser.py`:
     ```python
     import unittest
     from arithmetic_parser import ArithmeticParser

     class TestParser(unittest.TestCase):
         def setUp(self):
             self.parser = ArithmeticParser()
             self.parser.evaluator.variable_registry.register('x', 3.0)

         def test_basic(self):
             self.assertEqual(self.parser.parse("(10 - 5) / 2"), 2.5)

         def test_modulo(self):
             self.assertEqual(self.parser.parse("7 % 3"), 1.0)

         def test_cos(self):
             self.assertAlmostEqual(self.parser.parse("cos(0)"), 1.0, places=6)

         def test_variable(self):
             self.assertEqual(self.parser.parse("x + 5"), 8.0)

         def test_edge_cases(self):
             with self.assertRaises(Exception):
                 self.parser.parse("1 / 0")
             with self.assertRaises(Exception):
                 self.parser.parse("(1 + 2")

     if __name__ == '__main__':
         unittest.main()
     ```
   - Run: `make test`.
5. *Document*:
   - *README.md*:
     ```markdown
     # Extended Arithmetic Parser

     A modular arithmetic expression parser supporting custom operators, functions, and variables.

     ## Features
     - Operators: +, -, *, /, % (new)
     - Functions: sqrt, abs, pow, max, min, cos (new)
     - Variables: e.g., `x + 5`
     - Enhanced validation and error handling

     ## Setup
     ```bash
     pip install pytest pytest-cov pdoc3
     git clone <your-repo>
     cd project
     make run
     ```

     ## Usage
     ```bash
     make run   # Run main.py
     make test  # Run tests
     make clean # Remove __pycache__
     make docs  # Generate API docs
     ```

     ## Architecture
     - *Tokenizer*: Extended for `VARIABLE` tokens.
     - *Evaluator*: Added variable resolution with `VariableRegistry`.
     - *Registries*: Added `%` and `cos`.
     - *Validator*: Enhanced sequence checking.

     ## Examples
     ```python
     from arithmetic_parser import ArithmeticParser
     parser = ArithmeticParser()
     parser.evaluator.variable_registry.register('x', 3.0)
     print(parser.parse("7 % 3"))     # Output: 1.0
     print(parser.parse("cos(0)"))    # Output: 1.0
     print(parser.parse("x + 5"))     # Output: 8.0
     ```
     
