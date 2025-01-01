import re

class CodeOptimizer:
    def __init__(self, stop_var="stop_variable"):
        self.variables = {}  # hold variable assignments
        self.used_variables = set()  # track variables that are used
        self.final_variables = set()  # track final output variables
        self.stop_var = stop_var  # variable to prevent elimination (e.g., 'stop_variable')

    def extract_variables_from_expression(self, expression):
        # match variable names (assuming variables are identifiers like x, t1, etc.)
        return set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expression))

    def constant_folding(self, expression):
        # try evaluate the expression directly and fold constants, if possible
        try:
            result = eval(expression)
            return str(result)
        except:
            return expression

    def analyze_code(self, code_lines):
        for line in code_lines:
            parts = line.split("=")
            if len(parts) == 2:
                var, expr = parts
                var = var.strip()
                expr = expr.strip()

                # fold constants in the expression
                expr = self.constant_folding(expr)
                self.variables[var] = expr

                # track variables used in the expression
                used_vars = self.extract_variables_from_expression(expr)
                self.used_variables.update(used_vars)

    def eliminate_dead_code(self):
        for var in list(self.variables):
            if var != self.stop_var and var not in self.used_variables:
                del self.variables[var]

    def optimize_code(self, code_lines):
        self.analyze_code(code_lines)
        self.eliminate_dead_code()

        # rebuild optimised code after elimination
        optimized_code = []
        for var, expr in self.variables.items():
            optimized_code.append(f"{var} = {expr}")
        
        return optimized_code


# Example usage
code_lines = [
    "x = 2025",
    "y = 1477",
    "t1 = x + y",
    "t2 = 7 + 9",
    "t3 = 5 * t2",
    "t4 = t3 / 2",
    "t5 = t1 - t4",
    "z = t5",  # 'z' is not used anywhere
    "stop_variable = 0" # special
]

optimizer = CodeOptimizer()
optimized_code = optimizer.optimize_code(code_lines)

print("After Dead Code Elimination and Optimisation:")
for line in optimized_code:
    print(line)