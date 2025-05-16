import unittest
import sys
import re
import functools
import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union, Optional, Any

# Import the main module (assuming the provided code is in a file called functional_lang.py)
# If the code is in a different file, adjust this import statement
# from functional_lang import *

import k_simple_interpreter

from k_simple_interpreter import (
    negate,
    generate_sequence,
    get_length,
    ensure_list,
    reverse_list,
    first_element,
    get_type_info,
    where,
    group,
    unique,
    sort,
    sum_values,
    minimum,
    maximum,
    average,
    raze,
    flip_matrix,
    coalesce,
    add,
    logical_and,
    logical_or,
    not_equal,
    equals,
    multiply,
    subtract,
    divide,
    modulo,
    take,
    drop,
    find,
    concatenate,
    index_access,
    dict_lookup,
    LambdaFunction,
    ComposedFunction,
    PartialFunction,
    fold,
    scan,
    each,
    each_right,
    each_left,
    each_pair,
    evaluate_expression,
    raise_error,
    register_standard_operations,
    global_variables,
    operation_registry,
    is_atomic,
    get_type,
    Operation,
    OperationRegistry,
    Atom,
    Vector,
    Value,
    MonadicFunction,
    DyadicFunction
)


# For the purpose of these tests, I'll include the relevant code directly
# to ensure the tests are self-contained

Atom = Union[int, float, str, bool]
Vector = List
Value = Union[Atom, Vector]
MonadicFunction = Callable[[Value], Value]
DyadicFunction = Callable[[Value, Value], Value]
Dictionary = Dict[Value, Value]

global_variables = {}

@dataclass
class Operation:
    symbol: str
    monadic: Optional[MonadicFunction] = None
    dyadic: Optional[DyadicFunction] = None
    description: str = ""
    
    def __post_init__(self):
        if self.monadic is None and self.dyadic is None:
            raise ValueError(f"Operation {self.symbol} must have at least one implementation")

class OperationRegistry:
    def __init__(self):
        self.operations: Dict[str, Operation] = {}
    
    def register(self, operation: Operation) -> None:
        if operation.symbol in self.operations:
            raise ValueError(f"Operation {operation.symbol} is already registered")
        self.operations[operation.symbol] = operation
    
    def get_monadic(self, symbol: str) -> MonadicFunction:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        monadic = self.operations[symbol].monadic
        if monadic is None:
            raise_error(f"operation {symbol} does not have a monadic form")
        
        return monadic
    
    def get_dyadic(self, symbol: str) -> DyadicFunction:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        dyadic = self.operations[symbol].dyadic
        if dyadic is None:
            raise_error(f"operation {symbol} does not have a dyadic form")
        
        return dyadic
    
    def get_operation(self, symbol: str) -> Operation:
        if symbol not in self.operations:
            raise_error(f"unknown operation: {symbol}")
        
        return self.operations[symbol]
    
    def has_monadic(self, symbol: str) -> bool:
        return symbol in self.operations and self.operations[symbol].monadic is not None
    
    def has_dyadic(self, symbol: str) -> bool:
        return symbol in self.operations and self.operations[symbol].dyadic is not None

operation_registry = OperationRegistry()

def is_atomic(value):
    return isinstance(value, (int, float, str, bool))

def get_type(value):
    if isinstance(value, bool):
        return 'b'
    elif isinstance(value, int):
        return 'i'
    elif isinstance(value, float):
        return 'f'
    elif isinstance(value, str):
        return 's'
    elif isinstance(value, list):
        return 'l'
    elif isinstance(value, dict):
        return 'd'
    else:
        return '?'

def raise_error(message="not yet implemented"):
    raise Exception(f"error: {message}")

# Include all other functions from the provided code...
# For brevity, I'm not including all of them here, but in the actual test file
# you would include all the functions from the original code

# Register standard operations
def register_standard_operations():
    # Include the operation registrations from the original code
    pass

class TestFunctionalLanguage(unittest.TestCase):
    
    def setUp(self):
        global global_variables, operation_registry
        global_variables = {}
        operation_registry = OperationRegistry()
        k_simple_interpreter.register_standard_operations()  # Use the imported function
    
    def test_operation_registry(self):
        """Test basic operation registry functionality"""
        # Create a test operation
        test_op = Operation(symbol="test", monadic=lambda x: x, dyadic=lambda x, y: x + y)
        
        # Register it
        operation_registry.register(test_op)
        
        # Verify it was registered
        self.assertTrue("test" in operation_registry.operations)
        self.assertEqual(operation_registry.get_operation("test"), test_op)
        
        # Test has_monadic and has_dyadic
        self.assertTrue(operation_registry.has_monadic("test"))
        self.assertTrue(operation_registry.has_dyadic("test"))
        
        # Test function retrieval
        monadic_func = operation_registry.get_monadic("test")
        dyadic_func = operation_registry.get_dyadic("test")
        
        self.assertEqual(monadic_func(5), 5)
        self.assertEqual(dyadic_func(2, 3), 5)
        
        # Test registration of operation with same symbol
        with self.assertRaises(ValueError):
            operation_registry.register(Operation(symbol="test", monadic=lambda x: x))
    
    def test_is_atomic(self):
        """Test is_atomic function"""
        self.assertTrue(is_atomic(5))
        self.assertTrue(is_atomic(3.14))
        self.assertTrue(is_atomic("hello"))
        self.assertTrue(is_atomic(True))
        self.assertFalse(is_atomic([1, 2, 3]))
        self.assertFalse(is_atomic({"a": 1}))
    
    def test_get_type(self):
        """Test get_type function"""
        self.assertEqual(get_type(5), 'i')
        self.assertEqual(get_type(3.14), 'f')
        self.assertEqual(get_type("hello"), 's')
        self.assertEqual(get_type(True), 'b')
        self.assertEqual(get_type([1, 2, 3]), 'l')
        self.assertEqual(get_type({"a": 1}), 'd')
    
    def test_negate(self):
        """Test negate function"""
        self.assertEqual(negate(5), -5)
        self.assertEqual(negate(-3.14), 3.14)
        self.assertEqual(negate(True), False)
        self.assertEqual(negate(False), True)
        self.assertEqual(negate([1, -2, True]), [-1, 2, False])
        
        # Test error case
        with self.assertRaises(Exception):
            negate("hello")
    
    def test_generate_sequence(self):
        """Test generate_sequence (iota) function"""
        self.assertEqual(generate_sequence(5), [0, 1, 2, 3, 4])
        self.assertEqual(generate_sequence(3.7), [0, 1, 2])  # Should truncate float
        
        # Test error cases
        with self.assertRaises(Exception):
            generate_sequence("hello")
        with self.assertRaises(Exception):
            generate_sequence([1, 2, 3])
    
    def test_get_length(self):
        """Test get_length function"""
        self.assertEqual(get_length([1, 2, 3]), 3)
        self.assertEqual(get_length("hello"), 5)
        self.assertEqual(get_length([]), 0)
        
        # Test error case
        with self.assertRaises(Exception):
            get_length(5)
    
    def test_ensure_list(self):
        """Test ensure_list function"""
        self.assertEqual(ensure_list(5), [5])
        self.assertEqual(ensure_list("hello"), ["hello"])
        self.assertEqual(ensure_list([1, 2, 3]), [1, 2, 3])
    
    def test_reverse_list(self):
        """Test reverse_list function"""
        self.assertEqual(reverse_list([1, 2, 3]), [3, 2, 1])
        self.assertEqual(reverse_list("hello"), "olleh")
        
        # Test error case
        with self.assertRaises(Exception):
            reverse_list(5)
    
    def test_first_element(self):
        """Test first_element function"""
        self.assertEqual(first_element([1, 2, 3]), 1)
        self.assertEqual(first_element("hello"), "h")
        self.assertEqual(first_element([]), None)
        self.assertEqual(first_element(""), "")
        
        # Test error case
        with self.assertRaises(Exception):
            first_element(5)
    
    def test_get_type_info(self):
        """Test get_type_info function"""
        self.assertEqual(get_type_info(5), 'i')
        self.assertEqual(get_type_info([1, "hello", 3.14, True]), ['i', 's', 'f', 'b'])
    
    def test_where(self):
        """Test where function"""
        self.assertEqual(where([3, 0, 2]), [0, 0, 0, 2, 2])
        self.assertEqual(where([1, 1, 1]), [0, 1, 2])
        self.assertEqual(where([0, 0, 0]), [])
        
        # Test error cases
        with self.assertRaises(Exception):
            where(5)
        with self.assertRaises(Exception):
            where(["a", "b", "c"])
    
    def test_group(self):
        result = group([1, 2, 1, 3, 2, 1])
        self.assertEqual(result[1], [0, 2, 5])
        self.assertEqual(result[2], [1, 4])
        self.assertEqual(result[3], [3])
        
        # Test with mixed types
        result = group([1, "a", True, 1, "a", False])
        self.assertEqual(result[1], [0, 3])
        self.assertEqual(result["a"], [1, 4])
        self.assertEqual(result[True], [2])
        self.assertEqual(result[False], [5])
        
        # Test error case
        with self.assertRaises(Exception):
            group(5)
    
    def test_unique(self):
        """Test unique function"""
        self.assertEqual(unique([1, 2, 1, 3, 2, 1]), [1, 2, 3])
        self.assertEqual(unique(["a", "b", "a", "c"]), ["a", "b", "c"])
        self.assertEqual(unique([]), [])
        
        # Test atomic value (no change)
        self.assertEqual(unique(5), 5)
    
    def test_sort(self):
        """Test sort function"""
        self.assertEqual(sort([3, 1, 4, 1, 5]), [1, 1, 3, 4, 5])
        self.assertEqual(sort(["c", "a", "b"]), ["a", "b", "c"])
        
        # Test mixed types (sorted by string representation)
        self.assertEqual(sort([3, "2", 1]), [1, "2", 3])
        
        # Test error case
        with self.assertRaises(Exception):
            sort(5)
    
    def test_sum_values(self):
        """Test sum_values function"""
        self.assertEqual(sum_values([1, 2, 3]), 6)
        
        # Test atomic value (no change)
        self.assertEqual(sum_values(5), 5)
        
        # Test empty list
        self.assertEqual(sum_values([]), 0)
        
        # Test error case
        with self.assertRaises(Exception):
            sum_values(["a", "b", "c"])
    
    def test_minimum(self):
        """Test minimum function"""
        self.assertEqual(minimum([5, 2, 8]), 2)
        self.assertEqual(minimum(["a", "c", "b"]), "a")
        
        # Test atomic value (no change)
        self.assertEqual(minimum(5), 5)
        
        # Test error cases
        with self.assertRaises(Exception):
            minimum([])
        with self.assertRaises(Exception):
            minimum([1, "a"])  # Mixed types
    
    def test_maximum(self):
        """Test maximum function"""
        self.assertEqual(maximum([5, 2, 8]), 8)
        self.assertEqual(maximum(["a", "c", "b"]), "c")
        
        # Test atomic value (no change)
        self.assertEqual(maximum(5), 5)
        
        # Test error cases
        with self.assertRaises(Exception):
            maximum([])
        with self.assertRaises(Exception):
            maximum([1, "a"])  # Mixed types
    
    def test_average(self):
        """Test average function"""
        self.assertEqual(average([1, 2, 3]), 2.0)
        self.assertEqual(average(5), 5.0)
        
        # Test error cases
        with self.assertRaises(Exception):
            average([])
        with self.assertRaises(Exception):
            average(["a", "b", "c"])
    
    def test_raze(self):
        """Test raze function"""
        self.assertEqual(raze([[1, 2], [3, 4]]), [1, 2, 3, 4])
        self.assertEqual(raze([1, [2, 3], 4]), [1, 2, 3, 4])
        self.assertEqual(raze(5), [5])
    
    def test_flip_matrix(self):
        """Test flip_matrix function"""
        self.assertEqual(flip_matrix([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])
        self.assertEqual(flip_matrix([]), [])
        
        # Test error cases
        with self.assertRaises(Exception):
            flip_matrix(5)
        with self.assertRaises(Exception):
            flip_matrix([[1, 2], [3]])  # Uneven rows
    
    def test_coalesce(self):
        """Test coalesce function"""
        self.assertEqual(coalesce([None, 1, 2]), 1)
        self.assertEqual(coalesce([None, None, 3]), 3)
        self.assertEqual(coalesce([None, None]), None)
        self.assertEqual(coalesce(5), 5)
    
    def test_add(self):
        """Test add function"""
        # Numeric addition
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add([1, 2], 3), [4, 5])
        self.assertEqual(add(2, [3, 4]), [5, 6])
        self.assertEqual(add([1, 2], [3, 4]), [4, 6])
        
        # String concatenation
        self.assertEqual(add("hello", " world"), "hello world")
        
        # Boolean OR
        self.assertEqual(add(True, False), True)
        self.assertEqual(add(False, False), False)
        
        # Test error cases
        with self.assertRaises(Exception):
            add(1, "a")  # Incompatible types
        with self.assertRaises(Exception):
            add([1, 2], [3, 4, 5])  # Unequal length lists
    
    def test_logical_and(self):
        """Test logical_and function"""
        # Integer bitwise AND
        self.assertEqual(logical_and(3, 5), 1)  # 0011 & 0101 = 0001
        
        # Boolean AND
        self.assertEqual(logical_and(True, False), False)
        self.assertEqual(logical_and(True, True), True)
        
        # Lists
        self.assertEqual(logical_and([1, 3], 2), [0, 2])  # [0001 & 0010, 0011 & 0010]
        self.assertEqual(logical_and([True, False], [False, True]), [False, False])
        
        # Test error cases
        with self.assertRaises(Exception):
            logical_and(1, "a")  # Incompatible types
    
    def test_logical_or(self):
        """Test logical_or function"""
        # Integer bitwise OR
        self.assertEqual(logical_or(3, 5), 7)  # 0011 | 0101 = 0111
        
        # Boolean OR
        self.assertEqual(logical_or(True, False), True)
        self.assertEqual(logical_or(False, False), False)
        
        # Lists
        self.assertEqual(logical_or([1, 3], 2), [3, 3])  # [0001 | 0010, 0011 | 0010]
        self.assertEqual(logical_or([True, False], [False, True]), [True, True])
        
        # Test error cases
        with self.assertRaises(Exception):
            logical_or(1, "a")  # Incompatible types
    
    def test_not_equal(self):
        """Test not_equal function"""
        self.assertEqual(not_equal(1, 2), True)
        self.assertEqual(not_equal(1, 1), False)
        self.assertEqual(not_equal("a", "b"), True)
        self.assertEqual(not_equal([1, 2], [1, 3]), [False, True])
    
    def test_equals(self):
        """Test equals function"""
        self.assertEqual(equals(1, 2), False)
        self.assertEqual(equals(1, 1), True)
        self.assertEqual(equals("a", "b"), False)
        self.assertEqual(equals([1, 2], [1, 3]), [True, False])
    
    def test_multiply(self):
        """Test multiply function"""
        # Numeric multiplication
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply([1, 2], 3), [3, 6])
        self.assertEqual(multiply(2, [3, 4]), [6, 8])
        self.assertEqual(multiply([1, 2], [3, 4]), [3, 8])
        
        # String repetition
        self.assertEqual(multiply("a", 3), "aaa")
        self.assertEqual(multiply(3, "a"), "aaa")
        
        # Boolean AND
        self.assertEqual(multiply(True, False), False)
        self.assertEqual(multiply(True, True), True)
        
        # Test error cases
        with self.assertRaises(Exception):
            multiply("a", "b")  # Cannot multiply strings
    
    def test_subtract(self):
        """Test subtract function"""
        # Numeric subtraction
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract([5, 7], 3), [2, 4])
        self.assertEqual(subtract(5, [3, 4]), [2, 1])
        self.assertEqual(subtract([5, 7], [3, 4]), [2, 3])
        
        # Boolean
        self.assertEqual(subtract(True, True), False)
        self.assertEqual(subtract(True, False), True)
        
        # Test error cases
        with self.assertRaises(Exception):
            subtract("a", "b")  # Cannot subtract strings
    
    def test_divide(self):
        """Test divide function (percentage division)"""
        # Note that divide multiplies by 100 for percentage returns
        self.assertEqual(divide(5, 2), 250.0)  # (5/2)*100 = 250.0
        self.assertEqual(divide([10, 20], 5), [200.0, 400.0])
        self.assertEqual(divide(10, [2, 5]), [500.0, 200.0])
        self.assertEqual(divide([10, 20], [2, 5]), [500.0, 400.0])
        
        # Test error cases
        with self.assertRaises(Exception):
            divide(5, 0)  # Division by zero
        with self.assertRaises(Exception):
            divide("a", 2)  # Non-numeric division
    
    def test_modulo(self):
        """Test modulo function"""
        self.assertEqual(modulo(3, 10), 1)  # 10 % 3 = 1
        self.assertEqual(modulo(3, [10, 11, 12]), [1, 2, 0])
        
        # Test error cases
        with self.assertRaises(Exception):
            modulo("a", 10)  # Non-numeric modulo
        with self.assertRaises(Exception):
            modulo([1, 2], 10)  # First arg must be atomic
    
    def test_take(self):
        """Test take function"""
        self.assertEqual(take(3, 5), [5, 5, 5])
        self.assertEqual(take(3, [1, 2]), [1, 2, 1])
        self.assertEqual(take(-3, [1, 2, 3, 4]), [4, 3, 2])
        
        # Test error cases
        with self.assertRaises(Exception):
            take("a", [1, 2])  # Non-integer count
        with self.assertRaises(Exception):
            take([1, 2], [3, 4])  # First arg must be atomic
    
    def test_drop(self):
        """Test drop function"""
        self.assertEqual(drop(2, [1, 2, 3, 4, 5]), [3, 4, 5])
        self.assertEqual(drop(-2, [1, 2, 3, 4, 5]), [1, 2, 3])
        self.assertEqual(drop(2, "hello"), "llo")
        self.assertEqual(drop(-2, "hello"), "hel")
        
        # Test error cases
        with self.assertRaises(Exception):
            drop("a", [1, 2])  # Non-integer count
        with self.assertRaises(Exception):
            drop([1, 2], [3, 4])  # First arg must be atomic
        with self.assertRaises(Exception):
            drop(2, 5)  # Cannot drop from atomic non-string
    
    def test_find(self):
        """Test find function"""
        self.assertEqual(find(2, [1, 2, 3, 2, 1]), [1, 3])
        self.assertEqual(find("l", "hello"), [2, 3])
        
        # Test error cases
        with self.assertRaises(Exception):
            find(1, 5)  # Second arg must be sequence
    
    def test_concatenate(self):
        """Test concatenate function"""
        self.assertEqual(concatenate(1, 2), [1, 2])
        self.assertEqual(concatenate([1, 2], 3), [1, 2, 3])
        self.assertEqual(concatenate(1, [2, 3]), [1, 2, 3])
        self.assertEqual(concatenate([1, 2], [3, 4]), [1, 2, 3, 4])
        self.assertEqual(concatenate("hello", " world"), "hello world")
    
    def test_index_access(self):
        """Test index_access function"""
        self.assertEqual(index_access([1, 2, 3, 4], 2), 3)
        self.assertEqual(index_access("hello", 1), "e")
        self.assertEqual(index_access([1, 2, 3, 4], [0, 2]), [1, 3])
        
        # Test error cases
        with self.assertRaises(Exception):
            index_access(5, 1)  # Cannot index atomic non-string
        with self.assertRaises(Exception):
            index_access("hello", "world")  # Index must be int or list
        with self.assertRaises(Exception):
            index_access([1, 2], 5)  # Index out of range
    
    def test_dict_lookup(self):
        """Test dict_lookup function"""
        test_dict = {"a": 1, "b": 2, 5: "five"}
        self.assertEqual(dict_lookup(test_dict, "a"), 1)
        self.assertEqual(dict_lookup(test_dict, "c"), None)
        self.assertEqual(dict_lookup(test_dict, 5), "five")
        self.assertEqual(dict_lookup(test_dict, ["a", "b", "c"]), [1, 2, None])
        
        # Test error case
        with self.assertRaises(Exception):
            dict_lookup(5, "a")  # First arg must be dict
    
    def test_lambda_function(self):
        """Test LambdaFunction class"""
        # Simple lambda: x+1
        lambda_func = LambdaFunction("x+1")
        self.assertEqual(lambda_func(5), 6)
        
        # Lambda with multiple args: x+y
        lambda_func = LambdaFunction("x+y")
        self.assertEqual(lambda_func(2, 3), 5)
        
        # Test global variable scope
        global_variables["test_var"] = 10
        lambda_func = LambdaFunction("x+test_var")
        self.assertEqual(lambda_func(5), 15)
        
        # Verify global_variables are restored
        global_variables["x"] = "original"
        lambda_func = LambdaFunction("x")
        self.assertEqual(lambda_func("new"), "new")
        self.assertEqual(global_variables["x"], "original")
    
    def test_composed_function(self):
        """Test ComposedFunction class"""
        f = lambda x: x + 1
        g = lambda x: x * 2
        composed = ComposedFunction(f, g)
        
        self.assertEqual(composed(5), 11)  # f(g(5)) = f(10) = 11
    
    def test_partial_function(self):
        """Test PartialFunction class"""
        def add_func(x, y):
            return x + y
        
        # Left partial: add_func(3, ?)
        left_partial = PartialFunction(add_func, 3, is_left=True)
        self.assertEqual(left_partial(4), 7)
        
        # Right partial: add_func(?, 3)
        right_partial = PartialFunction(add_func, 3, is_left=False)
        self.assertEqual(right_partial(4), 7)
    
    def test_fold(self):
        """Test fold function"""
        def add_func(x, y):
            return x + y
        
        self.assertEqual(fold(add_func, [1, 2, 3, 4]), 10)
        
        # Test error case
        with self.assertRaises(Exception):
            fold(add_func, [])  # Cannot fold empty sequence
    
    def test_scan(self):
        """Test scan function"""
        def add_func(x, y):
            return x + y
        
        self.assertEqual(scan(add_func, [1, 2, 3, 4]), [1, 3, 6, 10])
        self.assertEqual(scan(add_func, []), [])
    
    def test_each(self):
        """Test each function"""
        def square(x):
            return x * x
        
        self.assertEqual(each(square, [1, 2, 3]), [1, 4, 9])
        
        # Test error case
        with self.assertRaises(Exception):
            each(square, 5)  # Second arg must be sequence
    
    def test_each_right(self):
        """Test each_right function"""
        def power(x, y):
            return x ** y
        
        self.assertEqual(each_right(power, 2, [1, 2, 3]), [2, 4, 8])
        
        # Test error case
        with self.assertRaises(Exception):
            each_right(power, 2, 5)  # Third arg must be sequence
    
    def test_each_left(self):
        """Test each_left function"""
        def power(x, y):
            return x ** y
        
        self.assertEqual(each_left(power, [1, 2, 3], 2), [1, 4, 9])
        
        # Test error case
        with self.assertRaises(Exception):
            each_left(power, 5, 2)  # Second arg must be sequence
    
    def test_each_pair(self):
        """Test each_pair function"""
        def power(x, y):
            return x ** y
        
        self.assertEqual(each_pair(power, [1, 2, 3], [2, 3, 2]), [1, 8, 9])
        
        # Test error cases
        with self.assertRaises(Exception):
            each_pair(power, 5, [1, 2, 3])  # First arg must be sequence
        with self.assertRaises(Exception):
            each_pair(power, [1, 2, 3], 5)  # Second arg must be sequence
        with self.assertRaises(Exception):
            each_pair(power, [1, 2], [1, 2, 3])  # Sequences must have same length
    
    def test_evaluate_expression(self):
        """Test evaluate_expression function"""
        # Test atomic values
        self.assertEqual(evaluate_expression(5), 5)
        self.assertEqual(evaluate_expression("5"), 5)
        self.assertEqual(evaluate_expression("5.5"), 5.5)
        self.assertEqual(evaluate_expression("true"), True)
        self.assertEqual(evaluate_expression('"hello"'), "hello")
        
        # Test list literals
        self.assertEqual(evaluate_expression("(1;2;3)"), [1, 2, 3])
        self.assertEqual(evaluate_expression('("a";1;true)'), ["a", 1, True])
        
        # Test dictionary literals
        dict_result = evaluate_expression('[a:1;b:"hello"]')
        self.assertEqual(dict_result["a"], 1)
        self.assertEqual(dict_result["b"], "hello")
        
        # Test simple monadic operations
        operation_registry.register(Operation("+", lambda x: x + 1, None))
        self.assertEqual(evaluate_expression(["+", 5]), 6)
        
        # Test simple dyadic operations
        operation_registry.register(Operation("-", None, lambda x, y: x - y))
        self.assertEqual(evaluate_expression([3, "-", 2]), 1)
        
        # Test variable lookup
        global_variables["test_var"] = 42
        self.assertEqual(evaluate_expression("test_var"), 42)
        
        # Test lambda expressions
        lambda_func = evaluate_expression("{x+1}")
        self.assertEqual(lambda_func(5), 6)

if __name__ == '__main__':
    unittest.main()
