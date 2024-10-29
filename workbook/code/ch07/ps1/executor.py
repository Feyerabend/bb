# executor.py
from stack import Stack
from output_buffer import OutputBuffer
from lexer import Token

class Executor:
    def __init__(self, stack: Stack, buffer: OutputBuffer):
        self.stack = stack
        self.buffer = buffer

    def execute(self, tokens: list[Token]):
        for token in tokens:
            print(f"Executing token: {token.type} {token.value}")  # Debug statement

            if token.type == "number":
                self.stack.push(token.value)
                print(f"Stack after push: {self.stack.items}")  # Debug statement

            elif token.type == "operator":

                if token.value == "add":
                    if len(self.stack.items) < 2:
                        print("Error: Not enough values on the stack for 'add'")
                        continue
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a + b)
                    print(f"Stack after add: {self.stack.items}")  # Debug statement

                elif token.value == "sub":
                    if len(self.stack.items) < 2:
                        print("Error: Not enough values on the stack for 'sub'")
                        continue
                    b = self.stack.pop()
                    a = self.stack.pop()
                    self.stack.push(a - b)
                    print(f"Stack after sub: {self.stack.items}")  # Debug statement

                elif token.value == "setpixel":
                    if len(self.stack.items) < 2:
                        print("Error: Not enough values on the stack for 'setpixel'")
                        continue
                    y = self.stack.pop()
                    x = self.stack.pop()
                    print(f"Setting pixel at ({x}, {y})")  # Debug statement
                    if isinstance(x, int) and isinstance(y, int):  # Ensure x and y are integers
                        self.buffer.set_pixel(x, y, (255, 0, 0))  # Set to red

                    else:
                        print("Error: setpixel expects two integers")

                else:
                    print(f"Unknown operator '{token.value}' encountered.")

            else:
                print(f"Warning: Unknown token '{token.value}' encountered.")