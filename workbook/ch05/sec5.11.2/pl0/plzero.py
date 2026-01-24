from enum import Enum, auto
from typing import List, Dict, Optional
import re


class Operation(Enum):
    LIT = auto()  # Load literal
    OPR = auto()  # Operation
    LOD = auto()  # Load from memory
    STO = auto()  # Store to memory
    CAL = auto()  # Call procedure
    INT = auto()  # Allocate stack space
    JMP = auto()  # Unconditional jump
    JPC = auto()  # Conditional jump
    HLT = auto()  # Halt

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l  # level (for LOD, STO, CAL)
        self.a = a  # address/value

    def __repr__(self):
        return f"{self.op.name} {self.l} {self.a}"

class PL0Interpreter:
    def __init__(self, code: List[Instruction], stack_size=10000):
        self.code = code
        self.s = [0] * stack_size  # stack
        self.p = 0  # program counter
        self.b = 1  # base pointer
        self.t = 0  # top stack pointer
        self.debug = False
        self.halted = False

    def base(self, level: int) -> int:
        """Find base pointer at given level"""
        current_b = self.b
        while level > 0:
            current_b = self.s[current_b]
            level -= 1
        return current_b

    def run(self):
        # Initialize main frame
        self.t = 2
        self.s[1] = 0  # static link
        self.s[2] = 0  # dynamic link
        self.s[3] = len(self.code)  # return address (not used in main)
        
        while self.p < len(self.code) and not self.halted:
            i = self.code[self.p]
            
            if self.debug:
                stack_view = ' '.join([str(self.s[j]) for j in range(max(0, self.t-5), self.t+1)])
                print(f"[{self.p:3d}] {str(i):15s} | BP={self.b:3d} SP={self.t:3d} | Stack: ...{stack_view}")
            
            self.p += 1
            self._execute(i)

    def _execute(self, i: Instruction):
        """Execute a single instruction"""
        
        if i.op == Operation.LIT:
            # Push literal value onto stack
            self.t += 1
            self.s[self.t] = i.a

        elif i.op == Operation.OPR:
            # Perform operation based on operation code
            if i.a == 0:  # Return from procedure
                return_value = self.s[self.t]
                self.t = self.b - 1
                self.p = self.s[self.b + 2]
                self.b = self.s[self.b + 1]
                self.t += 1
                self.s[self.t] = return_value
                
            elif i.a == 1:  # Negate (unary -)
                self.s[self.t] = -self.s[self.t]
                
            elif i.a == 2:  # Addition
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = left + right
                
            elif i.a == 3:  # Subtraction
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = left - right
                
            elif i.a == 4:  # Multiplication
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = left * right
                
            elif i.a == 5:  # Division
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = left // right
                
            elif i.a == 6:  # Odd check
                self.s[self.t] = self.s[self.t] % 2
                
            elif i.a == 7:  # Modulo
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = left % right
                
            elif i.a == 8:  # Equality (==)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left == right)
                
            elif i.a == 9:  # Not equal (!=)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left != right)
                
            elif i.a == 10:  # Less than (<)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left < right)
                
            elif i.a == 11:  # Greater than (>)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left > right)
                
            elif i.a == 12:  # Less than or equal (<=)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left <= right)
                
            elif i.a == 13:  # Greater than or equal (>=)
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left >= right)
                
            elif i.a == 14:  # Logical AND
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left and right)
                
            elif i.a == 15:  # Logical OR
                right = self.s[self.t]
                self.t -= 1
                left = self.s[self.t]
                self.s[self.t] = int(left or right)

        elif i.op == Operation.LOD:
            # Load value from memory address
            addr = self.base(i.l) + i.a
            self.t += 1
            self.s[self.t] = self.s[addr]

        elif i.op == Operation.STO:
            # Store value to memory address
            addr = self.base(i.l) + i.a
            self.s[addr] = self.s[self.t]
            self.t -= 1

        elif i.op == Operation.CAL:
            # Call procedure
            new_bp = self.t + 1
            self.s[new_bp] = self.base(i.l)  # static link
            self.s[new_bp + 1] = self.b      # dynamic link
            self.s[new_bp + 2] = self.p      # return address
            self.b = new_bp
            self.t = new_bp + 2
            self.p = i.a

        elif i.op == Operation.INT:
            # Allocate stack space
            self.t += i.a

        elif i.op == Operation.JMP:
            # Unconditional jump
            self.p = i.a

        elif i.op == Operation.JPC:
            # Conditional jump (jump if top of stack is 0/false)
            if self.s[self.t] == 0:
                self.p = i.a
            self.t -= 1

        elif i.op == Operation.HLT:
            # Halt execution
            self.halted = True



class Compiler:
    def __init__(self):
        self.symbol_table: Dict[str, int] = {}
        self.code: List[Instruction] = []
        self.var_offset = 3  # Variables start at offset 3 (after SL, DL, RA)
    
    def compile(self, program: str) -> List[Instruction]:
        """Compile a simple PL/0-like program"""
        self.symbol_table.clear()
        self.code.clear()
        
        # Parse and clean lines
        lines = [line.strip() for line in program.split('\n') 
                if line.strip() and not line.strip().startswith('//')]
        
        # First pass - collect variable declarations
        var_count = 0
        statements = []
        for line in lines:
            if line.startswith('var '):
                var_name = line[4:].strip().rstrip(';')
                self.symbol_table[var_name] = self.var_offset + var_count
                var_count += 1
            else:
                statements.append(line)
        
        # Allocate space for variables
        if var_count > 0:
            self.code.append(Instruction(Operation.INT, 0, var_count))
        
        # Second pass - process statements
        for line in statements:
            if line.startswith('if '):
                self._compile_if(line)
            elif line.startswith('while '):
                self._compile_while(line)
            elif '=' in line:
                self._compile_assignment(line)
        
        # Add halt instruction
        self.code.append(Instruction(Operation.HLT, 0, 0))
        return self.code
    
    def _compile_assignment(self, line: str):
        """Compile assignment statement"""
        var_name, expr = [part.strip() for part in line.rstrip(';').split('=', 1)]
        
        if var_name not in self.symbol_table:
            raise ValueError(f"Undeclared variable: {var_name}")
        
        # Compile expression
        self._compile_expression(expr)
        
        # Store result
        var_address = self.symbol_table[var_name]
        self.code.append(Instruction(Operation.STO, 0, var_address))
    
    def _compile_if(self, line: str):
        """Compile if statement (basic version without else)"""
        # Expected format: if <condition> then <statement>
        match = re.match(r'if\s+(.+?)\s+then\s+(.+)', line, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid if statement: {line}")
        
        condition = match.group(1).strip()
        statement = match.group(2).strip()
        
        # Compile condition
        self._compile_expression(condition)
        
        # JPC - jump if false
        jpc_addr = len(self.code)
        self.code.append(Instruction(Operation.JPC, 0, 0))  # placeholder
        
        # Compile statement
        if '=' in statement:
            self._compile_assignment(statement)
        
        # Patch JPC address
        self.code[jpc_addr].a = len(self.code)
    
    def _compile_while(self, line: str):
        """Compile while loop"""
        # Expected format: while <condition> do <statement>
        match = re.match(r'while\s+(.+?)\s+do\s+(.+)', line, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid while statement: {line}")
        
        condition = match.group(1).strip()
        statement = match.group(2).strip()
        
        # Loop start
        loop_start = len(self.code)
        
        # Compile condition
        self._compile_expression(condition)
        
        # JPC - jump if false (exit loop)
        jpc_addr = len(self.code)
        self.code.append(Instruction(Operation.JPC, 0, 0))  # placeholder
        
        # Compile statement
        if '=' in statement:
            self._compile_assignment(statement)
        
        # Jump back to loop start
        self.code.append(Instruction(Operation.JMP, 0, loop_start))
        
        # Patch JPC address
        self.code[jpc_addr].a = len(self.code)
    
    def _compile_expression(self, expr: str):
        """Compile expressions with operator precedence"""
        expr = expr.strip()
        
        # Logical OR (lowest precedence)
        if self._split_operator(expr, '||'):
            return
        
        # Logical AND
        if self._split_operator(expr, '&&'):
            return
        
        # Comparison operators (must check multi-char first)
        for op in ['==', '!=', '<=', '>=']:
            if self._split_operator(expr, op):
                return
        
        for op in ['<', '>']:
            if self._split_operator(expr, op):
                return
        
        # Addition/Subtraction (check from right for left-associativity)
        if self._split_operator(expr, '+'):
            return
        if self._split_operator(expr, '-'):
            return
        
        # Multiplication/Division/Modulo
        if self._split_operator(expr, '*'):
            return
        if self._split_operator(expr, '/'):
            return
        if self._split_operator(expr, '%'):
            return
        
        # Unary operators
        if expr.startswith('-') and len(expr) > 1 and not expr[1].isdigit():
            self._compile_expression(expr[1:])
            self.code.append(Instruction(Operation.OPR, 0, 1))  # negate
            return
        
        # Parentheses
        if expr.startswith('(') and expr.endswith(')') and self._matching_paren(expr, 0) == len(expr) - 1:
            self._compile_expression(expr[1:-1])
            return
        
        # Operands (literals or variables)
        self._compile_operand(expr)
    
    def _matching_paren(self, expr: str, start: int) -> int:
        """Find matching closing parenthesis"""
        if expr[start] != '(':
            return -1
        depth = 0
        for i in range(start, len(expr)):
            if expr[i] == '(':
                depth += 1
            elif expr[i] == ')':
                depth -= 1
                if depth == 0:
                    return i
        return -1
    
    def _split_operator(self, expr: str, op: str) -> bool:
        """Try to split expression by operator, respecting precedence and parentheses"""
        # Search from right to left for left-associative operators
        depth = 0
        for i in range(len(expr) - 1, -1, -1):
            if expr[i] == ')':
                depth += 1
            elif expr[i] == '(':
                depth -= 1
            elif depth == 0 and i + len(op) <= len(expr) and expr[i:i+len(op)] == op:
                # Make sure it's not part of a larger operator
                if op in ['<', '>'] and i + 1 < len(expr) and expr[i+1] == '=':
                    continue
                if op == '=' and i > 0 and expr[i-1] in ['=', '!', '<', '>']:
                    continue
                if op == '=' and i + 1 < len(expr) and expr[i+1] == '=':
                    continue
                
                left = expr[:i].strip()
                right = expr[i+len(op):].strip()
                
                if left and right:  # Valid split
                    self._compile_expression(left)
                    self._compile_expression(right)
                    
                    # Map operator to OPR code
                    op_map = {
                        '+': 2, '-': 3, '*': 4, '/': 5, '%': 7,
                        '==': 8, '!=': 9, '<': 10, '>': 11, '<=': 12, '>=': 13,
                        '&&': 14, '||': 15
                    }
                    self.code.append(Instruction(Operation.OPR, 0, op_map[op]))
                    return True
        return False
    
    def _compile_operand(self, operand: str):
        """Compile literal or variable"""
        operand = operand.strip()
        
        # Check for negative literal
        if operand.startswith('-') and operand[1:].isdigit():
            value = int(operand)
            self.code.append(Instruction(Operation.LIT, 0, value))
            return
        
        # Check for literal number
        if operand.isdigit():
            value = int(operand)
            self.code.append(Instruction(Operation.LIT, 0, value))
        elif operand in self.symbol_table:
            # Variable - load its value
            var_address = self.symbol_table[operand]
            self.code.append(Instruction(Operation.LOD, 0, var_address))
        else:
            raise ValueError(f"Undeclared variable or invalid operand: {operand}")




def test_basic_arithmetic():
    print("=" * 60)
    print("TEST 1: Basic Arithmetic")
    print("=" * 60)
    
    program = """
    var x
    var y
    var z
    
    x = 10 + 5
    y = x * 2
    z = y - 3
    """
    
    compiler = Compiler()
    code = compiler.compile(program)
    
    print("\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"{i:3d}: {instr}")
    
    interpreter = PL0Interpreter(code)
    interpreter.run()
    
    print("\nResults:")
    for var_name, address in sorted(compiler.symbol_table.items()):
        print(f"  {var_name} = {interpreter.s[address]}")
    print(f"  Expected: x=15, y=30, z=27")


def test_comparisons():
    print("\n" + "=" * 60)
    print("TEST 2: Comparisons")
    print("=" * 60)
    
    program = """
    var a
    var b
    var result1
    var result2
    
    a = 10
    b = 5
    result1 = a > b
    result2 = a == b
    """
    
    compiler = Compiler()
    code = compiler.compile(program)
    
    print("\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"{i:3d}: {instr}")
    
    interpreter = PL0Interpreter(code)
    interpreter.run()
    
    print("\nResults:")
    for var_name, address in sorted(compiler.symbol_table.items()):
        print(f"  {var_name} = {interpreter.s[address]}")
    print(f"  Expected: a=10, b=5, result1=1 (true), result2=0 (false)")


def test_if_statement():
    print("\n" + "=" * 60)
    print("TEST 3: If Statement")
    print("=" * 60)
    
    program = """
    var x
    var result
    
    x = 10
    result = 0
    if x > 5 then result = 100
    """
    
    compiler = Compiler()
    code = compiler.compile(program)
    
    print("\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"{i:3d}: {instr}")
    
    interpreter = PL0Interpreter(code)
    interpreter.run()
    
    print("\nResults:")
    for var_name, address in sorted(compiler.symbol_table.items()):
        print(f"  {var_name} = {interpreter.s[address]}")
    print(f"  Expected: x=10, result=100")


def test_while_loop():
    print("\n" + "=" * 60)
    print("TEST 4: While Loop")
    print("=" * 60)
    
    program = """
    var counter
    var sum
    
    counter = 5
    sum = 0
    while counter > 0 do sum = sum + counter
    """
    
    compiler = Compiler()
    code = compiler.compile(program)
    
    print("\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"{i:3d}: {instr}")
    
    print("\nExecution trace:")
    interpreter = PL0Interpreter(code)
    interpreter.debug = True
    interpreter.run()
    
    print("\nResults:")
    for var_name, address in sorted(compiler.symbol_table.items()):
        print(f"  {var_name} = {interpreter.s[address]}")
    print(f"  Expected: counter=0, sum=15 (5+4+3+2+1)")


def test_factorial():
    print("\n" + "=" * 60)
    print("TEST 5: Factorial (manual code)")
    print("=" * 60)
    
    # Manual factorial code using documented instructions
    code = [
        # main: int n = 5, result
        Instruction(Operation.INT, 0, 2),    # allocate n and result
        Instruction(Operation.LIT, 0, 5),    # push 5
        Instruction(Operation.STO, 0, 3),    # n = 5
        Instruction(Operation.LOD, 0, 3),    # load n
        Instruction(Operation.CAL, 0, 7),    # call factorial
        Instruction(Operation.STO, 0, 4),    # result = factorial(n)
        Instruction(Operation.HLT, 0, 0),    # halt

        # factorial(n) @7
        Instruction(Operation.INT, 0, 3),    # allocate local n, result, temp
        Instruction(Operation.LOD, 1, 3),    # load parameter n
        Instruction(Operation.STO, 0, 3),    # store in local n
        Instruction(Operation.LIT, 0, 1),    # push 1
        Instruction(Operation.STO, 0, 4),    # result = 1

        # loop: while n > 1
        Instruction(Operation.LOD, 0, 3),    # load n
        Instruction(Operation.LIT, 0, 1),    # push 1
        Instruction(Operation.OPR, 0, 11),   # n > 1
        Instruction(Operation.JPC, 0, 25),   # if false, exit loop

        # result = result * n
        Instruction(Operation.LOD, 0, 4),    # load result
        Instruction(Operation.LOD, 0, 3),    # load n
        Instruction(Operation.OPR, 0, 4),    # multiply
        Instruction(Operation.STO, 0, 4),    # store result

        # n = n - 1
        Instruction(Operation.LOD, 0, 3),    # load n
        Instruction(Operation.LIT, 0, 1),    # push 1
        Instruction(Operation.OPR, 0, 3),    # subtract
        Instruction(Operation.STO, 0, 3),    # store n

        Instruction(Operation.JMP, 0, 12),   # jump to loop start

        # return result
        Instruction(Operation.LOD, 0, 4),    # load result
        Instruction(Operation.OPR, 0, 0),    # return
    ]
    
    print("\nManually created code:")
    for i, instr in enumerate(code):
        print(f"{i:3d}: {instr}")
    
    interpreter = PL0Interpreter(code)
    interpreter.run()
    
    print(f"\nResult: 5! = {interpreter.s[4]}")
    print(f"Expected: 120")


if __name__ == "__main__":
    test_basic_arithmetic()
    test_comparisons()
    test_if_statement()
    test_while_loop()
    test_factorial()
