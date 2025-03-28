from enum import Enum, auto
from typing import List

class Operation(Enum):
    LIT=auto(); OPR=auto(); LOD=auto(); STO=auto(); INT=auto(); JMP=auto(); JPC=auto(); CAL=auto()

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l
        self.a = a

class Interpreter:
    def __init__(self, code: List[Instruction]):
        self.code = code
        self.s = [0] * 1000  # Stack
        self.p = 0           # Program counter
        self.b = 1           # Base pointer
        self.t = 0           # Stack pointer
    
    def base(self, l: int) -> int:
        b = self.b
        while l > 0:
            b = self.s[b]
            l -= 1
        return b
    
    def run(self):
        # Initialize main program frame
        self.s[1] = 0  # Static Link (SL)
        self.s[2] = 0  # Dynamic Link (DL)
        self.s[3] = 0  # Return Address (RA)
        self.t = 3      # Stack pointer
        
        while self.p < len(self.code):
            i = self.code[self.p]
            self.p += 1
            
            if i.op == Operation.LIT:
                self.t += 1
                self.s[self.t] = i.a
            
            elif i.op == Operation.OPR:
                if i.a == 0:  # Return
                    self.t = self.b - 1
                    self.p = self.s[self.t + 3]
                    self.b = self.s[self.t + 2]
                elif i.a == 2:  # Add
                    self.t -= 1
                    self.s[self.t] += self.s[self.t + 1]
                elif i.a == 3:  # Subtract
                    self.t -= 1
                    self.s[self.t] -= self.s[self.t + 1]
                elif i.a == 4:  # Multiply
                    self.t -= 1
                    self.s[self.t] *= self.s[self.t + 1]
            
            elif i.op == Operation.LOD:
                self.t += 1
                self.s[self.t] = self.s[self.base(i.l) + i.a]
            
            elif i.op == Operation.STO:
                self.s[self.base(i.l) + i.a] = self.s[self.t]
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
                # Push new stack frame
                self.s[self.t + 1] = self.base(i.l)  # SL
                self.s[self.t + 2] = self.b          # DL
                self.s[self.t + 3] = self.p          # RA
                self.b = self.t + 1                  # New base
                self.p = i.a                         # Jump to procedure
                self.t += 3

def test():
    # Main program with procedure call
    code = [
        # Allocate 2 variables (x at 3, y at 4)
        Instruction(Operation.INT, 0, 2),
        
        # x = 10
        Instruction(Operation.LIT, 0, 10),
        Instruction(Operation.STO, 0, 3),
        
        # CALL double(x)
        Instruction(Operation.LOD, 0, 3),  # Load x
        Instruction(Operation.CAL, 1, 14), # Call procedure at address 14
        Instruction(Operation.STO, 0, 4),  # Store result in y
        
        # Return
        Instruction(Operation.OPR, 0, 0),
        
        # Procedure double (address 14)
        Instruction(Operation.INT, 0, 1),  # Allocate 1 local
        
        # double = param * 2
        Instruction(Operation.LOD, 1, 3),  # Load parameter (at SL+3)
        Instruction(Operation.LIT, 0, 2),
        Instruction(Operation.OPR, 0, 4),  # Multiply
        
        # Return result
        Instruction(Operation.OPR, 0, 0)
    ]
    
    interpreter = Interpreter(code)
    interpreter.run()
    print(f"x = {interpreter.s[3]}, y = {interpreter.s[4]}")  # Should print x=10, y=20

if __name__ == "__main__":
    test()