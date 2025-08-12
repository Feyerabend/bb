import random
from abc import ABC, abstractmethod
from typing import Any, Iterator, Callable, List, Union

class Strategy(ABC):
    """Base class for all generation strategies"""
    
    @abstractmethod
    def generate(self, random_state: random.Random, size: int) -> Any:
        """Generate a value using this strategy"""
        pass
    
    @abstractmethod
    def shrink(self, value: Any) -> Iterator[Any]:
        """Generate smaller versions of the given value"""
        pass

class IntegerStrategy(Strategy):
    """Generate integers within a specified range"""
    
    def __init__(self, min_value: int = 0, max_value: int = 100):
        self.min_value = min_value
        self.max_value = max_value
    
    def generate(self, random_state: random.Random, size: int) -> int:
        return random_state.randint(self.min_value, self.max_value)
    
    def shrink(self, value: int) -> Iterator[int]:
        """Shrink towards zero or the minimum value"""
        target = 0 if self.min_value <= 0 <= self.max_value else self.min_value
        
        if value == target:
            return
        
        # Try direct shrink to target
        if target != value:
            yield target
        
        # Try intermediate values
        diff = abs(value - target)
        for i in range(1, diff):
            if value > target:
                candidate = value - i
                if candidate >= self.min_value:
                    yield candidate
            else:
                candidate = value + i
                if candidate <= self.max_value:
                    yield candidate

class TupleStrategy(Strategy):
    """Generate tuples by combining multiple strategies"""
    
    def __init__(self, *strategies: Strategy):
        self.strategies = strategies
    
    def generate(self, random_state: random.Random, size: int) -> tuple:
        return tuple(
            strategy.generate(random_state, size) 
            for strategy in self.strategies
        )
    
    def shrink(self, value: tuple) -> Iterator[tuple]:
        """Shrink by shrinking individual elements"""
        if not value or len(value) != len(self.strategies):
            return
        
        # Try shrinking each element independently
        for i, (element, strategy) in enumerate(zip(value, self.strategies)):
            for shrunk_element in strategy.shrink(element):
                yield value[:i] + (shrunk_element,) + value[i+1:]

class OneOfStrategy(Strategy):
    """Choose from multiple strategies with optional weights"""
    
    def __init__(self, *strategies: Strategy, weights: List[float] = None):
        self.strategies = strategies
        self.weights = weights or [1.0] * len(strategies)
        
        if len(self.weights) != len(strategies):
            raise ValueError("Number of weights must match number of strategies")
    
    def generate(self, random_state: random.Random, size: int) -> Any:
        chosen_strategy = random_state.choices(self.strategies, weights=self.weights)[0]
        return chosen_strategy.generate(random_state, size)
    
    def shrink(self, value: Any) -> Iterator[Any]:
        """Try to shrink using each strategy that might have generated this value"""
        for strategy in self.strategies:
            try:
                yield from strategy.shrink(value)
            except (TypeError, ValueError):
                # This strategy might not be able to shrink this value
                continue

class ListStrategy(Strategy):
    """Generate lists of elements using a given strategy"""
    
    def __init__(self, element_strategy: Strategy, min_size: int = 0, max_size: int = 10):
        self.element_strategy = element_strategy
        self.min_size = min_size
        self.max_size = max_size
    
    def generate(self, random_state: random.Random, size: int) -> List[Any]:
        list_size = random_state.randint(self.min_size, min(self.max_size, size))
        return [
            self.element_strategy.generate(random_state, size)
            for _ in range(list_size)
        ]
    
    def shrink(self, value: List[Any]) -> Iterator[List[Any]]:
        """Shrink by removing elements and shrinking individual elements"""
        if not value:
            return
        
        # Try empty list if allowed
        if self.min_size == 0:
            yield []
        
        # Try removing elements
        for i in range(len(value)):
            if len(value) - 1 >= self.min_size:
                yield value[:i] + value[i+1:]
        
        # Try shrinking individual elements
        for i, element in enumerate(value):
            for shrunk_element in self.element_strategy.shrink(element):
                yield value[:i] + [shrunk_element] + value[i+1:]

class ConstantStrategy(Strategy):
    """Generate constant values"""
    
    def __init__(self, value: Any):
        self.value = value
    
    def generate(self, random_state: random.Random, size: int) -> Any:
        return self.value
    
    def shrink(self, value: Any) -> Iterator[Any]:
        return iter([])  # Constants cannot be shrunk

class RecursiveStrategy(Strategy):
    """Generate recursive data structures with controlled depth"""
    
    def __init__(self, base_strategy: Strategy, 
                 recursive_combinator: Callable[[Strategy], Strategy],
                 max_depth: int = 5):
        self.base_strategy = base_strategy
        self.recursive_combinator = recursive_combinator
        self.max_depth = max_depth
    
    def generate(self, random_state: random.Random, size: int) -> Any:
        """Generate recursive structures with depth control"""
        return self._generate_recursive(random_state, size, depth=0)
    
    def _generate_recursive(self, random_state: random.Random, 
                          size: int, depth: int) -> Any:
        """Internal recursive generation with depth tracking"""
        # Force base case at maximum depth or with increasing probability
        if depth >= self.max_depth or random_state.random() < (depth / self.max_depth):
            return self.base_strategy.generate(random_state, size)
        
        # Create a proxy strategy that maintains depth tracking
        class DepthTrackingStrategy(Strategy):
            def __init__(self, parent_strategy, current_depth):
                self.parent_strategy = parent_strategy
                self.current_depth = current_depth
            
            def generate(self, random_state, size):
                return self.parent_strategy._generate_recursive(
                    random_state, size, self.current_depth + 1
                )
            
            def shrink(self, value):
                return self.parent_strategy.shrink(value)
        
        # Create depth-tracking strategy
        recursive_strategy = DepthTrackingStrategy(self, depth)
        
        # Apply combinator to create recursive structure
        combined_strategy = self.recursive_combinator(recursive_strategy)
        return combined_strategy.generate(random_state, max(1, size // 2))
    
    def shrink(self, value: Any) -> Iterator[Any]:
        """Shrink by reducing to base cases and structural simplification"""
        # Try converting to base case
        if hasattr(value, '__iter__') and not isinstance(value, str):
            try:
                for base_val in self.base_strategy.shrink(next(iter(value))):
                    yield base_val
            except (StopIteration, TypeError):
                pass
        
        # Try structural shrinking based on the combinator type
        if isinstance(value, (list, tuple)):
            # Remove recursive elements
            for i in range(len(value)):
                yield value[:i] + value[i+1:]
        elif isinstance(value, dict):
            # Remove recursive key-value pairs
            items = list(value.items())
            for i in range(len(items)):
                yield dict(items[:i] + items[i+1:])

# Example: Binary tree generation
def binary_tree_combinator(node_strategy: Strategy) -> Strategy:
    """Combinator for creating binary tree nodes"""
    return TupleStrategy(
        IntegerStrategy(1, 100),  # Node value
        OneOfStrategy(  # Left child
            ConstantStrategy(None),  # Leaf
            node_strategy,  # Recursive subtree
            weights=[0.4, 0.6]
        ),
        OneOfStrategy(  # Right child
            ConstantStrategy(None),  # Leaf
            node_strategy,  # Recursive subtree
            weights=[0.4, 0.6]
        )
    )

# Example: List combinator for generating nested lists
def nested_list_combinator(element_strategy: Strategy) -> Strategy:
    """Combinator for creating nested lists"""
    return ListStrategy(
        OneOfStrategy(
            IntegerStrategy(1, 10),  # Simple integer elements
            element_strategy,        # Recursive nested lists
            weights=[0.7, 0.3]
        ),
        min_size=1,
        max_size=5
    )

# Usage examples
if __name__ == "__main__":
    # Binary tree example
    binary_tree_strategy = RecursiveStrategy(
        ConstantStrategy(None),  # Base case: leaf node
        binary_tree_combinator,
        max_depth=4
    )
    
    # Nested list example
    nested_list_strategy = RecursiveStrategy(
        ListStrategy(IntegerStrategy(1, 10), min_size=0, max_size=3),  # Base case: simple list
        nested_list_combinator,
        max_depth=3
    )
    
    # Generate some examples
    rng = random.Random(42)
    
    print("Binary Tree Examples:")
    for i in range(3):
        tree = binary_tree_strategy.generate(rng, 10)
        print(f"Tree {i+1}: {tree}")
    
    print("\nNested List Examples:")
    for i in range(3):
        nested = nested_list_strategy.generate(rng, 10)
        print(f"List {i+1}: {nested}")
    
    # Demonstrate shrinking
    print("\nShrinking Example:")
    tree = binary_tree_strategy.generate(rng, 10)
    print(f"Original tree: {tree}")
    print("Shrunk versions:")
    for i, shrunk in enumerate(binary_tree_strategy.shrink(tree)):
        if i >= 5:  # Limit output
            break
        print(f"  {shrunk}")

# Complex data structures often exhibit recursive patterns that require
# careful handling to prevent infinite generation while maintaining structural
# validity.

