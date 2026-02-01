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
        self.s = [0] * 1000
        self.p = 0
        self.b = 1
        self.t = 0
        self.debug = True

    def base(self, l: int) -> int:
        b = self.b
        while l > 0:
            b = self.s[b]
            l -= 1
        return b
    
    def run(self):
        self.t = 3
        self.s[1] = 0  # SL
        self.s[2] = 0  # DL
        self.s[3] = len(self.code)  # set main's RA to exit point

        while self.p < len(self.code):
            i = self.code[self.p]
            if self.debug:
                op_str = f"{i.op.name} {i.l} {i.a}".ljust(12)
                stack_preview = self.s[max(0, self.b-2):self.t+3]
                print(f"[{self.p}] {op_str} | BP={self.b} SP={self.t} RA={self.s[self.b+2]} STACK: {stack_preview}")
            
            self.p += 1

            if i.op == Operation.LIT:
                self.t += 1
                self.s[self.t] = i.a

            elif i.op == Operation.STO:
                addr = self.base(i.l) + i.a
                self.s[addr] = self.s[self.t]
                self.t -= 1
                if self.debug:
                    print(f"    Stored {self.s[addr]} at {addr}")

            elif i.op == Operation.LOD:
                addr = self.base(i.l) + i.a
                self.t += 1
                self.s[self.t] = self.s[addr]
                if self.debug:
                    print(f"    Loaded {self.s[self.t]} from {addr}")

            elif i.op == Operation.INT:
                self.t += i.a

            elif i.op == Operation.CAL:
                print(f"\n--> CALL to {i.a}: Param={self.s[self.t]}")
                new_bp = self.t + 1
                self.s[new_bp] = self.base(i.l)
                self.s[new_bp + 1] = self.b
                self.s[new_bp + 2] = self.p
                self.b = new_bp
                self.t = new_bp + 2
                print(f"    New BP={new_bp} SL={self.s[new_bp]} DL={self.s[new_bp+1]} RA={self.s[new_bp+2]}")
                self.p = i.a

            elif i.op == Operation.OPR:
                if i.a == 0:
                    return_value = self.s[self.t]
                    print(f"\n<-- RETURN: Value={return_value}")
                    self.t = self.b - 1
                    self.p = self.s[self.b + 2]
                    self.b = self.s[self.b + 1]
                    self.t += 1
                    self.s[self.t] = return_value
                    print(f"    Restored BP={self.b} SP={self.t} RA={self.p}")

                elif i.a == 2:
                    self.t -= 1
                    self.s[self.t] += self.s[self.t + 1]

                elif i.a == 4:
                    self.t -= 1
                    self.s[self.t] *= self.s[self.t + 1]

def test():
    code = [
        Instruction(Operation.INT, 0, 2),   # allocate space for 2 variables on the stack
        Instruction(Operation.LIT, 0, 10),  # push literal 10 onto the stack
        Instruction(Operation.STO, 0, 3),   # store the top of the stack (10) at address 3 (variable x)
        Instruction(Operation.LOD, 0, 3),   # load the value from address 3 (x) onto the stack
        Instruction(Operation.CAL, 0, 9),   # call the function at address 9 (square function)
        Instruction(Operation.LIT, 0, 1),   # push literal 1 onto the stack
        Instruction(Operation.OPR, 0, 2),   # add the top two values on the stack (result of square(x) + 1)
        Instruction(Operation.STO, 0, 4),   # store the result in address 4 (variable y)
        Instruction(Operation.OPR, 0, 0),   # return (end execution)

        # Square procedure (at address 9)
        Instruction(Operation.LOD, 1, 3),   # load the value of x (passed as parameter)
        Instruction(Operation.LOD, 1, 3),   # load the value of x again
        Instruction(Operation.OPR, 0, 4),   # multiply the top two values (x * x)
        Instruction(Operation.OPR, 0, 0)    # return the result
    ]
   
    interpreter = Interpreter(code)
    interpreter.run()
    print(f"Final state: x={interpreter.s[4]}, y={interpreter.s[5]}")

if __name__ == "__main__":
    test()
