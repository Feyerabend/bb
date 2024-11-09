# executor.py

from environment import Environment
from stack import Stack
from lexer import Token, Lexer
from parser import ASTNode, Parser

class Executor:
    def __init__(self, stack: Stack, env: Environment):
        self.stack = stack  # Stack to manage operand values
        self.env = env  # Environment to manage variable names, procedures, and dictionaries

    def execute(self, ast: ASTNode):
        """Main entry point for execution, processing each node in the AST recursively."""
        self._process_node(ast)

    def _process_node(self, node: ASTNode):
        """Process an AST node based on its type, handling variable assignments, commands, etc."""
        if node.type == "Store":
            # Handle variable assignment (store operator)
            self._handle_store(node)
        elif node.type == "Command":
            # Handle PostScript commands like `moveto`, `newpath`, etc.
            self._handle_command(node)
        elif node.type == "Operator":
            # Execute operators like arithmetic, stack manipulation
            self._handle_operator(node)

#            operands = [self.stack.pop() for _ in range(2)]
#            result = self.run_operator(node.value, operands)
#            self.stack.push(result)

        elif node.type == "Block":
            # Evaluate a block of code inside `{ }`
            self._evaluate_block(node)
        elif node.type == "Number":
            # Push number directly to the stack
            self.stack.push(node.value)
        elif node.type == "Name":
             # If the node is a variable reference (no `/`), just evaluate it
            value = self._evaluate(node)
            self.stack.push(value)
        
        # Recursively process any child nodes
        for child in node.children:
            self._process_node(child)

    def _handle_store(self, node: ASTNode):
        """ Handle storage of variables or dictionary entries """
        if node.parent and node.parent.type == "Dictionary":
            # Store as dictionary entry, stripping the `/` for the key name
            dict_name = node.parent.value.lstrip('/')
            key_name = node.value.lstrip('/')  # Strip `/` for dictionary keys
            value = self._evaluate(node.children[0])
            self.env.add_to_dict(dict_name, key_name, value)
        else:
            # Store as a regular variable (no `/` expected in variable names)
            variable_name = node.value  # Use name directly as a variable
            value = self._evaluate(node.children[0])
            self.env.define(variable_name, value)

    def _evaluate(self, node: ASTNode) -> any:
        """ Evaluate a node for its value """
        if node.type == "Number":
            return node.value
        elif node.type == "Name":
            # Look up variables directly without any prefix handling
            return self.env.lookup(node.value)
        else:
            raise ValueError(f"Unknown node type for evaluation: {node.type}")

    def _handle_command(self, node: ASTNode):
        """Handle PostScript commands like `moveto`, `newpath`, etc."""
        command_name = node.value
        if command_name == "moveto":
            y = self.stack.pop()
            x = self.stack.pop()
            print(f"Moving to coordinates: {x}, {y}")
        elif command_name == "newpath":
            print("Starting a new path...")
        # Additional commands can be added here...

    def _handle_operator(self, node: ASTNode):
        """Handle operators like `add`, `sub`, etc., which operate on values from the stack."""
        operator_name = node.value
        operands = []

        # Collect the required operands for the operator
        while len(operands) < 2:
            operands.append(self.stack.pop())

        # Execute the operation
        result = self.run_operator(operator_name, operands)
        
        # Push the result back onto the stack
        if result is not None:
            self.stack.push(result)

    def run_operator(self, operator: str, operands: list[any]) -> any:
        """Execute a specific operator (e.g., add, sub) on operands and return the result."""
        if operator == "add":
            return operands[1] + operands[0]  # Operand order matters here
        elif operator == "sub":
            return operands[1] - operands[0]
        elif operator == "mul":
            return operands[1] * operands[0]
        elif operator == "div":
            return operands[1] / operands[0]
        elif operator == "neg":
            return -operands[0]
        elif operator == "dup":
            self.stack.push(operands[0])  # Duplicate the operand
            return operands[0]
        elif operator == "exch":
            self.stack.push(operands[0])  # Push second operand first to stack
            self.stack.push(operands[1])  # Then push first operand
            return None
        elif operator == "pop":
            return None  # pop discards the top of the stack
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _evaluate_block(self, node: ASTNode):
        """Evaluate a block of code, which allows executing a series of commands in `{}`."""
        self.env.enter_scope()  # Enter a new scope for the block
        for child in node.children:
            self._process_node(child)
        self.env.exit_scope()  # Exit the block scope

# Example usage of the Executor class

code = """
/x 10 def
/y 20 def
x y add
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

stack = Stack()
env = Environment()
executor = Executor(stack, env)

executor.execute(ast)
print(f"Stack after execution: {stack.items}")
