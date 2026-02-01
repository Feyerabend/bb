
# TAC to RISC-V-like assembly
def tac_to_riscv(tac_program):
    assembly = []
    register_map = {}  # map variables to registers
    next_reg = 1       # registers x1, x2, ..., x31

    def get_register(var):
        nonlocal next_reg
        if var not in register_map:
            register_map[var] = f"x{next_reg}"
            next_reg += 1
        return register_map[var]

    for instruction in tac_program:
        inst_type = instruction["type"]

        if inst_type == "assignment":
            dest = instruction["dest"]
            rhs = instruction["rhs"]
            if rhs["type"] == "term":
                reg = get_register(dest)
                val = rhs["value"]
                assembly.append(f"ADDI {reg}, x0, {val}  # {dest} = {val}")
            elif rhs["type"] == "binary_op":
                dest_reg = get_register(dest)
                left = get_register(rhs["left"]["value"])
                right = get_register(rhs["right"]["value"])
                op = rhs["operator"]
                op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}
                assembly.append(f"{op_map[op]} {dest_reg}, {left}, {right}")

        elif inst_type == "if":
            condition = instruction["condition"]
            left = get_register(condition["left"]["value"])
            right = get_register(condition["right"]["value"])
            label = instruction["label"]
            op = condition["operator"]
            op_map = {"<=": "SLE", "<": "SLT"}
            temp_reg = f"x{next_reg}"
            next_reg += 1
            assembly.append(f"{op_map[op]} {temp_reg}, {left}, {right}")
            assembly.append(f"BEQ {temp_reg}, x0, {label}")

        elif inst_type == "goto":
            label = instruction["label"]
            assembly.append(f"J {label}")

        elif inst_type == "label":
            label = instruction["identifier"]
            assembly.append(f"{label}:")

        elif inst_type == "print":
            value = instruction["value"]
            reg = get_register(value)
            assembly.append(f"PRINT {reg}  # print {value}")

        elif inst_type == "halt":
            assembly.append("HALT")

    return "\n".join(assembly)


# TAC program for factorial calculation
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

# Translate the program to RISC-V-like assembly
assembly_output = tac_to_riscv(factorial_program)
print(assembly_output)

# start:
#   ADDI x1, x0, 5  # n = 5
#   ADDI x2, x0, 1  # result = 1
# loop:
#   SLE x4, x1, x3
#   BEQ x4, x0, end
#   MUL x2, x2, x1
#   SUB x1, x1, x5
#   J loop
# end:
#   PRINT x2  # print result
#   HALT
