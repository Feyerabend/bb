class SimpleVirtualMachine:
    def __init__(self):
        self.stack = []  # operands
        self.memory = {}  # variables

    def execute(self, instructions):
        for instruction in instructions:
            parts = instruction.split()  # split instruction into parts
            op = parts[0]

            if op == "PUSH":
                # push a constant onto stack
                self.stack.append(int(parts[1]))

            elif op == "STORE":
                # pop top of stack and store it in memory
                var_name = parts[1]
                value = self.stack.pop()
                self.memory[var_name] = value

            elif op == "LOAD":
                # load a variable's value and push onto stack
                var_name = parts[1]
                if var_name not in self.memory:
                    raise RuntimeError(f"Undefined variable: {var_name}")
                self.stack.append(self.memory[var_name])

            elif op == "ADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)

            elif op == "SUB":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif op == "MUL":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif op == "DIV":
                b = self.stack.pop()
                a = self.stack.pop()
                if b == 0:
                    raise RuntimeError("Division by zero")
                self.stack.append(a // b)
            else:
                raise RuntimeError(f"Unknown instruction: {instruction}")

    def dump_memory(self):
        return self.memory


# Symbol Table: {'x': None, 'y': None, 'z': None}
code = ['PUSH 2025', 'STORE x', 'PUSH 1477', 'STORE y', 'LOAD x', 'LOAD y', 'ADD', 'PUSH 5', 'PUSH 7', 'PUSH 9', 'ADD', 'MUL', 'PUSH 2', 'DIV', 'SUB', 'STORE z']

vm = SimpleVirtualMachine()
vm.execute(code)

# memory contents after execution (no separate print statement)
print("Memory:", vm.dump_memory())
