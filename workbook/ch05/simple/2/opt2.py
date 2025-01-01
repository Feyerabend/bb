class Optimizer:
    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.optimized_tac = []
        self.symbol_table = {}
        self.used_variables = set()

    def optimize(self):
        # 1: Process each TAC line
        for line in self.tac_code:
            self._process_tac(line)
        
        # 2: Remove dead code
        self._remove_dead_code()

        # 3: Return the optimised TAC code
        return self.optimized_tac

    def _process_tac(self, line):
        parts = line.split(" = ")
        lhs = parts[0].strip()  # variable
        rhs = parts[1].strip()  # expression

        if rhs.isdigit():
            # constant assignment
            self.optimized_tac.append(f"{lhs} = {rhs}")
            self.used_variables.add(lhs)
        elif "+" in rhs or "-" in rhs or "*" in rhs or "/" in rhs:
            # arithmetic
            self._process_expression(lhs, rhs)
        else:
            # variable or other simple expression
            self.optimized_tac.append(f"{lhs} = {rhs}")
            self.used_variables.add(lhs)

    def _process_expression(self, lhs, rhs):
        rhs_parts = rhs.split(" ")
        
        for i, part in enumerate(rhs_parts):
            if part.isdigit():
                rhs_parts[i] = str(int(part))  # convert to int for constant folding
        
        # Constant Folding: If both operands are constants, fold the expression
        if len(rhs_parts) == 3 and rhs_parts[0].isdigit() and rhs_parts[2].isdigit():
            left = int(rhs_parts[0])
            op = rhs_parts[1]
            right = int(rhs_parts[2])
            result = self._evaluate_constant_expression(left, op, right)
            self.optimized_tac.append(f"{lhs} = {result}")
            self.used_variables.add(lhs)
        else:

            # Common Subexpression Elimination: Reuse previously computed expressions
            rhs_str = " ".join(rhs_parts)
            if rhs_str in self.symbol_table:
                self.optimized_tac.append(f"{lhs} = {self.symbol_table[rhs_str]}")
            else:
                self.optimized_tac.append(f"{lhs} = {rhs_str}")
                self.symbol_table[rhs_str] = lhs
            self.used_variables.add(lhs)

    def _evaluate_constant_expression(self, left, op, right):
        if op == "+":
            return left + right
        elif op == "-":
            return left - right
        elif op == "*":
            return left * right
        elif op == "/":
            return left // right
        return None

    def _remove_dead_code(self):
        # keep only assignments that are used in final TAC
        self.optimized_tac = [line for line in self.optimized_tac if self._is_used(line)]

    def _is_used(self, line):
        lhs = line.split(" = ")[0].strip()
        return lhs in self.used_variables


# example TAC (before)
tac_code = [
    "x = 2025",
    "y = 1477",
    "t1 = x + y",
    "t2 = 7 + 9",
    "t3 = 5 * t2",
    "t4 = t3 / 2",
    "t5 = t1 - t4",
    "z = t5",
    "t6 = x + y",  # redundant computation (CSE)
    "t7 = 0"       # dead code, not used later
]

optimizer = Optimizer(tac_code)
optimized_tac = optimizer.optimize()

print("Optimised TAC:")
for line in optimized_tac:
    print(line)