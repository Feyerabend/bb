from .base import BinaryOperator, UnaryOperator, OperatorRegistry
from ...core.exceptions import OperatorError


class AdditionOperator(BinaryOperator):
    """Addition operator (+)."""
    
    def __init__(self):
        super().__init__("+", precedence=1)
    
    def apply(self, a: float, b: float) -> float:
        return a + b


class SubtractionOperator(BinaryOperator):
    """Subtraction operator (-)."""
    
    def __init__(self):
        super().__init__("-", precedence=1)
    
    def apply(self, a: float, b: float) -> float:
        return a - b


class MultiplicationOperator(BinaryOperator):
    """Multiplication operator (*)."""
    
    def __init__(self):
        super().__init__("*", precedence=2)
    
    def apply(self, a: float, b: float) -> float:
        return a * b


class DivisionOperator(BinaryOperator):
    """Division operator (/)."""
    
    def __init__(self):
        super().__init__("/", precedence=2)
    
    def apply(self, a: float, b: float) -> float:
        if b == 0:
            raise OperatorError("Division by zero")
        return a / b


class UnaryMinusOperator(UnaryOperator):
    """Unary minus operator (-)."""
    
    def __init__(self):
        super().__init__("-", precedence=3, associativity="right")
    
    def apply(self, a: float) -> float:
        return -a


def create_arithmetic_registry() -> OperatorRegistry:
    """Create and populate the standard arithmetic operator registry."""
    registry = OperatorRegistry()
    
    # Register standard operators
    registry.register(AdditionOperator())
    registry.register(SubtractionOperator())
    registry.register(MultiplicationOperator())
    registry.register(DivisionOperator())
    
    return registry