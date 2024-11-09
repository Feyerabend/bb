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
            # Numbers first, including negative numbers and floating-point
            ("NUMBER", r"-?\d+(\.\d+)?"),  # Matches numbers, negative or positive
            ("OPERATOR", r"\b(add|sub|mul|div|idiv|neg|mod|dup|exch|clear|pop|def|lt|eq|gt)\b"),  # Operators (specific keywords)
            ("COMMAND", r"\b(newpath|moveto|lineto|rlineto|curveto|closepath|stroke|fill|setcolor|setgray|setlinewidth|dict|begin|end|load|store|if|ifelse|repeat|showpage|while)\b"),  # Commands
            ("NAME", r"/[a-zA-Z_][a-zA-Z0-9_]*"),  # Names (e.g., /x)
            ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),  # Identifiers (e.g., x, y)
            ("STRING", r"\(.*?\)"),  # Strings (e.g., (abc))
            ("LBRACE", r"{"),  # Left brace
            ("RBRACE", r"}"),  # Right brace
            ("WHITESPACE", r"\s+"),  # Ignore whitespace
            ("COMMENT", r"%.*"),  # Comments starting with '%'
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
                    # Only add to the token list if it's not whitespace or a comment
                    if token_type != "WHITESPACE" and token_type != "COMMENT":
                        value = match.group(0)
                        if token_type == "NUMBER":
                            value = float(value) if '.' in value else int(value)
                        elif token_type == "STRING":
                            value = value[1:-1]  # Strip parentheses from strings
                        # Debugging: Show which token is matched
                        print(f"Matched: {token_type} with value: {value}")
                        tokens.append(Token(token_type, value))
                    
                    # Move the index forward by the length of the match
                    index = match.end(0)
                    break

            # If no pattern matched, raise an error for an unexpected character
            if not match:
                raise ValueError(f"Unexpected character: {self.code[index]}")
        
        return tokens