import re

class Token:
    def __init__(self, type: str, value: any):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.patterns = [
            ("NUMBER", r"-?\d+(\.\d+)?"),  # Match numbers, including negative and floating point
            ("NAME", r"/[a-zA-Z_][a-zA-Z0-9_]*"),  # Match names starting with '/'
            ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  # Match identifiers (e.g., x, y)
            ("STRING", r"\(.*?\)"),  # Match string literals (e.g., (abc))
            ("OPERATOR", r"\b(add|sub|mul|div|idiv|neg|mod|dup|exch|clear|pop|def)\b"),  # Match operators
            ("COMMAND", r"\b(newpath|moveto|lineto|rlineto|curveto|closepath|stroke|fill|setcolor|setgray|setlinewidth|dict|begin|end|load|store|if|ifelse|repeat|showpage)\b"),  # Match commands
            ("LBRACE", r"{"),  # Left brace
            ("RBRACE", r"}"),  # Right brace
            ("WHITESPACE", r"\s+"),  # Match whitespaces, should be skipped
            ("COMMENT", r"%.*"),  # Match comments starting with '%'
        ]

    def tokenize(self) -> list[Token]:
        tokens = []
        index = 0
        while index < len(self.code):
            match = None
            for token_type, pattern in self.patterns:
                regex = re.compile(pattern)
                match = regex.match(self.code, index)
                if match:
                    if token_type != "WHITESPACE" and token_type != "COMMENT":  # Skip whitespace (do not add to token list)
                        value = match.group(0)
                        if token_type == "NUMBER":
                            value = float(value) if '.' in value else int(value)
                        elif token_type == "STRING":
                            value = value[1:-1]  # Strip parentheses from strings
                        tokens.append(Token(token_type, value))
                    index = match.end(0)
                    break
            if not match:
                raise ValueError(f"Unexpected character: {self.code[index]}")
        return tokens