
from lexer import Lexer
from parser import Parser, ASTNode
from environment import Environment


class PostScriptTest:
    @staticmethod
    def run_test(code: str):
        print("Input PostScript code:")
        print(code)
        
        # Initialize the environment (used for variable lookups and definitions)
        env = Environment()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("\nTokens:")
        print(tokens)

        parser = Parser(tokens, env)
        ast = parser.parse()
        print("\nAST:")
        print(ast)

        # For demonstration purposes, we'll print the value of variables if defined
        if isinstance(ast, ASTNode) and ast.type == 'Literal':
            print(f"\nEvaluating AST value: {ast.value}")

# Running the test with variable definitions
code = """
x 10 def
y 20 def
x y add
"""
PostScriptTest.run_test(code)
