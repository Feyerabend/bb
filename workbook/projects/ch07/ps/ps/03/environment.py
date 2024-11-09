class Environment:
    def __init__(self):
        # Start with a global scope, which is an empty dictionary.
        self.scopes = [{}]  # Each scope is a dictionary of name-value pairs.

    def define(self, name: str, value: any):
        """Define a variable in the current scope."""
        self.scopes[-1][name] = value

    def lookup(self, name: str) -> any:
        """Look up a variable's value starting from the innermost scope."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Variable '{name}' not found.")

    def enter_scope(self):
        """Enter a new scope."""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise RuntimeError("Cannot exit global scope.")