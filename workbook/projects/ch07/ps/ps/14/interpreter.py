from stack import Stack
from environment import Environment

class Interpreter:
    def __init__(self):
        self.stack = Stack()  # Stack for intermediate values
        self.environment = Environment()  # Environment for variable and procedure definitions

    def execute(self, ast):
        """
        Executes the AST (abstract syntax tree) by pushing items to the stack
        and performing actions when necessary.
        """
        if not ast:  # Empty AST
            return
        
        # Process the AST by pushing elements onto the stack and handling them
        for token in ast:
            if isinstance(token, (int, float)):  # Numbers are pushed to the stack
                self.stack.push(token)

            elif isinstance(token, str):  # Could be a variable or procedure
                if token.startswith("/"):  # Variable or procedure name
                    self.stack.push(token)
                else:
                    self._handle_command(token)

            elif isinstance(token, list):  # If it's a procedure definition
                self.stack.push(token)

            elif isinstance(token, tuple) and token[0] == "comment":  # Ignore comments
                continue

            else:
                raise ValueError(f"Unsupported AST node: {token}")

    def _handle_def(self):
        value = self.stack.pop()
        name = self.stack.pop()

        if isinstance(value, list):
            self.environment.define_procedure(name, value)
        else:
            self.environment.define_variable(name, value)

    def _handle_get(self):
        print("get")
        variable_name = self.stack.pop()
        print("var:", variable_name)
        value = self.environment.lookup(variable_name)

        print(type(value))  # Check the type
        if callable(value):
            print("This is a function!")
            # Call it with appropriate arguments if needed
        else:
            print("This is a value, not a function.")

        self.stack.push(value)

    def _handle_command(self, command):
        """
        Handle PostScript-like commands ('add', 'sub', etc.) on the stack.
        """
        if command == 'add':
            self._binary_op(lambda x, y: x + y)
        elif command == 'sub':
            self._binary_op(lambda x, y: x - y)
        elif command == 'mul':
            self._binary_op(lambda x, y: x * y)
        elif command == 'div':
            self._binary_op(lambda x, y: x / y if y != 0 else float('inf'))
        elif command == 'dup':
            if self.stack.size() > 0:
                self.stack.push(self.stack.peek())
        elif command == 'pop':
            if self.stack.size() > 0:
                self.stack.pop()
        elif command == 'def':
            if self.stack.size() > 0:
                self._handle_def()
        elif command == 'get':
            if self.stack.size() > 0:
                self._handle_get()
        else:
            raise ValueError(f"Unsupported command: {command}")

    def _binary_op(self, operation):
        """
        Performs a binary operation on the top two values of the stack.
        """
        if self.stack.size() < 2:
            raise ValueError("Insufficient values on the stack for operation")
        y = self.stack.pop()
        x = self.stack.pop()
        self.stack.push(operation(x, y))

    def get_stack(self):
        """
        Get a copy of the current stack.
        """
        return self.stack.copy()


# Example Usage

interpreter = Interpreter()

# Define a variable '/name' with value 5
interpreter.execute(['/name', 5, 'def'])  # Define '/name' as 5

# Retrieve the value of '/name'
interpreter.execute(['/name', 'get'])  # Get the value of '/name' -> 5
print(interpreter.get_stack())  # [5]

# Define a procedure '/add_two' that adds 2 to the value on the stack
interpreter.execute(['/add_two', [2, 'add'], 'def'])  # Define procedure '/add_two'

# Execute the procedure '/add_two' on the stack value 3
interpreter.execute([3, '/add_two'])  # Stack will have [5] (3 + 2)
print(interpreter.get_stack())  # [5]

# Define a procedure '/square' that duplicates and then multiplies the top of the stack
interpreter.execute(['/square', ['dup', 'mul'], 'def'])  # Define procedure '/square'

# Execute the procedure '/square' on the value 4
interpreter.execute([4, '/square'])  # 4 * 4 -> stack: [16]
print(interpreter.get_stack())  # [16]