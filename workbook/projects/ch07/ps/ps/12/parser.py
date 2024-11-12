import re
from enum import Enum, auto

class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    LITERAL = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMENT = auto()

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    NUM_REGEX = re.compile(r'-?\d+(\.\d+)?')
    ID_REGEX = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    LITERAL_REGEX = re.compile(r'/[a-zA-Z_][a-zA-Z0-9_]*')
    COMMENT_REGEX = re.compile(r'%.*')
    
    def __init__(self, code):
        self.code = code
        self.pos = 0

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            char = self.code[self.pos]

            if char.isspace(): # whitespace
                self.pos += 1
                continue

            if match := self.NUM_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.NUMBER, float(match.group())))
                self.pos = match.end()
                continue

            if match := self.ID_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.IDENTIFIER, match.group()))
                self.pos = match.end()
                continue

            # literals (beginning with /literal)
            if match := self.LITERAL_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.LITERAL, match.group()))
                self.pos = match.end()
                continue

            # comments
            if match := self.COMMENT_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.COMMENT, match.group().strip()))
                self.pos = match.end()
                continue

            # arrays
            if char == '[':
                tokens.append(Token(TokenType.LBRACKET, '['))
                self.pos += 1
                continue
            if char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']'))
                self.pos += 1
                continue
            # procedures (blocks)
            if char == '{':
                tokens.append(Token(TokenType.LBRACE, '{'))
                self.pos += 1
                continue
            if char == '}':
                tokens.append(Token(TokenType.RBRACE, '}'))
                self.pos += 1
                continue

            # unknown characters
            raise SyntaxError(f"Unexpected character: {char}")
        
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        ast = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == TokenType.LBRACKET:
                ast.append(self.parse_array())
            elif token.type == TokenType.LBRACE:
                ast.append(self.parse_block())
            else:
                ast.append(self.parse_expression(token))
            self.advance() # self.pos += 1
        return ast

    def parse_expression(self, token):
        if token.type in {TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LITERAL, TokenType.COMMENT}:
            return token.value
        raise SyntaxError(f"Unexpected token: {token}")

    def parse_array(self):
        self.advance() # self.pos += 1  # Skip '['
        array = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == TokenType.RBRACKET:
                break
            elif token.type == TokenType.LBRACKET:
                array.append(self.parse_array())
            elif token.type == TokenType.LBRACE:
                array.append(self.parse_block())
            else:
                array.append(self.parse_expression(token))
            self.advance() # self.pos += 1
        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.RBRACKET:
            raise SyntaxError("Unclosed array")
        return array

    def parse_block(self):
        self.pos += 1  # Skip '{'
        block = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.type == TokenType.RBRACE:
                break
            elif token.type == TokenType.LBRACKET:
                block.append(self.parse_array())
            elif token.type == TokenType.LBRACE:
                block.append(self.parse_block())
            else:
                block.append(self.parse_expression(token))
            self.advance() # self.pos += 1
        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.RBRACE:
            raise SyntaxError("Unclosed block")
        return block

    def get_next_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        raise SyntaxError("Unexpected end of input")
    
    def has_tokens(self):
        return self.pos < len(self.tokens)
    
    def advance(self):
        self.pos += 1

# Example Usage
if __name__ == "__main__":
    code = """
    100 200 moveto
    [1 2 3 add] [100 200] gsave
    % This is a comment with a command: moveto
    { /x 3 add } stroke
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)  # Should print the parsed AST
