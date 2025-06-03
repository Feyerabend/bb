from abc import ABC, abstractmethod
from typing import Dict, List
import math


class BaseFunction(ABC):
    """Abstract base class for all mathematical functions."""
    
    def __init__(self, name: str, arity: int):
        self.name = name
        self.arity = arity  # Number of arguments
    
    @abstractmethod
    def apply(self, *args: float) -> float:
        """Apply the function to the given arguments."""
        pass
    
    def validate_args(self, args: List[float]) -> None:
        """Validate function arguments."""
        if len(args) != self.arity:
            raise ValueError(f"Function {self.name} expects {self.arity} arguments, got {len(args)}")


class FunctionRegistry:
    """Registry for all available functions."""
    
    def __init__(self):
        self._functions: Dict[str, BaseFunction] = {}
    
    def register(self, function: BaseFunction):
        """Register a new function."""
        self._functions[function.name] = function
    
    def get(self, name: str) -> BaseFunction:
        """Get a function by name."""
        if name not in self._functions:
            raise ValueError(f"Unknown function: {name}")
        return self._functions[name]
    
    def is_registered(self, name: str) -> bool:
        """Check if a function is registered."""
        return name in self._functions
    
    def get_all_names(self) -> List[str]:
        """Get all registered function names."""
        return list(self._functions.keys())