# lexer.py

import re

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []

    def tokenize(self):
        token_specification = [
            ('NUMBER', r'\d+(\.\d*)?'),     # integer or decimal number
            ('NAME', r'/[a-zA-Z_]\w*'),     # variable names
            ('OPERATOR', r'[a-zA-Z]+'),     # operators
            ('WHITESPACE', r'[ \t]+'),      # spaces and tabs
            ('NEWLINE', r'\n'),             # line endings
            ('SKIP', r'[ \t]+'),            # skip spaces and tabs
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        
        for match in re.finditer(tok_regex, self.source):
            kind = match.lastgroup
            value = match.group()
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'WHITESPACE' or kind == 'SKIP':
                continue
            self.tokens.append((kind, value))
        return self.tokens
