from ..components.operators.base import BinaryOperator
from ..components.functions.base import BaseFunction
from ..api.parser_api import ArithmeticParserAPI
import math


class PowerOperator(BinaryOperator):
    """Power operator (**) - example of adding new operators."""
    
    def __init__(self):
        super().__init__("**", precedence=3, associativity="right")
    
    def apply(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)


class ModuloOperator(BinaryOperator):
    """Modulo operator (%) - another extension example."""
    
    def __init__(self):
        super().__init__("%", precedence=2)
    
    def apply(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Modulo by zero")
        return a % b


class SinFunction(BaseFunction):
    """Sine function - example of adding trigonometric functions."""
    
    def __init__(self):
        super().__init__("sin", arity=1)
    
    def apply(self, x: float) -> float:
        return math.sin(x)


class LogFunction(BaseFunction):
    """Natural logarithm function."""
    
    def __init__(self):
        super().__init__("log", arity=1)
    
    def apply(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Logarithm of non-positive number")
        return math.log(x)


def demonstrate_extensions():
    """Demonstrate how to extend the parser with new operators and functions."""
    
    print("EXTENSION DEMONSTRATION")
    print("=" * 40)
    
    # Create parser
    parser = ArithmeticParserAPI()
    
    print("Original capabilities:")
    print(f"Operators: {parser.get_supported_operators()}")
    print(f"Functions: {parser.get_supported_functions()}")
    
    # Add new operators
    parser.add_operator(PowerOperator())
    parser.add_operator(ModuloOperator())
    
    # Add new functions
    parser.add_function(SinFunction())
    parser.add_function(LogFunction())
    
    print("\nAfter extensions:")
    print(f"Operators: {parser.get_supported_operators()}")
    print(f"Functions: {parser.get_supported_functions()}")
    
    # Test new capabilities
    test_expressions = [
        "2 ** 3",           # Power operator
        "10 % 3",           # Modulo operator
        "sin(1.5708)",      # Sine function (π/2)
        "log(2.718)",       # Natural log function (e)
        "2 ** 3 + sqrt(16)" # Mixed old and new features
    ]
    
    print("\nTesting extended functionality:")
    for expr in test_expressions:
        try:
            result = parser.parse(expr)
            print(f"'{expr}' = {result:.4f}")
        except Exception as e:
            print(f"'{expr}' -> Error: {e}")