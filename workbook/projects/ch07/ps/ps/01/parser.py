# parser.py

from lexer import Token

class ASTNode:
    def __init__(self, type: str, value: any = None, children: list['ASTNode'] = None):
        self.type = type
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return f"ASTNode(type={self.type}, value={self.value}, children={self.children})"

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> ASTNode:
        return self.parse_statements()

    def parse_statements(self) -> ASTNode:
        statements = []
        while self.position < len(self.tokens):
            if self.current_token().type == "RBRACE":
                break
            statements.append(self.parse_expression())
        return ASTNode("Program", children=statements)

    def parse_expression(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == "NUMBER":
            self.position += 1
            return ASTNode("Number", value=token.value)
        
        elif token.type == "NAME":
            self.position += 1
            return ASTNode("Name", value=token.value)
        
        elif token.type == "STRING":
            self.position += 1
            return ASTNode("String", value=token.value)
        
        elif token.type == "COMMAND":
            self.position += 1
            return ASTNode("Command", value=token.value)
        
        elif token.type == "OPERATOR":
            self.position += 1
            return ASTNode("Operator", value=token.value)
        
        elif token.type == "LBRACE":
            self.position += 1
            block = self.parse_statements()
            self.expect_token("RBRACE")
            return ASTNode("Block", children=block.children)
        
        elif token.type == "RBRACE":
            raise ValueError("Unmatched closing brace '}'")
        
        else:
            raise ValueError(f"Unexpected token: {token}")

    def expect_token(self, expected_type):
        if self.current_token().type != expected_type:
            raise ValueError(f"Expected token type {expected_type}, got {self.current_token().type}")
        self.position += 1

    def current_token(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return Token("EOF", None)