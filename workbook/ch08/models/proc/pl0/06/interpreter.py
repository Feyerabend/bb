from enum import Enum, auto
from typing import List

class Operation(Enum):
    LIT = auto(); OPR = auto(); LOD = auto(); STO = auto()
    INT = auto(); JMP = auto(); JPC = auto(); CAL = auto()

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l
        self.a = a

class PL0Interpreter:
    def __init__(self, code: List[Instruction], stack_size=10000):
        self.code = code
        self.s = [0] * stack_size
        self.p = 0
        self.b = 1  # Base pointer
        self.t = 0  # Stack pointer
        self.debug = True

    def base(self, level: int) -> int:
        current_b = self.b
        while level > 0:
            current_b = self.s[current_b]
            level -= 1
        return current_b

    def run(self):
        # Initialize main frame
        self.t = 3
        self.s[1] = 0  # Static link
        self.s[2] = 0  # Dynamic link
        self.s[3] = len(self.code)  # Return address
        
        while self.p < len(self.code):
            i = self.code[self.p]
            if self.debug:
                current_n = self.s[self.base(0)+3]
                current_result = self.s[self.base(0)+4]
                print(f"[{self.p}] {i.op.name} {i.l} {i.a} | BP={self.b} SP={self.t} | n={current_n} result={current_result}")
            
            self.p += 1

            if i.op == Operation.LIT:
                self.t += 1
                self.s[self.t] = i.a

            elif i.op == Operation.OPR:
                if i.a == 0:  # Return
                    return_value = self.s[self.t]
                    self.t = self.b - 1
                    self.p = self.s[self.b + 2]
                    self.b = self.s[self.b + 1]
                    self.t += 1
                    self.s[self.t] = return_value
                else:
                    right = self.s[self.t]
                    self.t -= 1
                    left = self.s[self.t]
                    
                    if i.a == 3:  # Subtraction
                        self.s[self.t] = left - right
                    elif i.a == 4:  # Multiplication
                        self.s[self.t] = left * right
                    elif i.a == 12:  # Greater than
                        self.s[self.t] = int(left > right)

            elif i.op == Operation.LOD:
                addr = self.base(i.l) + i.a
                self.t += 1
                self.s[self.t] = self.s[addr]

            elif i.op == Operation.STO:
                addr = self.base(i.l) + i.a
                self.s[addr] = self.s[self.t]
                self.t -= 1

            elif i.op == Operation.INT:
                self.t += i.a

            elif i.op == Operation.JMP:
                self.p = i.a

            elif i.op == Operation.JPC:
                if self.s[self.t] == 0:
                    self.p = i.a
                self.t -= 1

            elif i.op == Operation.CAL:
                new_bp = self.t + 1
                self.s[new_bp] = self.base(i.l)
                self.s[new_bp + 1] = self.b
                self.s[new_bp + 2] = self.p
                self.b = new_bp
                self.t = new_bp + 2
                self.p = i.a

def test_factorial():
    code = [
        # main: int n = 5, result
        Instruction(Operation.INT, 0, 2),
        Instruction(Operation.LIT, 0, 5),
        Instruction(Operation.STO, 0, 3),  # n at address 4
        Instruction(Operation.LOD, 0, 3),  # Load n
        Instruction(Operation.CAL, 0, 7),  # Call factorial
        Instruction(Operation.STO, 0, 4),  # Store result at address 5
        Instruction(Operation.OPR, 0, 0),  # Halt
        
        # factorial(n) @7
        Instruction(Operation.INT, 0, 3),
        Instruction(Operation.LOD, 1, 3),  # Load parameter
        Instruction(Operation.STO, 0, 3),  # Store local n
        Instruction(Operation.LIT, 0, 1),  # Initialize result=1
        Instruction(Operation.STO, 0, 4),
        Instruction(Operation.LOD, 0, 3),  # Loop start
        Instruction(Operation.LIT, 0, 1),
        Instruction(Operation.OPR, 0, 12),  # n > 1?
        Instruction(Operation.JPC, 0, 25),  # Exit if false
        Instruction(Operation.LOD, 0, 4),  # result
        Instruction(Operation.LOD, 0, 3),  # n
        Instruction(Operation.OPR, 0, 4),  # Multiply
        Instruction(Operation.STO, 0, 4),  # Update result
        Instruction(Operation.LOD, 0, 3),  # n
        Instruction(Operation.LIT, 0, 1),  # 1
        Instruction(Operation.OPR, 0, 3),  # Subtract
        Instruction(Operation.STO, 0, 3),  # Update n
        Instruction(Operation.JMP, 0, 12),  # Loop back
        Instruction(Operation.LOD, 0, 4),  # Return result
        Instruction(Operation.OPR, 0, 0),  # Return
    ]
    
    interpreter = PL0Interpreter(code)
    interpreter.run()
    print(f"\nFinal result: 5! = {interpreter.s[5]}")

if __name__ == "__main__":
    print("Running factorial test:")
    test_factorial()