class LispError(Exception):
    """Custom exception for Lisp interpreter errors."""
    pass

class Environment:
    """Represents an environment for variable bindings."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def set(self, name, value):
        """Set a variable in the current environment."""
        self.bindings[name] = value

    def get(self, name):
        """Get a variable from the current environment or its parent."""
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise LispError(f"Undefined variable: {name}")

class Lisp:
    """Represents a simple Lisp interpreter."""
    def __init__(self):
        self.env = Environment()  # Global environment
        self._initialize_builtins()  # Initialize built-in functions

    def _initialize_builtins(self):
        """Initialize built-in functions."""
        self.env.set('+', self._add)
        self.env.set('-', self._subtract)
        self.env.set('*', self._multiply)
        self.env.set('/', self._divide)

    def _add(self, args):
        return sum(self.eval(arg) for arg in args)

    def _subtract(self, args):
        return self.eval(args[0]) - sum(self.eval(arg) for arg in args[1:])

    def _multiply(self, args):
        product = 1
        for arg in args:
            product *= self.eval(arg)
        return product

    def _divide(self, args):
        if len(args) == 0:
            raise LispError("Division by zero.")
        result = self.eval(args[0])
        for arg in args[1:]:
            result /= self.eval(arg)
        return result

    def eval(self, expr, env=None):
        """Evaluate an expression."""
        if env is None:
            env = self.env
        if isinstance(expr, int) or isinstance(expr, float):  # Numeric literals
            return expr
        elif isinstance(expr, str):  # Variable
            return env.get(expr)
        elif isinstance(expr, list):  # List represents an expression
            if expr[0] == 'define':  # Define a new variable or function
                return self.eval_define(expr, env)
            elif expr[0] == 'lambda':  # Create a function
                return self.eval_lambda(expr)
            else:
                func = self.eval(expr[0], env)  # Evaluate the function
                args = [self.eval(arg, env) for arg in expr[1:]]  # Evaluate the arguments
                return self.apply(func, args)  # Apply the function to arguments
        raise LispError(f"Unknown expression: {expr}")

    def eval_define(self, expr, env):
        """Evaluate a define expression."""
        _, name, value = expr
        env.set(name, self.eval(value, env))  # Bind the value in the given environment
        return None

    def eval_lambda(self, expr):
        """Evaluate a lambda expression."""
        _, params, body = expr
        return (params, body, self.env)  # Return a tuple representing the closure

    def apply(self, func, args):
        """Apply a function to given arguments."""
        if isinstance(func, tuple):  # Check if it's a closure
            params, body, closure_env = func
            new_env = Environment(closure_env)
            for param, arg in zip(params, args):
                new_env.set(param, arg)
            return self.eval(body, new_env)  # Evaluate the function body in the new environment
        else:
            return func(args)  # Call built-in functions

# Example Usage
if __name__ == '__main__':
    lisp = Lisp()

    # Define a simple function
    lisp.eval(['define', 'add', ['lambda', ['x', 'y'], ['+', 'x', 'y']]])

    # Call the add function
    result = lisp.eval(['add', 3, 5])
    print(f"3 + 5 = {result}")  # Output: 3 + 5 = 8

    # Define a function that adds 10 to its input
    lisp.eval(['define', 'add_ten', ['lambda', ['x'], ['+', 'x', 10]]])

    # Call the add_ten function
    result = lisp.eval(['add_ten', 5])
    print(f"5 + 10 = {result}")  # Output: 5 + 10 = 15