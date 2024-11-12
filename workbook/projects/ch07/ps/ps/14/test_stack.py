import unittest
from stack import Stack

class TestStack(unittest.TestCase):

    def setUp(self):
        """Set up a new stack for each test."""
        self.stack = Stack()

    def test_push_pop(self):
        """Test pushing and popping items from the stack."""
        self.stack.push(10)
        self.assertEqual(self.stack.pop(), 10)

        self.stack.push(3.14)
        self.assertEqual(self.stack.pop(), 3.14)

    def test_peek(self):
        """Test peeking at the top item of the stack."""
        self.stack.push('hello')
        self.assertEqual(self.stack.peek(), 'hello')

    def test_is_empty(self):
        """Test if the stack is empty."""
        self.assertTrue(self.stack.is_empty())
        self.stack.push(10)
        self.assertFalse(self.stack.is_empty())

    def test_size(self):
        """Test the size of the stack."""
        self.assertEqual(self.stack.size(), 0)
        self.stack.push(1)
        self.stack.push(2)
        self.assertEqual(self.stack.size(), 2)

    def test_clear(self):
        """Test clearing the stack."""
        self.stack.push(1)
        self.stack.push(2)
        self.stack.clear()
        self.assertTrue(self.stack.is_empty())

    def test_pop_empty_stack(self):
        """Test popping from an empty stack raises IndexError."""
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_peek_empty_stack(self):
        """Test peeking from an empty stack raises IndexError."""
        with self.assertRaises(IndexError):
            self.stack.peek()

    def test_push_multiple_types(self):
        """Test pushing different types onto the stack."""
        self.stack.push(10)
        self.stack.push("string")
        self.stack.push([1, 2, 3])
        self.stack.push({'a': 1, 'b': 2})
        self.assertEqual(self.stack.pop(), {'a': 1, 'b': 2})
        self.assertEqual(self.stack.pop(), [1, 2, 3])
        self.assertEqual(self.stack.pop(), "string")
        self.assertEqual(self.stack.pop(), 10)

    def test_stack_repr(self):
        """Test the string representation of the stack."""
        self.stack.push(10)
        self.stack.push("hello")
        self.assertEqual(repr(self.stack), "Stack([10, 'hello'])")

    def test_contains(self):
        """Test the 'in' operator for the stack."""
        self.stack.push(10)
        self.stack.push("hello")
        self.assertIn(10, self.stack)
        self.assertIn("hello", self.stack)
        self.assertNotIn(3.14, self.stack)

    def test_ast(self):
        """Test ast for the stack."""
        ast = [5, 3.7, 'add']
        for node in ast:
            if isinstance(node, (int, float)):  # push numbers to stack
                self.stack.push(node)
        self.assertIn(5, self.stack)
        self.assertIn(3.7, self.stack)
        self.assertNotIn('add', self.stack)

if __name__ == "__main__":
    unittest.main()
