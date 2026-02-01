
class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children or []

    def __repr__(self):
        if isinstance(self.value, int): # or (int, float) - float not tested
            value_repr = str(self.value)
        elif self.kind == "IDENTIFIER":
            value_repr = f'"{self.value}"'
        else:
            value_repr = str(self.value)
        
        return (f"ASTNode(kind={self.kind}, value={value_repr}, "
                f"children={self.children})")

class CompilerUtils:
    def __init__(self, ast, constant_folding=True):
        self.ast = ast
        self.symbol_table = {}
        self.instructions = []
        self.constant_folding = constant_folding  # enable or disable

    def build_symbol_table(self, node=None):
        if node is None:
            node = self.ast

        if node.kind == "PROGRAM":
            for child in node.children:
                self.build_symbol_table(child)
        elif node.kind == "ASSIGN":
            var_name = node.children[0].value  # left-hand: IDENTIFIER
            expr = node.children[1]  # right-hand: expression

            # 1: add the variable to the symbol table if it's not already there
            if var_name not in self.symbol_table:
                self.symbol_table[var_name] = None  # mark as uninitialised

            # 2: evaluate constants, if constant folding is enabled
            if self.constant_folding:
                constant_value = self.evaluate_constant(expr)
                if constant_value is not None:
                    # if constant, store the value
                    self.symbol_table[var_name] = constant_value
            else:
                # if constant folding, just store the expression in the symbol table
                self.symbol_table[var_name] = None

    def evaluate_constant(self, node):

        if node.kind == "NUMBER":
            return node.value

        elif node.kind == "IDENTIFIER":
            # look up variable in the symbol table (constants only)
            return self.symbol_table.get(node.value)

        elif node.kind == "PLUS":
            left = self.evaluate_constant(node.children[0])
            right = self.evaluate_constant(node.children[1])
            return left + right if left is not None and right is not None else None

        elif node.kind == "MINUS":
            left = self.evaluate_constant(node.children[0])
            right = self.evaluate_constant(node.children[1])
            return left - right if left is not None and right is not None else None

        elif node.kind == "TIMES":
            left = self.evaluate_constant(node.children[0])
            right = self.evaluate_constant(node.children[1])
            return left * right if left is not None and right is not None else None

        elif node.kind == "DIVIDE":
            left = self.evaluate_constant(node.children[0])
            right = self.evaluate_constant(node.children[1])
            return left // right if left is not None and right is not None else None

        return None

    def generate_code(self, node=None):
        if node is None:
            node = self.ast

        if node.kind == "PROGRAM":
            for child in node.children:
                self.generate_code(child)

        elif node.kind == "ASSIGN":
            var_name = node.children[0].value  # left-hand
            expr = node.children[1]  # right-hand
            # generate code for the right-hand side expression
            self.generate_code(expr)
            self.instructions.append(f"STORE {var_name}")

        elif node.kind in { "PLUS", "MINUS", "TIMES", "DIVIDE" }:
            self.generate_code(node.children[0])  # left operand
            self.generate_code(node.children[1])  # right operand
            op_map = {
                "PLUS": "ADD",
                "MINUS": "SUB",
                "TIMES": "MUL",
                "DIVIDE": "DIV"
            }
            self.instructions.append(op_map[node.kind])

        elif node.kind == "NUMBER":
            self.instructions.append(f"PUSH {node.value}")

        elif node.kind == "IDENTIFIER":
            self.instructions.append(f"LOAD {node.value}")

    def compile(self):
        self.build_symbol_table()
        self.generate_code()
        return self.symbol_table, self.instructions

# example
ast = ASTNode(kind="PROGRAM", value=None, children=[ASTNode(kind="ASSIGN", value=None, children=[ASTNode(kind="IDENTIFIER", value="x", children=[]), ASTNode(kind="NUMBER", value=2025, children=[])]), ASTNode(kind="ASSIGN", value=None, children=[ASTNode(kind="IDENTIFIER", value="y", children=[]), ASTNode(kind="NUMBER", value=1477, children=[])]), ASTNode(kind="ASSIGN", value=None, children=[ASTNode(kind="IDENTIFIER", value="z", children=[]), ASTNode(kind="MINUS", value=None, children=[ASTNode(kind="PLUS", value=None, children=[ASTNode(kind="IDENTIFIER", value="x", children=[]), ASTNode(kind="IDENTIFIER", value="y", children=[])]), ASTNode(kind="DIVIDE", value=None, children=[ASTNode(kind="TIMES", value=None, children=[ASTNode(kind="NUMBER", value=5, children=[]), ASTNode(kind="PLUS", value=None, children=[ASTNode(kind="NUMBER", value=7, children=[]), ASTNode(kind="NUMBER", value=9, children=[])])]), ASTNode(kind="NUMBER", value=2, children=[])])])])])

compiler = CompilerUtils(ast, constant_folding=True)
symbol_table, instructions = compiler.compile()
print("Symbol Table:", symbol_table)
print("Instructions:", instructions)

# Output:
# Symbol Table: {'x': 2025, 'y': 1477, 'z': 3462}
# Instructions: [
# 'PUSH 2025',
# 'STORE x',
# 'PUSH 1477',
# 'STORE y',
# 'LOAD x',
# 'LOAD y',
# 'ADD',
# 'PUSH 5',
# 'PUSH 7',
# 'PUSH 9',
# 'ADD',
# 'MUL',
# 'PUSH 2',
# 'DIV',
# 'SUB',
# 'STORE z']

compiler = CompilerUtils(ast, constant_folding=False)
symbol_table, instructions = compiler.compile()
print("Symbol Table:", symbol_table)
print("Instructions:", instructions)

# Output:
# Symbol Table: {'x': None, 'y': None, 'z': None}
# Same instructions as above
