
from stack import Stack
from environment import Environment
from parser import ASTNode
from lexer import Token

class Executor:
    def __init__(self, stack: 'Stack', env: 'Environment'):
        self.stack = stack
        self.env = env

    def execute(self, ast: ASTNode):
        # Process the AST node types
        if ast.type == 'Literal':
            # Push a literal value onto the stack
            print(f"[DEBUG] Pushing literal value: {ast.value}")
            self.stack.push(ast.value)

        elif ast.type == 'Operator':
            # Handle operators (add, sub, etc.)
            operator = ast.value
            print(f"[DEBUG] Running operator: {operator}")
            if operator == 'add':
                operand2 = self.stack.pop()
                operand1 = self.stack.pop()
                result = self.run_operator(operator, [operand1, operand2])
                print(f"[DEBUG] Result of add: {result}")
                self.stack.push(result)

        elif ast.type == 'Define':
            # Define a variable in the environment
            var_name = ast.value
            value = ast.children[0].value
            print(f"[DEBUG] Defining variable: {var_name} = {value}")
            self.env.define(var_name, value)

        elif ast.type == 'Identifier':
            # Handle identifiers (x, y, etc.) by looking up and pushing their values
            var_name = ast.value
            value = self.env.lookup(var_name)
            print(f"[DEBUG] Pushing variable {var_name} value: {value} to stack")
            self.stack.push(value)

        else:
            raise ValueError(f"[DEBUG] Unknown AST node type: {ast.type}")

    def run_operator(self, operator: str, operands: list[any]) -> any:
        if operator == 'add':
            return operands[0] + operands[1]
        else:
            raise ValueError(f"[DEBUG] Unknown operator: {operator}")
