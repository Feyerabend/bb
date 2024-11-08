# executor.py

class Executor:
    def __init__(self, stack, environment):
        self.stack = stack
        self.environment = environment

    def execute(self, tokens):
        for token in tokens:
            print(f"Processing token: {token}")
            if isinstance(token, int):
                self.stack.push(token)
                print(f"Stack after push: {self.stack.items}")
            elif token in ["add", "mul", "exch"]:
                self._apply_operator(token)
            else:
                self._define_name(token)
    
    def _apply_operator(self, operator):
        print(f"Applying operator: {operator}")
        if operator == "add":
            self._require_stack(2)
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a + b)
            print(f"Stack after add: {self.stack.items}")
        
        elif operator == "mul":
            self._require_stack(2)
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(a * b)
            print(f"Stack after mul: {self.stack.items}")

        elif operator == "exch":
            print(f"Stack before exch: {self.stack.items}")
            self._require_stack(2)
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.push(b)
            self.stack.push(a)
            print(f"Stack after exch: {self.stack.items}")

    def _require_stack(self, n):
        print(f"Checking stack size: {self.stack.size()} (need {n})")
        if self.stack.size() < n:
            raise IndexError(f"Insufficient values in the stack for operation requiring {n} values.")

    def _define_name(self, name):
        if name.startswith("/"):
            value = self.stack.pop()
            self.environment.define(name, value)
            print(f"Defining name: {name} with value {value}")
