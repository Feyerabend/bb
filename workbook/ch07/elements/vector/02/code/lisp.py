import re
from typing import List, Dict, Any, Callable, Optional, Union, Tuple


class LispError(Exception):
    pass

class SyntaxError(LispError):
    pass

class RuntimeError(LispError):
    pass


class Environment:
    def __init__(self, parent=None):
        self.bindings: Dict[str, Any] = {}
        self.parent = parent
    
    def define(self, name: str, value: Any) -> Any:
        self.bindings[name] = value
        return value
    
    def get(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: Any) -> Any:
        if name in self.bindings:
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.set(name, value)
        raise RuntimeError(f"Cannot set undefined variable: {name}")
    
    def contains(self, name: str) -> bool:
        if name in self.bindings:
            return True
        return self.parent.contains(name) if self.parent else False


class Procedure:
    def __init__(self, params: List[str], body: Any, env: Environment, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter
    
    def __call__(self, *args):
        if len(args) != len(self.params):
            raise RuntimeError(f"Expected {len(self.params)} arguments, got {len(args)}")

        env = Environment(self.env)        
        for param, arg in zip(self.params, args):
            env.define(param, arg)
        
        return self.interpreter.eval(self.body, env)
    
    def __repr__(self):
        return f"<Procedure: ({', '.join(self.params)})>"


class Lisp:    

    SPECIAL_FORMS = {
        'quote', 'if', 'define', 'lambda', 'begin', 'let', 'set!', 'while', 'cond', 'and', 'or'
    }
    
    def __init__(self):
        self.global_env = Environment()
        self._setup_global_environment()
    
    def _setup_global_environment(self):
        
        self.global_env.define('+', lambda *args: sum(args))
        self.global_env.define('-', lambda a, *args: a - sum(args) if args else -a)
        
        def multiply(*args):
            if not args:
                return 1
            result = 1
            for arg in args:
                result *= arg
            return result
        self.global_env.define('*', multiply)
        
        def divide(a, *args):
            if not args:
                return 1 / a
            result = a
            for arg in args:
                if arg == 0:
                    raise RuntimeError("Division by zero")
                result /= arg
            return result
        self.global_env.define('/', divide)
        
        self.global_env.define('%', lambda a, b: a % b)
        
        self.global_env.define('expt', lambda a, b: a ** b)
        
        self.global_env.define('true', True)
        self.global_env.define('false', False)
        
        self.global_env.define('=', lambda a, b: a == b)
        self.global_env.define('<', lambda a, b: a < b)
        self.global_env.define('>', lambda a, b: a > b)
        self.global_env.define('<=', lambda a, b: a <= b)
        self.global_env.define('>=', lambda a, b: a >= b)
        self.global_env.define('!=', lambda a, b: a != b)
        
        self.global_env.define('cons', lambda a, b: [a] + (b if isinstance(b, list) else [b]))
        self.global_env.define('car', lambda x: x[0] if x else None)
        self.global_env.define('cdr', lambda x: x[1:] if x else [])
        self.global_env.define('list', lambda *args: list(args))
        self.global_env.define('append', lambda *args: sum(args, []))
        self.global_env.define('null?', lambda x: not x)
        self.global_env.define('empty?', lambda x: len(x) == 0 if isinstance(x, list) else False)
        self.global_env.define('length', lambda x: len(x) if isinstance(x, list) else 0)
        
        self.global_env.define('not', lambda x: not x)
        
        self.global_env.define('number?', lambda x: isinstance(x, (int, float)))
        self.global_env.define('integer?', lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer()))
        self.global_env.define('float?', lambda x: isinstance(x, float))
        self.global_env.define('symbol?', lambda x: isinstance(x, str) and not (x.startswith('"') and x.endswith('"')))
        self.global_env.define('string?', lambda x: isinstance(x, str) and x.startswith('"') and x.endswith('"'))
        self.global_env.define('list?', lambda x: isinstance(x, list))
        self.global_env.define('procedure?', lambda x: callable(x))
        self.global_env.define('boolean?', lambda x: isinstance(x, bool))
        
        self.global_env.define('compose', lambda f, g: lambda *args: f(g(*args)))
        self.global_env.define('pipe', lambda x, *funcs: self._pipe(x, funcs))
        self.global_env.define('apply', lambda f, args: f(*args))
        
        self.global_env.define('map', lambda f, lst: [f(x) for x in lst])
        self.global_env.define('filter', lambda f, lst: [x for x in lst if f(x)])
        self.global_env.define('reduce', self._reduce)
        
        self.global_env.define('string-append', lambda *args: ''.join(str(arg) for arg in args))
        self.global_env.define('string-length', lambda s: len(s) - 2 if isinstance(s, str) and s.startswith('"') and s.endswith('"') else 0)
        self.global_env.define('substring', lambda s, start, end=None: 
            s[start+1:end+1] if end is not None else s[start+1:-1] if isinstance(s, str) and s.startswith('"') and s.endswith('"') else "")
        
        # Extend I/O ..
        self.global_env.define('display', lambda *args: print(*args, end=""))
        self.global_env.define('newline', lambda: print())
        self.global_env.define('print', print)
        
        self.global_env.define('abs', abs)
        self.global_env.define('min', min)
        self.global_env.define('max', max)
        self.global_env.define('floor', lambda x: int(x // 1))
        self.global_env.define('ceiling', lambda x: int(x // 1 + (1 if x % 1 else 0)))
        self.global_env.define('round', round)
        
        # vector specific functions could be added here
        # e.g.: self.global_env.define('draw-line', lambda x1, y1, x2, y2: ...)
        # vector specific functions
        self.global_env.define('point', lambda x, y: {'x': float(x), 'y': float(y)})
        self.global_env.define('draw-line', lambda x1, y1, x2, y2: f"Drawing line from ({x1}, {y1}) to ({x2}, {y2})")
        self.global_env.define('draw-circle', lambda x, y, radius: f"Drawing circle at ({x}, {y}) with radius {radius}")
        self.global_env.define('draw-rectangle', lambda x, y, width, height: f"Drawing rectangle at ({x}, {y}) with width {width} and height {height}")
        self.global_env.define('set-color', lambda r, g, b: f"Setting color to RGB({r}, {g}, {b})")
        self.global_env.define('clear-canvas', lambda: "Clearing canvas")    

    def _reduce(self, f, lst, initial=None):
        if not lst:
            if initial is None:
                raise RuntimeError("reduce: empty list with no initial value")
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
        result = x
        for f in funcs:
            result = f(result)
        return result

    def tokenize(self, program: str) -> List[str]:
        # string literals with escaped quotes, parentheses, and other tokens
        token_regex = r'("(?:\\"|.)*?")|([()])|([^\s()]+)'
        tokens = []
        
        for match in re.finditer(token_regex, program):
            string_token, paren_token, other_token = match.groups()
            if string_token:
                tokens.append(string_token)
            elif paren_token:
                tokens.append(paren_token)
            elif other_token:
                # comments as per lisp
                if other_token.startswith(';'):
                    continue
                tokens.append(other_token)
        # quote
        processed = []
        i = 0
        while i < len(tokens):
            if tokens[i] == "'":
                processed.extend(['(', 'quote'])
                i += 1
                # if next token is a '(', we need to find matching ')'
                if i < len(tokens) and tokens[i] == '(':
                    processed.append('(')
                    depth = 1
                    i += 1
                    while i < len(tokens) and depth > 0:
                        if tokens[i] == '(':
                            depth += 1
                        elif tokens[i] == ')':
                            depth -= 1
                        processed.append(tokens[i])
                        i += 1
                    processed.append(')')
                # just a single token
                elif i < len(tokens):
                    processed.append(tokens[i])
                    processed.append(')')
                    i += 1
                else:
                    raise SyntaxError("Unexpected end of input after quote")
            else:
                processed.append(tokens[i])
                i += 1
                
        return processed

    def parse(self, program: str) -> Any:
        tokens = self.tokenize(program)
        if not tokens:
            return None
        return self._read_from_tokens(tokens)

    def _read_from_tokens(self, tokens: List[str]) -> Any:
        if not tokens:
            raise SyntaxError("Unexpected end of input")
        
        token = tokens.pop(0)
        
        if token == '(':
            L = []
            while tokens and tokens[0] != ')':
                L.append(self._read_from_tokens(tokens))
            
            if not tokens:
                raise SyntaxError("Missing closing parenthesis")
            
            tokens.pop(0)  # no ')'
            return L
        elif token == ')':
            raise SyntaxError("Unexpected closing parenthesis")
        else:
            return self._atom(token)
    
    def _atom(self, token: str) -> Any:
        # string literals
        if token.startswith('"') and token.endswith('"'):
            return token  # keep quotes for now, but remove during evaluation

        # integers
        try:
            return int(token)
        except ValueError:
            # floating point numbers
            try:
                return float(token)
            except ValueError:
                # boolean values
                if token.lower() == 'true':
                    return True
                elif token.lower() == 'false':
                    return False
                # it's a symbol
                return token
    
    def eval(self, expr: Any, env: Optional[Environment] = None) -> Any:
        if env is None:
            env = self.global_env
        
        # constants: strings, numbers, booleans
        if isinstance(expr, (int, float, bool)):
            return expr
        
        # string literals (with quotes)
        if isinstance(expr, str) and expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]  # remove quotes
        
        # variable references
        if isinstance(expr, str):
            return env.get(expr)
        
        # empty list
        if not expr:
            return []
        
        # list expressions
        first, *rest = expr
        
        # special forms
        if first == 'quote':
            return self._eval_quote(expr, env)
        elif first == 'if':
            return self._eval_if(expr, env)
        elif first == 'cond':
            return self._eval_cond(expr, env)
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
        elif first == 'and':
            return self._eval_and(expr, env)
        elif first == 'or':
            return self._eval_or(expr, env)
        
        # function application
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in rest]
        
        try:
            return self.apply(func, args)
        except Exception as e:
            if not isinstance(e, LispError):
                raise RuntimeError(f"Error applying {first}: {str(e)}")
            raise
    
    def apply(self, func: Callable, args: List[Any]) -> Any:
        return func(*args)
    
    def _eval_quote(self, expr: List, env: Environment) -> Any:
        if len(expr) != 2:
            raise SyntaxError("quote requires exactly 1 argument")
        return expr[1]
    
    def _eval_if(self, expr: List, env: Environment) -> Any:
        if len(expr) < 3 or len(expr) > 4:
            raise SyntaxError("if requires 2 or 3 arguments")
        
        condition = self.eval(expr[1], env)
        
        if condition:
            return self.eval(expr[2], env)
        elif len(expr) == 4:
            return self.eval(expr[3], env)
        else:
            return None
    
    def _eval_cond(self, expr: List, env: Environment) -> Any:
        if len(expr) < 2:
            raise SyntaxError("cond requires at least one clause")
        
        for clause in expr[1:]:
            if not isinstance(clause, list) or len(clause) < 2:
                raise SyntaxError("cond clause must be a list with at least 2 elements")
            
            test = clause[0]
            expressions = clause[1:]
            
            if test == 'else':
                return self._eval_begin(['begin'] + expressions, env)
            
            # eval test condition
            if self.eval(test, env):
                return self._eval_begin(['begin'] + expressions, env)
        
        return None
    
    def _eval_and(self, expr: List, env: Environment) -> bool:
        if len(expr) == 1:
            return True
        
        for operand in expr[1:]:
            result = self.eval(operand, env)
            if not result:
                return False
        
        return True
    
    def _eval_or(self, expr: List, env: Environment) -> bool:
        if len(expr) == 1:
            return False
        
        for operand in expr[1:]:
            result = self.eval(operand, env)
            if result:
                return result
        
        return False
    
    def _eval_begin(self, expr: List, env: Environment) -> Any:
        if len(expr) < 2:
            raise SyntaxError("begin requires at least 1 expression")
        
        result = None
        for sub_expr in expr[1:]:
            result = self.eval(sub_expr, env)
        
        return result
    
    def _eval_define(self, expr: List, env: Environment) -> Any:
        if len(expr) != 3:
            raise SyntaxError("define requires exactly 2 arguments")
        
        name = expr[1]
        
        # function definition shorthand
        if isinstance(name, list):
            func_name = name[0]
            params = name[1:]
            body = expr[2]
            return env.define(func_name, Procedure(params, body, env, self))
        
        # variable definition
        value = self.eval(expr[2], env)
        return env.define(name, value)
    
    def _eval_lambda(self, expr: List, env: Environment) -> Procedure:
        if len(expr) != 3:
            raise SyntaxError("lambda requires exactly 2 arguments")
        
        params = expr[1]
        if not isinstance(params, list):
            raise SyntaxError("lambda parameters must be a list")
        
        body = expr[2]
        return Procedure(params, body, env, self)
    
    def _eval_let(self, expr: List, env: Environment) -> Any:
        if len(expr) < 3:
            raise SyntaxError("let requires at least 2 arguments")
        
        bindings = expr[1]
        if not isinstance(bindings, list):
            raise SyntaxError("let bindings must be a list")
        
        new_env = Environment(env)
        
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise SyntaxError("let binding must be a list of length 2")
            
            name = binding[0]
            value = self.eval(binding[1], env)
            new_env.define(name, value)
        
        return self._eval_begin(['begin'] + expr[2:], new_env)
    
    def _eval_set(self, expr: List, env: Environment) -> Any:
        if len(expr) != 3:
            raise SyntaxError("set! requires exactly 2 arguments")
        
        var_name = expr[1]
        if not isinstance(var_name, str):
            raise SyntaxError("First argument to set! must be a symbol")
        
        new_value = self.eval(expr[2], env)
        
        return env.set(var_name, new_value)
    
    def _eval_while(self, expr: List, env: Environment) -> Any:
        if len(expr) < 3:
            raise SyntaxError("while requires a condition and at least one expression in the body")
        
        condition = expr[1]
        body = expr[2:]
        result = None
        
        while self.eval(condition, env):
            result = self._eval_begin(['begin'] + body, env)
        
        return result
    
    def parse_program(self, program: str) -> List[Any]:
        # no comments
        program = re.sub(r';.*$', '', program, flags=re.MULTILINE)
        
        # balanced expression
        open_count = program.count('(')
        close_count = program.count(')')
        
        if open_count != close_count:
            raise SyntaxError(f"Unbalanced parentheses: {open_count} opening and {close_count} closing")
        
        # split program into individual expressions
        expressions = []
        tokens = self.tokenize(program)
        
        while tokens:
            # skip empty
            if not tokens:
                break
                
            # parse next expression
            expr = self._read_from_tokens(tokens.copy())
            tokens = tokens[len(self.tokenize(self._to_string(expr))):]
            expressions.append(expr)
        
        return expressions
    
    def _to_string(self, expr: Any) -> str:
        if isinstance(expr, list):
            return '(' + ' '.join(self._to_string(x) for x in expr) + ')'
        else:
            return str(expr)
    
    def run(self, program: str) -> Any:
        try:
            # try parse program as a single expression
            parsed = self.parse(program)
            return self.eval(parsed)
        except LispError as e:
            # if fails, try break it into multiple expressions
            try:
                expressions = []
                lines = []
                
                for line in program.splitlines():
                    # skip comments and empty lines
                    if not line.strip() or line.strip().startswith(';'):
                        continue
                    
                    lines.append(line)
                    full_text = '\n'.join(lines)
                    
                    # count parentheses to check if we have complete expressions
                    open_count = full_text.count('(')
                    close_count = full_text.count(')')
                    
                    if open_count == close_count:
                        try:
                            expr = self.parse(full_text)
                            expressions.append(expr)
                            lines = []
                        except SyntaxError:
                            # not a complete expression yet, continue to next line
                            pass

                # process any remaining lines
                if lines:
                    try:
                        expr = self.parse('\n'.join(lines))
                        expressions.append(expr)
                    except SyntaxError as e:
                        print(f"Syntax error in remaining code: {e}")

                # eval all expressions
                result = None
                for expr in expressions:
                    result = self.eval(expr)
                
                return result
            except Exception as e:
                # if all else fails, re-raise the original error
                raise e
    
    def run_file(self, filename: str) -> Any:
        with open(filename, 'r') as f:
            program = f.read()
        return self.run(program)


class LispREPL:
    
    def __init__(self):
        self.lisp = Lisp()
        self.history: List[str] = []
    
    def start(self):
        print("Lisp REPL (Type 'exit' to quit, 'help' for commands)\n")
        
        while True:
            try:
                # read input, supporting multi-line expressions
                lines = []
                prompt = "> "

                while True:
                    line = input(prompt).rstrip()
                    
                    if not line and not lines:
                        continue
                    
                    if line.lower() in ("exit", "quit"):
                        print("Bye!")
                        return
                    
                    if line.lower() == "help":
                        self._print_help()
                        break
                    
                    if line.lower() == "history":
                        self._print_history()
                        break
                    
                    lines.append(line)
                    
                    # if we have a complete expression
                    full_text = '\n'.join(lines)
                    open_count = full_text.count('(')
                    close_count = full_text.count(')')
                    
                    if open_count == close_count:
                        break
                    
                    prompt = "... "
                
                if not lines:
                    continue
                
                # join the lines into a single expression
                expr = '\n'.join(lines)
                
                # add to history
                self.history.append(expr)
                
                # eval and print result
                result = self.lisp.run(expr)
                print(f"  {result}\n")
                
            except KeyboardInterrupt:
                print("\nInterrupted")
            except EOFError:
                print("\nGoodbye!")
                break
            except LispError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {type(e).__name__}: {e}")
    
    def _print_help(self):
        print("\nCommands:")
        print("  exit, quit - Exit the REPL")
        print("  help       - Show this help")
        print("  history    - Show command history")
        print("\nExample expressions:")
        print("  (+ 1 2 3)                   - Basic arithmetic")
        print("  (define x 42)               - Define a variable")
        print("  (define (square x) (* x x)) - Define a function")
        print("  (map (lambda (x) (* x x)) '(1 2 3 4)) - Higher-order functions")
    
    def _print_history(self):
        print("\nCommand History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i}: {cmd}")


def register_vector_rasterizer_commands(lisp: Lisp):
    # register vector rasterizer specific commands to the interpreter
    # here we could implement commands for a vector rasterizer

    #  simple Point class
    class Point:
        def __init__(self, x, y):
            self.x = float(x)
            self.y = float(y)
        
        def __repr__(self):
            return f"Point({self.x}, {self.y})"
    
    # register point constructor
    lisp.global_env.define('point', lambda x, y: Point(x, y))
    
    # register point accessors
    lisp.global_env.define('point-x', lambda p: p.x)
    lisp.global_env.define('point-y', lambda p: p.y)
    
    # register basic drawing operations (placeholders)
    lisp.global_env.define('draw-line', lambda p1, p2, color=None: 
                           f"Drawing line from {p1} to {p2}" + (f" with color {color}" if color else ""))
    
    lisp.global_env.define('draw-circle', lambda center, radius, color=None:
                           f"Drawing circle at {center} with radius {radius}" + (f" with color {color}" if color else ""))
    
    lisp.global_env.define('draw-rectangle', lambda p1, width, height, color=None:
                           f"Drawing rectangle at {p1} with width {width} and height {height}" + 
                           (f" with color {color}" if color else ""))
    
    lisp.global_env.define('draw-polygon', lambda points, color=None:
                           f"Drawing polygon with points {points}" + (f" with color {color}" if color else ""))
    
    # register color operations
    lisp.global_env.define('rgb', lambda r, g, b: {'r': r, 'g': g, 'b': b})
    lisp.global_env.define('rgba', lambda r, g, b, a: {'r': r, 'g': g, 'b': b, 'a': a})
    
    # register transformation operations
    lisp.global_env.define('translate', lambda obj, dx, dy: f"Translating {obj} by ({dx}, {dy})")
    lisp.global_env.define('rotate', lambda obj, angle, center=None: 
                           f"Rotating {obj} by {angle} degrees" + 
                           (f" around {center}" if center else ""))
    lisp.global_env.define('scale', lambda obj, sx, sy=None: 
                           f"Scaling {obj} by ({sx}, {sy if sy is not None else sx})")
    
    # register canvas operations
    lisp.global_env.define('clear', lambda color=None: f"Clearing canvas" + (f" with color {color}" if color else ""))
    lisp.global_env.define('save', lambda filename: f"Saving canvas to {filename}")
    lisp.global_env.define('set-canvas-size', lambda width, height: f"Setting canvas size to {width}x{height}")


if __name__ == '__main__':
    lisp = Lisp()
    
    # register vector commands
    register_vector_rasterizer_commands(lisp)

    repl = LispREPL()
    repl.start()
