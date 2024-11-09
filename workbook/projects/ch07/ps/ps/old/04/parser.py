from lexer import Token
from environment import Environment


class ASTNode:
    def __init__(self, type: str, value: any, children: list['ASTNode'] = None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {self.children})"

class Parser:
    def __init__(self, tokens: list[Token], env: Environment):
        self.tokens = tokens
        self.position = 0
        self.env = env

    def parse(self) -> ASTNode:
        if not self.tokens:
            return None
        return self.parse_expression(self.tokens)

    def parse_expression(self, tokens: list[Token]) -> ASTNode:
        token = tokens[self.position]
        print(f"[DEBUG] Parsing token: {token.type} {token.value}")

        if token.type == 'NUMBER':
            # Literal number
            self.position += 1
            return ASTNode('Literal', token.value)

        elif token.type == 'IDENTIFIER':
            # Handle variable definitions or lookups
            if self.position + 1 < len(tokens) and tokens[self.position + 1].type == 'NUMBER' and \
                (self.position + 2 < len(tokens) and tokens[self.position + 2].type == 'IDENTIFIER' and tokens[self.position + 2].value == 'def'):
                # Variable definition (x 10 def)
                var_name = token.value
                self.position += 1  # Skip to the number token
                value_token = tokens[self.position]
                if value_token.type == 'NUMBER':
                    print(f"[DEBUG] Defining variable: {var_name} = {value_token.value}")
                    self.env.define(var_name, value_token.value)
                    self.position += 1  # Skip the number token
                    self.position += 1  # Skip the 'def' token
                    return ASTNode('Define', var_name, [ASTNode('Literal', value_token.value)])

            # Handle variable lookup (x, y)
            var_name = token.value
            self.position += 1
            value = self.env.lookup(var_name)
            return ASTNode('Literal', value)

        elif token.type == 'OPERATOR':
            operator = token.value
            self.position += 1
            return ASTNode('Operator', operator)

        else:
            raise ValueError(f"[DEBUG] Unexpected token: {token}")
