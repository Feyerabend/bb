class SSAConverter:
    def __init__(self, tac_program):
        self.tac_program = tac_program
        self.variable_versions = {}  # Tracks versions of variables
        self.ssa_program = []        # Stores the SSA program as structured data
        self.current_label = None    # Tracks the current label for context
        self.phi_functions = {}      # Stores the phi functions for SSA

    def get_new_version(self, var):
        """
        Increment and return a new version for a variable. Constants remain unchanged.
        """
        if var.isdigit():  # Constants remain unchanged - more digits?
            return var
        if var not in self.variable_versions:
            self.variable_versions[var] = 0
        else:
            self.variable_versions[var] += 1
        return f"{var}_{self.variable_versions[var]}"

    def get_current_version(self, var):
        """
        Return the current version of a variable. Constants remain unchanged.
        """
        if var.isdigit():  # Constants remain unchanged
            return var
        return f"{var}_{self.variable_versions.get(var, 0)}"

    def convert(self):
        """
        Convert TAC to SSA form.
        """
        for stmt in self.tac_program:
            if stmt['type'] == "assignment":
                # Rename left-hand variable and update right-hand operands
                new_var = self.get_new_version(stmt['left'])
                rhs = stmt['right']
                if rhs['type'] == "binary_op":
                    rhs['left'] = self.get_current_version(rhs['left'])
                    rhs['right'] = self.get_current_version(rhs['right'])
                elif rhs['type'] == "term":
                    rhs['value'] = self.get_current_version(rhs['value'])
                self.ssa_program.append({
                    "type": "assignment",
                    "dest": new_var,
                    "rhs": rhs
                })
                self.add_phi_for_variable(stmt['left'])
            elif stmt['type'] == "if":
                # Update condition variable
                condition = stmt['condition']
                condition['value'] = self.get_current_version(condition['value'])
                self.ssa_program.append({
                    "type": "if",
                    "condition": condition,
                    "target": stmt['label']
                })
            elif stmt['type'] == "goto":
                self.ssa_program.append({"type": "goto", "target": stmt['label']})
            elif stmt['type'] == "label":
                # At a label, insert phi functions for variables that need merging
                self.insert_phi_functions(stmt['name'])
                self.current_label = stmt['name']
                self.ssa_program.append({"type": "label", "name": self.current_label})
        return self.ssa_program

    def add_phi_for_variable(self, var):
        """
        Adds a phi function for the given variable at the appropriate label.
        """
        if var not in self.phi_functions:
            self.phi_functions[var] = []
        self.phi_functions[var].append(self.get_current_version(var))

    def insert_phi_functions(self, label):
        """
        Insert phi functions for all variables that need to be merged at this label.
        """
        for var, versions in self.phi_functions.items():
            if len(versions) > 1:  # Only create phi functions for variables with multiple versions
                self.ssa_program.append({
                    "type": "assignment",
                    "dest": f"{var}_phi",
                    "rhs": {
                        "type": "phi",
                        "versions": versions
                    }
                })
                # Reset phi versions for the next block
                self.phi_functions[var] = []

    def print_ssa(self):
        """
        Print the SSA program in a readable format.
        """
        for stmt in self.ssa_program:
            if stmt['type'] == "assignment":
                rhs = stmt['rhs']
                if rhs['type'] == "binary_op":
                    print(f"{stmt['dest']} = {rhs['left']} {rhs['operator']} {rhs['right']}")
                elif rhs['type'] == "term":
                    print(f"{stmt['dest']} = {rhs['value']}")
                elif rhs['type'] == "phi":
                    print(f"{stmt['dest']} = phi({', '.join(rhs['versions'])})")
            elif stmt['type'] == "if":
                condition = stmt['condition']
                print(f"if {condition['value']} goto {stmt['target']}")
            elif stmt['type'] == "goto":
                print(f"goto {stmt['target']}")
            elif stmt['type'] == "label":
                print(f"label {stmt['name']}:")

# Example of how to use the SSAConverter
def test_ssa_converter():
    tac_program = [
        {"type": "assignment", "left": "x", "right": {"type": "term", "value": "10"}},
        {"type": "assignment", "left": "t1", "right": {"type": "binary_op", "left": "x", "operator": "<", "right": "15"}},
        {"type": "label", "name": "label_1"},
        {"type": "if", "condition": {"type": "term", "value": "t1"}, "label": "label_2"},
        {"type": "assignment", "left": "t2", "right": {"type": "binary_op", "left": "x", "operator": "+", "right": "1"}},
        {"type": "assignment", "left": "x", "right": {"type": "term", "value": "t2"}},
        {"type": "print", "value": "x"},
        {"type": "goto", "label": "label_1"},
        {"type": "label", "name": "label_2"},
    ]

    converter = SSAConverter(tac_program)
    ssa_program = converter.convert()
    converter.print_ssa()

if __name__ == "__main__":
    test_ssa_converter()