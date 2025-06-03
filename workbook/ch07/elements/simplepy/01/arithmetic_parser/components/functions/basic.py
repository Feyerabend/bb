import math
from .base import BaseFunction, FunctionRegistry


class SqrtFunction(BaseFunction):
    """Square root function."""
    
    def __init__(self):
        super().__init__("sqrt", arity=1)
    
    def apply(self, x: float) -> float:
        if x < 0:
            raise ValueError("Square root of negative number")
        return math.sqrt(x)


class AbsFunction(BaseFunction):
    """Absolute value function."""
    
    def __init__(self):
        super().__init__("abs", arity=1)
    
    def apply(self, x: float) -> float:
        return abs(x)


class PowFunction(BaseFunction):
    """Power function (base, exponent)."""
    
    def __init__(self):
        super().__init__("pow", arity=2)
    
    def apply(self, base: float, exponent: float) -> float:
        return math.pow(base, exponent)


class MaxFunction(BaseFunction):
    """Maximum of two numbers."""
    
    def __init__(self):
        super().__init__("max", arity=2)
    
    def apply(self, a: float, b: float) -> float:
        return max(a, b)


class MinFunction(BaseFunction):
    """Minimum of two numbers."""
    
    def __init__(self):
        super().__init__("min", arity=2)
    
    def apply(self, a: float, b: float) -> float:
        return min(a, b)


def create_basic_function_registry() -> FunctionRegistry:
    """Create and populate the basic function registry."""
    registry = FunctionRegistry()
    
    # Register basic functions
    registry.register(SqrtFunction())
    registry.register(AbsFunction())
    registry.register(PowFunction())
    registry.register(MaxFunction())
    registry.register(MinFunction())
    
    return registry