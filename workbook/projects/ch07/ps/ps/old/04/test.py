class Token:
    def __init__(self, type: str, value: any):
        self.type = type
        self.value = value

class Environment:
    def __init__(self):
        self.global_scope = {}
        self.scopes = [self.global_scope]  # Stack of scopes

    def define(self, name: str, value: any):
        # Define a variable or a function in the current scope
        self.global_scope[name] = value  # Always define in the global scope for functions

    def lookup(self, name: str) -> any:
        # Lookup a variable or function in the current and outer scopes
        if name in self.global_scope:
            return self.global_scope[name]
        raise KeyError(f"Variable or function '{name}' not found.")

    def enter_scope(self):
        # Create a new scope (i.e., function or block)
        self.scopes.append({})

    def exit_scope(self):
        # Exit the current scope
        self.scopes.pop()

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value: any):
        self.stack.append(value)

    def pop(self) -> any:
        return self.stack.pop() if self.stack else None

    def peek(self) -> any:
        return self.stack[-1] if self.stack else None

class Executor:
    def __init__(self, stack: 'Stack', env: 'Environment'):
        self.stack = stack
        self.env = env

    def execute(self, ast: 'ASTNode'):
        # Execute a statement or expression from the AST
        if ast.type == 'literal':
            self.stack.push(ast.value)
        elif ast.type == 'operator':
            self.run_operator(ast.value, ast.children)
        elif ast.type == 'procedure':
            self.evaluate_procedure(ast.value)
        elif ast.type == 'conditional':
            self.execute_conditional(ast)
        elif ast.type == 'identifier':
            self.execute_identifier(ast.value)

    def run_operator(self, operator: str, operands: list):
        # Perform operations like addition, subtraction, etc.
        if operator == 'add':
            result = operands[0] + operands[1]
        elif operator == 'sub':
            result = operands[0] - operands[1]
        elif operator == 'mul':
            result = operands[0] * operands[1]
        elif operator == 'div':
            result = operands[0] / operands[1]
        else:
            raise ValueError(f"Unknown operator: {operator}")
        
        self.stack.push(result)

    def evaluate_procedure(self, procedure: list):
        # Evaluate a procedure (similar to a function call)
        self.env.enter_scope()  # New scope for function call
        for token in procedure:
            self.execute(token)
        self.env.exit_scope()  # Exit the scope after execution

    def execute_conditional(self, conditional: 'ASTNode'):
        # Handle conditionals (if and else)
        condition = conditional.children[0]
        true_branch = conditional.children[1]
        false_branch = None
        if len(conditional.children) > 2:
            false_branch = conditional.children[2]

        self.execute(condition)
        condition_result = self.stack.pop()
        
        if condition_result:
            # Execute the true branch
            for node in true_branch:
                self.execute(node)
        elif false_branch:
            # Execute the false branch (else)
            for node in false_branch:
                self.execute(node)

    def execute_identifier(self, name: str):
        # Look up an identifier in the environment
        value = self.env.lookup(name)
        if callable(value):
            # It's a function, execute it
            self.stack.push(value)  # Push the function itself, so it can be executed
        else:
            # It's a variable, push its value onto the stack
            self.stack.push(value)

class ASTNode:
    def __init__(self, type: str, value: any, children: list = None):
        self.type = type
        self.value = value
        self.children = children or []

class Lexer:
    def __init__(self, code: str):
        self.code = code

    def tokenize(self) -> list[Token]:
        tokens = []
        lines = self.code.splitlines()

        for line in lines:
            line = line.strip()
            if line.startswith("%%"):  # Ignore comments
                continue
            code = line.split()
            for item in code:
                if item in ['add', 'sub', 'mul', 'div', 'def', 'if', 'else']:
                    tokens.append(Token('keyword', item))
                elif item.replace('.', '', 1).isdigit():  # Handles both integers and floats
                    tokens.append(Token('literal', float(item) if '.' in item else int(item)))
                else:
                    tokens.append(Token('identifier', item))
        return tokens

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        return self.parse_statement()

    def parse_statement(self) -> ASTNode:
        token = self.tokens[self.pos]
        
        if token.type == 'literal':
            self.pos += 1
            return ASTNode('literal', token.value)
        
        elif token.type == 'keyword' and token.value == 'def':
            self.pos += 1
            name_token = self.tokens[self.pos]
            self.pos += 1
            body_tokens = self.parse_body()
            return ASTNode('procedure', (name_token.value, body_tokens))
        
        elif token.type == 'keyword' and token.value == 'if':
            self.pos += 1
            condition = self.parse_statement()
            true_branch = self.parse_statement()
            false_branch = None
            if self.pos < len(self.tokens) and self.tokens[self.pos].value == 'else':
                self.pos += 1
                false_branch = self.parse_statement()
            return ASTNode('conditional', None, [condition, true_branch, false_branch])

        elif token.type == 'keyword' and token.value in ['add', 'sub', 'mul', 'div']:
            self.pos += 1
            operand1 = self.parse_statement()
            operand2 = self.parse_statement()
            return ASTNode('operator', token.value, [operand1, operand2])

        else:
            # It must be an identifier or something else
            self.pos += 1
            return ASTNode('identifier', token.value)

    def parse_body(self):
        body = []
        while self.pos < len(self.tokens) and self.tokens[self.pos].value != 'def':
            body.append(self.parse_statement())
        return body

def run_postscript(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    stack = Stack()
    env = Environment()
    executor = Executor(stack, env)
    
    executor.execute(ast)
    
    return stack.peek()

# Example usage:
code = """
%% This is a comment
3 4 add 5 sub def result
result
"""
result = run_postscript(code)
print(f"Result: {result}")

# More complex example with function definition and conditionals
code2 = """
/myFunc {
    5 3 add
} def

myFunc
"""
result2 = run_postscript(code2)
print(f"Result2: {result2}")