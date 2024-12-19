import sys

# simulation version .. time and mem
class VirtualMachine:
    def __init__(self, program):
        self.program = program  # Parsed program as a list of statements
        self.pc = 0             # Program counter
        self.memory = {}        # Variable storage
        self.stack = []         # Call stack
        self.labels = {}        # Map label to instruction index
        self.running = True     # Control execution loop
        self.clock_cycles = 0   # Track simulated clock cycles

        # clock cycle cost per instruction type
        self.instruction_cost = {
            "assignment": 3,
            "if": 2,
            "goto": 1,
            "print": 4,
            "label": 0,
            "call": 5,
            "return": 4,
            "halt": 1,
        }

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
            return self.apply_operator(left, operator, right)
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
        self.clock_cycles += self.instruction_cost.get(inst_type, 1)

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

            self.stack.append((self.pc + 1, self.memory.copy()))

            for i in range(arg_count):
                arg_key = f"arg{i}"
                if arg_key in self.memory:
                    self.memory[arg_key] = self.memory[arg_key]
                else:
                    self.memory[arg_key] = 0  # 0, if no argument

            if func_name in self.labels:
                self.pc = self.labels[func_name] - 1  # -1 to offset PC increment
            else:
                raise ValueError(f"Undefined function label: {func_name}")

        elif inst_type == "return":
            if self.stack:
                # restore program counter and memory state
                self.pc, self.memory = self.stack.pop()
                self.pc -= 1  # -1 to offset PC increment
            else:
                self.running = False  # no stack frames; "halt"

        elif inst_type == "halt":
            self.running = False

        else:
            raise ValueError(f"Unknown instruction type: {inst_type}")

    def run(self):
        while self.running and self.pc < len(self.program):
            instruction = self.fetch_next_instruction()
            if instruction:
                self.execute_instruction(instruction)
            self.pc += 1
        print(f"Total clock cycles: {self.clock_cycles}")
        print(f"Program memory usage: {self.measure_program_memory()} bytes")
        print(f"Runtime memory usage: {self.measure_runtime_memory()} bytes")

    def measure_program_memory(self):
        return sum(sys.getsizeof(stmt) for stmt in self.program)

    def measure_runtime_memory(self):
        memory_usage = sys.getsizeof(self.memory)
        stack_usage = sum(sys.getsizeof(frame) for frame in self.stack)
        return memory_usage + stack_usage



factorial_program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "n", "rhs": {"type": "term", "value": "5"}},  # input number 5! = 120
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "1"}},
    {"type": "label", "identifier": "loop"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "n"}, "operator": "<=", "right": {"type": "term", "value": "0"}}, "label": "end"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "result"}, "operator": "*", "right": {"type": "term", "value": "n"}}},
    {"type": "assignment", "dest": "n", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "n"}, "operator": "-", "right": {"type": "term", "value": "1"}}},
    {"type": "goto", "label": "loop"},
    {"type": "label", "identifier": "end"},
    {"type": "print", "value": "result"},
    {"type": "halt"},
]

print("\nfactorial")
vm = VirtualMachine(factorial_program)
vm.run()

fibonacci_program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "a", "rhs": {"type": "term", "value": "0"}},
    {"type": "assignment", "dest": "b", "rhs": {"type": "term", "value": "1"}},
    {"type": "assignment", "dest": "limit", "rhs": {"type": "term", "value": "10"}},  # 10 terms
    {"type": "assignment", "dest": "count", "rhs": {"type": "term", "value": "0"}},
    {"type": "label", "identifier": "loop"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "count"}, "operator": ">=", "right": {"type": "term", "value": "limit"}}, "label": "end"},
    {"type": "print", "value": "a"},
    {"type": "assignment", "dest": "temp", "rhs": {"type": "term", "value": "b"}},
    {"type": "assignment", "dest": "b", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "a"}, "operator": "+", "right": {"type": "term", "value": "b"}}},
    {"type": "assignment", "dest": "a", "rhs": {"type": "term", "value": "temp"}},
    {"type": "assignment", "dest": "count", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "count"}, "operator": "+", "right": {"type": "term", "value": "1"}}},
    {"type": "goto", "label": "loop"},
    {"type": "label", "identifier": "end"},
    {"type": "halt"},
]

print("\nfibonacci")
vm = VirtualMachine(fibonacci_program)
vm.run()

function_call_program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "arg0", "rhs": {"type": "term", "value": "42"}},  # 42 as an argument
    {"type": "call", "identifier": "hello", "arg_count": 1},
    {"type": "halt"},
    {"type": "label", "identifier": "hello"},
    {"type": "print", "value": "arg0"},  # print argument
    {"type": "return"},
]

print("\nfunction call with arguments")
vm = VirtualMachine(function_call_program)
vm.run()


program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "term", "value": "10"}},
    {"type": "label", "identifier": "loop"},
    {"type": "print", "value": "x"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": "-", "right": {"type": "term", "value": "1"}}},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": ">", "right": {"type": "term", "value": "0"}}, "label": "loop"},
    {"type": "halt"},
]

print("\ncount from 10")
vm = VirtualMachine(program)
vm.run()





'''
        elif inst_type == "call":
            func_name = instruction["identifier"]
            arg_count = instruction["arg_count"]
            self.stack.append((self.pc, self.memory.copy()))  # current state onto stack
            self.pc = self.labels[func_name] - 1

        elif inst_type == "return":
            if self.stack:
                self.pc, self.memory = self.stack.pop()
            else:
                self.running = False
'''