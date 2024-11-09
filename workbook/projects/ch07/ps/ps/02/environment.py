
class Environment:
    def __init__(self):
        """Initialize the environment with a global scope."""
        self.scopes = [{}] # one global scope

    def define(self, name: str, value: any):
        """Define a variable in the current scope."""
        if value is None:
            raise TypeError("Cannot define a variable with a None value.")
        self.scopes[-1][name] = value

    def lookup(self, name: str) -> any:
        """Lookup a variable in the current scope or parent scopes."""
        for scope in reversed(self.scopes):  # search from innermost scope to outermost
            if name in scope:
                return scope[name]
        raise KeyError(f"Variable '{name}' not found.")

    def enter_scope(self):
        """Enter a new scope."""
        self.scopes.append({})  # a new empty scope

    def exit_scope(self):
        """Exit the current scope and discard its contents."""
        if len(self.scopes) == 1:
            raise RuntimeError("Cannot exit the global scope.")
        self.scopes.pop()  # remove current scope
