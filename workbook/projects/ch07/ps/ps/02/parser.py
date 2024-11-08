
from lexer import Token

class ASTNode:
    def __init__(self, type: str, value: any, children: list['ASTNode'] = None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {self.children})"

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> ASTNode:
        if not self.tokens:
            return None
        return self.parse_expression(self.tokens)

    def parse_expression(self, tokens: list[Token]) -> ASTNode:
        token = tokens[self.position]
        
        if token.type == 'NUMBER':
            self.position += 1
            return ASTNode('Literal', token.value)
        elif token.type == 'IDENTIFIER':
            self.position += 1
            return ASTNode('Operator', token.value)
        elif token.type == 'LPAREN':
            self.position += 1
            children = []
            while self.tokens[self.position].type != 'RPAREN':
                children.append(self.parse_expression(self.tokens))
            self.position += 1  # Skip the RPAREN
            return ASTNode('Group', None, children)
        else:
            raise ValueError(f"Unexpected token: {token}")
