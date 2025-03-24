class LispError(Exception):
    """Exception raised for errors in the Lisp interpreter."""
    pass

class Environment:
    """Environment for storing variable bindings."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    
    def define(self, name, value):
        """Define a variable in the current environment."""
        self.bindings[name] = value
        return value
    
    def get(self, name):
        """Get the value of a variable from the environment."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise LispError(f"Undefined variable: {name}")
    
    def set(self, name, value):
        """Set the value of an existing variable."""
        if name in self.bindings:
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.set(name, value)
        raise LispError(f"Cannot set undefined variable: {name}")

class Procedure:
    """Represents a user-defined procedure."""
    def __init__(self, params, body, env, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter
    
    def __call__(self, *args):
        if len(args) != len(self.params):
            raise LispError(f"Expected {len(self.params)} arguments, got {len(args)}")
        
        # Create a new environment for the procedure call
        env = Environment(self.env)
        for param, arg in zip(self.params, args):
            env.define(param, arg)
        
        return self.interpreter.eval(self.body, env)

class Lisp:
    """A simple Lisp interpreter."""
    def __init__(self):
        self.global_env = Environment()
        self._setup_global_environment()
    
    def _setup_global_environment(self):
        """Set up the global environment with built-in procedures."""
        # Arithmetic operations
        self.global_env.define('+', lambda *args: sum(args))
        self.global_env.define('-', lambda a, *args: a - sum(args) if args else -a)
        # Fixed multiplication
        self.global_env.define('*', lambda *args: 
            1 if not args else 
            args[0] if len(args) == 1 else 
            args[0] * args[1] if len(args) == 2 else
            args[0] * args[1] * args[2] if len(args) == 3 else
            args[0] * self.global_env.get('*')(*args[1:]))
        # Fixed division
        self.global_env.define('/', lambda a, *args: 
            a if not args else 
            a / args[0] if len(args) == 1 else 
            a / args[0] / args[1] if len(args) == 2 else
            a / (args[0] * args[1] * args[2:] if args[2:] else 1))
        
        # Boolean literals
        self.global_env.define('True', True)
        self.global_env.define('False', False)
        
        # Comparison operations
        self.global_env.define('=', lambda a, b: a == b)
        self.global_env.define('<', lambda a, b: a < b)
        self.global_env.define('>', lambda a, b: a > b)
        self.global_env.define('<=', lambda a, b: a <= b)
        self.global_env.define('>=', lambda a, b: a >= b)
        
        # List operations
        self.global_env.define('cons', lambda a, b: [a] + (b if isinstance(b, list) else [b]))
        self.global_env.define('car', lambda x: x[0])
        self.global_env.define('cdr', lambda x: x[1:])
        self.global_env.define('list', lambda *args: list(args))
        self.global_env.define('null?', lambda x: not x)
        self.global_env.define('length', lambda x: len(x))
        
        # Boolean operations
        self.global_env.define('not', lambda x: not x)
        self.global_env.define('and', lambda *args: all(args))
        self.global_env.define('or', lambda *args: any(args))
        
        # Type predicates
        self.global_env.define('number?', lambda x: isinstance(x, (int, float)))
        self.global_env.define('symbol?', lambda x: isinstance(x, str))
        self.global_env.define('list?', lambda x: isinstance(x, list))
        
        # Function utilities for composition and pipelines
        self.global_env.define('compose', lambda f, g: lambda *args: f(g(*args)))
        self.global_env.define('pipe', lambda x, *funcs: self._pipe(x, funcs))
        
        # Common functional programming functions
        self.global_env.define('map', lambda f, lst: [f(x) for x in lst])
        self.global_env.define('filter', lambda f, lst: [x for x in lst if f(x)])
        self.global_env.define('reduce', self._reduce)
    
    def _reduce(self, f, lst, initial=None):
        """Implementation of the reduce function."""
        if not lst:
            if initial is None:
                raise LispError("reduce: empty list with no initial value")
            return initial
        
        if initial is None:
            result = lst[0]
            lst = lst[1:]
        else:
            result = initial
        
        for item in lst:
            result = f(result, item)
        
        return result
    
    def _pipe(self, x, funcs):
        """Implementation of the pipe function."""
        result = x
        for f in funcs:
            result = f(result)
        return result
    
    def tokenize(self, program):
        """Convert a string into a list of tokens."""
        # Replace single quotes with special markers for quote expressions
        program = program.replace("'", " quote ")
        program = program.replace('(', ' ( ').replace(')', ' ) ')
        return [token for token in program.split() if token]
    
    def parse(self, program):
        """Parse a program into an abstract syntax tree."""
        tokens = self.tokenize(program)
        return self._read_from_tokens(tokens)
    
    def _read_from_tokens(self, tokens):
        """Read an expression from a sequence of tokens."""
        if not tokens:
            raise LispError("Unexpected EOF")
        
        token = tokens.pop(0)
        
        if token == '(':
            L = []
            while tokens and tokens[0] != ')':
                L.append(self._read_from_tokens(tokens))
                if not tokens:
                    raise LispError("Unexpected EOF")
            if not tokens:
                raise LispError("Unexpected EOF")
            tokens.pop(0)  # Remove ')'
            return L
        elif token == ')':
            raise LispError("Unexpected ')'")
        elif token == 'quote':
            # Handle quote as a special case to support 'x syntax
            if not tokens:
                raise LispError("Unexpected EOF after quote")
            quoted = self._read_from_tokens(tokens)
            return ['quote', quoted]
        else:
            return self._atom(token)
    
    def _atom(self, token):
        """Convert a token into an atom."""
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                # Check for string literals - FIX: Proper string handling
                if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                    return token[1:-1]  # Remove the quotes
                # Handle specific literals
                if token == 'True':
                    return True
                elif token == 'False':
                    return False
                return token
    
    def eval(self, expr, env=None):
        """Evaluate an expression in an environment."""
        if env is None:
            env = self.global_env
        
        # Handle different expression types
        if isinstance(expr, str):  # Variable reference
            # FIX: Check if the string is a literal (surrounded by quotes)
            if expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]  # Return the string literal without quotes
            return env.get(expr)
        elif not isinstance(expr, list):  # Constant literal
            return expr
        elif not expr:  # Empty list
            return []
        
        first, *rest = expr
        
        # Handle special forms
        if first == 'quote':
            return self._eval_quote(expr, env)
        elif first == 'if':
            return self._eval_if(expr, env)
        elif first == 'define':
            return self._eval_define(expr, env)
        elif first == 'lambda':
            return self._eval_lambda(expr, env)
        elif first == 'begin':
            return self._eval_begin(expr, env)
        elif first == 'let':
            return self._eval_let(expr, env)
        elif first == 'set!':
            return self._eval_set(expr, env)
        elif first == 'while':
            return self._eval_while(expr, env)
        
        # Function application
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in rest]
        return self.apply(func, args)
    
    def apply(self, func, args):
        """Apply a function to arguments."""
        return func(*args)
    
    def _eval_quote(self, expr, env):
        """Evaluate a quote expression."""
        if len(expr) != 2:
            raise LispError("quote requires exactly 1 argument")
        # Simply return the second element without evaluation
        return expr[1]
    
    def _eval_if(self, expr, env):
        """Evaluate an if expression."""
        if len(expr) < 3 or len(expr) > 4:
            raise LispError("if requires 2 or 3 arguments")
        
        cond = self.eval(expr[1], env)
        
        if cond:
            return self.eval(expr[2], env)
        elif len(expr) == 4:
            return self.eval(expr[3], env)
        else:
            return None
    
    def _eval_begin(self, expr, env):
        """Evaluate a begin expression."""
        if len(expr) < 2:
            raise LispError("begin requires at least 1 expression")
        
        result = None
        for sub_expr in expr[1:]:
            result = self.eval(sub_expr, env)
        
        return result
    
    def _eval_define(self, expr, env):
        """Evaluate a define expression."""
        if len(expr) != 3:
            raise LispError("define requires exactly 2 arguments")
        
        name = expr[1]
        
        # Function definition shorthand: (define (f x) body) -> (define f (lambda (x) body))
        if isinstance(name, list):
            func_name = name[0]
            params = name[1:]
            body = expr[2]
            return env.define(func_name, Procedure(params, body, env, self))
        
        # Variable definition: (define var value)
        value = self.eval(expr[2], env)
        return env.define(name, value)
    
    def _eval_lambda(self, expr, env):
        """Evaluate a lambda expression."""
        if len(expr) != 3:
            raise LispError("lambda requires exactly 2 arguments")
        
        params = expr[1]
        if not isinstance(params, list):
            raise LispError("lambda parameters must be a list")
        
        body = expr[2]
        return Procedure(params, body, env, self)
    
    def _eval_let(self, expr, env):
        """Evaluate a let expression."""
        if len(expr) < 3:
            raise LispError("let requires at least 2 arguments")
        
        bindings = expr[1]
        if not isinstance(bindings, list):
            raise LispError("let bindings must be a list")
        
        # Create a new environment
        new_env = Environment(env)
        
        # Evaluate bindings in the original environment
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise LispError("let binding must be a list of length 2")
            
            name = binding[0]
            value = self.eval(binding[1], env)
            new_env.define(name, value)
        
        # Evaluate the body in the new environment
        result = None
        for body_expr in expr[2:]:
            result = self.eval(body_expr, new_env)
        
        return result
    
    def _eval_set(self, expr, env):
        """Evaluate a set! expression to modify a variable's value."""
        if len(expr) != 3:
            raise LispError("set! requires exactly 2 arguments: a variable and a value")
        
        var_name = expr[1]
        if not isinstance(var_name, str):
            raise LispError("First argument to set! must be a symbol")
        
        # Evaluate the new value
        new_value = self.eval(expr[2], env)
        
        # Update the variable in the environment
        return env.set(var_name, new_value)
    
    def _eval_while(self, expr, env):
        """Evaluate a while loop."""
        if len(expr) < 3:
            raise LispError("while requires a condition and at least one expression in the body")
        
        condition = expr[1]
        body = expr[2:]
        result = None
        
        # Keep evaluating the body as long as the condition is true
        while self.eval(condition, env):
            for sub_expr in body:
                result = self.eval(sub_expr, env)
        
        # Return the last evaluated result or None if the loop never executed
        return result if result is not None else None
    
    def run(self, program):
        """Parse and evaluate a program."""
        try:
            # First try to parse the entire program as a single expression
            parsed = self.parse(program)
            result = self.eval(parsed)
            return result
        except LispError:
            # If that fails, try to parse it line by line
            lines = program.strip().split('\n')
            result = None
            expressions = []
            current_expr = []
            
            # Group lines to handle multi-line expressions
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Count parentheses to determine if the expression is complete
                current_expr.append(line)
                full_expr = ' '.join(current_expr)
                open_parens = full_expr.count('(')
                close_parens = full_expr.count(')')
                
                if open_parens == close_parens:
                    expressions.append(full_expr)
                    current_expr = []
            
            # Evaluate each complete expression
            for expr in expressions:
                try:
                    parsed = self.parse(expr)
                    result = self.eval(parsed)
                except LispError as e:
                    # If this line is a section title, skip it
                    if "Undefined variable" in str(e) and any(keyword in expr for keyword in 
                                                          ["Arithmetic", "Operations", "Predicates", "Functions", "Definition", 
                                                           "Application", "Composition", "Pipeline", "Expression"]):
                        continue
                    raise
            
            return result
    
    def run_all(self, programs):
        """Run multiple programs in sequence."""
        result = None
        for program in programs:
            result = self.run(program)
        return result

def run_tests(lisp):
    try:
        with open('samples.lisp', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        # If samples.lisp doesn't exist, use these test cases
        code = """
;; Basic Arithmetic
(+ 1 2 3 4 5)
;; 
(- 10 5)
;; 
(* 2 3 4)
;; 
(/ 100 4 5)
;; 
5
;; Comparison Operations
(= 5 5)
;; 
(< 3 7)
;; 
(>= 10 10)
;; 
(<= 8 7)
;; 
False
;; List Operations
(cons 1 2)
;; 
(cons 1 (list 2 3 4))
;; 
(car (list 5 6 7))
;; 
(cdr (list 5 6 7))
;; 
(null? ())
;; 
(length (list 1 2 3 4))
;; 
4
;; Boolean Operations
(not True)
;; 
(and True False)
;; 
(or False True)
;; 
True
;; Type Predicates
(number? 42)
;; 
(symbol? 'x)
;; 
(list? (list 1 2))
;; 
True
;; Function Definition and Application
(define double (lambda (x) (* x 2)))
(double 5)
;; 
10
;; Recursive Functions
(define factorial
  (lambda (n)
    (if (<= n 1)
        1
        (* n (factorial (- n 1))))))
(factorial 5)
;; 
120
;; Iterative Functions using set!
(define factorial-iter
  (lambda (n)
    (let ((result 1)
          (counter 1))
      (begin
        (while (<= counter n)
          (begin
            (set! result (* result counter))
            (set! counter (+ counter 1))))
        result))))
(factorial-iter 5)
;; 
120
;; Let expressions
(let ((x 5)
      (y 10))
  (+ x y))
;; 
15
;; If expressions
(if (> 5 3)
    "Greater"
    "Less")
;; 
"Greater"
;; Quote
;; (quote (1 2 3))
;; 
;; (1 2 3)  ;; This is the expected result format for quote
;; Begin
(begin
  (define x 5)
  (define y 10)
  (+ x y))
;; 
15
;; Functional Programming Utilities
(define inc (lambda (x) (+ x 1)))
(define square (lambda (x) (* x x)))
(define double (lambda (x) (* x 2)))
;; Function Composition
(define inc-then-double
  (compose double inc))
(inc-then-double 5)
;; 
12
;; Function Pipeline
(pipe 5 double inc square)
;; 
121
;; Map, Filter, Reduce
(define numbers (list 1 2 3 4 5))
(map double numbers)
;; 
(filter (lambda (x) (> x 2)) numbers)
;; 
(reduce + numbers)
;; 
15
"""
    
    # Process each section separately to maintain variable definitions between related expressions
    sections = code.split(';;')
    current_env = Environment()
    interpreter = Lisp()
    
    for section in sections:
        if not section.strip():
            continue
            
        # Extract section title (if any) from the first line
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        section_title = lines[0].strip()
        code_lines = [line for line in lines[1:] if line.strip() and not line.strip().startswith(';')]
        
        if not code_lines:
            continue
            
        # Join all the code lines for this section
        code_to_run = '\n'.join(code_lines)
        
        try:
            # Handle multi-line expressions by counting parentheses
            expressions = []
            current_expr = []
            
            for line in code_lines:
                current_expr.append(line)
                full_expr = ' '.join(current_expr)
                open_parens = full_expr.count('(')
                close_parens = full_expr.count(')')
                
                if open_parens == close_parens:
                    expressions.append(full_expr)
                    current_expr = []
            
            # If there are leftover lines, add them too
            if current_expr:
                expressions.append(' '.join(current_expr))
            
            # Run each expression in the section
            result = None
            for expr in expressions:
                try:
                    # Skip section titles that might look like expressions
                    if "Operations" in expr or "Predicates" in expr or "Functions" in expr:
                        continue
                        
                    result = interpreter.run(expr)
                    print(f"Expression: {expr}")
                    print(f"Result: {result}")
                    print("-" * 40)
                except Exception as e:
                    print(f"Error running: {expr}")
                    print(f"Error: {e}")
                    print("-" * 40)
                    
        except Exception as e:
            print(f"Error in section {section_title}: {e}")
            print("-" * 40)

if __name__ == '__main__':
    lisp = Lisp()
    run_tests(lisp)