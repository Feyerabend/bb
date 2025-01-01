class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f"ASTNode(kind={self.kind}, value={self.value}, children={self.children})"


class TACGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.tac = []
        self.temp_counter = 0

    def generate_tac(self, node=None):
        if node is None:
            node = self.ast

        if node.kind == "PROGRAM":
            for child in node.children:
                self.generate_tac(child)

        elif node.kind == "ASSIGN":
            var_name = node.children[0].value  # Left-hand side (variable)
            expr = node.children[1]  # Right-hand side (expression)
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


# example
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
tac_generator = TACGenerator(ast)
tac_generator.generate_tac()

for instruction in tac_generator.get_tac():
    print(instruction)
