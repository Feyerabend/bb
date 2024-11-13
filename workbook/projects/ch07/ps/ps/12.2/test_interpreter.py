import unittest
from interpreter import OperandStack, DictionaryStack, Interpreter

class TestOperandStack(unittest.TestCase):
    def setUp(self):
        self.stack = OperandStack()

    def test_push_pop(self):
        self.stack.push(10)
        self.stack.push(20)
        self.assertEqual(self.stack.pop(), 20)
        self.assertEqual(self.stack.pop(), 10)

    def test_top(self):
        self.stack.push(10)
        self.assertEqual(self.stack.top(), 10)
        self.assertEqual(self.stack.pop(), 10)

    def test_stack_underflow(self):
        with self.assertRaises(ValueError):
            self.stack.pop()

    def test_clear(self):
        self.stack.push(1)
        self.stack.push(2)
        self.stack.clear()
        with self.assertRaises(ValueError):
            self.stack.pop()

class TestCoreOperations(unittest.TestCase):
    def setUp(self):
        self.stack = OperandStack()
        self.dict_stack = DictionaryStack()
        self.interpreter = Interpreter(self.stack, self.dict_stack)

    def test_add(self):
        self.stack.push(3)
        self.stack.push(7)
        self.interpreter.add()
        self.assertEqual(self.stack.pop(), 10)

    def test_sub(self):
        self.stack.push(10)
        self.stack.push(4)
        self.interpreter.sub()
        self.assertEqual(self.stack.pop(), 6)

    def test_mul(self):
        self.stack.push(3)
        self.stack.push(5)
        self.interpreter.mul()
        self.assertEqual(self.stack.pop(), 15)

    def test_div(self):
        self.stack.push(8)
        self.stack.push(2)
        self.interpreter.div()
        self.assertEqual(self.stack.pop(), 4)

    def test_div_zero(self):
        self.stack.push(8)
        self.stack.push(0)
        with self.assertRaises(ZeroDivisionError):
            self.interpreter.div()

    def test_dup(self):
        self.stack.push(42)
        self.interpreter.dup()
        self.assertEqual(self.stack.pop(), 42)
        self.assertEqual(self.stack.pop(), 42)

    def test_exch(self):
        self.stack.push(1)
        self.stack.push(2)
        self.interpreter.exch()
        self.assertEqual(self.stack.pop(), 1)
        self.assertEqual(self.stack.pop(), 2)

    def test_pop(self):
        self.stack.push(42)
        self.interpreter.pop()
        with self.assertRaises(ValueError):
            self.stack.pop()

class TestDictionaryStack(unittest.TestCase):
    def setUp(self):
        self.dict_stack = DictionaryStack()

    def test_define_and_lookup(self):
        self.dict_stack.define("x", 10)
        self.assertEqual(self.dict_stack.lookup("x"), 10)

    def test_nested_scope(self):
        self.dict_stack.define("x", 10)
        self.dict_stack.push_scope()
        self.dict_stack.define("x", 20)  # Override in new scope
        self.assertEqual(self.dict_stack.lookup("x"), 20)
        self.dict_stack.pop_scope()
        self.assertEqual(self.dict_stack.lookup("x"), 10)  # Original value restored

    def test_undefined_name(self):
        with self.assertRaises(KeyError):
            self.dict_stack.lookup("nonexistent")

    def test_pop_global_scope(self):
        with self.assertRaises(ValueError):
            self.dict_stack.pop_scope()  # Cannot pop the last scope

class TestProcedures(unittest.TestCase):
    def setUp(self):
        self.stack = OperandStack()
        self.dict_stack = DictionaryStack()
        self.interpreter = Interpreter(self.stack, self.dict_stack)

    def test_define_variable(self):
        self.dict_stack.define("myVar", 100)
        self.assertEqual(self.dict_stack.lookup("myVar"), 100)

    def test_define_and_execute_procedure(self):
        procedure = ["dup", "mul"]
        self.dict_stack.define("square", procedure)
        self.stack.push(3)
        self.interpreter.execute_procedure("square")
        self.assertEqual(self.stack.pop(), 9)  # 3 squared

    def test_if_true(self):
        self.stack.push(True)
        self.stack.push(["42"])
        self.interpreter.if_()
        self.assertEqual(self.stack.pop(), 42)

    def test_if_false(self):
        self.stack.push(False)
        self.stack.push(["42"])
        self.interpreter.if_()
        with self.assertRaises(ValueError):
            self.stack.pop()  # Stack should be empty if condition was false

    def test_ifelse_true(self):
        self.stack.push(True)
        self.stack.push(["42"])
        self.stack.push(["99"])
        self.interpreter.ifelse()
        self.assertEqual(self.stack.pop(), 42)

    def test_ifelse_false(self):
        self.stack.push(False)
        self.stack.push(["42"])
        self.stack.push(["99"])
        self.interpreter.ifelse()
        self.assertEqual(self.stack.pop(), 99)

# Run the tests
if __name__ == "__main__":
    unittest.main()
