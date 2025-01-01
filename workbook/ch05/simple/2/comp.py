
class TacToVmConverter:
    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.vm_code = []
        self.symbol_table = {}
        
    def convert(self):
        for line in self.tac_code:
            self._process_tac(line)
        return self.symbol_table, self.vm_code
        
    def _process_tac(self, line):
        # split TAC line into left-hand side, operation, and right-hand side
        parts = line.split(" = ")
        lhs = parts[0].strip()  # left-hand side (x, t1, etc.)
        rhs = parts[1].strip()  # right-hand side (2025, x + y, etc.)

        # if right-hand side is simple number, PUSH it
        if rhs.isdigit():
            self.vm_code.append(f"PUSH {rhs}")
            self.vm_code.append(f"STORE {lhs}")
        elif rhs.isidentifier():  # but if it's a variable, LOAD it
            self.vm_code.append(f"LOAD {rhs}")
            self.vm_code.append(f"STORE {lhs}")
        else:  # otherwise, arithmetic operations
            self._process_expression(lhs, rhs)

    def _process_expression(self, lhs, rhs):
        # split expression by operator (+, -, *, /)
        for op in ["+", "-", "*", "/"]:
            if op in rhs:
                left_expr, right_expr = rhs.split(op)
                left_expr = left_expr.strip()
                right_expr = right_expr.strip()

                # instructions for both operands
                temp1 = self._get_temp_var()
                temp2 = self._get_temp_var()

                # left and right operands (recursive!)
                self._process_operand(temp1, left_expr)
                self._process_operand(temp2, right_expr)

                # perform operation
                self.vm_code.append(f"LOAD {temp1}")
                self.vm_code.append(f"LOAD {temp2}")

                op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}
                self.vm_code.append(op_map[op])

                # store the result in the left-hand side variable
                self.vm_code.append(f"STORE {lhs}")
                return

    def _process_operand(self, temp, operand):
        if operand.isdigit():
            self.vm_code.append(f"PUSH {operand}")
            self.vm_code.append(f"STORE {temp}")
        elif operand.isidentifier():
            self.vm_code.append(f"LOAD {operand}")
            self.vm_code.append(f"STORE {temp}")
    
    def _get_temp_var(self):
        # generate temporary variable name
        temp_var = f"t{len(self.symbol_table) + 1}"
        self.symbol_table[temp_var] = None
        return temp_var


# example
tac_code = [
    "x = 2025",
    "y = 1477",
    "t1 = x + y",
    "t2 = 7 + 9",
    "t3 = 5 * t2",
    "t4 = t3 / 2",
    "t5 = t1 - t4",
    "z = t5"
]

# convert TAC to VM instructions
converter = TacToVmConverter(tac_code)
symbol_table, vm_code = converter.convert()

print("Symbol Table:", symbol_table)
print("VM Instructions:", vm_code)
