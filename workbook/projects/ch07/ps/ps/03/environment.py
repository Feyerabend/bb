class Environment:
    def __init__(self):
        # Initialize with a global scope
        self.scopes = [{}]

    def define(self, name: str, value: any):
        """Define a variable, procedure, or dictionary in the current scope."""
        if isinstance(value, dict):
            # If the value is a dictionary, store it as a PostScript dictionary
            self.scopes[-1][name] = value
        elif callable(value):
            # If the value is callable (i.e., a procedure), it's a procedure
            self.scopes[-1][name] = value
        else:
            # Otherwise, it's a regular variable
            self.scopes[-1][name] = value

    def lookup(self, name: str) -> any:
        """Look up a variable, procedure, or dictionary by name."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Variable, procedure, or dictionary '{name}' not found")

    def invoke(self, name: str, *args):
        """Invoke a procedure by name with arguments."""
        try:
            proc = self.lookup(name)  # Look up the procedure
            if callable(proc):
                return proc(*args)
            else:
                raise TypeError(f"'{name}' is not a procedure")
        except NameError as e:
            raise NameError(f"Procedure '{name}' not found") from e

    def enter_scope(self):
        """Enter a new scope (e.g., for a new function call or nested dictionary)."""
        self.scopes.append({})

    def exit_scope(self):
        """Exit the current scope."""
        self.scopes.pop()

    def add_to_dict(self, dict_name: str, key: str, value: any):
        """Add a key-value pair to an existing dictionary."""
        dict_obj = self.lookup(dict_name)
        if isinstance(dict_obj, dict):
            dict_obj[key] = value
        else:
            raise TypeError(f"'{dict_name}' is not a dictionary")

    def lookup_in_dict(self, dict_name: str, key: str) -> any:
        """Look up a key in a dictionary defined in the environment."""
        dict_obj = self.lookup(dict_name)
        if isinstance(dict_obj, dict):
            if key in dict_obj:
                return dict_obj[key]
            else:
                raise KeyError(f"Key '{key}' not found in dictionary '{dict_name}'")
        else:
            raise TypeError(f"'{dict_name}' is not a dictionary")