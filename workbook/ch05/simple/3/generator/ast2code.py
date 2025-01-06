
class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f"ASTNode(kind={self.kind}, value={self.value}, children={self.children})"

class AssemblyGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.tac = []
        self.temp_counter = 0
        self.label_counter = 0
        self.assembly = []
        self.registers = {}

    def generate_tac(self, node=None):
        if node is None:
            node = self.ast

        if node.kind == "PROGRAM":
            for child in node.children:
                self.generate_tac(child)

        elif node.kind == "ASSIGN":
            var_name = node.children[0].value  # left-hand: variable
            expr = node.children[1]  # right-hand: expression
            result = self.generate_expression(expr)
            self.tac.append(f"{var_name} = {result}")

        elif node.kind in {"PLUS", "MINUS", "TIMES", "DIVIDE"}:
            left = self.generate_expression(node.children[0])
            right = self.generate_expression(node.children[1])
            temp_result = self.new_temp()
            op_map = {
                "PLUS": "+",
                "MINUS": "-",
                "TIMES": "*",
                "DIVIDE": "/"
            }
            self.tac.append(f"{temp_result} = {left} {op_map[node.kind]} {right}")
            return temp_result

        elif node.kind == "NUMBER":
            return node.value

        elif node.kind == "IDENTIFIER":
            return node.value

    def generate_expression(self, expr):
        if expr.kind in {"PLUS", "MINUS", "TIMES", "DIVIDE"}:
            left = self.generate_expression(expr.children[0])
            right = self.generate_expression(expr.children[1])
            temp_result = self.new_temp()
            op_map = {
                "PLUS": "+",
                "MINUS": "-",
                "TIMES": "*",
                "DIVIDE": "/"
            }
            self.tac.append(f"{temp_result} = {left} {op_map[expr.kind]} {right}")
            return temp_result

        elif expr.kind == "NUMBER":
            return expr.value

        elif expr.kind == "IDENTIFIER":
            return expr.value

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def get_tac(self):
        return self.tac

    def generate_assembly(self):
        for instruction in self.tac:
            parts = instruction.split(" = ")
            if len(parts) == 2:
                # assignment
                lhs = parts[0]
                rhs = parts[1]
                if rhs.isdigit():  # a constant
                    self.assembly.append(f"MOV {lhs}, #{rhs}")
                else:  # a variable or temp
                    # break down into the proper three-address instruction
                    op_parts = rhs.split(" ")
                    if len(op_parts) == 3:
                        lhs_reg = op_parts[0]
                        operator = op_parts[1]
                        rhs_reg = op_parts[2]
                        if operator == "+":
                            self.assembly.append(f"ADD {lhs}, {lhs_reg}, {rhs_reg}")
                        elif operator == "-":
                            self.assembly.append(f"SUB {lhs}, {lhs_reg}, {rhs_reg}")
                        elif operator == "*":
                            self.assembly.append(f"MUL {lhs}, {lhs_reg}, {rhs_reg}")
                        elif operator == "/":
                            self.assembly.append(f"SDIV {lhs}, {lhs_reg}, {rhs_reg}")
                    else:
                        self.assembly.append(f"MOV {lhs}, {rhs}")

    def print_assembly(self):
        print("\n".join(self.assembly))


# example AST creation
ast = ASTNode(kind="PROGRAM", value=None, children=[
    ASTNode(kind="ASSIGN", value=None, children=[
        ASTNode(kind="IDENTIFIER", value="x", children=[]),
        ASTNode(kind="NUMBER", value=2025, children=[])
    ]),
    ASTNode(kind="ASSIGN", value=None, children=[
        ASTNode(kind="IDENTIFIER", value="y", children=[]),
        ASTNode(kind="NUMBER", value=1477, children=[])
    ]),
    ASTNode(kind="ASSIGN", value=None, children=[
        ASTNode(kind="IDENTIFIER", value="z", children=[]),
        ASTNode(kind="MINUS", value=None, children=[
            ASTNode(kind="PLUS", value=None, children=[
                ASTNode(kind="IDENTIFIER", value="x", children=[]),
                ASTNode(kind="IDENTIFIER", value="y", children=[])
            ]),
            ASTNode(kind="DIVIDE", value=None, children=[
                ASTNode(kind="TIMES", value=None, children=[
                    ASTNode(kind="NUMBER", value=5, children=[]),
                    ASTNode(kind="PLUS", value=None, children=[
                        ASTNode(kind="NUMBER", value=7, children=[]),
                        ASTNode(kind="NUMBER", value=9, children=[])
                    ])
                ]),
                ASTNode(kind="NUMBER", value=2, children=[])
            ])
        ])
    ])
])

# generate TAC from AST
tac_generator = AssemblyGenerator(ast)
tac_generator.generate_tac()

# print TAC
print("TAC Code:")
for instruction in tac_generator.get_tac():
    print(instruction)

# generate Assembly from TAC
tac_generator.generate_assembly()

# print Assembly
print("\nAssembly Code:")
tac_generator.print_assembly()
