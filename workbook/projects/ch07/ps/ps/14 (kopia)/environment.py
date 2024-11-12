
class Environment:
    def __init__(self):
        self.scopes = [{}] # one global scope

    def define_procedure(self, name: str, value: any):
        self.define(name, any)

    def define_variable(self, name: str, value: any):
        self.define(name, any)

    def define(self, name: str, value: any):
        if value is None:
            raise TypeError("Cannot define a variable with a None value.")
        self.scopes[-1][name] = value

    def lookup(self, name: str) -> any:
        for scope in reversed(self.scopes):  # search from innermost scope to outermost
            if name in scope:
                return scope[name]
        raise KeyError(f"Variable '{name}' not found.")

    def enter_scope(self):
        self.scopes.append({})  # a new empty scope

    def exit_scope(self):
        if len(self.scopes) == 1:
            raise RuntimeError("Cannot exit the global scope.")
        self.scopes.pop()  # remove current scope
