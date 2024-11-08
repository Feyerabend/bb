# environment.py

class Environment:
    def __init__(self):
        self.dictionary_stack = [{}]

    def define(self, name, value):
        self.dictionary_stack[-1][name] = value

    def lookup(self, name):
        for d in reversed(self.dictionary_stack):
            if name in d:
                return d[name]
        raise NameError(f"Undefined name: {name}")

    def push_dict(self):
        self.dictionary_stack.append({})

    def pop_dict(self):
        if len(self.dictionary_stack) == 1:
            raise IndexError("Cannot pop the last dictionary")
        return self.dictionary_stack.pop()