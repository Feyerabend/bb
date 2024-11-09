import unittest
from old_parser import Lexer, Token

class TestLexer(unittest.TestCase):

    def test_tokenize_numbers(self):
        # Test case for numbers
        code = "123 -456 78.9"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NUMBER", 123),
            Token("NUMBER", -456),
            Token("NUMBER", 78.9)
        ])

    def test_tokenize_identifiers(self):
        # Test case for identifiers (variable names)
        code = "/x /y /variable_1"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("IDENTIFIER", "/x"),
            Token("IDENTIFIER", "/y"),
            Token("IDENTIFIER", "/variable_1")
        ])

    def test_tokenize_operators(self):
        # Test case for operators
        code = "+ - * /"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("PLUS", '+'),
            Token("MINUS", '-'),
            Token("MULT", '*'),
            Token("DIV", '/')
        ])

    def test_tokenize_parentheses(self):
        # Test case for parentheses
        code = "( )"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("LPAREN", '('),
            Token("RPAREN", ')')
        ])

    def test_tokenize_mixed(self):
        # Test case for mixed input (numbers, operators, and parentheses)
        code = "3 + 5 * (10 - 2)"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NUMBER", 3),
            Token("PLUS", '+'),
            Token("NUMBER", 5),
            Token("MULT", '*'),
            Token("LPAREN", '('),
            Token("NUMBER", 10),
            Token("MINUS", '-'),
            Token("NUMBER", 2),
            Token("RPAREN", ')')
        ])

    def test_tokenize_whitespace(self):
        # Test case to check if whitespaces are properly skipped
        code = "  123   -456   78.9   "
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [
            Token("NUMBER", 123),
            Token("NUMBER", -456),
            Token("NUMBER", 78.9)
        ])

    def test_tokenize_invalid(self):
        # Test case for invalid input (should raise an error)
        code = "123 + abc"
        lexer = Lexer(code)
        with self.assertRaises(ValueError):
            lexer.tokenize()

    def test_tokenize_empty(self):
        # Test case for empty input (should produce no tokens)
        code = ""
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(tokens, [])

if __name__ == "__main__":
    unittest.main()
