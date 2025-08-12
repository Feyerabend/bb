from typing import Callable, Any, Tuple
import time

class ShrinkingResult:
    """Results from the shrinking process"""
    def __init__(self, minimal_case: Any, iterations: int, 
                 time_spent: float, reduction_ratio: float):
        self.minimal_case = minimal_case
        self.iterations = iterations
        self.time_spent = time_spent
        self.reduction_ratio = reduction_ratio

def shrink_failure(property_func: Callable[[Any], bool], 
                  failing_input: Any, 
                  strategy: Strategy, 
                  max_iterations: int = 1000,
                  max_time: float = 30.0) -> ShrinkingResult:
    """Find minimal failing case through systematic reduction
    
    Args:
        property_func: Property that should return True for valid inputs
        failing_input: Known failing input to be minimized
        strategy: Strategy with shrink method for the input type
        max_iterations: Maximum number of shrinking attempts
        max_time: Maximum time to spend shrinking (seconds)
        
    Returns:
        ShrinkingResult with minimal case and process statistics
    """
    start_time = time.time()
    current = failing_input
    iterations = 0
    original_complexity = _estimate_complexity(failing_input)
    
    # Verify the input actually fails
    if _test_property(property_func, current):
        raise ValueError("Input doesn't actually fail the property")
    
    print(f"Starting shrinking from complexity {original_complexity}")
    
    while (iterations < max_iterations and 
           time.time() - start_time < max_time):
        
        found_simpler = False
        
        # Try all shrinking candidates from current state
        for candidate in strategy.shrink(current):
            iterations += 1
            
            # Check termination conditions
            if (iterations >= max_iterations or 
                time.time() - start_time >= max_time):
                break
            
            # Test if this simplified version still fails
            if not _test_property(property_func, candidate):
                current = candidate
                found_simpler = True
                complexity = _estimate_complexity(current)
                print(f"  Shrunk to complexity {complexity} after {iterations} iterations")
                break  # Greedy: take first improvement found
        
        if not found_simpler:
            break  # No further simplification possible
    
    final_complexity = _estimate_complexity(current)
    reduction_ratio = (original_complexity - final_complexity) / max(original_complexity, 1)
    time_spent = time.time() - start_time
    
    print(f"Shrinking complete: {original_complexity} → {final_complexity} "
          f"({reduction_ratio:.2%} reduction) in {iterations} iterations")
    
    return ShrinkingResult(current, iterations, time_spent, reduction_ratio)

def _test_property(property_func: Callable, test_input: Any) -> bool:
    """Test property function, handling exceptions as failures"""
    try:
        result = property_func(test_input)
        return bool(result)  # Ensure boolean return
    except (AssertionError, Exception):
        return False  # Any exception counts as property failure

def _estimate_complexity(value: Any) -> int:
    """Estimate the structural complexity of a test value"""
    if value is None:
        return 0
    elif isinstance(value, (bool, int, float)):
        return abs(int(value)) if isinstance(value, (int, float)) else 1
    elif isinstance(value, str):
        return len(value)
    elif isinstance(value, (list, tuple)):
        return len(value) + sum(_estimate_complexity(item) for item in value)
    elif isinstance(value, dict):
        return (len(value) + 
                sum(_estimate_complexity(k) + _estimate_complexity(v) 
                    for k, v in value.items()))
    else:
        return 1  # Unknown types get minimal complexity
