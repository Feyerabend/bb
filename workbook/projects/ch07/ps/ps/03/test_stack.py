import unittest
from stack import Stack

class TestStack(unittest.TestCase):
    
    def test_push(self):
        stack = Stack()
        stack.push(10)
        stack.push(20)
        self.assertEqual(len(stack.stack), 2)
        self.assertEqual(stack.peek(), 20)
        
    def test_pop(self):
        stack = Stack()
        stack.push(10)
        stack.push(20)

        popped_value = stack.pop()
        self.assertEqual(popped_value, 20)
        self.assertEqual(len(stack.stack), 1)
        
        popped_value = stack.pop()
        self.assertEqual(popped_value, 10)
        self.assertEqual(len(stack.stack), 0)
        
    def test_pop_empty_stack(self):
        stack = Stack()

        with self.assertRaises(IndexError):
            stack.pop()

    def test_peek(self):
        stack = Stack()
        stack.push(10)
        stack.push(20)
        
        self.assertEqual(stack.peek(), 20)
        
    def test_peek_empty_stack(self):
        stack = Stack()

        with self.assertRaises(IndexError):
            stack.peek()

    def test_stack_order(self):
        stack = Stack()
        stack.push(1)
        stack.push(2)
        stack.push(3)
        
        self.assertEqual(stack.pop(), 3)
        self.assertEqual(stack.pop(), 2)
        self.assertEqual(stack.pop(), 1)

if __name__ == '__main__':
    unittest.main()
