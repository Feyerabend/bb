class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children if children is not None else []

def print_ast(node, indent="", is_last=True):
    prefix = "└── " if is_last else "├── "
    
    print(f"{indent}{prefix}{node.kind}({node.value})")
    
    indent += "    " if is_last else "│   "
    for i, child in enumerate(node.children):
        print_ast(child, indent, is_last=(i == len(node.children) - 1))


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

print_ast(ast)
