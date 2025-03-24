import re


class LispError(Exception):
    pass

class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    
    def define(self, name, value):
        self.bindings[name] = value
        return value
    
    def get(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise LispError(f"Undefined variable: {name}")
    
    def set(self, name, value):
        if name in self.bindings:
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.set(name, value)
        raise LispError(f"Cannot set undefined variable: {name}")

class Procedure:
    def __init__(self, params, body, env, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter
    
    def __call__(self, *args):
        if len(args) != len(self.params):
            raise LispError(f"Expected {len(self.params)} arguments, got {len(args)}")
        
        env = Environment(self.env)
        for param, arg in zip(self.params, args):
            env.define(param, arg)
        
        return self.interpreter.eval(self.body, env)

class Lisp:
    def __init__(self):
        self.global_env = Environment()
        self._setup_global_environment()
    
    def _setup_global_environment(self):

        self.global_env.define('+', lambda *args: sum(args))
        self.global_env.define('-', lambda a, *args: a - sum(args) if args else -a)

        self.global_env.define('*', lambda *args: 
            1 if not args else 
            args[0] if len(args) == 1 else 
            args[0] * args[1] if len(args) == 2 else
            args[0] * args[1] * args[2] if len(args) == 3 else
            args[0] * self.global_env.get('*')(*args[1:]))

        self.global_env.define('/', lambda a, *args: 
            a if not args else 
            a / args[0] if len(args) == 1 else 
            a / args[0] / args[1] if len(args) == 2 else
            a / (args[0] * args[1] * args[2:] if args[2:] else 1))
        
        self.global_env.define('True', True)
        self.global_env.define('False', False)
        
        self.global_env.define('=', lambda a, b: a == b)
        self.global_env.define('<', lambda a, b: a < b)
        self.global_env.define('>', lambda a, b: a > b)
        self.global_env.define('<=', lambda a, b: a <= b)
        self.global_env.define('>=', lambda a, b: a >= b)
        
        self.global_env.define('cons', lambda a, b: [a] + (b if isinstance(b, list) else [b]))
        self.global_env.define('car', lambda x: x[0])
        self.global_env.define('cdr', lambda x: x[1:])
        self.global_env.define('list', lambda *args: list(args))
        self.global_env.define('null?', lambda x: not x)
        self.global_env.define('length', lambda x: len(x))
        
        self.global_env.define('not', lambda x: not x)
        self.global_env.define('and', lambda *args: all(args))
        self.global_env.define('or', lambda *args: any(args))
        
        self.global_env.define('number?', lambda x: isinstance(x, (int, float)))
        self.global_env.define('symbol?', lambda x: isinstance(x, str))
        self.global_env.define('list?', lambda x: isinstance(x, list))
        
        self.global_env.define('compose', lambda f, g: lambda *args: f(g(*args)))
        self.global_env.define('pipe', lambda x, *funcs: self._pipe(x, funcs))
        
        self.global_env.define('map', lambda f, lst: [f(x) for x in lst])
        self.global_env.define('filter', lambda f, lst: [x for x in lst if f(x)])
        self.global_env.define('reduce', self._reduce)
    
    def _reduce(self, f, lst, initial=None):
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
        result = x
        for f in funcs:
            result = f(result)
        return result
    

    def tokenize(self, program):
        # Match quoted strings, parentheses, or other tokens
        token_regex = r'("(?:\\"|.)*?")|([()])|([^\s()]+)'
        tokens = []
        for match in re.finditer(token_regex, program):
            string_token, paren_token, other_token = match.groups()
            if string_token:
                tokens.append(string_token)
            elif paren_token:
                tokens.append(paren_token)
            elif other_token:
                tokens.append(other_token)
        # Replace single quotes with 'quote'
        processed = []
        for token in tokens:
            if token == "'":
                processed.append('quote')
            else:
                processed.append(token)
        return processed

    def parse(self, program):
        tokens = self.tokenize(program)
        return self._read_from_tokens(tokens)


    def _read_from_tokens(self, tokens):
        if not tokens:
            raise LispError("Unexpected EOF")
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens and tokens[0] != ')':
                L.append(self._read_from_tokens(tokens))
            if not tokens:
                raise LispError("Unexpected EOF")
            tokens.pop(0)  # remove ')'
            return L
        elif token == ')':
            raise LispError("Unexpected ')'")
        else:
            return self._atom(token)
    
    def _atom(self, token):
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                if token == 'True':
                    return True
                elif token == 'False':
                    return False
                return token  # do NOT strip quotes here!




    def eval(self, expr, env=None):
        if env is None:
            env = self.global_env

        # Handle string literals (e.g., "100")
        if isinstance(expr, str):
            # Check if it's a quoted string (e.g., starts/ends with ")
            if len(expr) >= 2 and expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]  # Strip quotes and return the inner string
            else:
                # Treat as a symbol and look it up
                return env.get(expr)

        # Handle constants (numbers, booleans, etc.)
        if not isinstance(expr, list):
            return expr

        # Handle empty list
        if not expr:
            return []

        # Handle special forms (e.g., quote, if)
        first, *rest = expr
        if first == 'quote':
            return self._eval_quote(expr, env)
        # ... rest of special forms ...

        # Handle function application
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in rest]
        return self.apply(func, args)


    def eval(self, expr, env=None):
        if env is None:
            env = self.global_env
        
#        print(f"Evaluating: {expr}")  # Debug statement
        if isinstance(expr, str):
            if len(expr) >= 2 and expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]
            else:
                return env.get(expr)
        
        if not isinstance(expr, list):
            return expr
        
        if not expr:
            return []
        
        first, *rest = expr
        if first == 'quote':
            result = self._eval_quote(expr, env)
 #           print(f"Result of quote: {result}")
            return result
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
        
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in rest]
        return self.apply(func, args)   
 
    def apply(self, func, args):
        return func(*args)
    
    def _eval_quote(self, expr, env):
        if len(expr) != 2:
            raise LispError("quote requires exactly 1 argument")
        return expr[1] # return as string or as list?
    
    def _eval_if(self, expr, env):
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
        if len(expr) < 2:
            raise LispError("begin requires at least 1 expression")
        
        result = None
        for sub_expr in expr[1:]:
            result = self.eval(sub_expr, env)
        
        return result
    
    def _eval_define(self, expr, env):
        if len(expr) != 3:
            raise LispError("define requires exactly 2 arguments")
        
        name = expr[1]
        
        # definition shorthand: (define (f x) body) -> (define f (lambda (x) body))
        if isinstance(name, list):
            func_name = name[0]
            params = name[1:]
            body = expr[2]
            return env.define(func_name, Procedure(params, body, env, self))
        
        # variable definition: (define var value)
        value = self.eval(expr[2], env)
        return env.define(name, value)
    
    def _eval_lambda(self, expr, env):
        if len(expr) != 3:
            raise LispError("lambda requires exactly 2 arguments")
        
        params = expr[1]
        if not isinstance(params, list):
            raise LispError("lambda parameters must be a list")
        
        body = expr[2]
        return Procedure(params, body, env, self)
    
    def _eval_let(self, expr, env):
        if len(expr) < 3:
            raise LispError("let requires at least 2 arguments")
        
        bindings = expr[1]
        if not isinstance(bindings, list):
            raise LispError("let bindings must be a list")
        
        new_env = Environment(env)
        
        # evaluate bindings in the original environment
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise LispError("let binding must be a list of length 2")
            
            name = binding[0]
            value = self.eval(binding[1], env)
            new_env.define(name, value)
        
        # evaluate the body in the new environment
        result = None
        for body_expr in expr[2:]:
            result = self.eval(body_expr, new_env)
        
        return result
    
    def _eval_set(self, expr, env):
        if len(expr) != 3:
            raise LispError("set! requires exactly 2 arguments: a variable and a value")
        
        var_name = expr[1]
        if not isinstance(var_name, str):
            raise LispError("First argument to set! must be a symbol")
        
        new_value = self.eval(expr[2], env)
        
        return env.set(var_name, new_value)
    
    def _eval_while(self, expr, env):
        if len(expr) < 3:
            raise LispError("while requires a condition and at least one expression in the body")
        
        condition = expr[1]
        body = expr[2:]
        result = None
        
        # keep evaluating body as long as condition true
        while self.eval(condition, env):
            for sub_expr in body:
                result = self.eval(sub_expr, env)
        
        # return last evaluated result or None if loop never executed
        return result if result is not None else None
    
    def run(self, program):
        try:
            # try to parse the entire program as a single expression
            parsed = self.parse(program)
            result = self.eval(parsed)
            return result
        except LispError:
            # else try to parse it line by line
            lines = program.strip().split('\n')
            result = None
            expressions = []
            current_expr = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                current_expr.append(line)
                full_expr = ' '.join(current_expr)
                open_parens = full_expr.count('(')
                close_parens = full_expr.count(')')
                
                if open_parens == close_parens:
                    expressions.append(full_expr)
                    current_expr = []
            
            for expr in expressions:
                try:
                    parsed = self.parse(expr)
                    result = self.eval(parsed)
                except LispError as e:
                    # ifline is a section title, skip it
                    if "Undefined variable" in str(e) and any(keyword in expr for keyword in 
                                                          ["Arithmetic", "Operations", "Predicates", "Functions", "Definition", 
                                                           "Application", "Composition", "Pipeline", "Expression"]):
                        continue
                    raise
            
            return result
    
    def run_all(self, programs):
        result = None
        for program in programs:
            result = self.run(program)
        return result

def run_tests(lisp):
    try:
        with open('samples.lisp', 'r') as f:
            code = f.read()
    except FileNotFoundError:
        pass # exit?
    
    # process each section separately to maintain variable definitions between related expressions
    sections = code.split(';;')
    current_env = Environment()
    interpreter = Lisp()
    
    for section in sections:
        if not section.strip():
            continue
            
        # extract section title (if any) from the first line
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        section_title = lines[0].strip()
        code_lines = [line for line in lines[1:] if line.strip() and not line.strip().startswith(';')]
        
        if not code_lines:
            continue
            
        # join all the code lines for this section
        code_to_run = '\n'.join(code_lines)
        
        try:
            # multi-line expressions by counting parentheses
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
            
            # if there are leftover lines, add them too
            if current_expr:
                expressions.append(' '.join(current_expr))
            
            # run each expression in the section
            result = None
            for expr in expressions:
                try:
                    # skip section titles that might look like expressions
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

#    lisp = Lisp()
#    print(lisp.run("(quote (1 2 3))"))  # Should print [1, 2, 3]
#    print(lisp.run("(quote x)"))        # Should print 'x'
