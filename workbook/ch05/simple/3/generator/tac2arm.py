class ARMAssembler:
    def __init__(self):
        self.instructions = []
        self.register_map = {}  # Maps variables to registers
        self.register_counter = 0  # To allocate registers
        self.label_counter = 0  # To generate unique labels if needed

    def new_register(self):
        reg = f"r{self.register_counter}"
        self.register_counter += 1
        if self.register_counter > 12:
            raise ValueError("Register overflow: Too many variables for available registers.")
        return reg

    def get_register(self, variable):
        if variable not in self.register_map:
            reg = self.new_register()
            self.register_map[variable] = reg
        return self.register_map[variable]

    def generate_arm(self, program):
        self.add_preamble()
        for statement in program:
            if statement["type"] == "assignment":
                dest = self.get_register(statement["dest"])
                rhs = statement["rhs"]
                self.generate_rhs(dest, rhs)

            elif statement["type"] == "if":
                condition = statement["condition"]
                label = statement["label"]
                self.generate_condition(condition, label)

            elif statement["type"] == "goto":
                label = statement["label"]
                self.instructions.append(f"B {label}")

            elif statement["type"] == "label":
                label = statement["identifier"]
                self.instructions.append(f"{label}:")

            elif statement["type"] == "print":
                variable = statement["value"]
                reg = self.get_register(variable)
                self.instructions.append(f"MOV r0, {reg}")  # Move variable to r0
                self.instructions.append(f"BL printf")  # Call printf function (assumed in runtime)

            elif statement["type"] == "call":
                func_name = statement["identifier"]
                arg_count = statement["arg_count"]
                for i in range(arg_count):
                    arg_key = f"arg{i}"
                    arg_reg = self.get_register(arg_key)
                    self.instructions.append(f"MOV r{i}, {arg_reg}")  # Pass arguments in r0, r1, ...
                self.instructions.append(f"BL {func_name}")

            elif statement["type"] == "return":
                self.instructions.append(f"BX lr")  # Return to caller (link register)

            elif statement["type"] == "halt":
                self.instructions.append(f"BL exit")  # Exit the program

        self.add_postamble()

    def generate_rhs(self, dest, rhs):
        if rhs["type"] == "term":
            value = rhs["value"]
            if isinstance(value, str) and value.isdigit():  # Immediate value
                self.instructions.append(f"MOV {dest}, #{value}")
            else:  # Variable
                reg = self.get_register(value)
                self.instructions.append(f"MOV {dest}, {reg}")
        elif rhs["type"] == "binary_op":
            left = rhs["left"]
            right = rhs["right"]
            operator = rhs["operator"]

            left_reg = self.get_register(left["value"]) if left["type"] == "term" else None
            right_reg = self.get_register(right["value"]) if right["type"] == "term" else None

            if operator == "+":
                self.instructions.append(f"ADD {dest}, {left_reg}, {right_reg}")
            elif operator == "-":
                self.instructions.append(f"SUB {dest}, {left_reg}, {right_reg}")
            elif operator == "*":
                self.instructions.append(f"MUL {dest}, {left_reg}, {right_reg}")
            elif operator == "/":
                self.instructions.append(f"UDIV {dest}, {left_reg}, {right_reg}")

    def generate_condition(self, condition, label):
        left = condition["left"]
        right = condition["right"]
        operator = condition["operator"]

        left_reg = self.get_register(left["value"])
        right_reg = self.get_register(right["value"])
        self.instructions.append(f"CMP {left_reg}, {right_reg}")

        if operator == "==":
            self.instructions.append(f"BEQ {label}")
        elif operator == "!=":
            self.instructions.append(f"BNE {label}")
        elif operator == "<":
            self.instructions.append(f"BLT {label}")
        elif operator == "<=":
            self.instructions.append(f"BLE {label}")
        elif operator == ">":
            self.instructions.append(f"BGT {label}")
        elif operator == ">=":
            self.instructions.append(f"BGE {label}")

    def add_preamble(self):
        self.instructions.append(".section .data")
        self.instructions.append(".section .text")
        self.instructions.append(".global _start")
        self.instructions.append("_start:")

    def add_postamble(self):
        self.instructions.append("exit:")
        self.instructions.append("MOV r7, #1")  # Syscall for exit
        self.instructions.append("SVC #0")      # Trigger syscall

    def get_code(self):
        return "\n".join(self.instructions)


# simple TAC program
tac_program = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "term", "value": "10"}},
    {"type": "label", "identifier": "loop"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": "==", "right": {"type": "term", "value": "0"}}, "label": "end"},
    {"type": "assignment", "dest": "x", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "x"}, "operator": "-", "right": {"type": "term", "value": "1"}}},
    {"type": "goto", "label": "loop"},
    {"type": "label", "identifier": "end"},
    {"type": "halt"}
]

assembler = ARMAssembler()
assembler.generate_arm(tac_program)
print(assembler.get_code())


factorial_tac = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "n", "rhs": {"type": "term", "value": "5"}},  # Compute factorial of 5
    {"type": "assignment", "dest": "result", "rhs": {"type": "term", "value": "1"}},  # result = 1
    {"type": "label", "identifier": "loop"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "n"}, "operator": "==", "right": {"type": "term", "value": "0"}}, "label": "end"},
    {"type": "assignment", "dest": "result", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "result"}, "operator": "*", "right": {"type": "term", "value": "n"}}},  # result *= n
    {"type": "assignment", "dest": "n", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "n"}, "operator": "-", "right": {"type": "term", "value": "1"}}},  # n -= 1
    {"type": "goto", "label": "loop"},
    {"type": "label", "identifier": "end"},
    {"type": "print", "value": "result"},  # Print result
    {"type": "halt"}
]


fibonacci_tac = [
    {"type": "label", "identifier": "start"},
    {"type": "assignment", "dest": "count", "rhs": {"type": "term", "value": "10"}},  # count = 10
    {"type": "assignment", "dest": "a", "rhs": {"type": "term", "value": "0"}},  # a = 0
    {"type": "assignment", "dest": "b", "rhs": {"type": "term", "value": "1"}},  # b = 1
    {"type": "label", "identifier": "loop"},
    {"type": "if", "condition": {"type": "binary_op", "left": {"type": "term", "value": "count"}, "operator": "==", "right": {"type": "term", "value": "0"}}, "label": "end"},
    {"type": "print", "value": "a"},  # print a
    {"type": "assignment", "dest": "temp", "rhs": {"type": "term", "value": "b"}},  # temp = b
    {"type": "assignment", "dest": "b", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "a"}, "operator": "+", "right": {"type": "term", "value": "b"}}},  # b = a + b
    {"type": "assignment", "dest": "a", "rhs": {"type": "term", "value": "temp"}},  # a = temp
    {"type": "assignment", "dest": "count", "rhs": {"type": "binary_op", "left": {"type": "term", "value": "count"}, "operator": "-", "right": {"type": "term", "value": "1"}}},  # count -= 1
    {"type": "goto", "label": "loop"},
    {"type": "label", "identifier": "end"},
    {"type": "halt"}
]


assembler = ARMAssembler()
assembler.generate_arm(factorial_tac)
print("\nFactorial ARM Assembly:")
print(assembler.get_code())

assembler = ARMAssembler()
assembler.generate_arm(fibonacci_tac)
print("\nFibonacci ARM Assembly:")
print(assembler.get_code())

