# test_parser.py
import unittest
from parser import Parser, ASTNode
from lexer import Lexer

class TestParser(unittest.TestCase):
    
    def parse_code(self, code: str):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_parse_number(self):
        code = "123"
        ast = self.parse_code(code)
        self.assertEqual(ast, ASTNode("Number", value=123))
    
    def test_parse_name(self):
        code = "x"
        ast = self.parse_code(code)
        self.assertEqual(ast, ASTNode("Name", value="x"))
    
    def test_parse_operator(self):
        code = "add"
        ast = self.parse_code(code)
        self.assertEqual(ast, ASTNode("Operator", value="add"))
    
    def test_parse_command(self):
        code = "moveto"
        ast = self.parse_code(code)
        self.assertEqual(ast, ASTNode("Command", value="moveto"))
    
    def test_parse_string(self):
        code = "(Hello World)"
        ast = self.parse_code(code)
        self.assertEqual(ast, ASTNode("String", value="Hello World"))
    
    def test_parse_expression_in_block(self):
        code = "{ add 123 moveto }"
        ast = self.parse_code(code)
        block_node = ASTNode("Block", children=[
            ASTNode("Operator", value="add"),
            ASTNode("Number", value=123),
            ASTNode("Command", value="moveto")
        ])
        self.assertEqual(ast, block_node)
    
    def test_parse_unexpected_token(self):
        code = "add +"
        with self.assertRaises(ValueError):
            self.parse_code(code)

if __name__ == "__main__":
    unittest.main()
