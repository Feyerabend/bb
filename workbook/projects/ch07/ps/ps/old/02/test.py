
from lexer import Lexer
from parser import Parser

class PostScriptTest:
    @staticmethod
    def run_test(code: str):
        print("Input PostScript code:")
        print(code)
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print("\nTokens:")
        print(tokens)

        parser = Parser(tokens)
        ast = parser.parse()
        print("\nAST:")
        print(ast)

# Running the test with a PostScript sample
code = "10 20 add"
PostScriptTest.run_test(code)

code = "3 4 mul 5 add"
PostScriptTest.run_test(code)

code = "( 10 20 add )"
PostScriptTest.run_test(code)
