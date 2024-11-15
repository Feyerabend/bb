import re
from enum import Enum, auto

from parser import Token, TokenType, ASTNode, Lexer, Parser


class PSObject:
    def execute(self, interpreter):
        pass

class Number(PSObject):
    def __init__(self, value):
        self.value = value
    
    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Boolean(PSObject):
    def __init__(self, value):
        self.value = value

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class String(PSObject):
    def __init__(self, value):
        self.value = value

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Array(PSObject):
    def __init__(self, elements):
        self.elements = elements

    def execute(self, interpreter):
        interpreter.operand_stack.append(self)

class Name(PSObject):
    def __init__(self, name):
        self.name = name

    def execute(self, interpreter):
        value = interpreter.lookup(self.name)
        if isinstance(value, Procedure):
            interpreter.execution_stack.append(interpreter.current_object_stream)
            interpreter.current_object_stream = value.elements
        elif value is not None:
            value.execute(interpreter)
        else:
            raise NameError(f"Undefined name: {self.name}")

class Operator(PSObject):
    def __init__(self, func):
        self.func = func

    def execute(self, interpreter):
        self.func(interpreter)

class Procedure(PSObject):
    def __init__(self, elements):
        self.elements = elements

    def execute(self, interpreter):
        interpreter.execution_stack.append(interpreter.current_object_stream)
        interpreter.current_object_stream = self.elements

# --- Interpreter Class Definition ---

class Interpreter:
    def __init__(self):
        self.operand_stack = []
        self.execution_stack = []
        self.dictionary_stack = [{}]
        self.current_object_stream = []

    def lookup(self, name):
        for dictionary in reversed(self.dictionary_stack):
            if name in dictionary:
                return dictionary[name]
        return None

    def define(self, name, value):
        self.dictionary_stack[-1][name] = value

    def execute_ast(self, ast):
        for node in ast:
            self.execute_node(node)

    def execute_def(self, node):
        # Ensure node.value is structured as expected
        print(f"Debugging DEF node: {node}")  # See the entire node for clarity
        print(f"Debugging DEF node value: {node.value}")  # Specifically inspect the value
    # Continue with the rest of the function...
        if isinstance(node.value, dict) and "name" in node.value and "value" in node.value:
            definition_name = node.value["name"]
            definition_value = node.value["value"]
    
            if definition_name and definition_value:
                self.dictionary_stack.define(definition_name, definition_value)
        else:
            raise SyntaxError("Invalid DEF node format.")


    def execute_equals(self):
        """Handles the '=' command to print the top of the operand stack."""
        if self.operand_stack:
            print(self.operand_stack.pop())

    def execute_dequals(self):
        """Handles the '==' command to print a syntactic representation of the top of the operand stack."""
        if self.operand_stack:
            print(repr(self.operand_stack.pop()))


    def execute_node(self, node):
        if node.type == TokenType.NUMBER:
            Number(node.value).execute(self)
        elif node.type == TokenType.LITERAL:
            self.operand_stack.append(Name(node.value[1:]))  # remove '/'
        elif node.type == TokenType.IDENTIFIER:
            if node.value == "def":  # ugly: handle 'def'
                self.execute_def(node)
            else:
                Name(node.value).execute(self)
        elif node.type == TokenType.LBRACKET:
            array_elements = [self.convert_ast_to_obj(el) for el in node.value]
            Array(array_elements).execute(self)
        elif node.type == TokenType.LBRACE:
            block_elements = [self.convert_ast_to_obj(el) for el in node.value]
            Procedure(block_elements).execute(self)
        elif node.type == TokenType.EQUALS:
            self.execute_equals()
        elif node.type == TokenType.DEQUALS:
            self.execute_dequals()
        elif node.type == TokenType.DEF:
            self.execute_def(node)
        else:
            raise SyntaxError(f"Unhandled AST node type: {node.type}")

    def convert_ast_to_obj(self, node):
        """Helper to convert ASTNode to corresponding PS object"""
        if node.type == TokenType.NUMBER:
            return Number(node.value)
        elif node.type == TokenType.LITERAL:
            return Name(node.value[1:])
        elif node.type == TokenType.IDENTIFIER:
            return Name(node.value)
        elif node.type == TokenType.LBRACKET:
            return Array([self.convert_ast_to_obj(el) for el in node.value])
        elif node.type == TokenType.LBRACE:
            return Procedure([self.convert_ast_to_obj(el) for el in node.value])
        else:
            raise SyntaxError(f"Unhandled AST node type in conversion: {node.type}")

# --- Testing ---

# Define some basic operators
def add(interpreter):
    b = interpreter.operand_stack.pop().value
    a = interpreter.operand_stack.pop().value
    interpreter.operand_stack.append(Number(a + b))

def print_stack(interpreter):
    print("Stack:", [obj.value if isinstance(obj, (Number, String, Boolean)) else obj for obj in interpreter.operand_stack])

# Add these operations to the interpreter
interpreter = Interpreter()
interpreter.define("add", Operator(add))
interpreter.define("=", Operator(print_stack))

# Test cases
code = """
5 3 add =
/sum { 2 add } def
10 sum =
"""
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Execute parsed AST
interpreter.execute_ast(ast)