# parser.py

from lexer import Lexer

class Parser:
    def __init__(self, source):
        self.lexer = Lexer(source)

    def parse(self):
        return self.lexer.tokenize()