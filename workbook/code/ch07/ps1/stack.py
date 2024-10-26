# stack.py
class Stack:
    def __init__(self):
        self.items = []

    def push(self, value: any):
        self.items.append(value)

    def pop(self) -> any:
        if not self.items:
            raise IndexError("Attempted to pop from an empty stack")
        return self.items.pop()

    def peek(self) -> any:
        if not self.items:
            return None
        return self.items[-1]