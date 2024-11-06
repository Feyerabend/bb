# lexer.py
class Token:
    def __init__(self, type: str, value: any):
        self.type = type
        self.value = value

class Lexer:
    def __init__(self, code: str):
        self.code = code.split()  # Simplified to split by whitespace

    def tokenize(self) -> list[Token]:
        tokens = []
        for word in self.code:
            if word.isdigit():
                tokens.append(Token("number", int(word)))
            elif word in ["add", "sub", "setpixel"]:
                tokens.append(Token("operator", word))
            else:
                tokens.append(Token("unknown", word))
        return tokens