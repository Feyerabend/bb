import sys

# simulation of a machine with certain 'clock cycles'
# to illustrate cost of running each instruction
class VirtualMachine:
    def __init__(self, program, max_depth=1000):
        self.program = program  # parsed program as a list of statements
        self.pc = 0             # program counter
        self.memory = {}        # variable storage
        self.stack = []         # call stack
        self.labels = {}        # map label to instruction index
        self.running = True     # control execution loop
        self.clock_cycles = 0   # simulated clock cycles
        self.max_depth = max_depth  # max allowed recursion depth

        # cost map
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

        self.call_depth = 0  # call depth for recursion limits
        self.executed_instructions = {}  # executed instructions for debugging

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

        # Debugging output
        print(f"PC: {self.pc}, Executing: {inst_type}, Instruction: {instruction}")
        self.executed_instructions[self.pc] = self.executed_instructions.get(self.pc, 0) + 1
        if self.executed_instructions[self.pc] > 10:
            print(f"Warning: Instruction at PC {self.pc} has been executed more than 10 times.")

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

            if self.call_depth >= self.max_depth:
                raise RecursionError(f"Max recursion depth reached: {self.max_depth}")

            self.call_depth += 1
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
                # Save the return value before restoring memory
                return_value = self.memory.get("result", 0)
                # Restore program counter and memory state
                self.pc, self.memory = self.stack.pop()
                # Set the result in the caller's memory
                self.memory["result"] = return_value
                self.pc -= 1  # -1 to offset PC increment
                self.call_depth -= 1  # decrease recursion depth
            else:
                self.running = False

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

        print(f"Total 'clock cycles': {self.clock_cycles}")
        print(f"Program memory usage: {self.measure_program_memory()} bytes")
        print(f"Runtime memory usage: {self.measure_runtime_memory()} bytes")

    def measure_program_memory(self):
        return sum(sys.getsizeof(stmt) for stmt in self.program)

    def measure_runtime_memory(self):
        memory_usage = sys.getsizeof(self.memory)
        stack_usage = sum(sys.getsizeof(frame) for frame in self.stack)
        return memory_usage + stack_usage
