
class Interpreter:
    def __init__(self):
        self.stack = []

    def execute(self, ast):
        for node in ast:
            if isinstance(node, (int, float)):  # push numbers to stack
                self.stack.append(node)
            elif isinstance(node, str):  # operations and commands
                self._handle_command(node)
            elif isinstance(node, tuple) and node[0] == "comment":
                # ..  ignore
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
            if self.stack:
                self.stack.append(self.stack[-1])
        elif command == 'pop':
            if self.stack:
                self.stack.pop()
        else:
            raise ValueError(f"Unsupported command: {command}")

    def _binary_op(self, operation):
        if len(self.stack) < 2:
            raise ValueError("Insufficient values on the stack for operation")
        y = self.stack.pop()
        x = self.stack.pop()
        self.stack.append(operation(x, y))

    def get_stack(self):
        return self.stack.copy()
