from enum import Enum, auto
from typing import List

class Operation(Enum):
    LIT=auto(); OPR=auto(); LOD=auto(); STO=auto(); INT=auto(); JMP=auto(); JPC=auto()

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l
        self.a = a

class Interpreter:
    def __init__(self, code: List[Instruction]):
        self.code = code
        self.s = [0] * 1000
        self.p = 0
        self.b = 1
        self.t = 0
    
    def base(self, l: int) -> int:
        b = self.b
        while l > 0:
            b = self.s[b]
            l -= 1
        return b
    
    def run(self):
        self.s[1] = 0  # SL
        self.s[2] = 0  # DL
        self.s[3] = 0  # RA
        self.t = 3
        
        while self.p < len(self.code):
            i = self.code[self.p]
            self.p += 1
            
            if i.op == Operation.LIT:
                self.t += 1
                self.s[self.t] = i.a
            
            elif i.op == Operation.OPR:
                if i.a == 0:  # return
                    self.t = self.b - 1
                    self.p = self.s[self.t + 3]
                    self.b = self.s[self.t + 2]
                elif i.a == 1:  # load (dereference)
                    self.s[self.t] = self.s[self.s[self.t]]
                elif i.a == 2:  # add
                    self.t -= 1
                    self.s[self.t] += self.s[self.t + 1]
                elif i.a == 3:  # subtract
                    self.t -= 1
                    self.s[self.t] -= self.s[self.t + 1]
                elif i.a == 4:  # multiply
                    self.t -= 1
                    self.s[self.t] *= self.s[self.t + 1]
                elif i.a == 8:  # equal
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] == self.s[self.t + 1])
                elif i.a == 12: # greater than
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] > self.s[self.t + 1])
            
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

def test():

    code = [
        # allocate 2 variables (addresses 3 and 4)
        Instruction(Operation.INT, 0, 2),

        # x = 10
        Instruction(Operation.LIT, 0, 10),
        Instruction(Operation.STO, 0, 3),

        # y = (x * 3) - 5
        Instruction(Operation.LOD, 0, 3),  # load x
        Instruction(Operation.LIT, 0, 3),
        Instruction(Operation.OPR, 0, 4),  # multiply
        Instruction(Operation.LIT, 0, 5),
        Instruction(Operation.OPR, 0, 3),  # subtract
        Instruction(Operation.STO, 0, 4),  # store y (should be 25)
        
        # if y > 20 then x = x - 1 (not y!)
        Instruction(Operation.LOD, 0, 4),  # load y
        Instruction(Operation.LIT, 0, 20),
        Instruction(Operation.OPR, 0, 12), # greater than
        Instruction(Operation.JPC, 0, 19), # skip if false
        Instruction(Operation.LOD, 0, 3),  # load x
        Instruction(Operation.LIT, 0, 1),
        Instruction(Operation.OPR, 0, 3),  # subtract
        Instruction(Operation.STO, 0, 3),  # store x (now 9)
        
        # return
        Instruction(Operation.OPR, 0, 0)
    ]
    
    interpreter = Interpreter(code)
    interpreter.run()
    print(f"x = {interpreter.s[3]}, y = {interpreter.s[4]}")  # Output: x = 9, y = 25

if __name__ == "__main__":
    test()