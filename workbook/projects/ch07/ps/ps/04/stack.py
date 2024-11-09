class Stack:
    def __init__(self):
        # The stack will hold items of any type.
        self.items = []

    def push(self, value: any):
        """Push an item onto the stack."""
        self.items.append(value)

    def pop(self) -> any:
        """Pop an item from the stack and return it. Raise IndexError if the stack is empty."""
        if not self.items:
            raise IndexError("pop from empty stack")
        return self.items.pop()

    def peek(self) -> any:
        """Return the top item of the stack without removing it. Raise IndexError if empty."""
        if not self.items:
            raise IndexError("peek from empty stack")
        return self.items[-1]

    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self.items) == 0

    def size(self) -> int:
        """Return the size of the stack."""
        return len(self.items)

    def clear(self):
        """Clear the stack."""
        self.items.clear()

    def __repr__(self):
        """Return a string representation of the stack."""
        return f"Stack({self.items})"

    def __contains__(self, item):
        """Check if an item is in the stack."""
        return item in self.items
