# main.py

from lexer import Lexer
from parser import Parser



code = """
/x 10 def
/y 20 def
x y moveto
50 60.98 lineto
{ x -10 add } repeat
"""

# Tokenize the code
lexer = Lexer(code)
tokens = lexer.tokenize()

# Parse the tokens into an AST
parser = Parser(tokens)
ast = parser.parse()

import pprint

# Output the AST structure
pprint.pprint(ast)





code = """
10 20 add
"""

# Tokenize the code
lexer = Lexer(code)
tokens = lexer.tokenize()

# Parse the tokens into an AST
parser = Parser(tokens)
ast = parser.parse()

import pprint

# Output the AST structure
pprint.pprint(ast)





code = """
% PS sample bluebook
newpath
270 360 moveto
0 72 rlineto
72 0 rlineto
0 -72 rlineto
closepath
fill
showpage
"""

# Tokenize the code
lexer = Lexer(code)
tokens = lexer.tokenize()

# Parse the tokens into an AST
parser = Parser(tokens)
ast = parser.parse()

import pprint

# Output the AST structure
pprint.pprint(ast)
