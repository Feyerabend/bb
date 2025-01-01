class SimpleVirtualMachine:
    def __init__(self):
        self.stack = []  # operands
        self.memory = {}  # for variables

    def execute(self, instructions):
        """Execute instructions in the given format."""
        for instruction in instructions:
            parts = instruction.split()  # .. into parts
            op = parts[0]

            if op == "PUSH":
                self.stack.append(int(parts[1]))

            elif op == "STORE":
                # pop top of stack and store in memory
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


code = ['PUSH 2025', 'STORE x', 'PUSH 1477', 'STORE y', 'LOAD x', 'STORE t1', 'LOAD y', 'STORE t2', 'LOAD t1', 'LOAD t2', 'ADD', 'STORE t1', 'PUSH 7', 'STORE t3', 'PUSH 9', 'STORE t4', 'LOAD t3', 'LOAD t4', 'ADD', 'STORE t2', 'PUSH 5', 'STORE t5', 'LOAD t2', 'STORE t6', 'LOAD t5', 'LOAD t6', 'MUL', 'STORE t3', 'LOAD t3', 'STORE t7', 'PUSH 2', 'STORE t8', 'LOAD t7', 'LOAD t8', 'DIV', 'STORE t4', 'LOAD t1', 'STORE t9', 'LOAD t4', 'STORE t10', 'LOAD t9', 'LOAD t10', 'SUB', 'STORE t5', 'LOAD t5', 'STORE z']
vm = SimpleVirtualMachine()
vm.execute(code)

# print memory contents after execution (we have no print instruction)
print("Memory:", vm.dump_memory())
