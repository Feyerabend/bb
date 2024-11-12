import unittest
from parser import Lexer, Parser

class TestPostScriptParser(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer
        self.parser = Parser

    def test_basic_commands(self):
        code = "100 200 moveto 300 400 lineto stroke"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [100, 200, 'moveto', 300, 400, 'lineto', 'stroke']
        self.assertEqual(ast, expected_ast)

    def test_literal_parsing(self):
        code = "/myLiteral 42"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = ['/myLiteral', 42]
        self.assertEqual(ast, expected_ast)

    def test_array_parsing(self):
        code = "[1 2 3 add] [100 200] gsave"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[1, 2, 3, 'add'], [100, 200], 'gsave']
        self.assertEqual(ast, expected_ast)
    
    def test_nested_array(self):
        code = "[1 2 [3 4] dup]"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[1, 2, [3, 4], 'dup']]
        self.assertEqual(ast, expected_ast)

    def test_block_parsing(self):
        code = "{ 10 20 moveto 30 40 lineto }"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[10, 20, 'moveto', 30, 40, 'lineto']]
        self.assertEqual(ast, expected_ast)

    def test_nested_block(self):
        code = "{ 1 { 2 3 add } mul }"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[1, [2, 3, 'add'], 'mul']]
        self.assertEqual(ast, expected_ast)
    
    def test_comments_parsing(self):
        code = """
        100 200 moveto
        % This is a comment with a command: moveto
        300 400 lineto stroke
        """
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [100, 200, 'moveto', '% This is a comment with a command: moveto', 300, 400, 'lineto', 'stroke']
        self.assertEqual(ast, expected_ast)

    def test_comment_with_directive(self):
        code = "300 400 moveto % Change color: setcolor 1.0 0.5 0.5"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [300, 400, 'moveto', '% Change color: setcolor 1.0 0.5 0.5']
        self.assertEqual(ast, expected_ast)

    def test_combined_structure(self):
        code = """
        100 200 moveto
        [300 400] dup
        { /x 3 add } gsave
        stroke
        """
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [
            100, 200, 'moveto', 
            [300, 400], 'dup', 
            ['/x', 3, 'add'], 
            'gsave', 
            'stroke'
        ]
        self.assertEqual(ast, expected_ast)

    def test_large_number_parsing(self):
        code = "1000000000 -1234567890"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [1000000000, -1234567890]
        self.assertEqual(ast, expected_ast)

    def test_floating_point_numbers(self):
        code = "1.23 4.56 add"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [1.23, 4.56, 'add']
        self.assertEqual(ast, expected_ast)

    def test_malformed_input(self):
        code = "100 200 moveto ]"
        with self.assertRaises(SyntaxError):
            tokens = self.lexer(code).tokenize()
            self.parser(tokens).parse()

    def test_empty_array(self):
        code = "[] 100 dup"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[], 100, 'dup']
        self.assertEqual(ast, expected_ast)

    def test_empty_block(self):
        code = "{}"
        tokens = self.lexer(code).tokenize()
        ast = self.parser(tokens).parse()
        expected_ast = [[]]
        self.assertEqual(ast, expected_ast)

# Run the tests
if __name__ == "__main__":
    unittest.main()
