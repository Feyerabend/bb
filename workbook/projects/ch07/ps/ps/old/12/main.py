# main.py

from lexer import Lexer
from parser import Parser, ASTNode

class PSInterpreter:
    def __init__(self):
        self.dictionary_stack = []  # Stack of dictionaries
        self.global_scope = {}  # Global dictionary for top-level variables

    def analyze(self, ast: ASTNode):
        """ Post-process the AST to handle dictionaries, procedures, and variable assignments. """
        self._process_node(ast)

    def _process_node(self, node: ASTNode):
        """ Recursive function to process the AST and handle different types of nodes. """
        if node.type == "Store":
            # Handle the store operator (assigning a value to a variable)
            self._handle_store(node)
        elif node.type == "Command":
            # Handle PostScript commands
            self._handle_command(node)

        # Recursively process child nodes
        for child in node.children:
            self._process_node(child)

    def _handle_store(self, node: ASTNode):
        """ Handle the store operator (variable assignment). """
        variable_name = node.value  # The variable being stored
        value_node = node.children[0]  # The value being assigned
        value = self._evaluate(value_node)  # Evaluate the value

        # Get the current dictionary and store the variable
        current_dict = self.dictionary_stack[-1] if self.dictionary_stack else self.global_scope
        current_dict[variable_name] = value

    def _handle_command(self, node: ASTNode):
        """ Handle PostScript commands like `moveto`, `lineto`, etc. """
        command_name = node.value
        if command_name == "newpath":
            print("Creating new path...")
        elif command_name == "moveto":
            print("Moving to coordinates...")
        elif command_name == "lineto":
            print("Drawing line to coordinates...")

    def _evaluate(self, node: ASTNode):
        """ Evaluate a value node (e.g., numbers, strings). """
        if node.type == "Number":
            return node.value
        elif node.type == "String":
            return node.value
        # Add more evaluation logic for other types...

# Example Usage
code = """
/x 10 def
/y 20 def
x y moveto
50 60.98 lineto
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Instantiate the PostScript interpreter and analyze the AST
interpreter = PSInterpreter()
interpreter.analyze(ast)
