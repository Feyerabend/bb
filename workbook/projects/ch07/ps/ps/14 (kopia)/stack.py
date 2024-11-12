class Stack:
    def __init__(self):
        self.items = []

    def push(self, value: any):
        self.items.append(value)

    def pop(self) -> any:
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self) -> any:
        if not self.items:
            raise IndexError("peek from empty stack")
        return self.items[-1]

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)

    def clear(self):
        self.items.clear()

    def get_stack(self):
        return self.items  # items as a list

    def copy(self):
        new_stack = Stack()
        new_stack.items = self.items.copy() # built-in copy
        return new_stack.items

    def __repr__(self):
        return f"Stack({self.items})"

    def __contains__(self, item):
        return item in self.items
