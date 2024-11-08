# test_interpreter.py

from stack import Stack
from lexer import Lexer
from parser import Parser
from executor import Executor

# test.py

from stack import Stack
from executor import Executor

def test_interpreter():
    # Initialize the stack and environment
    stack = Stack()
    environment = {}
    executor = Executor(stack, environment)

    # Define a test case with enough elements for `exch`
    tokens = [10, 20, 'add', 5, 'mul', 'exch']

    print("Executing test case...")
    executor.execute(tokens)  # Execute the test tokens
    print("Test execution complete.")
    print(f"Final Stack: {stack.items}")  # Print the final stack contents

# Run the test
if __name__ == "__main__":
    test_interpreter()
