# test_lexer.py
import unittest
from lexer import Lexer, Token

class TestLexer(unittest.TestCase):
    
    def test_tokenize_numbers(self):
        code = "123 -456 78.9"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NUMBER", 123),
            Token("NUMBER", -456),
            Token("NUMBER", 78.9)
        ])

    def test_tokenize_names_and_identifiers(self):
        code = "/x /y z"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NAME", "/x"),
            Token("NAME", "/y"),
            Token("IDENTIFIER", "z")
        ])
    
    def test_tokenize_string(self):
        code = "(Hello World)"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("STRING", "Hello World")
        ])
    
    def test_tokenize_operator(self):
        code = "add sub mul"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("OPERATOR", "add"),
            Token("OPERATOR", "sub"),
            Token("OPERATOR", "mul")
        ])

    def test_tokenize_command(self):
        code = "moveto lineto curveto"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("COMMAND", "moveto"),
            Token("COMMAND", "lineto"),
            Token("COMMAND", "curveto")
        ])

    def test_skip_whitespace(self):
        code = "/x  123   /y 456"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NAME", "/x"),
            Token("NUMBER", 123),
            Token("NAME", "/y"),
            Token("NUMBER", 456)
        ])
    
    def test_unexpected_character(self):
        code = "/x & y"
        lexer = Lexer(code)
        with self.assertRaises(ValueError):
            lexer.tokenize()

if __name__ == "__main__":
    unittest.main()
