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
        self.env = env  # environment to manage variable values

    def parse(self) -> ASTNode:
        if not self.tokens:
            return None
        return self.parse_expression(self.tokens)

    def parse_expression(self, tokens: list[Token]) -> ASTNode:
        token = tokens[self.position]

        if token.type == 'NUMBER':
            # Number token, just return a literal node
            self.position += 1
            return ASTNode('Literal', token.value)

        elif token.type == 'IDENTIFIER':
            # Identifier token, check if it's followed by 'def' for definition
            if self.position + 1 < len(tokens) and tokens[self.position + 1].type == 'NUMBER' and \
                (self.position + 2 < len(tokens) and tokens[self.position + 2].type == 'IDENTIFIER' and tokens[self.position + 2].value == 'def'):
                # Handle a definition: x 10 def
                var_name = token.value
                self.position += 1  # Move to the number
                value_token = tokens[self.position]
                if value_token.type == 'NUMBER':
                    self.env.define(var_name, value_token.value)
                    self.position += 1  # Skip the number token
                    self.position += 1  # Skip the 'def' token
                    return ASTNode('Define', var_name, [ASTNode('Literal', value_token.value)])
                else:
                    raise SyntaxError("Expected a number after def.")
            else:
                # Otherwise, it's a lookup for a defined variable
                var_name = token.value
                self.position += 1
                value = self.env.lookup(var_name)
                return ASTNode('Literal', value)

        elif token.type == 'OPERATOR':
            # Operator token (e.g., add, sub, etc.)
            self.position += 1
            return ASTNode('Operator', token.value)
        
        elif token.type == 'LPAREN':
            # Grouping (parentheses)
            self.position += 1
            children = []
            while self.tokens[self.position].type != 'RPAREN':
                children.append(self.parse_expression(self.tokens))
            self.position += 1  # Skip the RPAREN
            return ASTNode('Group', None, children)
        
        else:
            raise ValueError(f"Unexpected token: {token}")
