import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Dict, Strategy

@dataclass
class TestResult:
    """Comprehensive test execution results"""
    passed: bool
    examples_tried: int
    shrink_iterations: int
    execution_time: float
    minimal_failing_case: Optional[Any] = None
    exception: Optional[Exception] = None
    complexity_reduction: float = 0.0
    coverage_info: Optional[Dict] = None

def test_property(property_func: Callable[[Any], bool], 
                 strategy: Strategy,
                 max_examples: int = 100,
                 random_seed: Optional[int] = None,
                 verbose: bool = False) -> TestResult:
    """Execute a comprehensive property-based test
    
    Args:
        property_func: Property function returning True for valid inputs
        strategy: Strategy for generating test inputs
        max_examples: Maximum test cases to generate before declaring success
        random_seed: Optional seed for reproducible test runs
        verbose: Whether to print progress information
        
    Returns:
        TestResult containing detailed execution information
    """
    start_time = time.time()
    random_state = random.Random(random_seed)
    
    if verbose:
        print(f"Testing property with up to {max_examples} examples")
        print(f"Random seed: {random_seed}")
    
    for example_count in range(max_examples):
        # Generate progressively more complex examples
        size = _calculate_size(example_count, max_examples)
        test_case = strategy.generate(random_state, size)
        
        if verbose and example_count % 20 == 0:
            print(f"  Generated example {example_count + 1}/{max_examples}")
        
        try:
            # Execute property function
            result = property_func(test_case)
            
            if not result:
                raise AssertionError("Property returned False")
                
        except Exception as e:
            # Property failed - begin comprehensive failure analysis
            if verbose:
                print(f"Property failed at example {example_count + 1}")
                print(f"Failure type: {type(e).__name__}")
            
            # Perform shrinking to find minimal failing case
            shrink_result = shrink_failure(
                lambda x: _test_property(property_func, x), 
                test_case, 
                strategy,
                max_iterations=500
            )
            
            execution_time = time.time() - start_time
            
            return TestResult(
                passed=False,
                examples_tried=example_count + 1,
                shrink_iterations=shrink_result.iterations,
                execution_time=execution_time,
                minimal_failing_case=shrink_result.minimal_case,
                exception=e,
                complexity_reduction=shrink_result.reduction_ratio
            )
    
    # All examples passed successfully
    execution_time = time.time() - start_time
    
    if verbose:
        print(f"Property passed on all {max_examples} examples")
        print(f"Total execution time: {execution_time:.3f}s")
    
    return TestResult(
        passed=True,
        examples_tried=max_examples,
        shrink_iterations=0,
        execution_time=execution_time
    )

def _calculate_size(example_num: int, max_examples: int) -> int:
    """Calculate appropriate size parameter for test generation"""
    # Start small and gradually increase complexity
    if max_examples <= 1:
        return 10
    
    # Linear growth from 1 to 50, with some examples at size 0
    progress = example_num / (max_examples - 1)
    if example_num < 3:
        return example_num  # Very simple cases first
    else:
        return int(1 + progress * 49)  # Scale from 1 to 50

# Example usage and demonstration
if __name__ == "__main__":
    # Test the framework with a simple property
    def test_list_length_property(lst):
        """Property: reversing a list twice should yield original"""
        return list(reversed(list(reversed(lst)))) == lst
    
    # Run property test
    result = test_property(
        test_list_length_property,
        ListStrategy(IntegerStrategy(-10, 10)),
        max_examples=50,
        random_seed=42,
        verbose=True
    )
    
    print(f"\nTest Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"Examples tried: {result.examples_tried}")
    print(f"Execution time: {result.execution_time:.3f}s")
    if not result.passed:
        print(f"Minimal failing case: {result.minimal_failing_case}")
        print(f"Shrinking iterations: {result.shrink_iterations}")

#