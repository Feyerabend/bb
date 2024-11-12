
from stack import Stack
from environment import Environment

class Interpreter:
    def __init__(self):
        self.stack = Stack()
        self.procedures = Environment()

    def execute(self, ast):
        if not ast:  # empty?
            return
        for node in ast:
            if isinstance(node, (int, float)):  # push numbers to stack
                self.stack.push(node)
            elif isinstance(node, str):  # operations and commands
                if node.startswith("/"):  # (might be) procedure call
                    self._handle_procedure_call(node)
                else:
                    self._handle_command(node)
            elif isinstance(node, tuple) and node[0] == "comment":
                # .. ignore
                continue
            else:
                raise ValueError(f"Unsupported AST node: {node}")

    def _handle_command(self, command):
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
        else:
            raise ValueError(f"Unsupported command: {command}")

    def _handle_procedure_call(self, procedure_name):
        try:
            value = self.procedures.lookup(procedure_name)
        except KeyError as e:
            raise ValueError(f"Undefined procedure: {procedure_name}")
        procedure = value
        self.execute(procedure)

    def define_procedure(self, name, body):
        if not name.startswith('/'):
            raise ValueError("Procedure name must start with '/'")
        self.procedures.define(name, body)

    def _binary_op(self, operation):
        if self.stack.size() < 2:
            raise ValueError("Insufficient values on the stack for operation")
        y = self.stack.pop()
        x = self.stack.pop()
        self.stack.push(operation(x, y))

    def get_stack(self):
        return self.stack.copy()


interpreter = Interpreter()

# Define a procedure named '/add_two' that adds 2 to the value on the stack
interpreter.define_procedure('/add_two', [2, 'add'])

# Define a procedure that squares a number
interpreter.define_procedure('/square', ['dup', 'mul'])

# Now you can execute these procedures
interpreter.execute([5, '/add_two'])  # 5 + 2 -> stack: [7]
print(interpreter.get_stack())  # [7]

interpreter.execute([4, '/square'])  # 4 * 4 -> stack: [16]
print(interpreter.get_stack())  # [16]


#/name 5 def
#/name get
#/name { ... code ... } def
