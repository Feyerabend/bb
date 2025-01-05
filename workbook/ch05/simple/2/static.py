
class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children if children is not None else []

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


class StaticChecker:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = { }  # symbols (consts, vars, procedures)
        self.errors = []

    def check(self):
        self.visit(self.ast)
        return self.errors

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr, value in node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        self.visit(item)
            elif isinstance(value, ASTNode):
                self.visit(value)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for const in node.consts:
            self.visit(const)
        for var in node.vars:
            self.visit(var)
        for proc in node.procedures:
            self.visit(proc)
        if node.statement:
            self.visit(node.statement)

    def visit_ConstDeclaration(self, node):
        if node.ident in self.symbol_table:
            self.errors.append((4, f"Duplicate declaration of constant '{node.ident}'"))
        else:
            self.symbol_table[node.ident] = ('const', node.value)

    def visit_VarDeclaration(self, node):
        for ident in node.idents:
            if ident in self.symbol_table:
                self.errors.append((4, f"Duplicate declaration of variable '{ident}'"))
            else:
                self.symbol_table[ident] = ('var', None)

    def visit_ProcedureDeclaration(self, node):
        if node.ident in self.symbol_table:
            self.errors.append((4, f"Duplicate declaration of procedure '{node.ident}'"))
        else:
            self.symbol_table[node.ident] = ('procedure', node.block)
        self.visit(node.block)

    def visit_AssignmentStatement(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append((11, f"Undeclared identifier '{node.ident}'"))
        elif self.symbol_table[node.ident][0] == 'const':
            self.errors.append((12, f"Assignment to constant '{node.ident}' is not allowed"))
        self.visit(node.expression)

    def visit_CallStatement(self, node):
        if node.ident not in self.symbol_table:
            self.errors.append((11, f"Undeclared identifier '{node.ident}'"))
        elif self.symbol_table[node.ident][0] != 'procedure':
            self.errors.append((15, f"Call of non-procedure '{node.ident}' is not allowed"))

    def visit_IfStatement(self, node):
        self.visit(node.condition)
        self.visit(node.then_statement)

    def visit_WhileStatement(self, node):
        self.visit(node.condition)
        self.visit(node.do_statement)

    def visit_Condition(self, node):
        self.visit(node.left)
        if node.right:
            self.visit(node.right)

    def visit_Expression(self, node):
        if node.left:
            self.visit(node.left)
        if node.right:
            self.visit(node.right)

checker = StaticChecker(ast)
errors = checker.check()

if errors:
    for code, message in errors:
        print(f"Error {code}: {message}")
else:
    print("Static analysis passed with no errors.")
