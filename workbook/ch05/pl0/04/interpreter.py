from enum import Enum, auto
from typing import List

class Operation(Enum):
    LIT = auto()    # push literal value to stack
    OPR = auto()    # perform operation
    LOD = auto()    # load variable to stack
    STO = auto()    # store value from stack to variable
    INT = auto()    # increment stack pointer (allocate stack space)
    JMP = auto()    # unconditional jump
    JPC = auto()    # conditional jump
    CAL = auto()    # call procedure

class Instruction:
    def __init__(self, op: Operation, l: int, a: int):
        self.op = op
        self.l = l  # lexicographical level
        self.a = a  # argument/address

class Interpreter:
    def __init__(self, code: List[Instruction], debug: bool = False):
        self.code = code
        self.s = [0] * 1000  # stack
        self.p = 0           # program counter
        self.b = 1           # base pointer
        self.t = 0           # top of stack pointer
        self.debug = debug

    def base(self, l: int) -> int:
        b = self.b
        while l > 0:
            b = self.s[b]
            l -= 1
        return b
    
    def print_debug(self, msg: str):
        if self.debug:
            print(msg)
            print(f"Stack: {self.s[1:self.t+1]}")
            print(f"P: {self.p-1}, B: {self.b}, T: {self.t}\n")
    
    def run(self):
        # init stack frame
        self.s[1] = 0  # Static Link (SL)
        self.s[2] = 0  # Dynamic Link (DL)
        self.s[3] = 0  # Return Address (RA)
        self.t = 3     # top of stack
        
        while self.p < len(self.code):
            i = self.code[self.p]
            
            if self.debug:
                print(f"Executing instruction {self.p}: {i.op}, l={i.l}, a={i.a}")
            
            self.p += 1
            
            if i.op == Operation.LIT:
                # push literal value to stack
                self.t += 1
                self.s[self.t] = i.a
            
            elif i.op == Operation.OPR:
                if i.a == 0:  # return from procedure
                    self.t = self.b - 1
                    self.p = self.s[self.t + 3]
                    self.b = self.s[self.t + 2]
                elif i.a == 1:  # negate
                    self.s[self.t] = -self.s[self.t]
                elif i.a == 2:  # add
                    self.t -= 1
                    self.s[self.t] += self.s[self.t + 1]
                elif i.a == 3:  # subtract
                    self.t -= 1
                    self.s[self.t] -= self.s[self.t + 1]
                elif i.a == 4:  # multiply
                    self.t -= 1
                    self.s[self.t] *= self.s[self.t + 1]
                elif i.a == 5:  # divide
                    self.t -= 1
                    if self.s[self.t + 1] == 0:
                        raise ValueError("Division by zero")
                    self.s[self.t] //= self.s[self.t + 1]
                elif i.a == 6:  # modulo
                    self.t -= 1
                    self.s[self.t] %= self.s[self.t + 1]
                elif i.a == 7:  # equal
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] == self.s[self.t + 1])
                elif i.a == 8:  # not equal
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] != self.s[self.t + 1])
                elif i.a == 9:  # less than
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] < self.s[self.t + 1])
                elif i.a == 10:  # greater than or equal
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] >= self.s[self.t + 1])
                elif i.a == 11:  # greater than
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] > self.s[self.t + 1])
                elif i.a == 12:  # less than or equal
                    self.t -= 1
                    self.s[self.t] = int(self.s[self.t] <= self.s[self.t + 1])

            elif i.op == Operation.LOD:
                # load value from variable
                self.t += 1
                self.s[self.t] = self.s[self.base(i.l) + i.a]

            elif i.op == Operation.STO:
                # store value to variable
                self.s[self.base(i.l) + i.a] = self.s[self.t]
                self.t -= 1

            elif i.op == Operation.INT:
                # allocate stack space
                self.t += i.a

            elif i.op == Operation.JMP:
                # unconditional jump
                self.p = i.a
            
            elif i.op == Operation.JPC:
                # conditional jump (pop stack and jump if 0)
                if self.s[self.t] == 0:
                    self.p = i.a
                self.t -= 1
            
            elif i.op == Operation.CAL:
                # call procedure
                # push new stack frame
                self.s[self.t + 1] = self.base(i.l)  # Static Link (SL)
                self.s[self.t + 2] = self.b          # Dynamic Link (DL)
                self.s[self.t + 3] = self.p          # Return Address (RA)
                self.b = self.t + 1                  # new base
                self.p = i.a                         # jump to procedure
                self.t += 3

def test():

    code = [
        # allocate variables
        Instruction(Operation.INT, 0, 3),
        
        # a = 0
        Instruction(Operation.LIT, 0, 0),
        Instruction(Operation.STO, 0, 3),
        
        # b = 15
        Instruction(Operation.LIT, 0, 15),
        Instruction(Operation.STO, 0, 4),
        
        # call max(a, b)
        Instruction(Operation.LOD, 0, 3),  # push a
        Instruction(Operation.LOD, 0, 4),  # push b
        Instruction(Operation.CAL, 1, 30), # call max procedure
        Instruction(Operation.STO, 0, 5),  # store result in c
        
        # return from main
        Instruction(Operation.OPR, 0, 0),
        
        # procedure max (address 30)
        Instruction(Operation.INT, 0, 1),  # allocate local space
        
        # compare a with b
        Instruction(Operation.LOD, 1, 3),  # load first param
        Instruction(Operation.LOD, 1, 4),  # load second param
        Instruction(Operation.OPR, 0, 9),  # less Than comparison
        
        # conditional jump if not less (jump to return b)
        Instruction(Operation.JPC, 0, 42), 
        
        # return a (if a < b)
        Instruction(Operation.LOD, 1, 3),
        Instruction(Operation.OPR, 0, 0),
        
        # return b (address 42)
        Instruction(Operation.LOD, 1, 4),
        Instruction(Operation.OPR, 0, 0)
    ]
    
    interpreter = Interpreter(code)
    interpreter.run()
    print(f"a = {interpreter.s[3]}, b = {interpreter.s[4]}, c = {interpreter.s[5]}")
    # Output: a = 0, b = 15, c = 15

if __name__ == "__main__":
    test()
