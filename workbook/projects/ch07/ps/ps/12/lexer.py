# lexer.py
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
        self.index = 0

    def tokenize(self) -> list[Token]:
        tokens = []
        while self.index < len(self.code):
            char = self.code[self.index]

            if char.isspace():
                self.index += 1
                continue

            if char == '%':
                tokens.append(self._skip_comment())
                continue

            if char.isdigit() or (char == '-' and self._peek().isdigit()):
                tokens.append(self._number())

            elif char == '/':
                tokens.append(self._name())

            elif char == '(':
                tokens.append(self._string())

            elif char.isalpha():
                tokens.append(self._identifier())

            elif char == '{':
                tokens.append(Token("LBRACE", char))
                self.index += 1

            elif char == '}':
                tokens.append(Token("RBRACE", char))
                self.index += 1

            else:
                raise ValueError(f"Unexpected character: {char}")
        
        return tokens

    def _skip_comment(self):
        self.index += 1  # skip '%'
        start = self.index
        while self.index < len(self.code) and self.code[self.index] != '\n':
            self.index += 1
        value = self.code[start:self.index]
        self.index += 1  # skip '\n'
        return Token("COMMENT", value)

    def _number(self):
        num_re = re.compile(r'-?\d+(\.\d+)?')
        match = num_re.match(self.code, self.index)
        if not match:
            raise ValueError("Invalid number format")
        num_str = match.group(0)
        self.index += len(num_str)
        return Token("NUMBER", float(num_str) if '.' in num_str else int(num_str))

    def _name(self):
        self.index += 1
        name = '/'
        while self.index < len(self.code) and self.code[self.index].isalpha():
            name += self.code[self.index]
            self.index += 1
        return Token("NAME", name)

    def _string(self):
        self.index += 1  # skip '('
        start = self.index
        while self.index < len(self.code) and self.code[self.index] != ')':
            self.index += 1
        if self.index >= len(self.code):
            raise ValueError("Unterminated string")
        value = self.code[start:self.index]
        self.index += 1  # skip ')'
        return Token("STRING", value)

    def _identifier(self):
        start = self.index
        while self.index < len(self.code) and self.code[self.index].isalpha():
            self.index += 1
        value = self.code[start:self.index]
        return Token("OPERATOR", value)
