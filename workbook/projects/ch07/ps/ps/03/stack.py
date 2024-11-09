class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value: any):
        print(f"[DEBUG] Pushing to stack: {value}")
        self.stack.append(value)

    def pop(self) -> any:
        if not self.stack:
            raise IndexError("Pop from empty stack")
        value = self.stack.pop()
        print(f"[DEBUG] Popping from stack: {value}")
        return value

    def peek(self) -> any:
        if not self.stack:
            raise IndexError("Peek from empty stack")
        value = self.stack[-1]
        print(f"[DEBUG] Peeking at stack: {value}")
        return value