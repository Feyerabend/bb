import unittest
from interpreter import Interpreter

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_addition(self):
        ast = [5, 3, 'add']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [8])

    def test_subtraction(self):
        ast = [10, 4, 'sub']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [6])

    def test_multiplication(self):
        ast = [6, 7, 'mul']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [42])

    def test_division(self):
        ast = [10, 2, 'div']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [5.0])

    def test_division_by_zero(self):
        ast = [10, 0, 'div']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [float('inf')])

    def test_dup(self):
        ast = [4, 'dup']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [4, 4])

    def test_pop(self):
        ast = [4, 7, 'pop']
        self.interpreter.execute(ast)
        self.assertEqual(self.interpreter.get_stack(), [4])

    def test_complex_expression(self):
        ast = [5, 1, 'add', 3, 'mul', 8, 'sub']
        self.interpreter.execute(ast)
        # (5 + 1) * 3 - 8 = 10
        self.assertEqual(self.interpreter.get_stack(), [10])

    def test_nested_operations(self):
        ast = [10, 3, 'mul', 6, 'add', 2, 'div']
        self.interpreter.execute(ast)
        # ((10 * 3) + 6) / 2 = 18
        self.assertEqual(self.interpreter.get_stack(), [18.0])

# Run the tests
if __name__ == "__main__":
    unittest.main()
