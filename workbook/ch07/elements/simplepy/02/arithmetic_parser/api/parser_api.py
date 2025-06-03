from typing import Dict, List, Optional
from ..core.tokenizer import Tokenizer
from ..core.evaluator import Evaluator
from ..core.exceptions import ParserError, TokenizationError
from ..components.operators.arithmetic import create_arithmetic_registry
from ..components.functions.basic import create_basic_function_registry

class ArithmeticParserAPI:
    """
    Main public API for parsing arithmetic expressions.
    """
    
    def __init__(self, enable_functions: bool = True):
        self.operator_registry = create_arithmetic_registry()
        self.function_repository = create_basic_function_registry() if enable_functions else None
        self.tokenizer = Tokenizer(self.operator_registry, self.function_repository)
        self.evaluator = Evaluator(self.operator_registry, self.function_repository)
    
    def parse(self, expression: str) -> float:
        """
        Parse and evaluate an arithmetic expression.
        
        Args:
            expression: String containing the arithmetic expression
            
        Returns:
            Numerical result of the expression
            
        Raises:
            ParserError: If the expression cannot be parsed or evaluated
        """
        try:
            tokens = self.tokenizer.tokenize(expression)
            result = self.evaluator.evaluate(tokens)
            # Round to 6 decimals for display, but only if result is not an exact integer
            if result == int(result):
                return float(result)  # Return exact integer as float (e.g., 8.0)
            return round(result, 6)  # Round to 6 decimals for non-integers
        except TokenizationError as e:
            raise ParserError(f"Failed to tokenize '{expression}': {e}")
        except ValueError as e:
            raise ParserError(f"Evaluation error in '{expression}': {e}")
        except Exception as e:
            raise ParserError(f"Failed to parse '{expression}': {e}")
    
    def validate(self, expression: str) -> bool:
        """Check if an expression is valid without evaluating it."""
        try:
            self.tokenizer.tokenize(expression)
            return True
        except Exception:
            return False
    
    def get_supported_operators(self) -> List[str]:
        """Get list of supported operators."""
        return self.operator_registry.get_all_symbols()
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported functions."""
        if self.function_repository:
            return self.function_repository.get_all_names()
        return []
    
    def add_operator(self, operator):
        """Add a custom operator (extension point)."""
        if not hasattr(operator, 'apply') or not callable(operator.apply):
            raise ValueError("Operator must have a valid 'apply' method")
        if not hasattr(operator, 'precedence') or not isinstance(operator.precedence, (int, float)):
            raise ValueError("Operator must have a numeric 'precedence'")
        if not hasattr(operator, 'associativity') or operator.associativity not in ['left', 'right']:
            raise ValueError("Operator must have 'associativity' of 'left' or 'right'")
        if operator in self.operator_registry.get_all_symbols():
            raise ValueError(f"Operator '{operator}' already exists")
        self.operator_registry.register(operator)
    
    def add_function(self, function):
        """Add a custom function (extension point)."""
        if not self.function_repository:
            raise ParserError("Functions are disabled")
        if not hasattr(function, 'apply') or not callable(function.apply):
            raise ValueError("Function must have a valid 'apply' method")
        if not hasattr(function, 'arity') or not isinstance(function.arity, int):
            raise ValueError("Function must have a numeric 'arity'")
        if function in self.function_repository.get_all_names():
            raise ValueError(f"Function '{function}' already exists")
        self.function_repository.register(function)