from enum import Enum, auto
from typing import List

class Operation(Enum):
    LIT=auto(); OPR=auto(); STO=auto(); INT=auto()

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l
        self.a = a

class Interpreter:
    def __init__(self, code: List[Instruction]):
        self.code = code
        self.s = [0] * 10  # Tiny stack for testing
        self.p = 0  # Program counter
        self.b = 0  # Base pointer
        self.t = -1 # Stack pointer
    
    def run(self):
        # Initialize stack frame
        self.t = 2
        self.s[0] = 0  # SL
        self.s[1] = 0  # DL
        self.s[2] = 0  # RA
        
        while self.p < len(self.code):
            i = self.code[self.p]
            self.p += 1
            
            if i.op == Operation.LIT:
                self.t += 1
                self.s[self.t] = i.a
            
            elif i.op == Operation.OPR:
                if i.a == 0:  # Return
                    break
                elif i.a == 2:  # Add
                    self.s[self.t-1] += self.s[self.t]
                    self.t -= 1
            
            elif i.op == Operation.STO:
                self.s[i.a] = self.s[self.t]  # Direct addressing
                self.t -= 1
            
            elif i.op == Operation.INT:
                self.t += i.a

def test():
    # Simple program: x = 3 + 5 (store at address 3)
    code = [
        Instruction(Operation.INT, 0, 1),  # Allocate space
        Instruction(Operation.LIT, 0, 3),
        Instruction(Operation.LIT, 0, 5),
        Instruction(Operation.OPR, 0, 2),  # Add
        Instruction(Operation.STO, 0, 3),  # Store at 3
        Instruction(Operation.OPR, 0, 0)   # Return
    ]
    
    interpreter = Interpreter(code)
    interpreter.run()
    print("X =", interpreter.s[3])  # Will print "X = 8"

if __name__ == "__main__":
    test()