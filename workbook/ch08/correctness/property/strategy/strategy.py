
from abstract_strategy import Strategy
import random
import itertools

class IntegerStrategy(Strategy):
    """Generate integers with configurable range and distribution"""
    
    def __init__(self, min_value: int = -1000, max_value: int = 1000):
        if min_value >= max_value:
            raise ValueError("min_value must be less than max_value")
        self.min_value = min_value
        self.max_value = max_value
    
    def generate(self, random_state: random.Random, size: int) -> int:
        """Generate integers with size-dependent distribution"""
        # Small sizes favor simple values near zero
        if size < 10:
            # Bias toward smaller absolute values for simple cases
            limited_range = min(size * 2, abs(self.max_value - self.min_value) // 4)
            center = (self.min_value + self.max_value) // 2
            actual_min = max(self.min_value, center - limited_range)
            actual_max = min(self.max_value, center + limited_range)
        else:
            # Use full range for complex cases
            actual_min, actual_max = self.min_value, self.max_value
        
        return random_state.randint(actual_min, actual_max)
    
    def shrink(self, value: int) -> Iterator[int]:
        """Shrink integers toward zero through binary reduction"""
        if value == 0:
            return  # Cannot shrink zero further
        
        # Always try zero first as it's the simplest value
        yield 0
        
        # Then try progressively smaller absolute values
        current = abs(value)
        sign = 1 if value > 0 else -1
        
        while current > 1:
            current = current // 2
            candidate = sign * current
            if candidate != value:  # Avoid yielding the same value
                yield candidate


class ListStrategy(Strategy):
    """Generate lists using an element strategy"""
    
    def __init__(self, element_strategy: Strategy, 
                 min_length: int = 0, max_length: int = 50):
        if min_length < 0 or max_length < min_length:
            raise ValueError("Invalid length constraints")
        self.element_strategy = element_strategy
        self.min_length = min_length
        self.max_length = max_length
    
    def generate(self, random_state: random.Random, size: int) -> list:
        """Generate lists with size-dependent length distribution"""
        # Length grows with size but respects bounds
        max_len = min(self.max_length, max(self.min_length, size))
        length = random_state.randint(self.min_length, max_len)
        
        # Generate elements with reduced size to prevent exponential growth
        element_size = max(1, size // 2) if length > 0 else size
        
        return [
            self.element_strategy.generate(random_state, element_size)
            for _ in range(length)
        ]
    
    def shrink(self, value: list) -> Iterator[list]:
        """Shrink lists through element removal and element shrinking"""
        if not value:
            return  # Empty lists cannot be shrunk
        
        # Phase 1: Remove elements (try removing from different positions)
        for i in range(len(value)):
            # Try removing element at position i
            yield value[:i] + value[i+1:]
        
        # Phase 2: Try removing multiple elements
        if len(value) > 2:
            # Remove first half
            mid = len(value) // 2
            yield value[mid:]
            yield value[:mid]
        
        # Phase 3: Shrink individual elements while keeping structure
        for i, element in enumerate(value):
            for shrunken_element in self.element_strategy.shrink(element):
                new_list = value.copy()
                new_list[i] = shrunken_element
                yield new_list
