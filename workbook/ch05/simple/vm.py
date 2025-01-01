class SimpleVirtualMachine:
    def __init__(self):
        self.stack = []  # Operand stack
        self.memory = {}  # Memory for variables

    def execute(self, instructions):
        """Execute instructions in the given format."""
        for instruction in instructions:
            parts = instruction.split()  # Split instruction into parts
            op = parts[0]

            if op == "PUSH":
                # Push a constant onto the stack
                self.stack.append(int(parts[1]))
            elif op == "STORE":
                # Pop the top of the stack and store it in memory
                var_name = parts[1]
                value = self.stack.pop()
                self.memory[var_name] = value
            elif op == "LOAD":
                # Load a variable's value and push it onto the stack
                var_name = parts[1]
                if var_name not in self.memory:
                    raise RuntimeError(f"Undefined variable: {var_name}")
                self.stack.append(self.memory[var_name])
            elif op == "ADD":
                # Pop two values, add them, and push the result
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                # Pop two values, subtract them, and push the result
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                # Pop two values, multiply them, and push the result
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == "DIV":
                # Pop two values, divide them, and push the result
                b = self.stack.pop()
                a = self.stack.pop()
                if b == 0:
                    raise RuntimeError("Division by zero")
                self.stack.append(a // b)
            else:
                raise RuntimeError(f"Unknown instruction: {instruction}")

    def dump_memory(self):
        """Return the contents of the VM's memory."""
        return self.memory


# Symbol Table: {'x': None, 'y': None, 'z': None}
code = ['PUSH 2025', 'STORE x', 'PUSH 1477', 'STORE y', 'LOAD x', 'LOAD y', 'ADD', 'PUSH 5', 'PUSH 7', 'PUSH 9', 'ADD', 'MUL', 'PUSH 2', 'DIV', 'SUB', 'STORE z']

# Example
vm = SimpleVirtualMachine()
vm.execute(code)

# Print the memory contents after execution
print("Memory:", vm.dump_memory())
