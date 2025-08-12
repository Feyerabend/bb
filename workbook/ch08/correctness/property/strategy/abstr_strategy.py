from abc import ABC, abstractmethod
import random
from typing import Any, Iterator#, Optional

class Strategy(ABC):
    """Abstract base class for all test input generation strategies"""
    
    @abstractmethod
    def generate(self, random_state: random.Random, size: int) -> Any:
        """Generate a test value of appropriate complexity
        
        Args:
            random_state: Seeded random number generator for reproducibility
            size: Hint for complexity/size of generated value (0-100)
            
        Returns:
            Generated value according to this strategy's distribution
        """
        pass
    
    @abstractmethod
    def shrink(self, value: Any) -> Iterator[Any]:
        """Generate progressively simpler versions of a value
        
        Args:
            value: Complex value to be simplified
            
        Yields:
            Simpler variants that maintain the same type and structure
        """
        pass
    
    def map(self, transform_func):
        """Transform generated values through a mapping function"""
        return MappedStrategy(self, transform_func)
    
    def filter(self, predicate_func):
        """Filter generated values that satisfy a predicate"""
        return FilteredStrategy(self, predicate_func)

