from typing import Union, Tuple, List, Any, Callable, Optional, Iterator
from abc import ABC, abstractmethod
import random
from itertools import islice


class Strategy(ABC):
    """Abstract base class for all test data generation strategies"""
    
    @abstractmethod
    def generate(self, random_state: random.Random, size: int) -> Any:
        """Generate a value using the given random state and size hint"""
        pass
    
    @abstractmethod
    def shrink(self, value: Any) -> Iterator[Any]:
        """Generate shrunk versions of the given value"""
        pass


class OneOfStrategy(Strategy):
    """Choose randomly from multiple strategies with weighted selection"""
    
    def __init__(self, *strategies: Strategy, weights: Optional[List[float]] = None):
        if not strategies:
            raise ValueError("OneOfStrategy requires at least one strategy")
        self.strategies = strategies
        self.weights = weights or [1.0] * len(strategies)
        
        if len(self.weights) != len(strategies):
            raise ValueError("Number of weights must match number of strategies")
        
        # Normalize weights
        total_weight = sum(self.weights)
        if total_weight <= 0:
            raise ValueError("Total weight must be positive")
        self.weights = [w / total_weight for w in self.weights]
    
    def generate(self, random_state: random.Random, size: int) -> Any:
        """Select strategy based on weights and generate value"""
        chosen = random_state.choices(self.strategies, weights=self.weights)[0]
        return chosen.generate(random_state, size)
    
    def shrink(self, value: Any) -> Iterator[Any]:
        """Try shrinking with each strategy that could have produced this value"""
        for strategy in self.strategies:
            try:
                yield from strategy.shrink(value)
            except (TypeError, AttributeError, ValueError):
                continue  # Strategy cannot shrink this value type


class TupleStrategy(Strategy):
    """Generate tuples by combining multiple strategies"""
    
    def __init__(self, *element_strategies: Strategy):
        if not element_strategies:
            raise ValueError("TupleStrategy requires at least one element strategy")
        self.element_strategies = element_strategies
    
    def generate(self, random_state: random.Random, size: int) -> tuple:
        """Generate tuple with each element from its respective strategy"""
        element_size = max(1, size // len(self.element_strategies))
        return tuple(
            strategy.generate(random_state, element_size)
            for strategy in self.element_strategies
        )
    
    def shrink(self, value: tuple) -> Iterator[tuple]:
        """Shrink tuples by shrinking individual elements"""
        if not isinstance(value, tuple) or len(value) != len(self.element_strategies):
            return  # Cannot shrink tuples with wrong arity
        
        # Shrink each element position independently
        for i, (element, strategy) in enumerate(zip(value, self.element_strategies)):
            for shrunken_element in strategy.shrink(element):
                yield value[:i] + (shrunken_element,) + value[i+1:]


class DictionaryStrategy(Strategy):
    """Generate dictionaries with configurable key and value strategies"""
    
    def __init__(self, key_strategy: Strategy, value_strategy: Strategy,
                 min_size: int = 0, max_size: int = 20):
        if min_size < 0:
            raise ValueError("min_size must be non-negative")
        if max_size < min_size:
            raise ValueError("max_size must be >= min_size")
            
        self.key_strategy = key_strategy
        self.value_strategy = value_strategy
        self.min_size = min_size
        self.max_size = max_size
    
    def generate(self, random_state: random.Random, size: int) -> dict:
        """Generate dictionary with size-dependent number of entries"""
        dict_size = random_state.randint(
            self.min_size, 
            min(self.max_size, max(self.min_size, size))
        )
        
        result = {}
        attempts = 0
        max_attempts = dict_size * 3 if dict_size > 0 else 1

        # Allow for key collisions by trying multiple times
        element_size = max(1, size // 2)
        
        while len(result) < dict_size and attempts < max_attempts:
            try:
                key = self.key_strategy.generate(random_state, element_size)
                # Keys must be hashable
                hash(key)  # This will raise TypeError if not hashable
                value = self.value_strategy.generate(random_state, element_size)
                result[key] = value
            except TypeError:
                # Generated key is not hashable, try again
                pass
            attempts += 1
        
        return result
    
    def shrink(self, value: dict) -> Iterator[dict]:
        """Shrink dictionaries by removing entries and shrinking keys/values"""
        if not isinstance(value, dict) or not value:
            return
        
        # Phase 1: Remove entries
        items = list(value.items())
        for i in range(len(items)):
            # Create dict without item at position i
            new_dict = {k: v for j, (k, v) in enumerate(items) if j != i}
            yield new_dict
        
        # Phase 2: Remove multiple entries (divide and conquer)
        if len(items) > 2:
            mid = len(items) // 2
            yield dict(items[:mid])
            yield dict(items[mid:])
        
        # Phase 3: Shrink individual keys and values
        for key, val in items:
            # Try shrinking the key
            for shrunken_key in self.key_strategy.shrink(key):
                try:
                    # Ensure the shrunken key is hashable
                    hash(shrunken_key)
                    if shrunken_key not in value:  # Avoid key conflicts
                        new_dict = value.copy()
                        del new_dict[key]
                        new_dict[shrunken_key] = val
                        yield new_dict
                except (TypeError, KeyError):
                    continue
            
            # Try shrinking the value
            for shrunken_val in self.value_strategy.shrink(val):
                new_dict = value.copy()
                new_dict[key] = shrunken_val
                yield new_dict


# Example concrete strategies for demonstration
class IntegerStrategy(Strategy):
    """Generate integers within a specified range"""
    
    def __init__(self, min_value: int = -1000, max_value: int = 1000):
        self.min_value = min_value
        self.max_value = max_value
    
    def generate(self, random_state: random.Random, size: int) -> int:
        # Size influences the range of generated integers
        adjusted_max = min(self.max_value, size * 10)
        adjusted_min = max(self.min_value, -size * 10)
        return random_state.randint(adjusted_min, adjusted_max)
    
    def shrink(self, value: int) -> Iterator[int]:
        if not isinstance(value, int):
            return
        
        # Shrink towards zero
        if value == 0:
            return
        
        # Generate progressively smaller values
        if value > 0:
            for i in range(value - 1, -1, -1):
                if i >= self.min_value:
                    yield i
        else:  # value < 0
            for i in range(value + 1, 1):
                if i <= self.max_value:
                    yield i


class StringStrategy(Strategy):
    """Generate strings with configurable length and character set"""
    
    def __init__(self, alphabet: str = "abcdefghijklmnopqrstuvwxyz", 
                 min_length: int = 0, max_length: int = 100):
        self.alphabet = alphabet
        self.min_length = min_length
        self.max_length = max_length
    
    def generate(self, random_state: random.Random, size: int) -> str:
        length = random_state.randint(
            self.min_length,
            min(self.max_length, max(self.min_length, size))
        )
        return ''.join(random_state.choices(self.alphabet, k=length))
    
    def shrink(self, value: str) -> Iterator[str]:
        if not isinstance(value, str):
            return
        
        # Shrink by removing characters
        for i in range(len(value)):
            if len(value) - 1 >= self.min_length:
                yield value[:i] + value[i+1:]
        
        # Shrink by reducing length from the end
        for length in range(len(value) - 1, self.min_length - 1, -1):
            if length >= 0:
                yield value[:length]


# Example usage and testing
if __name__ == "__main__":
    # Create some example strategies
    int_strategy = IntegerStrategy(0, 100)
    str_strategy = StringStrategy(min_length=1, max_length=10)
    
    # Test OneOfStrategy
    choice_strategy = OneOfStrategy(int_strategy, str_strategy, weights=[0.7, 0.3])
    
    # Test TupleStrategy
    tuple_strategy = TupleStrategy(int_strategy, str_strategy, int_strategy)
    
    # Test DictionaryStrategy
    dict_strategy = DictionaryStrategy(str_strategy, int_strategy, min_size=1, max_size=5)
    
    # Generate some test data
    rng = random.Random(42)
    
    print("OneOfStrategy examples:")
    for _ in range(5):
        print(f"  {choice_strategy.generate(rng, 10)}")
    
    print("\nTupleStrategy examples:")
    for _ in range(3):
        print(f"  {tuple_strategy.generate(rng, 10)}")
    
    print("\nDictionaryStrategy examples:")
    for _ in range(3):
        print(f"  {dict_strategy.generate(rng, 5)}")
    
    # Test shrinking
    print("\nShrinking examples:")
    test_tuple = (50, "hello", 25)
    print(f"Original tuple: {test_tuple}")
    print("Shrunk versions:")
    for i, shrunk in enumerate(islice(tuple_strategy.shrink(test_tuple), 5)):
        print(f"  {shrunk}")
    
    test_dict = {"key1": 42, "key2": 17}
    print(f"\nOriginal dict: {test_dict}")
    print("Shrunk versions:")
    for i, shrunk in enumerate(islice(dict_strategy.shrink(test_dict), 5)):
        print(f"  {shrunk}")
