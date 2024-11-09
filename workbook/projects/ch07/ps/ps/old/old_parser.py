
# Token class to represent different types of tokens

class Token:
    def __init__(self, type: str, value: any):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.position = 0

    def get_next_char(self, offset=0):
        if self.position + offset < len(self.code):
            return self.code[self.position + offset]
        return None

    def advance(self):
        self.position += 1

    def skip_whitespace(self):
        while self.get_next_char() is not None and self.get_next_char().isspace():
            self.advance()

    def tokenize(self):
        tokens = []
        while self.position < len(self.code):
            self.skip_whitespace()
            char = self.get_next_char()

            if char is None:
                break

            if char.isdigit() or (char == '-' and self.get_next_char(1) and self.get_next_char(1).isdigit()):
                tokens.append(self.tokenize_number())

            elif char.isalpha() or char == '/':
                tokens.append(self.tokenize_identifier())

            elif char == '+':
                tokens.append(Token('PLUS', '+'))
                self.advance()

            elif char == '-':
                tokens.append(Token('MINUS', '-'))
                self.advance()

            elif char == '*':
                tokens.append(Token('MULT', '*'))
                self.advance()

            elif char == '/':
                tokens.append(Token('DIV', '/'))
                self.advance()

            elif char == '(':
                tokens.append(Token('LPAREN', '('))
                self.advance()

            elif char == ')':
                tokens.append(Token('RPAREN', ')'))
                self.advance()

            else:
                raise ValueError(f"Unexpected character: {char}")

        return tokens

    def tokenize_number(self):
        num_str = ''
        char = self.get_next_char()

        if char == '-':
            num_str += char
            self.advance()
            char = self.get_next_char()

        while char is not None and char.isdigit():
            num_str += char
            self.advance()
            char = self.get_next_char()

        if char == '.':
            num_str += char
            self.advance()
            char = self.get_next_char()
            while char is not None and char.isdigit():
                num_str += char
                self.advance()
                char = self.get_next_char()

        return Token('NUMBER', float(num_str))

    def tokenize_identifier(self):
        identifier = ''
        char = self.get_next_char()

        while char is not None and (char.isalpha() or char.isdigit() or char == '_'):
            identifier += char
            self.advance()
            char = self.get_next_char()

        return Token('IDENTIFIER', identifier)


# ASTNode class to represent nodes in the abstract syntax tree
class ASTNode:
    def __init__(self, type: str, value: any, children: list = None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"ASTNode(type={self.type}, value={self.value}, children={self.children})"

# Parser class to parse tokens and generate the AST
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def get_current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def advance(self):
        self.position += 1

    def parse(self):
        return self.parse_expression()

        # Expression: term ((PLUS | MINUS) term)*
    def parse_expression(self):
        node = self.parse_term()
        while self.get_current_token() and self.get_current_token().type in ('PLUS', 'MINUS'):
            op = self.get_current_token()
            self.advance()
            right_node = self.parse_term()
            node = ASTNode('BINARY_OP', op.value, [node, right_node])
        return node

        # Term: factor ((MULT | DIV) factor)*
    def parse_term(self):
        node = self.parse_factor()
        while self.get_current_token() and self.get_current_token().type in ('MULT', 'DIV'):
            op = self.get_current_token()
            self.advance()
            right_node = self.parse_factor()
            node = ASTNode('BINARY_OP', op.value, [node, right_node])
        return node

        # Factor: NUMBER | IDENTIFIER | LPAREN expression RPAREN
    def parse_factor(self):
        token = self.get_current_token()

        if token.type == 'NUMBER':
            self.advance()
            return ASTNode('NUMBER', token.value)

        elif token.type == 'IDENTIFIER':
            self.advance()
            return ASTNode('IDENTIFIER', token.value)

        elif token.type == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            if self.get_current_token().type == 'RPAREN':
                self.advance()
                return node
            else:
                raise ValueError("Expected closing parenthesis")

        else:
            raise ValueError(f"Unexpected token: {token.type}")

# Example Usage
code = "3 + 5 * (10 - 2)"
lexer = Lexer(code)
tokens = lexer.tokenize()

print("Tokens:", tokens)

parser = Parser(tokens)
ast = parser.parse()

print("AST:", ast)
