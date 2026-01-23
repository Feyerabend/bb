class SSAConverter:
    def __init__(self, tac_program):
        self.tac_program = tac_program
        self.variable_versions = { }
        self.ssa_program = []
        self.label_to_phi = { }

    def get_new_version(self, var):
        if var not in self.variable_versions:
            self.variable_versions[var] = 0
        else:
            self.variable_versions[var] += 1
        return f"{var}_{self.variable_versions[var]}"

    def get_current_version(self, var):
        if var.isdigit():
            return var
        return f"{var}_{self.variable_versions.get(var, 0)}"

    def add_phi_function(self, label, var):
        if label not in self.label_to_phi:
            self.label_to_phi[label] = {}
        if var not in self.label_to_phi[label]:
            self.label_to_phi[label][var] = []
        self.label_to_phi[label][var].append(self.get_current_version(var))

    def convert(self):
        for stmt in self.tac_program:

            if stmt['type'] == "assignment":
                new_var = self.get_new_version(stmt['left'])
                if stmt['right']['type'] == "binary_op":
                    left = self.get_current_version(stmt['right']['left'])
                    right = self.get_current_version(stmt['right']['right'])
                    stmt['right']['left'] = left
                    stmt['right']['right'] = right
                elif stmt['right']['type'] == "term":
                    stmt['right']['value'] = self.get_current_version(stmt['right']['value'])
                stmt['left'] = new_var
                self.ssa_program.append(stmt)

            elif stmt['type'] == "if":
                condition = stmt['condition']
                if condition['type'] == "term":
                    condition['value'] = self.get_current_version(condition['value'])
                stmt['condition'] = condition
                label = stmt['label']
                for var in self.variable_versions:
                    self.add_phi_function(label, var)

                self.ssa_program.append(stmt)

            elif stmt['type'] == "goto":
                label = stmt['label']
                for var in self.variable_versions:
                    self.add_phi_function(label, var)
                self.ssa_program.append(stmt)

            elif stmt['type'] == "label":
                self.ssa_program.append(stmt)
                label_name = stmt['name']
                if label_name in self.label_to_phi:
                    for var, versions in self.label_to_phi[label_name].items():
                        phi_stmt = {
                            "type": "phi",
                            "var": var,
                            "versions": versions
                        }
                        self.ssa_program.append(phi_stmt)
            else:
                self.ssa_program.append(stmt)
        return self.ssa_program

    def print_ssa_program(self):
        for stmt in self.ssa_program:
            if stmt['type'] == "assignment":
                right = stmt['right']
                if right['type'] == "binary_op":
                    print(f"{stmt['left']} = {right['left']} {right['operator']} {right['right']}")
                elif right['type'] == "term":
                    print(f"{stmt['left']} = {right['value']}")
            elif stmt['type'] == "if":
                condition = stmt['condition']
                print(f"if {condition['value']} goto {stmt['label']}")
            elif stmt['type'] == "goto":
                print(f"goto {stmt['label']}")
            elif stmt['type'] == "label":
                print(f"label {stmt['name']}:")
            elif stmt['type'] == "phi":
                versions = ", ".join(stmt['versions'])
                print(f"{stmt['var']} = phi({versions})")
            else:
                print(f"Unknown statement type: {stmt}")

tac_program = [
    {"type": "assignment", "left": "x", "right": {"type": "term", "value": "10"}},
    {"type": "assignment", "left": "t1", "right": {"type": "binary_op", "left": "x", "operator": "<", "right": "15"}},
    {"type": "label", "name": "label_1"},
    {"type": "if", "condition": {"type": "term", "value": "t1"}, "label": "label_2"},
    {"type": "assignment", "left": "t2", "right": {"type": "binary_op", "left": "x", "operator": "+", "right": "1"}},
    {"type": "assignment", "left": "x", "right": {"type": "term", "value": "t2"}},
    {"type": "goto", "label": "label_1"},
    {"type": "label", "name": "label_2"}
]

ssa_converter = SSAConverter(tac_program)
ssa_program = ssa_converter.convert()

ssa_converter.print_ssa_program()
