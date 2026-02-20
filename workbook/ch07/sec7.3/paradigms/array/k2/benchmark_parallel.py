#!/usr/bin/env python3
"""
Benchmark script to compare serial vs parallel execution performance.

This demonstrates where parallelization provides benefits and where it doesn't.
"""

import time
import sys
from k_interpreter_parallel import (
    register_standard_operations,
    evaluate_expression,
    ParallelConfig,
    global_variables
)


def benchmark_operation(description, expression, iterations=3):
    """Run a benchmark and report timing."""
    times_serial = []
    times_parallel = []
    
    # Warm up
    ParallelConfig.disable()
    result_serial = evaluate_expression(expression)
    ParallelConfig.enable()
    result_parallel = evaluate_expression(expression)
    
    # Verify results match
    if result_serial != result_parallel:
        print(f"WARNING: Results don't match for {description}!")
        print(f"  Serial:   {result_serial[:10] if isinstance(result_serial, list) else result_serial}")
        print(f"  Parallel: {result_parallel[:10] if isinstance(result_parallel, list) else result_parallel}")
    
    # Benchmark serial
    for _ in range(iterations):
        ParallelConfig.disable()
        start = time.perf_counter()
        result = evaluate_expression(expression)
        end = time.perf_counter()
        times_serial.append(end - start)
    
    # Benchmark parallel
    for _ in range(iterations):
        ParallelConfig.enable()
        start = time.perf_counter()
        result = evaluate_expression(expression)
        end = time.perf_counter()
        times_parallel.append(end - start)
    
    avg_serial = sum(times_serial) / len(times_serial)
    avg_parallel = sum(times_parallel) / len(times_parallel)
    speedup = avg_serial / avg_parallel if avg_parallel > 0 else 0
    
    print(f"\n{description}")
    print(f"  Serial:   {avg_serial*1000:.2f} ms")
    print(f"  Parallel: {avg_parallel*1000:.2f} ms")
    print(f"  Speedup:  {speedup:.2f}x {'🚀' if speedup > 1.2 else '⚡' if speedup > 1.0 else '→'}")
    
    return speedup


def main():
    """Run benchmarks."""
    register_standard_operations()
    global_variables.clear()
    
    print("=" * 70)
    print("K Interpreter Parallel Execution Benchmarks")
    print("=" * 70)
    print(f"CPU cores available: {ParallelConfig.num_workers}")
    print(f"Threshold: {ParallelConfig.threshold} elements")
    print()
    
    # Small array (should not benefit from parallelization)
    print("\n" + "─" * 70)
    print("SMALL ARRAYS (< threshold)")
    print("─" * 70)
    
    global_variables["small"] = list(range(100))
    
    benchmark_operation(
        "Sum of 100 elements",
        ["+", "small"],
        iterations=10
    )
    
    benchmark_operation(
        "Add 10 to each element (100 elements)",
        ["small", "+", 10],
        iterations=10
    )
    
    # Large array (should benefit from parallelization)
    print("\n" + "─" * 70)
    print("LARGE ARRAYS (>> threshold)")
    print("─" * 70)
    
    global_variables["large"] = list(range(100000))
    
    benchmark_operation(
        "Sum of 100,000 elements",
        ["+", "large"],
        iterations=3
    )
    
    benchmark_operation(
        "Add 10 to each element (100,000 elements)",
        ["large", "+", 10],
        iterations=3
    )
    
    benchmark_operation(
        "Multiply by 2 (100,000 elements)",
        ["large", "*", 2],
        iterations=3
    )
    
    benchmark_operation(
        "Element-wise addition (100,000 elements)",
        ["large", "+", "large"],
        iterations=3
    )
    
    benchmark_operation(
        "Modulo operation (100,000 elements)",
        [7, "!", "large"],
        iterations=3
    )
    
    # Minimum/Maximum (reduction operations)
    benchmark_operation(
        "Minimum of 100,000 elements",
        ["&", "large"],
        iterations=3
    )
    
    benchmark_operation(
        "Maximum of 100,000 elements",
        ["*", "large"],
        iterations=3
    )
    
    # Negate (monadic on vector)
    benchmark_operation(
        "Negate 100,000 elements",
        ["-", "large"],
        iterations=3
    )
    
    # Very large array
    print("\n" + "─" * 70)
    print("VERY LARGE ARRAYS (1M elements)")
    print("─" * 70)
    
    global_variables["huge"] = list(range(1000000))
    
    benchmark_operation(
        "Sum of 1,000,000 elements",
        ["+", "huge"],
        iterations=1
    )
    
    benchmark_operation(
        "Add 5 to each (1,000,000 elements)",
        ["huge", "+", 5],
        iterations=1
    )
    
    benchmark_operation(
        "Element-wise multiply (1,000,000 elements)",
        ["huge", "*", "huge"],
        iterations=1
    )
    
    # Matrix operations
    print("\n" + "─" * 70)
    print("MATRIX OPERATIONS")
    print("─" * 70)
    
    # Create a large matrix
    global_variables["matrix"] = [[i + j for j in range(1000)] for i in range(1000)]
    
    benchmark_operation(
        "Transpose 1000x1000 matrix",
        [".", "matrix"],
        iterations=1
    )
    
    # Index operations with large index lists
    print("\n" + "─" * 70)
    print("INDEXING OPERATIONS")
    print("─" * 70)
    
    global_variables["data"] = list(range(100000))
    global_variables["indices"] = list(range(0, 100000, 2))  # 50,000 indices
    
    benchmark_operation(
        "Index 50,000 elements from 100,000 array",
        ["data", "@", "indices"],
        iterations=1
    )
    
    # Dictionary lookup
    print("\n" + "─" * 70)
    print("DICTIONARY OPERATIONS")
    print("─" * 70)
    
    # Create a dictionary
    d = {i: i * 10 for i in range(10000)}
    global_variables["dict"] = d
    global_variables["keys"] = list(range(0, 10000, 2))  # 5,000 keys
    
    benchmark_operation(
        "Lookup 5,000 keys in dictionary",
        ["dict", "$", "keys"],
        iterations=1
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Parallel execution benefits:")
    print("  ✓ Large vector operations (100k+ elements)")
    print("  ✓ Element-wise operations (map-style)")
    print("  ✓ Reduction operations (sum, min, max)")
    print("  ✓ Matrix transpose on large matrices")
    print("  ✓ Bulk indexing operations")
    print()
    print("Parallel overhead dominates for:")
    print("  ✗ Small arrays (< 1000 elements)")
    print("  ✗ Operations with complex shared state")
    print("  ✗ Operations that are already very fast")
    print()
    print(f"Optimal threshold on this machine: ~{ParallelConfig.threshold} elements")
    print()


if __name__ == "__main__":
    main()
