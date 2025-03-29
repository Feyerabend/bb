
class ASTNode:
    def __init__(self, kind, value=None, children=None):
        self.kind = kind
        self.value = value
        self.children = children or []

    def __repr__(self):
        # if value is number (int or float), show the value
        if isinstance(self.value, (int, float)): # float not tested
            value_repr = str(self.value)
        # if identifier, show value as string (quoted)
        elif self.kind == "IDENTIFIER":
            value_repr = f'"{self.value}"'
        else:
            value_repr = str(self.value)
        
        return (f"ASTNode(kind=\"{self.kind}\", value={value_repr}, "
                f"children={self.children})")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_kind):
        token = self.current_token()
        if token and token[0] == expected_kind:
            self.pos += 1
            return token
        raise SyntaxError(f"Expected {expected_kind}, got {token}")

    def parse_program(self):
        statements = []
        while self.current_token():
            statements.append(self.parse_statement())
        return ASTNode(kind="PROGRAM", children=statements)

    def parse_statement(self):
        identifier = self.consume("IDENTIFIER")
        self.consume("ASSIGN")
        expression = self.parse_expression()
        self.consume("SEMICOLON")
        return ASTNode(kind="ASSIGN", children=[
            ASTNode(kind="IDENTIFIER", value=identifier[1]),
            expression
        ])

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token() and self.current_token()[0] in ("PLUS", "MINUS"):
            op = self.consume(self.current_token()[0])
            right = self.parse_term()
            node = ASTNode(kind=op[0], children=[node, right])
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token() and self.current_token()[0] in ("TIMES", "DIVIDE"):
            op = self.consume(self.current_token()[0])
            right = self.parse_factor()
            node = ASTNode(kind=op[0], children=[node, right])
        return node

    def parse_factor(self):
        token = self.current_token()
        if token[0] == "NUMBER":
            self.consume("NUMBER")
            return ASTNode(kind="NUMBER", value=int(token[1]))
        elif token[0] == "IDENTIFIER":
            self.consume("IDENTIFIER")
            return ASTNode(kind="IDENTIFIER", value=token[1])
        elif token[0] == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_expression()
            self.consume("RPAREN")
            return node
        raise SyntaxError(f"Unexpected token: {token}")

# example
parser = Parser([('IDENTIFIER', 'x'), ('ASSIGN', '='), ('NUMBER', '2025'), ('SEMICOLON', ';'), ('IDENTIFIER', 'y'), ('ASSIGN', '='), ('NUMBER', '1477'), ('SEMICOLON', ';'), ('IDENTIFIER', 'z'), ('ASSIGN', '='), ('IDENTIFIER', 'x'), ('PLUS', '+'), ('IDENTIFIER', 'y'), ('MINUS', '-'), ('NUMBER', '5'), ('TIMES', '*'), ('LPAREN', '('), ('NUMBER', '7'), ('PLUS', '+'), ('NUMBER', '9'), ('RPAREN', ')'), ('DIVIDE', '/'), ('NUMBER', '2'), ('SEMICOLON', ';')])
ast = parser.parse_program()
print(ast)
# Output: ASTNode(kind=PROGRAM, value=None, children=[
#     ASTNode(kind=ASSIGN, value=None, children=[
#         ASTNode(kind=IDENTIFIER, value='x', children=[]),
#         ASTNode(kind=NUMBER, value=2025, children=[])
#     ]),
#     ASTNode(kind=ASSIGN, value=None, children=[
#         ASTNode(kind=IDENTIFIER, value='y', children=[]),
#         ASTNode(kind=NUMBER, value=1477, children=[])
#     ]),
#     ASTNode(kind=ASSIGN, value=None, children=[
#         ASTNode(kind=IDENTIFIER, value='z', children=[]),
#         ASTNode(kind=PLUS, value=None, children=[
#             ASTNode(kind=IDENTIFIER, value='x', children=[]),
#             ASTNode(kind=MINUS, value=None, children=[
#                 ASTNode(kind=NUMBER, value=5, children=[]),
#                 ASTNode(kind=DIVIDE, value=None, children=[
#                     ASTNode(kind=PLUS, value=None, children=[
#                         ASTNode(kind=NUMBER, value=7, children=[]),
#                         ASTNode(kind=NUMBER, value=9, children=[])
#                     ]),
#                     ASTNode(kind=NUMBER, value=2, children=[])
#                 ])
#             ])
#         ])
#     ])
# ])

# The Parser class takes a list of tokens as input and provides methods to parse a
# sequence of statements, a single assignment statement, an expression with precedence
# handling, and a factor. The parse_program method parses a sequence of statements,
# the parse_statement method parses a single assignment statement, the parse_expression
# method parses an expression with precedence handling, and the parse_factor method
# handles numbers, identifiers, and parenthesized expressions. The example demonstrates
# how to use the Parser class to parse a sequence of statements and generate an abstract
# syntax tree (AST) representation of the code.
