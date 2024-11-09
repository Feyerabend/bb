import re

class Token:
    def __init__(self, type: str, value: any):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.position = 0
        self.tokens = []

    def tokenize(self) -> list[Token]:
        token_specification = [
            ('NUMBER',    r'\d+(\.\d*)?'),  # Integer or decimal number
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identifiers (e.g., 'add', 'mul')
            ('LPAREN',    r'\('),            # Left parenthesis
            ('RPAREN',    r'\)'),            # Right parenthesis
            ('OPERATOR',  r'[+\-*/]'),       # Operators (+, -, *, /)
            ('WHITESPACE', r'\s+'),          # Skip whitespace
            ('COMMENT',   r'%.*'),           # Skip comments
        ]
        master_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        for match in re.finditer(master_regex, self.code):
            kind = match.lastgroup
            value = match.group(kind)
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'WHITESPACE' or kind == 'COMMENT':
                continue
            self.tokens.append(Token(kind, value))
        return self.tokens
