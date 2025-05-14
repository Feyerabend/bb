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
        'quote', 'if', 'define', 'lambda', 'begin', 'let', 'let*', 'letrec',
        'set!', 'while', 'cond', 'and', 'or', 'define-macro'
    }
    
    def __init__(self):
        self.global_env = Environment()
        self._setup_global_environment()
    
    def _setup_global_environment(self):
        self.global_env.define('+', lambda *args: sum(args))
        self.global_env.define('-', lambda a, *args: a - sum(args) if args else -a)
        self.global_env.define('*', lambda *args: 1 if not args else self._multiply_all(args))
        
        def divide(a, *args):
            if not args:
                if a == 0:
                    raise RuntimeError("Division by zero")
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
        self.global_env.define('equal?', lambda a, b: a == b)
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
        self.global_env.define('string?', lambda x: isinstance(x, str))
        self.global_env.define('list?', lambda x: isinstance(x, list))
        self.global_env.define('procedure?', lambda x: callable(x) or (isinstance(x, tuple) and x[0] == 'macro'))
        self.global_env.define('boolean?', lambda x: isinstance(x, bool))
        self.global_env.define('compose', lambda f, g: lambda *args: f(g(*args)))
        self.global_env.define('pipe', lambda x, *funcs: self._pipe(x, funcs))
        self.global_env.define('apply', lambda f, args: f(*args))
        self.global_env.define('map', lambda f, lst: [f(x) for x in lst])
        self.global_env.define('filter', lambda f, lst: [x for x in lst if f(x)])
        self.global_env.define('reduce', self._reduce)
        self.global_env.define('string-append', lambda *args: ''.join(str(arg) for arg in args))
        self.global_env.define('string-length', lambda s: len(s) - 2 if isinstance(s, str) and s.startswith('"') and s.endswith('"') else len(s))
        self.global_env.define('substring', lambda s, start, end=None: 
            s[start+1:end+1] if end is not None else s[start+1:-1] if isinstance(s, str) and s.startswith('"') and s.endswith('"') else s[start:end])
        self.global_env.define('display', lambda *args: print(*args, end=""))
        self.global_env.define('newline', lambda: print())
        self.global_env.define('print', print)
        self.global_env.define('abs', abs)
        self.global_env.define('min', min)
        self.global_env.define('max', max)
        self.global_env.define('floor', lambda x: int(x // 1))
        self.global_env.define('ceiling', lambda x: int(x // 1 + (1 if x % 1 else 0)))
        self.global_env.define('round', round)
        self.global_env.define('point', lambda x, y: {'x': float(x), 'y': float(y)})
        self.global_env.define('draw-line', lambda x1, y1, x2, y2: f"Drawing line from ({x1}, {y1}) to ({x2}, {y2})")
        self.global_env.define('draw-circle', lambda x, y, radius: f"Drawing circle at ({x}, {y}) with radius {radius}")
        self.global_env.define('draw-rectangle', lambda x, y, width, height: f"Drawing rectangle at ({x}, {y}) with width {width} and height {height}")
        self.global_env.define('set-color', lambda r, g, b: f"Setting color to RGB({r}, {g}, {b})")
        self.global_env.define('clear-canvas', lambda: "Clearing canvas")
        self.global_env.define('draw-ellipse', lambda x, y, rx, ry: f"Drawing ellipse at ({x}, {y}) with radii ({rx}, {ry})")
        self.global_env.define('draw-text', lambda p, text, size: f"Drawing text '{text}' at ({p['x']}, {p['y']}) with font size {size}")
        self.global_env.define('set-line-width', lambda width: f"Setting line width to {width}")

    def _multiply_all(self, args):
        result = 1
        for arg in args:
            result *= arg
        return result
    
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
        token_regex = r'("(?:\\"|.)*?")|([()])|([^\s()]+)'
        tokens = []
        for match in re.finditer(token_regex, program):
            string_token, paren_token, other_token = match.groups()
            if string_token:
                tokens.append(string_token)
            elif paren_token:
                tokens.append(paren_token)
            elif other_token:
                if other_token.startswith(';'):
                    continue
                tokens.append(other_token)
        processed = []
        i = 0
        while i < len(tokens):
            if tokens[i] == "'":
                processed.extend(['(', 'quote'])
                i += 1
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
            tokens.pop(0)
            return L
        elif token == ')':
            raise SyntaxError("Unexpected closing parenthesis")
        else:
            return self._atom(token)
    
    def _atom(self, token: str) -> Any:
        if token.startswith('"') and token.endswith('"'):
            return token
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                if token.lower() == 'true':
                    return True
                elif token.lower() == 'false':
                    return False
                return token
    
    def eval(self, expr: Any, env: Optional[Environment] = None) -> Any:
        if env is None:
            env = self.global_env
        if isinstance(expr, (int, float, bool)):
            return expr
        if isinstance(expr, str) and expr.startswith('"') and expr.endswith('"'):
            return expr
        if isinstance(expr, str):
            if expr.startswith("'"):
                return expr[1:]
            return env.get(expr)
        if not expr:
            return []
        first, *rest = expr
        if isinstance(first, str) and env.contains(first):
            func = env.get(first)
            if isinstance(func, tuple) and func[0] == 'macro':
                macro = func[1]
                args = rest
                macro_result = macro(*args)
                return self.eval(macro_result, env)
        if first == 'quote':
            return self._eval_quote(expr, env)
        elif first == 'if':
            return self._eval_if(expr, env)
        elif first == 'cond':
            return self._eval_cond(expr, env)
        elif first == 'define':
            return self._eval_define(expr, env)
        elif first == 'define-macro':
            return self._eval_define_macro(expr, env)
        elif first == 'lambda':
            return self._eval_lambda(expr, env)
        elif first == 'begin':
            return self._eval_begin(expr, env)
        elif first == 'let':
            return self._eval_let(expr, env)
        elif first == 'let*':
            return self._eval_let_star(expr, env)
        elif first == 'letrec':
            return self._eval_letrec(expr, env)
        elif first == 'set!':
            return self._eval_set(expr, env)
        elif first == 'while':
            return self._eval_while(expr, env)
        elif first == 'and':
            return self._eval_and(expr, env)
        elif first == 'or':
            return self._eval_or(expr, env)
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in rest]
        return self.apply(func, args)
    
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
        return None
    
    def _eval_cond(self, expr: List, env: Environment) -> Any:
        if len(expr) < 2:
            raise SyntaxError("cond requires at least one clause")
        for clause in expr[1:]:
            if not isinstance(clause, list) or len(clause) < 2:
                raise SyntaxError("cond clause must be a list with at least 2 elements")
            test = clause[0]
            if test == 'else':
                return self._eval_begin(['begin'] + clause[1:], env)
            if len(clause) >= 3 and clause[1] == '=>':
                test_result = self.eval(test, env)
                if test_result:
                    proc = self.eval(clause[2], env)
                    return self.apply(proc, [test_result])
            if self.eval(test, env):
                return self._eval_begin(['begin'] + clause[1:], env)
        return None
    
    def _eval_and(self, expr: List, env: Environment) -> bool:
        if len(expr) == 1:
            return True
        result = True
        for operand in expr[1:]:
            result = self.eval(operand, env)
            if not result:
                return False
        return result
    
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
        if isinstance(name, list):
            func_name = name[0]
            params = name[1:]
            body = expr[2]
            return env.define(func_name, Procedure(params, body, env, self))
        value = self.eval(expr[2], env)
        return env.define(name, value)
    
    def _eval_define_macro(self, expr: List, env: Environment) -> Any:
        if len(expr) != 3:
            raise SyntaxError("define-macro requires exactly 2 arguments")
        name = expr[1]
        if not isinstance(name, list):
            raise SyntaxError("define-macro first argument must be a list (name params)")
        if not name:
            raise SyntaxError("define-macro: list cannot be empty")
        
        macro_name = name[0]
        if not isinstance(macro_name, str):
            raise SyntaxError("define-macro: macro name must be a symbol")
            
        params = name[1:]
        body = expr[2]
        
        if not isinstance(body, list):
            raise SyntaxError("define-macro: body must be a list")
            
        macro = Procedure(params, body, env, self)
        env.define(macro_name, ('macro', macro))
        return None
    
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
        
        if len(bindings) == 0:
            raise SyntaxError("let requires at least one binding")
        
        binding_names = set()
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise SyntaxError("let binding must be a list of length 2")
            name = binding[0]
            if name in binding_names:
                raise SyntaxError(f"let: duplicate binding name: {name}")
            binding_names.add(name)
        
        new_env = Environment(env)
        for binding in bindings:
            name = binding[0]
            value = self.eval(binding[1], env)
            new_env.define(name, value)
        return self._eval_begin(['begin'] + expr[2:], new_env)
    
    def _eval_let_star(self, expr: List, env: Environment) -> Any:
        if len(expr) < 3:
            raise SyntaxError("let* requires at least 2 arguments")
        bindings = expr[1]
        if not isinstance(bindings, list):
            raise SyntaxError("let* bindings must be a list")
        new_env = Environment(env)
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise SyntaxError("let* binding must be a list of length 2")
            name = binding[0]
            value = self.eval(binding[1], new_env)
            new_env.define(name, value)
        return self._eval_begin(['begin'] + expr[2:], new_env)
    
    def _eval_letrec(self, expr: List, env: Environment) -> Any:
        if len(expr) < 3:
            raise SyntaxError("letrec requires at least 2 arguments")
        bindings = expr[1]
        if not isinstance(bindings, list):
            raise SyntaxError("letrec bindings must be a list")
        new_env = Environment(env)
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise SyntaxError("letrec binding must be a list of length 2")
            name = binding[0]
            new_env.define(name, None)
        for binding in bindings:
            name = binding[0]
            value = self.eval(binding[1], new_env)
            new_env.set(name, value)
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
            raise SyntaxError("while requires a condition and at least one expression")
        condition = expr[1]
        body = expr[2:]
        result = None
        iteration_count = 0
        
        while self.eval(condition, env):
            for b in body:
                result = self.eval(b, env)
            
            iteration_count += 1
            if iteration_count > 10000:
                raise RuntimeError("Possible infinite loop detected in while")
        
        return None
    
    def parse_program(self, program: str) -> List[Any]:
        program = re.sub(r';.*$', '', program, flags=re.MULTILINE)
        open_count = program.count('(')
        close_count = program.count(')')
        if open_count != close_count:
            raise SyntaxError(f"Unbalanced parentheses: {open_count} opening and {close_count} closing")
        expressions = []
        tokens = self.tokenize(program)
        while tokens:
            tokens_copy = tokens.copy()
            expr = self._read_from_tokens(tokens_copy)
            expr_str = self._to_string(expr)
            expr_tokens = self.tokenize(expr_str)
            tokens = tokens[len(expr_tokens):]
            expressions.append(expr)
        return expressions
    
    def _to_string(self, expr: Any) -> str:
        if isinstance(expr, list):
            return '(' + ' '.join(self._to_string(x) for x in expr) + ')'
        else:
            return str(expr)
    
    def run(self, program: str) -> Any:
        expressions = self.parse_program(program)
        result = None
        for expr in expressions:
            result = self.eval(expr)
        return result
    
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
                    
                    full_text = '\n'.join(lines)
                    open_count = full_text.count('(')
                    close_count = full_text.count(')')
                    
                    if open_count == close_count:
                        break
                    
                    prompt = ".. "
                
                if not lines:
                    continue
                
                expr = '\n'.join(lines)
                self.history.append(expr)
                
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
        print("  (let* ((x 1) (y (+ x 1))) y) - Sequential bindings")
        print("  (letrec ((f (lambda (x) (if (<= x 0) 0 (f (- x 1))))) (f 5)) - Recursive bindings")
        print("  (draw-text (point 20 30) \"Hello\" 12) - Draw text")
    
    def _print_history(self):
        print("\nCommand History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i}: {cmd}")


class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __repr__(self):
        return f"Point({self.x}, {self.y})"


def register_vector_rasterizer_commands(lisp: Lisp):
    lisp.global_env.define('point', lambda x, y: Point(x, y))
    lisp.global_env.define('point-x', lambda p: p.x)
    lisp.global_env.define('point-y', lambda p: p.y)
    lisp.global_env.define('draw-line', lambda p1, p2, color=None: 
                           f"Drawing line from {p1} to {p2}" + (f" with color {color}" if color else ""))
    lisp.global_env.define('draw-circle', lambda center, radius, color=None:
                           f"Drawing circle at {center} with radius {radius}" + (f" with color {color}" if color else ""))
    lisp.global_env.define('draw-rectangle', lambda p1, width, height, color=None:
                           f"Drawing rectangle at {p1} with width {width} and height {height}" + 
                           (f" with color {color}" if color else ""))
    lisp.global_env.define('draw-polygon', lambda points, color=None:
                           f"Drawing polygon with points {points}" + (f" with color {color}" if color else ""))
    lisp.global_env.define('rgb', lambda r, g, b: {'r': r, 'g': g, 'b': b})
    lisp.global_env.define('rgba', lambda r, g, b, a: {'r': r, 'g': g, 'b': b, 'a': a})
    lisp.global_env.define('translate', lambda obj, dx, dy: f"Translating {obj} by ({dx}, {dy})")
    lisp.global_env.define('rotate', lambda obj, angle, center=None: 
                           f"Rotating {obj} by {angle} degrees" + (f" around {center}" if center else ""))
    lisp.global_env.define('scale', lambda obj, sx, sy=None: 
                           f"Scaling {obj} by ({sx}, {sy if sy is not None else sx})")
    lisp.global_env.define('clear', lambda color=None: f"Clearing canvas" + (f" with color {color}" if color else ""))
    lisp.global_env.define('save', lambda filename: f"Saving canvas to {filename}")
    lisp.global_env.define('set-canvas-size', lambda width, height: f"Setting canvas size to {width}x{height}")
    lisp.global_env.define('draw-text', lambda p, text, size, color=None:
                           f"Drawing text '{text}' at {p} with font size {size}" + 
                           (f" with color {color}" if color else ""))
    lisp.global_env.define('draw-ellipse', lambda center, rx, ry, color=None:
                           f"Drawing ellipse at {center} with radii ({rx}, {ry})" + 
                           (f" with color {color}" if color else ""))
    lisp.global_env.define('set-line-width', lambda width: f"Setting line width to {width}")


if __name__ == '__main__':
    lisp = Lisp()
    register_vector_rasterizer_commands(lisp)
    repl = LispREPL()
    repl.start()
