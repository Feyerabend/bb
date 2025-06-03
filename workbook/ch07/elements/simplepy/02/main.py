from arithmetic_parser import ArithmeticParserAPI
from arithmetic_parser.components.operators.base import BinaryOperator
from arithmetic_parser.components.functions.base import BaseFunction
import math


class PowerOperator(BinaryOperator):
    """Power operator (**) - example of adding new operators."""
    
    def __init__(self):
        super().__init__("**", precedence=3, associativity="right")
    
    def apply(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)


class SinFunction(BaseFunction):
    """Sine function - example of adding trigonometric functions."""
    
    def __init__(self):
        super().__init__("sin", arity=1)
    
    def apply(self, x: float) -> float:
        return math.sin(x)


def demonstrate_extensions():
    """Demonstrate how to extend the parser with new operators and functions."""
    
    print("EXTENSION DEMONSTRATION")
    print("=" * 40)
    
    # Create parser
    parser = ArithmeticParserAPI()
    
    print("Original capabilities:")
    print(f"Operators: {parser.get_supported_operators()}")
    print(f"Functions: {parser.get_supported_functions()}")
    
    # Add new operators and functions
    parser.add_operator(PowerOperator())
    parser.add_function(SinFunction())
    
    print("\nAfter extensions:")
    print(f"Operators: {parser.get_supported_operators()}")
    print(f"Functions: {parser.get_supported_functions()}")
    
    # Test new capabilities
    test_expressions = [
        "2 ** 3",           # Power operator
        "sin(1.5708)",      # Sine function (π/2)
        "2 ** 3 + sqrt(16)" # Mixed old and new features
    ]
    
    print("\nTesting extended functionality:")
    for expr in test_expressions:
        try:
            result = parser.parse(expr)
            print(f"'{expr}' = {result:.4f}")
        except Exception as e:
            print(f"'{expr}' -> Error: {e}")


def main():
    """Demonstrate the parser architecture and extensibility."""
    
    print("EXTENSIBLE ARITHMETIC PARSER")
    print("=" * 50)
    print()
    
    # Basic usage
    print("1. BASIC USAGE:")
    print("-" * 20)
    parser = ArithmeticParserAPI()
    
    basic_expressions = [
        "2 + 3 * 4",
        "(10 - 5) / 2",
        "sqrt(16) + abs(-3)",
        "max(5, 8) * min(2, 4)"
    ]
    
    for expr in basic_expressions:
        try:
            result = parser.parse(expr)
            print(f"'{expr}' = {result}")
        except Exception as e:
            print(f"'{expr}' -> Error: {e}")
    
    print()
    
    # Extension demonstration
    print("2. EXTENSION CAPABILITIES:")
    print("-" * 30)
    demonstrate_extensions()
    
    print()
    print("3. ARCHITECTURE BENEFITS:")
    print("-" * 30)
    print("✓ Modular design with clear separation of concerns")
    print("✓ Easy to extend with new operators and functions")
    print("✓ Plugin-like architecture for adding features")
    print("✓ Comprehensive error handling at each layer")
    print("✓ Testable components with single responsibilities")
    print("✓ Scalable structure ready for complex features")


if __name__ == "__main__":
    main()