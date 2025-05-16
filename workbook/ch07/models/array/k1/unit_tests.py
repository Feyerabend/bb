import unittest
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

class TestFunctionalLanguage(unittest.TestCase):
    
    def setUp(self):
        global global_variables, operation_registry
        global_variables = {}
        operation_registry = OperationRegistry()
        register_standard_operations()
    
    def test_operation_registry(self):
        test_op = Operation(symbol="test", monadic=lambda x: x, dyadic=lambda x, y: x + y)
        operation_registry.register(test_op)
        self.assertTrue("test" in operation_registry.operations)
        self.assertEqual(operation_registry.get_operation("test"), test_op)
        self.assertTrue(operation_registry.has_monadic("test"))
        self.assertTrue(operation_registry.has_dyadic("test"))
        monadic_func = operation_registry.get_monadic("test")
        dyadic_func = operation_registry.get_dyadic("test")
        self.assertEqual(monadic_func(5), 5)
        self.assertEqual(dyadic_func(2, 3), 5)
        operation_registry.register(Operation(symbol="test", monadic=lambda x: x))
    
    def test_is_atomic(self):
        self.assertTrue(is_atomic(5))
        self.assertTrue(is_atomic(3.14))
        self.assertTrue(is_atomic("hello"))
        self.assertTrue(is_atomic(True))
        self.assertFalse(is_atomic([1, 2, 3]))
        self.assertFalse(is_atomic({"a": 1}))
    
    def test_get_type(self):
        self.assertEqual(get_type(5), 'i')
        self.assertEqual(get_type(3.14), 'f')
        self.assertEqual(get_type("hello"), 's')
        self.assertEqual(get_type(True), 'b')
        self.assertEqual(get_type([1, 2, 3]), 'l')
        self.assertEqual(get_type({"a": 1}), 'd')
    
    def test_negate(self):
        self.assertEqual(negate(5), -5)
        self.assertEqual(negate(-3.14), 3.14)
        self.assertEqual(negate(True), False)
        self.assertEqual(negate(False), True)
        self.assertEqual(negate([1, -2, True]), [-1, 2, False])
        with self.assertRaises(Exception):
            negate("hello")
    
    def test_generate_sequence(self):
        self.assertEqual(generate_sequence(5), [0, 1, 2, 3, 4])
        self.assertEqual(generate_sequence(3.7), [0, 1, 2])
        with self.assertRaises(Exception):
            generate_sequence("hello")
        with self.assertRaises(Exception):
            generate_sequence([1, 2, 3])
    
    def test_get_length(self):
        self.assertEqual(get_length([1, 2, 3]), 3)
        self.assertEqual(get_length("hello"), 5)
        self.assertEqual(get_length([]), 0)
        with self.assertRaises(Exception):
            get_length(5)
    
    def test_ensure_list(self):
        self.assertEqual(ensure_list(5), [5])
        self.assertEqual(ensure_list("hello"), ["hello"])
        self.assertEqual(ensure_list([1, 2, 3]), [1, 2, 3])
    
    def test_reverse_list(self):
        self.assertEqual(reverse_list([1, 2, 3]), [3, 2, 1])
        self.assertEqual(reverse_list("hello"), "olleh")
        with self.assertRaises(Exception):
            reverse_list(5)
    
    def test_first_element(self):
        self.assertEqual(first_element([1, 2, 3]), 1)
        self.assertEqual(first_element("hello"), "h")
        self.assertEqual(first_element([]), None)
        self.assertEqual(first_element(""), "")
        with self.assertRaises(Exception):
            first_element(5)
    
    def test_get_type_info(self):
        self.assertEqual(get_type_info(5), 'i')
        self.assertEqual(get_type_info([1, "hello", 3.14, True]), ['i', 's', 'f', 'b'])
    
    def test_where(self):
        self.assertEqual(where([3, 0, 2]), [0, 0, 0, 2, 2])
        self.assertEqual(where([1, 1, 1]), [0, 1, 2])
        self.assertEqual(where([0, 0, 0]), [])
        with self.assertRaises(Exception):
            where(5)
        with self.assertRaises(Exception):
            where(["a", "b", "c"])
    
    def test_group(self):
        result = group([1, 2, 1, 3, 2, 1])
        self.assertEqual(result[1], [0, 2, 5])
        self.assertEqual(result[2], [1, 4])
        self.assertEqual(result[3], [3])
        result = group([1, "a", True, 1, "a", False])
        self.assertEqual(result[1], [0, 3])
        self.assertEqual(result["a"], [1, 4])
        self.assertEqual(result[True], [2])
        self.assertEqual(result[False], [5])
        with self.assertRaises(Exception):
            group(5)
    
    def test_unique(self):
        self.assertEqual(unique([1, 2, 1, 3, 2, 1]), [1, 2, 3])
        self.assertEqual(unique(["a", "b", "a", "c"]), ["a", "b", "c"])
        self.assertEqual(unique([]), [])
        self.assertEqual(unique(5), 5)
    
    def test_sort(self):
        self.assertEqual(sort([3, 1, 4, 1, 5]), [1, 1, 3, 4, 5])
        self.assertEqual(sort(["c", "a", "b"]), ["a", "b", "c"])
        self.assertEqual(sort([3, "2", 1]), [1, "2", 3])
        with self.assertRaises(Exception):
            sort(5)
    
    def test_sum_values(self):
        self.assertEqual(sum_values([1, 2, 3]), 6)
        self.assertEqual(sum_values(5), 5)
        self.assertEqual(sum_values([]), 0)
        with self.assertRaises(Exception):
            sum_values(["a", "b", "c"])
    
    def test_minimum(self):
        self.assertEqual(minimum([5, 2, 8]), 2)
        self.assertEqual(minimum(["a", "c", "b"]), "a")
        self.assertEqual(minimum(5), 5)
        with self.assertRaises(Exception):
            minimum([])
        with self.assertRaises(Exception):
            minimum([1, "a"])
    
    def test_maximum(self):
        self.assertEqual(maximum([5, 2, 8]), 8)
        self.assertEqual(maximum(["a", "c", "b"]), "c")
        self.assertEqual(maximum(5), 5)
        with self.assertRaises(Exception):
            maximum([])
        with self.assertRaises(Exception):
            maximum([1, "a"])
    
    def test_average(self):
        self.assertEqual(average([1, 2, 3]), 2.0)
        with self.assertRaises(Exception):
            average([])
        with self.assertRaises(Exception):
            average(["a", "b", "c"])
    
    def test_raze(self):
        self.assertEqual(raze([[1, 2], [3, 4]]), [1, 2, 3, 4])
        self.assertEqual(raze([1, [2, 3], 4]), [1, 2, 3, 4])
        self.assertEqual(raze(5), [5])
    
    def test_flip_matrix(self):
        self.assertEqual(flip_matrix([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]])
        self.assertEqual(flip_matrix([]), [])
        with self.assertRaises(Exception):
            flip_matrix(5)
        with self.assertRaises(Exception):
            flip_matrix([[1, 2], [3]])
    
    def test_coalesce(self):
        self.assertEqual(coalesce([None, 1, 2]), 1)
        self.assertEqual(coalesce([None, None, 3]), 3)
        self.assertEqual(coalesce([None, None]), None)
        self.assertEqual(coalesce(5), 5)
    
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add([1, 2], 3), [4, 5])
        self.assertEqual(add(2, [3, 4]), [5, 6])
        self.assertEqual(add([1, 2], [3, 4]), [4, 6])
        self.assertEqual(add("hello", " world"), "hello world")
        self.assertEqual(add(True, False), True)
        self.assertEqual(add(False, False), False)
        with self.assertRaises(Exception):
            add(1, "a")
        with self.assertRaises(Exception):
            add([1, 2], [3, 4, 5])
    
    def test_logical_and(self):
        self.assertEqual(logical_and(3, 5), 1)
        self.assertEqual(logical_and(True, False), False)
        self.assertEqual(logical_and(True, True), True)
        self.assertEqual(logical_and([1, 3], 2), [0, 2])
        self.assertEqual(logical_and([True, False], [False, True]), [False, False])
        with self.assertRaises(Exception):
            logical_and(1, "a")
    
    def test_logical_or(self):
        self.assertEqual(logical_or(3, 5), 7)
        self.assertEqual(logical_or(True, False), True)
        self.assertEqual(logical_or(False, False), False)
        self.assertEqual(logical_or([1, 3], 2), [3, 3])
        self.assertEqual(logical_or([True, False], [False, True]), [True, True])
        with self.assertRaises(Exception):
            logical_or(1, "a")
    
    def test_not_equal(self):
        self.assertEqual(not_equal(1, 2), True)
        self.assertEqual(not_equal(1, 1), False)
        self.assertEqual(not_equal("a", "b"), True)
        self.assertEqual(not_equal([1, 2], [1, 3]), [False, True])
    
    def test_equals(self):
        self.assertEqual(equals(1, 2), False)
        self.assertEqual(equals(1, 1), True)
        self.assertEqual(equals("a", "b"), False)
        self.assertEqual(equals([1, 2], [1, 3]), [True, False])
    
    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply([1, 2], 3), [3, 6])
        self.assertEqual(multiply(2, [3, 4]), [6, 8])
        self.assertEqual(multiply([1, 2], [3, 4]), [3, 8])
        self.assertEqual(multiply("a", 3), "aaa")
        self.assertEqual(multiply(3, "a"), "aaa")
        self.assertEqual(multiply(True, False), False)
        self.assertEqual(multiply(True, True), True)
        with self.assertRaises(Exception):
            multiply("a", "b")
    
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract([5, 7], 3), [2, 4])
        self.assertEqual(subtract(5, [3, 4]), [2, 1])
        self.assertEqual(subtract([5, 7], [3, 4]), [2, 3])
        self.assertEqual(subtract(True, True), False)
        self.assertEqual(subtract(True, False), True)
        with self.assertRaises(Exception):
            subtract("a", "b")
    
    def test_divide(self):
        self.assertEqual(divide(5, 2), 250.0)
        self.assertEqual(divide([10, 20], 5), [200.0, 400.0])
        self.assertEqual(divide(10, [2, 5]), [500.0, 200.0])
        self.assertEqual(divide([10, 20], [2, 5]), [500.0, 400.0])
        with self.assertRaises(Exception):
            divide(5, 0)
        with self.assertRaises(Exception):
            divide("a", 2)
    
    def test_modulo(self):
        self.assertEqual(modulo(3, 10), 3)
        self.assertEqual(modulo(3, [10, 11, 12]), [3, 3, 3])
        with self.assertRaises(Exception):
            modulo("a", 10)
        with self.assertRaises(Exception):
            modulo([1, 2], 10)
    
    def test_take(self):
        self.assertEqual(take(3, 5), [5, 5, 5])
        self.assertEqual(take(3, [1, 2]), [1, 2, 1])
        self.assertEqual(take(-3, [1, 2, 3, 4]), [4, 3, 2])
        with self.assertRaises(Exception):
            take("a", [1, 2])
        with self.assertRaises(Exception):
            take([1, 2], [3, 4])
    
    def test_drop(self):
        self.assertEqual(drop(2, [1, 2, 3, 4, 5]), [3, 4, 5])
        self.assertEqual(drop(-2, [1, 2, 3, 4, 5]), [1, 2, 3])
        self.assertEqual(drop(2, "hello"), "llo")
        self.assertEqual(drop(-2, "hello"), "hel")
        with self.assertRaises(Exception):
            drop("a", [1, 2])
        with self.assertRaises(Exception):
            drop([1, 2], [3, 4])
        with self.assertRaises(Exception):
            drop(2, 5)
    
    def test_find(self):
        self.assertEqual(find(2, [1, 2, 3, 2, 1]), [1, 3])
        self.assertEqual(find("l", "hello"), [2, 3])
        with self.assertRaises(Exception):
            find(1, 5)
    
    def test_concatenate(self):
        self.assertEqual(concatenate(1, 2), [1, 2])
        self.assertEqual(concatenate([1, 2], 3), [1, 2, 3])
        self.assertEqual(concatenate(1, [2, 3]), [1, 2, 3])
        self.assertEqual(concatenate([1, 2], [3, 4]), [1, 2, 3, 4])
        self.assertEqual(concatenate("hello", " world"), "hello world")
    
    def test_index_access(self):
        self.assertEqual(index_access([1, 2, 3, 4], 2), 3)
        self.assertEqual(index_access("hello", 1), "e")
        self.assertEqual(index_access([1, 2, 3, 4], [0, 2]), [1, 3])
        with self.assertRaises(Exception):
            index_access(5, 1)
        with self.assertRaises(Exception):
            index_access("hello", "world")
        with self.assertRaises(Exception):
            index_access([1, 2], 5)
    
    def test_dict_lookup(self):
        test_dict = {"a": 1, "b": 2, 5: "five"}
        self.assertEqual(dict_lookup(test_dict, "a"), 1)
        self.assertEqual(dict_lookup(test_dict, "c"), None)
        self.assertEqual(dict_lookup(test_dict, 5), "five")
        self.assertEqual(dict_lookup(test_dict, ["a", "b", "c"]), [1, 2, None])
        with self.assertRaises(Exception):
            dict_lookup(5, "a")
    
    def test_lambda_function(self):
        lambda_func = LambdaFunction("x+1")
        self.assertEqual(lambda_func(5), 6)
        lambda_func = LambdaFunction("x+y")
        self.assertEqual(lambda_func(2, 3), 5)
        global_variables["test_var"] = 10
        lambda_func = LambdaFunction("x+test_var")
        self.assertEqual(lambda_func(5), 15)
        global_variables["x"] = "original"
        lambda_func = LambdaFunction("x")
        self.assertEqual(lambda_func("new"), "new")
        self.assertEqual(global_variables["x"], "original")
    
    def test_composed_function(self):
        f = lambda x: x + 1
        g = lambda x: x * 2
        composed = ComposedFunction(f, g)
        self.assertEqual(composed(5), 11)
    
    def test_partial_function(self):
        def add_func(x, y):
            return x + y
        left_partial = PartialFunction(add_func, 3, is_left=True)
        self.assertEqual(left_partial(4), 7)
        right_partial = PartialFunction(add_func, 3, is_left=False)
        self.assertEqual(right_partial(4), 7)
    
    def test_fold(self):
        def add_func(x, y):
            return x + y
        self.assertEqual(fold(add_func, [1, 2, 3, 4]), 10)
        with self.assertRaises(Exception):
            fold(add_func, [])
    
    def test_scan(self):
        def add_func(x, y):
            return x + y
        self.assertEqual(scan(add_func, [1, 2, 3, 4]), [1, 3, 6, 10])
        self.assertEqual(scan(add_func, []), [])
    
    def test_each(self):
        def square(x):
            return x * x
        self.assertEqual(each(square, [1, 2, 3]), [1, 4, 9])
        with self.assertRaises(Exception):
            each(square, 5)
    
    def test_each_right(self):
        def power(x, y):
            return x ** y
        self.assertEqual(each_right(power, 2, [1, 2, 3]), [2, 4, 8])
        with self.assertRaises(Exception):
            each_right(power, 2, 5)
    
    def test_each_left(self):
        def power(x, y):
            return x ** y
        self.assertEqual(each_left(power, [1, 2, 3], 2), [1, 4, 9])
        with self.assertRaises(Exception):
            each_left(power, 5, 2)
    
    def test_each_pair(self):
        def power(x, y):
            return x ** y
        self.assertEqual(each_pair(power, [1, 2, 3], [2, 3, 2]), [1, 8, 9])
        with self.assertRaises(Exception):
            each_pair(power, 5, [1, 2, 3])
        with self.assertRaises(Exception):
            each_pair(power, [1, 2, 3], 5)
        with self.assertRaises(Exception):
            each_pair(power, [1, 2], [1, 2, 3])
    
    def test_evaluate_expression(self):
        self.assertEqual(evaluate_expression(5), 5)
        self.assertEqual(evaluate_expression("5"), 5)
        self.assertEqual(evaluate_expression("5.5"), 5.5)
        self.assertEqual(evaluate_expression("true"), True)
        self.assertEqual(evaluate_expression('"hello"'), "hello")
        self.assertEqual(evaluate_expression("(1;2;3)"), [1, 2, 3])
        self.assertEqual(evaluate_expression('("a";1;true)'), ["a", 1, True])
        dict_result = evaluate_expression('[a:1;b:"hello"]')
        self.assertEqual(dict_result["a"], 1)
        self.assertEqual(dict_result["b"], "hello")
        operation_registry.register(Operation("+", lambda x: x + 1, None))
        self.assertEqual(evaluate_expression(["+", 5]), 6)
        operation_registry.register(Operation("-", None, lambda x, y: x - y))
        self.assertEqual(evaluate_expression([3, "-", 2]), 1)
        global_variables["test_var"] = 42
        self.assertEqual(evaluate_expression("test_var"), 42)
        lambda_func = evaluate_expression("{x+1}")
        self.assertEqual(lambda_func(5), 6)

if __name__ == '__main__':
    unittest.main()