class LispError(Exception):
    """Custom exception for Lisp interpreter errors."""
    pass


class Environment:
    """Represents an environment for variable bindings."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
        # Keep a reference to the global environment for faster lookups
        if parent is None:
            self.global_env = self
        else:
            self.global_env = parent.global_env if hasattr(parent, 'global_env') else parent

    def set(self, name, value):
        """Set a variable in the current environment."""
        if not isinstance(name, str):
            raise LispError(f"Variable name must be a string: {name}")
        self.bindings[name] = value

    def get(self, name):
        """Get a variable from the current environment or its parent."""
        if not isinstance(name, str):
            raise LispError(f"Variable name must be a string: {name}")
        
        # First, check built-in functions in global environment
        if name in ('+', '-', '*', '/', '=', '<', '>', 'remainder', 'and', 'or', 'not'):
            if name in self.global_env.bindings:
                return self.global_env.bindings[name]
        
        # Then check local environment
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise LispError(f"Undefined variable: {name}")


class Lisp:
    """Represents a simple Lisp interpreter."""
    def __init__(self):
        self.env = Environment()  # global environment
        self._initialize_builtins()  # init built-in functions

    def _initialize_builtins(self):
        """Initialize built-in functions and special forms."""
        # Arithmetic operations
        self.env.set('+', self._add)
        self.env.set('-', self._subtract)
        self.env.set('*', self._multiply)
        self.env.set('/', self._divide)
        self.env.set('=', self._equal)
        self.env.set('<', self._less_than)
        self.env.set('>', self._greater_than)
        self.env.set('remainder', self._remainder)
        
        # Boolean operations
        self.env.set('and', self._and)
        self.env.set('or', self._or)
        self.env.set('not', self._not)
        
        # Constants
        self.env.set('true', True)
        self.env.set('false', False)
        self.env.set('nil', None)

    # Arithmetic operations
    def _add(self, args):
        if not args:
            return 0
        return sum(args)

    def _subtract(self, args):
        if not args:
            raise LispError("Subtraction requires at least one argument")
        if len(args) == 1:
            return -args[0]
        return args[0] - sum(args[1:])

    def _multiply(self, args):
        if not args:
            return 1
        product = 1
        for arg in args:
            product *= arg
        return product

    def _divide(self, args):
        if not args:
            raise LispError("Division requires at least one argument")
        if len(args) == 1:
            return 1 / args[0]
        
        result = args[0]
        for arg in args[1:]:
            if arg == 0:
                raise LispError("Division by zero.")
            result /= arg
        return result
    
    def _remainder(self, args):
        if len(args) != 2:
            raise LispError("Remainder requires exactly two arguments")
        if args[1] == 0:
            raise LispError("Division by zero in remainder")
        return args[0] % args[1]
    
    # Comparison operations
    def _equal(self, args):
        if len(args) != 2:
            raise LispError("Equality comparison requires exactly two arguments")
        return args[0] == args[1]
    
    def _less_than(self, args):
        if len(args) != 2:
            raise LispError("Less than comparison requires exactly two arguments")
        return args[0] < args[1]
    
    def _greater_than(self, args):
        if len(args) != 2:
            raise LispError("Greater than comparison requires exactly two arguments")
        return args[0] > args[1]
    
    # Boolean operations
    def _and(self, args):
        result = True
        for arg in args:
            if not arg:
                return False
            result = arg
        return result
    
    def _or(self, args):
        for arg in args:
            if arg:
                return arg
        return False
    
    def _not(self, args):
        if len(args) != 1:
            raise LispError("Not operation requires exactly one argument")
        return not args[0]

    def eval(self, expr, env=None):
        """Evaluate an expression."""
        if env is None:
            env = self.env
            
        # Handle literals
        if isinstance(expr, (int, float, bool)) or expr is None:
            return expr
        elif isinstance(expr, str):  # variable reference
            return env.get(expr)
        elif not isinstance(expr, list):  # invalid expression
            raise LispError(f"Invalid expression type: {type(expr)}")
        elif not expr:  # empty list
            return None
            
        # Handle special forms
        first = expr[0]
        
        if first == 'define':
            return self._eval_define(expr, env)
        elif first == 'lambda':
            return self._eval_lambda(expr, env)
        elif first == 'if':
            return self._eval_if(expr, env)
        elif first == 'quote':
            if len(expr) != 2:
                raise LispError("Quote requires exactly one argument")
            return expr[1]
        elif first == 'begin':
            return self._eval_begin(expr, env)
        elif first == 'cond':
            return self._eval_cond(expr, env)
        else:
            # Function application
            func = self.eval(first, env)
            if callable(func) and not isinstance(func, tuple):
                evaluated_args = [self.eval(arg, env) for arg in expr[1:]]
                return func(evaluated_args)
            elif isinstance(func, tuple):
                params, body, closure_env = func
                if len(params) != len(expr[1:]):
                    raise LispError(f"Function expected {len(params)} arguments, got {len(expr[1:])}")
                new_env = Environment(closure_env)
                for param, arg in zip(params, expr[1:]):
                    new_env.set(param, self.eval(arg, env))
                return self.eval(body, new_env)
            else:
                raise LispError(f"Not a function: {func}")

    def _eval_define(self, expr, env):
        """Evaluate a define expression."""
        if len(expr) != 3:
            raise LispError("Define requires exactly two arguments: name and value")
        _, name, value = expr
        if isinstance(value, list) and len(value) >= 3 and value[0] == 'lambda':
            _, params, body = value
            # Create a lambda and store it directly
            func = (params, body, env)
            # Store in current environment to allow recursion
            env.set(name, func)
        else:
            env.set(name, self.eval(value, env))
        return None

    def _eval_lambda(self, expr, env):
        """Evaluate a lambda expression."""
        if len(expr) != 3:
            raise LispError("Lambda requires parameters and body")
        _, params, body = expr
        if not isinstance(params, list):
            raise LispError("Lambda parameters must be a list")
        return (params, body, env)

    def _eval_if(self, expr, env):
        """Evaluate an if expression."""
        if len(expr) < 3 or len(expr) > 4:
            raise LispError("If requires a condition, then-expr, and optional else-expr")
        _, condition, then_expr = expr[:3]
        else_expr = expr[3] if len(expr) > 3 else None
        if self.eval(condition, env):
            return self.eval(then_expr, env)
        elif else_expr:
            return self.eval(else_expr, env)
        else:
            return None

    def _eval_begin(self, expr, env):
        """Evaluate a begin expression, returning the last result."""
        if len(expr) == 1:
            return None
        result = None
        for sub_expr in expr[1:]:
            result = self.eval(sub_expr, env)
        return result
    
    def _eval_cond(self, expr, env):
        """Evaluate a cond expression."""
        if len(expr) < 2:
            raise LispError("Cond requires at least one clause")
        for clause in expr[1:]:
            if not isinstance(clause, list) or len(clause) < 2:
                raise LispError("Each cond clause must be a list with at least a test and an expression")
            test, result_expr = clause[0], clause[1]
            if test == 'else':
                return self.eval(result_expr, env)
            if self.eval(test, env):
                return self.eval(result_expr, env)
        return None

    def parse(self, program):
        """Parse a string into a Lisp expression."""
        tokens = self._tokenize(program)
        return self._read_from_tokens(tokens)

    def _tokenize(self, program):
        """Convert a string into a list of tokens."""
        program = program.replace('(', ' ( ').replace(')', ' ) ').replace("'", " ' ")
        return program.split()

    def _read_from_tokens(self, tokens):
        """Read an expression from a sequence of tokens."""
        if not tokens:
            raise LispError("Unexpected EOF")
        token = tokens.pop(0)
        if token == '(':
            lst = []
            while tokens and tokens[0] != ')':
                lst.append(self._read_from_tokens(tokens))
            if not tokens:
                raise LispError("Missing closing parenthesis")
            tokens.pop(0)  # remove ')'
            return lst
        elif token == ')':
            raise LispError("Unexpected closing parenthesis")
        elif token == "'":  # Quote
            return ['quote', self._read_from_tokens(tokens)]
        else:
            return self._atom(token)

    def _atom(self, token):
        """Convert a token to an atom."""
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return token

    def run(self, program):
        """Parse and evaluate a program string."""
        return self.eval(self.parse(program))


# Example usage
if __name__ == '__main__':
    lisp = Lisp()

    # Test parsing and evaluation
    print("Basic arithmetic:")
    print(lisp.run("(+ 3 4)"))  # 7
    print(lisp.run("(* 3 (+ 2 3))"))  # 15

    # Function definition and calling
    print("\nFunction definitions:")
    lisp.run("(define square (lambda (x) (* x x)))")
    print("square function defined")
    print("Result of (square 5):", lisp.run("(square 5)"))  # 25

    # Simple conditional
    print("\nConditionals:")
    print("(if (= 1 1) 'true 'false):", lisp.run("(if (= 1 1) 'true 'false)"))  # true

    # Define and test a function with conditionals
    print("\nFunctions with conditionals:")
    lisp.run("""
    (define abs 
      (lambda (x) 
        (if (< x 0) 
            (- 0 x) 
            x)))
    """)
    print("abs function defined")
    print("(abs -5):", lisp.run("(abs -5)"))  # 5
    print("(abs 5):", lisp.run("(abs 5)"))    # 5

    # Higher-order functions
    print("\nHigher-order functions:")
    lisp.run("""
    (define make-adder 
      (lambda (n) 
        (lambda (x) (+ x n))))
    """)
    print("make-adder function defined")
    lisp.run("(define add-five (make-adder 5))")
    print("add-five function defined")
    print("(add-five 10):", lisp.run("(add-five 10)"))  # 15

    # Recursion
    print("\nRecursion - Factorial:")
    lisp.run("""
    (define factorial 
      (lambda (n)
        (if (= n 0)
            1
            (* n (factorial (- n 1))))))
    """)
    print("factorial function defined")
    print("(factorial 5):", lisp.run("(factorial 5)"))  # 120

    # Multiple expressions with begin
    print("\nBegin (multiple expressions):")
    result = lisp.run("""
    (begin
      (define x 10)
      (define y 20)
      (+ x y))
    """)
    print("Result of sequence:", result)  # 30
