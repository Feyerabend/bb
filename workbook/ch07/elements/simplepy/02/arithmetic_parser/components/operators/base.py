from abc import ABC, abstractmethod
from typing import Dict, List, Callable


class BaseOperator(ABC):
    """Abstract base class for all operators."""
    
    def __init__(self, symbol: str, precedence: int, associativity: str = "left"):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity  # "left" or "right"
    
    @abstractmethod
    def apply(self, *operands: float) -> float:
        """Apply the operator to the given operands."""
        pass
    
    @property
    def arity(self) -> int:
        """Number of operands this operator takes."""
        return 2  # Default to binary operators
    
    def __str__(self):
        return f"Operator({self.symbol})"


class UnaryOperator(BaseOperator):
    """Base class for unary operators."""
    
    @property
    def arity(self) -> int:
        return 1


class BinaryOperator(BaseOperator):
    """Base class for binary operators."""
    
    @property
    def arity(self) -> int:
        return 2


class OperatorRegistry:
    """
    Registry for all available operators.
    This pattern makes it easy to add new operators without modifying existing code.
    """
    
    def __init__(self):
        self._operators: Dict[str, BaseOperator] = {}
    
    def register(self, operator: BaseOperator):
        """Register a new operator."""
        self._operators[operator.symbol] = operator
    
    def get(self, symbol: str) -> BaseOperator:
        """Get an operator by symbol."""
        if symbol not in self._operators:
            raise ValueError(f"Unknown operator: {symbol}")
        return self._operators[symbol]
    
    def get_precedence(self, symbol: str) -> int:
        """Get operator precedence."""
        return self.get(symbol).precedence
    
    def is_registered(self, symbol: str) -> bool:
        """Check if an operator is registered."""
        return symbol in self._operators
    
    def get_all_symbols(self) -> List[str]:
        """Get all registered operator symbols."""
        return list(self._operators.keys())
