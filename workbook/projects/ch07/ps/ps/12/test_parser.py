import unittest
from lexer import Lexer, Token
from parser import Parser, ASTNode

class TestParser(unittest.TestCase):

    def test_comment_ignored(self):
        code = """
        /x 10 def
        % This is a comment
        /y 20 def
        x y moveto
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = ASTNode("Program", children=[
            ASTNode("Name", value='/x'),
            ASTNode("Number", value=10),
            ASTNode("Operator", value='def'),  # Now expecting 'Operator' instead of 'Name'
            ASTNode("Name", value='/y'),
            ASTNode("Number", value=20),
            ASTNode("Operator", value='def'),  # Same here
            ASTNode("Name", value='x'),
            ASTNode("Name", value='y'),
            ASTNode("Command", value='moveto')
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_conditional_ifelse(self):
        code = """
        /x 10 def
        /y 20 def
        x y eq {
            /z 30 def
        } {
            /z 40 def
        } ifelse
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = ASTNode("Program", children=[
            ASTNode("Name", value='/x'),
            ASTNode("Number", value=10),
            ASTNode("Operator", value='def'),
            ASTNode("Name", value='/y'),
            ASTNode("Number", value=20),
            ASTNode("Operator", value='def'),
            ASTNode("Name", value='x'),
            ASTNode("Name", value='y'),
            ASTNode("Operator", value='eq'),
            ASTNode("Block", children=[
                ASTNode("Name", value='/z'),
                ASTNode("Number", value=30),
                ASTNode("Operator", value='def')
            ]),
            ASTNode("Block", children=[
                ASTNode("Name", value='/z'),
                ASTNode("Number", value=40),
                ASTNode("Operator", value='def')
            ]),
            ASTNode("Command", value='ifelse')
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_nested_blocks(self):
        code = """
        /x 10 def
        {
            /y 20 def
            x y moveto
        } def
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = ASTNode("Program", children=[
            ASTNode("Name", value='/x'),
            ASTNode("Number", value=10),
            ASTNode("Operator", value='def'),
            ASTNode("Block", children=[
                ASTNode("Name", value='/y'),
                ASTNode("Number", value=20),
                ASTNode("Operator", value='def'),
                ASTNode("Name", value='x'),
                ASTNode("Name", value='y'),
                ASTNode("Command", value='moveto')
            ]),
            ASTNode("Operator", value='def')  # Expecting 'Operator' for def here as well
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_postscript_code(self):
        code = """
        /x 10 def
        /y 20 def
        x y moveto
        50 60.98 lineto
        { x -10 add } repeat
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = ASTNode("Program", children=[
            ASTNode("Name", value='/x'),
            ASTNode("Number", value=10),
            ASTNode("Operator", value='def'),
            ASTNode("Name", value='/y'),
            ASTNode("Number", value=20),
            ASTNode("Operator", value='def'),
            ASTNode("Name", value='x'),
            ASTNode("Name", value='y'),
            ASTNode("Command", value='moveto'),
            ASTNode("Number", value=50),
            ASTNode("Number", value=60.98),
            ASTNode("Command", value='lineto'),
            ASTNode("Block", children=[
                ASTNode("Name", value='x'),
                ASTNode("Number", value=-10),
                ASTNode("Operator", value='add'),
            ]),
            ASTNode("Command", value='repeat')
        ])

        self.assertEqual(str(ast), str(expected_ast))

    def test_while_loop(self):
        code = """
        /x 10 def
        /y 20 def
        { x y lt {
            x x 1 add def
        } while}
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expected_ast = ASTNode("Program", children=[
            ASTNode("Name", value='/x'),
            ASTNode("Number", value=10),
            ASTNode("Operator", value='def'),
            ASTNode("Name", value='/y'),
            ASTNode("Number", value=20),
            ASTNode("Operator", value='def'),
            ASTNode("Block", children=[
                ASTNode("Name", value='x'),
                ASTNode("Name", value='y'),
                ASTNode("Operator", value='lt'),
                ASTNode("Block", children=[
                    ASTNode("Name", value='x'),
                    ASTNode("Name", value='x'),
                    ASTNode("Number", value=1),
                    ASTNode("Operator", value='add'),
                    ASTNode("Operator", value='def')
                ]),
                ASTNode("Command", value='while')
            ])
        ])

        self.assertEqual(str(ast), str(expected_ast))

if __name__ == "__main__":
    unittest.main()