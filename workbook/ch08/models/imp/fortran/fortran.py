import re
import sys


class FortranLikeInterpreter:
    def __init__(self):
        self.variables = {}
        self.labels = {}
        self.program = []
        self.pc = 0  # program counter
        self.running = False
        
    def parse_line(self, line):
        line = line.strip().upper()
        if not line or line.startswith('!'):
            return None
            
        # label parsing
        label_match = re.match(r'^(\d+)\s+(.*)', line)
        if label_match:
            label, rest = label_match.groups()
            self.labels[label] = len(self.program)
            line = rest.strip()
 
        # operation type
        if ':=' in line:
            var, expr = line.split(':=', 1)
            return ('assign', var.strip(), expr.strip())
        elif line.startswith('GOTO'):
            return ('goto', line[4:].strip())
        elif line.startswith('IF'):
            match = re.match(r'IF\s*\((.*?)\)\s*GOTO\s*(\d+)', line)
            if match:
                return ('if_goto', *match.groups())
        elif line.startswith('PRINT'):
            items = line[5:].strip(' *').split(',')
            return ('print', [item.strip() for item in items])
        elif line == 'END':
            return ('end',)
        return None

    def tokenize(self, expr):
        tokens = []
        current = ''
        for char in expr:
            if char in '+-*/()':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(char)
            elif char.isspace():
                if current:
                    tokens.append(current)
                    current = ''
            else:
                current += char
        if current:
            tokens.append(current)
        return tokens

    def shunting_yard(self, tokens):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output = []
        stack = []
        for token in tokens:
            if token.replace('.', '', 1).isdigit():
                num = float(token) if '.' in token else int(token)
                output.append(num)
            elif token in precedence:
                while stack and stack[-1] != '(' and precedence[token] <= precedence.get(stack[-1], 0):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                raise ValueError(f"Invalid token: {token}")
        while stack:
            output.append(stack.pop())
        return output

    def evaluate_postfix(self, postfix):
        stack = []
        for token in postfix:
            if isinstance(token, (int, float)):
                stack.append(token)
            else:
                b = stack.pop()
                a = stack.pop()
                if token == '+': stack.append(a + b)
                elif token == '-': stack.append(a - b)
                elif token == '*': stack.append(a * b)
                elif token == '/': stack.append(a / b)
        return stack[0]

    def evaluate_expression(self, expr):
        # sub variables with longest names first to prevent partial matches
        for var in sorted(self.variables.keys(), key=lambda x: -len(x)):
            expr = expr.replace(var, str(self.variables[var]))

        try:
            tokens = self.tokenize(expr)
            postfix = self.shunting_yard(tokens)
            return self.evaluate_postfix(postfix)
        except:
            raise ValueError(f"Error evaluating expression: {expr}")

    def evaluate_condition(self, cond):

        # convert Fortran-style operators
        cond = cond.replace('.EQ.', '==').replace('.NE.', '!=')
        cond = cond.replace('.LT.', '<').replace('.LE.', '<=')
        cond = cond.replace('.GT.', '>').replace('.GE.', '>=')

        # split into components
        operators = ['!=', '==', '<=', '>=', '<', '>', '=']
        for op in operators:
            if op in cond:
                left, right = cond.split(op, 1)
                left_val = self.evaluate_expression(left.strip())
                right_val = self.evaluate_expression(right.strip())
                
                if op == '==': return left_val == right_val
                elif op == '!=': return left_val != right_val
                elif op == '<': return left_val < right_val
                elif op == '<=': return left_val <= right_val
                elif op == '>': return left_val > right_val
                elif op == '>=': return left_val >= right_val
                elif op == '=': return left_val == right_val
                
        raise ValueError(f"Invalid condition: {cond}")


    def execute(self, instruction):
        op = instruction[0]
        
        if op == 'assign':
            _, var, expr = instruction
            self.variables[var] = self.evaluate_expression(expr)
            self.pc += 1
            
        elif op == 'goto':
            _, label = instruction
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise ValueError(f"Undefined label: {label}")
                
        elif op == 'if_goto':
            _, condition, label = instruction
            if self.evaluate_condition(condition):
                if label in self.labels:
                    self.pc = self.labels[label]
                else:
                    raise ValueError(f"Undefined label: {label}")
            else:
                self.pc += 1
                
        elif op == 'print':
            _, items = instruction
            output = []
            for item in items:
                if item in self.variables:
                    output.append(str(self.variables[item]))
                else:
                    output.append(item)
            print(' '.join(output))
            self.pc += 1
            
        elif op == 'end':
            self.running = False
                
    def run(self):
        self.pc = 0
        self.running = True
        
        while self.running and self.pc < len(self.program):
            instruction = self.program[self.pc]
            self.execute(instruction)

    def load_program(self, code):
        self.program = []
        self.labels = {}
        
        for line in code.split('\n'):
            instruction = self.parse_line(line)
            if instruction:
                self.program.append(instruction)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            code = f.read()
        self.load_program(code)

# example
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run program from file
        interpreter = FortranLikeInterpreter()
        try:
            interpreter.load_from_file(sys.argv[1])
            interpreter.run()
        except FileNotFoundError:
            print(f"Error: File '{sys.argv[1]}' not found")
    else:
        # Run built-in sample
        interpreter = FortranLikeInterpreter()
        program = """
        ! Simple factorial calculation
           N := 5
           FACT := 1
        10 IF (N .GT. 1) GOTO 20
           PRINT *, "FACTORIAL IS", FACT
           GOTO 30
        20 FACT := FACT * N
           N := N - 1
           GOTO 10
        30 END
        """
        interpreter.load_program(program)
        interpreter.run()
