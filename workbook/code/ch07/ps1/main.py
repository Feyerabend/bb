# main.py
from lexer import Lexer
from stack import Stack
from executor import Executor
from output_buffer import OutputBuffer

class InterpreterEngine:
    def __init__(self):
        self.stack = Stack()
        self.buffer = OutputBuffer(10, 10)  # Small buffer for demo
        self.executor = Executor(self.stack, self.buffer)

    def load_and_execute(self, code: str):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.executor.execute(tokens)
        self.buffer.display()

if __name__ == "__main__":
    # Example PostScript-like commands to test
    code = "2 3 setpixel 5 5 setpixel 4 4 add 0 setpixel"
    engine = InterpreterEngine()
    engine.load_and_execute(code)