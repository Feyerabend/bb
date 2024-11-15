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
    HEADER = auto()
    STRING = auto()
    EQUALS = auto()
    DEQUALS = auto()
    DIRECTIVE = auto()
    DEF = auto()

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    NUM_REGEX = re.compile(r'-?\d+(\.\d+)?')
    ID_REGEX = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    LITERAL_REGEX = re.compile(r'/[a-zA-Z_*][a-zA-Z0-9_]*')  # Allow literals with *
    STRING_REGEX = re.compile(r'\(([^)]*)\)')  # Matches content within parentheses
    COMMENT_REGEX = re.compile(r'%.*')
    HEADER_REGEX = re.compile(r'%!PS-[^\s]+')
    DIRECTIVE_REGEX = re.compile(r'%%[^\n]+')
    DEF_REGEX = re.compile(r'\bdef\b')
    # =
    # ==

    def __init__(self, code):
        self.code = code
        self.pos = 0

    def advance(self):
        self.pos += 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            char = self.code[self.pos]

            # Print current position and character, translating newlines to "\n" for readability
            display_char = repr(char) if char == '\n' else f"'{char}'"
            print(f"Current position {self.pos}, char: {display_char}")

            if char.isspace():  # Skip whitespace
                self.advance() # self.pos += 1
                continue

            # String literals (inside parentheses)
            if match := self.STRING_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.STRING, match.group(1)))  # Capture text within ()
                self.pos = match.end()
                print(f"Matched STRING: {match.group(1)}")
                continue

            # Literal tokens (starting with '/')
            if match := self.LITERAL_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.LITERAL, match.group()))
                self.pos = match.end()
                print(f"Matched LITERAL: {match.group()}")
                continue

            # Number tokens
            if match := self.NUM_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.NUMBER, float(match.group())))
                self.pos = match.end()
                print(f"Matched NUMBER: {match.group()}")
                continue

            # Identifiers
            if match := self.ID_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.IDENTIFIER, match.group()))
                self.pos = match.end()
                print(f"Matched IDENTIFIER: {match.group()}")
                continue

            # Header
            if match := self.HEADER_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.HEADER, match.group()))
                self.pos = match.end()
                print(f"Matched HEADER: {match.group()}")
                continue

            # Directives (%% lines)
            if match := self.DIRECTIVE_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.DIRECTIVE, match.group().strip()))
                self.pos = match.end()
                print(f"Matched DIRECTIVE: {match.group().strip()}")
                continue

            # Comments (%)
            if match := self.COMMENT_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.COMMENT, match.group().strip()))
                self.pos = match.end()
                print(f"Matched COMMENT: {match.group().strip()}")
                continue

            # Definitions (def keyword)
            if match := self.DEF_REGEX.match(self.code, self.pos):
                tokens.append(Token(TokenType.DEF, match.group()))
                self.pos = match.end()
                print(f"Matched DEF: {match.group()}")
                continue

            if char == '=':
                self.advance()  # Move to the next character after the first '='
                # Peek ahead to check if the next character is also '='
                if self.pos < len(self.code) and self.code[self.pos] == '=':
                    tokens.append(Token(TokenType.DEQUALS, '=='))
                    self.advance()  # Consume the second '='
                    print("Matched DEQUALS: ==")
                else:
                    tokens.append(Token(TokenType.EQUALS, '='))
                    print("Matched EQUALS: =")
                continue

            # Array Brackets
            if char == '[':
                tokens.append(Token(TokenType.LBRACKET, '['))
                self.advance()
                print("Matched LBRACKET: [")
                continue
            if char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']'))
                self.advance()
                print("Matched RBRACKET: ]")
                continue

            # Procedure Braces
            if char == '{':
                tokens.append(Token(TokenType.LBRACE, '{'))
                self.advance()
                print("Matched LBRACE: {")
                continue
            if char == '}':
                tokens.append(Token(TokenType.RBRACE, '}'))
                self.advance()
                print("Matched RBRACE: }")
                continue

            # Unknown character handling
            raise SyntaxError(f"Unexpected character: {char} at position {self.pos}")

        return tokens


class ASTNode:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"ASTNode({self.type}, {repr(self.value)})"
    
    def __str__(self, level=0):
        indent = "  " * level
        if isinstance(self.value, list):
            child_str = "\n".join(child.__str__(level + 1) if isinstance(child, ASTNode) else f"{'  ' * (level + 1)}{child}" for child in self.value)
            return f"{indent}{self.type}:\n{child_str}"
        else:
            return f"{indent}{self.type}: {self.value}"

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
            elif token.type == TokenType.DEF:
                ast.append(self.parse_def())
            else:
                ast.append(self.parse_expression(token))
            self.advance()  # Move to the next token
        return ast

    def parse_expression(self, token):
        if token.type in {
           TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.LITERAL,
            TokenType.COMMENT, TokenType.HEADER, TokenType.DIRECTIVE}:
            return ASTNode(token.type, token.value)

        elif token.type == TokenType.EQUALS:
            return ASTNode(TokenType.EQUALS, '=')  # Handle '=' as a procedure call
    
        elif token.type == TokenType.DEQUALS:
            return ASTNode(TokenType.DEQUALS, '==')  # Handle '==' as a procedure call

        raise SyntaxError(f"Unexpected token: {token}")


    def parse_array(self):
        self.advance()  # skip '['
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
            self.advance()
        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.RBRACKET:
            raise SyntaxError("Unclosed array")
        return ASTNode(TokenType.LBRACKET, array)

    def parse_block(self):
        self.advance()  # skip '{'
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
            self.advance()
        if self.pos >= len(self.tokens) or self.tokens[self.pos].type != TokenType.RBRACE:
            raise SyntaxError("Unclosed block")
        return ASTNode(TokenType.LBRACE, block)

    def parse_def(self):
        # Assume 'name' and 'value' are parsed correctly

        name = self.parse_identifier()  # or however the identifier is parsed
        value = self.parse_expression()  # or however the value is parsed
        return ASTNode(TokenType.DEF, value={"name": name, "value": value})


#    def parse_def(self):
#        """Parse `/name { ... } def` definitions."""
        # literal name (e.g., /moveto)
#        name_token = self.tokens[self.pos - 1]  # literal name is right before 'def'
#        if name_token.type != TokenType.LITERAL:
#            raise SyntaxError(f"Expected literal name before 'def', found {name_token}")
#        # block definition
#        self.advance()  # move to block
#        if self.tokens[self.pos].type != TokenType.LBRACE:
#            raise SyntaxError("Expected '{' after literal name for 'def'")
#        block = self.parse_block()
#        return ASTNode(TokenType.DEF, {"name": name_token.value, "block": block})

    def get_next_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        raise SyntaxError("Unexpected end of input")
    
    def has_tokens(self):
        return self.pos < len(self.tokens)
    
    def advance(self):
        self.pos += 1

# Example PostScript-like code to parse and pretty-print
sample_code = """
% Sample comment
/width 5
/height 10
{ /width /height mul } % block example
[ 1 2 3 ] % array example
"""



# Run Lexer and Parser
lexer = Lexer(sample_code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Pretty print each ASTNode in the parsed AST
print("AST:")
for node in ast:
    print(node.__str__())
