import re
from collections import defaultdict

class SSAConverter:
    def __init__(self, tac_lines):
        self.tac_lines = tac_lines
        self.ssa_code = []
        self.variable_versions = defaultdict(int)
        self.defined_in_blocks = defaultdict(set)
        self.current_block = None
        self.block_predecessors = defaultdict(set)
        self.block_variables = defaultdict(set)

    def get_new_version(self, var):
        """Generate a new SSA version for a variable."""
        self.variable_versions[var] += 1
        return f"{var}_{self.variable_versions[var]}"

    def get_current_version(self, var):
        """Return the latest SSA version of a variable."""
        return f"{var}_{self.variable_versions[var]}" if var in self.variable_versions else var

    def insert_phi_functions(self):
        """Insert phi-functions for variables with multiple versions at loop headers."""
        for block, variables in self.block_variables.items():
            for var in variables:
                if len(self.block_predecessors[block]) > 1:  # Need a phi function
                    phi_name = self.get_new_version(var)
                    phi_args = []
                    for predecessor in self.block_predecessors[block]:
                        prev_version = self.get_current_version(var)
                        phi_args.append(f"{prev_version} from {predecessor}")
                    self.ssa_code.insert(0, f"{phi_name} = φ({', '.join(phi_args)})")
                    self.variable_versions[var] += 1  # Increment version after phi

    def process_line(self, line):
        tokens = line.strip().split()

        if not tokens:
            return

        if tokens[0].endswith(":"):  # Label (start of a basic block)
            self.current_block = tokens[0][:-1]
            self.ssa_code.append(line)
            return

        if tokens[0] == "CALL":  # Function Call Handling
            func_name = tokens[1]
            self.ssa_code.append(f"CALL {func_name}")
            return

        if "=" in tokens:  # Assignment
            var_name = tokens[0]
            expr = " ".join(tokens[2:])
            expr_with_versions = re.sub(
                r'\b([a-zA-Z_][a-zA-Z0-9_.]*)\b',
                lambda m: self.get_current_version(m.group(1)),
                expr
            )
            new_version = self.get_new_version(var_name)
            self.ssa_code.append(f"{new_version} = {expr_with_versions}")
            self.block_variables[self.current_block].add(var_name)
            return

        if tokens[0] in {"IF_NOT", "GOTO"}:  # Control Flow
            label = tokens[-1]
            self.block_predecessors[label].add(self.current_block)
            self.ssa_code.append(f"{tokens[0]} {self.get_current_version(tokens[1])} {label}")
            return

        if tokens[0] == "RETURN":  # Return Statement
            if len(tokens) > 1:
                return_value = self.get_current_version(tokens[1])
                self.ssa_code.append(f"RETURN {return_value}")
            else:
                self.ssa_code.append("RETURN")
            return

        print(f"Warning: Unexpected TAC line format: {line}")

    def convert(self):
        """Convert TAC to SSA form."""
        for line in self.tac_lines:
            self.process_line(line)
        self.insert_phi_functions()
        return "\n".join(self.ssa_code)


# Example TAC input
tac_code = """
computeGCD:
L0:
t0 = LOAD b.g
t1 = LOAD 0
t2 = != t0 t1
IF_NOT t2 L1
t3 = LOAD a.g
t4 = LOAD b.g
t5 = > t3 t4
IF_NOT t5 L2
t6 = LOAD a.g
t7 = LOAD b.g
t8 = - t6 t7
a.g = t8
L2:
t9 = LOAD a.g
t10 = LOAD b.g
t11 = <= t9 t10
IF_NOT t11 L3
t12 = LOAD b.g
t13 = LOAD a.g
t14 = - t12 t13
b.g = t14
L3:
GOTO L0
L1:
t15 = LOAD a.g
gcd.g = t15
RETURN
main:
t16 = LOAD 48
a.g = t16
t17 = LOAD 18
b.g = t17
CALL computeGCD
"""

# Convert TAC to SSA
ssa_converter = SSAConverter(tac_code.strip().split("\n"))
ssa_output = ssa_converter.convert()
print(ssa_output)