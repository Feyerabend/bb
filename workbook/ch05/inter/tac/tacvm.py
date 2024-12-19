
class VirtualMachine:
    def __init__(self, program):
        self.program = program  # Parsed program as a list of statements
        self.pc = 0             # Program counter
        self.memory = {}        # Variable storage
        self.stack = []         # Call stack
        self.labels = {}        # Map label to instruction index
        self.running = True     # Control execution loop

        self.preprocess_labels()

    def preprocess_labels(self):
        for idx, statement in enumerate(self.program):
            if statement["type"] == "label":
                self.labels[statement["identifier"]] = idx

    def fetch_next_instruction(self):
        if 0 <= self.pc < len(self.program):
            return self.program[self.pc]
        return None

    def evaluate_expression(self, expression):
        if expression["type"] == "term":
            value = expression["value"]
            if isinstance(value, str) and value.isdigit():
                return int(value)
            elif value in self.memory:
                return self.memory[value]
            else:
                raise ValueError(f"Undefined variable or invalid term: {value}")
        elif expression["type"] == "binary_op":
            left = self.evaluate_expression(expression["left"])
            right = self.evaluate_expression(expression["right"])
            operator = expression["operator"]
            if operator == "+":
                return left + right
            elif operator == "-":
                return left - right
            elif operator == "*":
                return left * right
            elif operator == "/":
                return left // right  # integer division
            elif operator == "&&":
                return int(bool(left and right))
            elif operator == "||":
                return int(bool(left or right))
            elif operator in ("<", "<=", ">", ">=", "==", "!="):
                return int(eval(f"{left} {operator} {right}"))  # eval!
            else:
                raise ValueError(f"Unknown operator: {operator}")
        else:
            raise ValueError(f"Invalid expression type: {expression['type']}")

    def apply_operator(self, left, operator, right):
        operations = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x // y,
            "&&": lambda x, y: x and y,
            "||": lambda x, y: x or y,
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
        }
        return operations[operator](left, right)

    def execute_instruction(self, instruction):
        inst_type = instruction["type"]

        if inst_type == "assignment":
            dest = instruction["dest"]
            value = self.evaluate_expression(instruction["rhs"])
            self.memory[dest] = value

        elif inst_type == "if":
            condition = self.evaluate_expression(instruction["condition"])
            if condition:
                label = instruction["label"]
                self.pc = self.labels[label] - 1  # -1 to offset PC increment

        elif inst_type == "goto":
            label = instruction["label"]
            self.pc = self.labels[label] - 1  # -1 to offset PC increment

        elif inst_type == "print":
            identifier = instruction["value"]
            print(self.memory.get(identifier, 0))

        elif inst_type == "label":
            pass  # labels handled in preprocessing

        elif inst_type == "call":
            func_name = instruction["identifier"]
            arg_count = instruction["arg_count"]
            # push current state onto the stack
            self.stack.append((self.pc, self.memory.copy()))
            # jump to function start (label)
            self.pc = self.labels[func_name] - 1

        elif inst_type == "return":
            if self.stack:
                self.pc, self.memory = self.stack.pop()
            else:
                self.running = False

        elif inst_type == "halt":
            return

        else:
            raise ValueError(f"Unknown instruction type: {inst_type}")

    def run(self):
        while self.running and self.pc < len(self.program):
            instruction = self.fetch_next_instruction()
            if instruction:
                self.execute_instruction(instruction)
            self.pc += 1

program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "term", "value": "10"}},
    {"type": "label", "identifier": "loop"},
    {"type": "print", "value": "x"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": "-", "right": {"type": "term", "value": "1"}}},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": ">", "right": {"type": "term", "value": "0"}}, "label": "loop"},
    {"type": "halt"},
]

vm = VirtualMachine(program)
vm.run()
