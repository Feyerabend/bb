import unittest
from interpreter import OperandStack, DictionaryStack, Interpreter

class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.stack = OperandStack()
        self.dict_stack = DictionaryStack()
        self.interpreter = Interpreter(self.stack, self.dict_stack)

    def test_array_handling(self):
        """Test that arrays are correctly pushed to the operand stack."""
        self.interpreter.execute([1, 2, 3])
        self.assertEqual(self.interpreter.operand_stack.pop(), [1, 2, 3])

    def test_block_handling(self):
        """Test that blocks (procedures) are pushed to the stack as blocks."""
        block = ['{', '/x', 42, 'def', '}']
        self.interpreter.execute(block)
        self.assertEqual(self.interpreter.operand_stack.pop(), block)

    def test_if_true(self):
        """Test if command with a true condition."""
        # Set up stack with condition and block
        self.interpreter.operand_stack.push(True)  # Condition
        self.interpreter.operand_stack.push(['{', 42, '}'])  # Block
        
        # Execute if command
        self.interpreter.if_()
        
        # Verify the block executed and result on the stack
        self.assertEqual(self.interpreter.operand_stack.pop(), 42)

    def test_if_false(self):
        """Test if command with a false condition."""
        # Set up stack with condition and block
        self.interpreter.operand_stack.push(False)  # Condition
        self.interpreter.operand_stack.push(['{', 42, '}'])  # Block
        
        # Execute if command
        self.interpreter.if_()
        
        # Verify the block did not execute
        self.assertEqual(len(self.interpreter.operand_stack), 0)

    def test_ifelse_true(self):
        """Test ifelse command with a true condition."""
        # Set up stack with condition, true block, and false block
        self.interpreter.operand_stack.push(True)  # Condition
        self.interpreter.operand_stack.push(['{', 42, '}'])  # True block
        self.interpreter.operand_stack.push(['{', 99, '}'])  # False block
        
        # Execute ifelse command
        self.interpreter.ifelse()
        
        # Verify the true block executed
        self.assertEqual(self.interpreter.operand_stack.pop(), 42)

    def test_ifelse_false(self):
        """Test ifelse command with a false condition."""
        # Set up stack with condition, true block, and false block
        self.interpreter.operand_stack.push(False)  # Condition
        self.interpreter.operand_stack.push(['{', 42, '}'])  # True block
        self.interpreter.operand_stack.push(['{', 99, '}'])  # False block
        
        # Execute ifelse command
        self.interpreter.ifelse()
        
        # Verify the false block executed
        self.assertEqual(self.interpreter.operand_stack.pop(), 99)

    def test_nested_blocks(self):
        """Test nested blocks to ensure recursive execution works."""
        # Define a procedure that uses nested blocks
        outer_block = [
            '{', 
            '/x', 10, 'def', 
            '{', 'x', 'dup', 'mul', '}',  # Square x
            '}'
        ]
    
        # Execute the outer block
        self.interpreter.execute(outer_block)
    
        # Extract the inner block (this would be evaluated by the procedure execution)
        inner_block = self.interpreter.operand_stack.pop()  # Pop the outer block
        self.assertEqual(inner_block, ['x', 'dup', 'mul'])  # Check the inner block
    
        # Execute the inner block to test nested execution
        self.interpreter.dictionary_stack.define_variable('/x', 5)
        self.interpreter.execute_procedure(inner_block)  # Execute the inner block
    
        # Verify result on the operand stack
        self.assertEqual(self.interpreter.operand_stack.pop(), 25)

# Run tests if this is the main module
if __name__ == "__main__":
    unittest.main()