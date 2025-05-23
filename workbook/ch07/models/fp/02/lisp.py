import re
from typing import Any, List, Union, Optional, Dict, Callable
from functools import reduce as functools_reduce
from abc import ABC, abstractmethod

class LispError(Exception):
    pass

class ParseError(LispError):
    pass

class RuntimeError(LispError):
    pass

class ErrorHandler:
    @staticmethod
    def parse_error(message: str, token: Optional[str] = None, pos: Optional[int] = None) -> ParseError:
        context = f" at position {pos} near '{token}'" if token and pos is not None else ""
        return ParseError(f"Parse error: {message}{context}")

    @staticmethod
    def runtime_error(message: str) -> RuntimeError:
        return RuntimeError(f"Runtime error: {message}")

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.bindings: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any) -> Any:
        if not isinstance(name, str):
            raise ErrorHandler.runtime_error(f"Variable name must be a string, got {type(name)}")
        self.bindings[name] = value
        return value

    def get(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise ErrorHandler.runtime_error(f"Undefined variable: {name}")

    def set(self, name: str, value: Any) -> Any:
        if name in self.bindings:
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.set(name, value)
        raise ErrorHandler.runtime_error(f"Cannot set undefined variable: {name}")

class Procedure:
    def __init__(self, params: List[str], body: Any, env: Environment, interpreter: 'Lisp'):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter
        if not isinstance(params, list):
            raise ErrorHandler.runtime_error("Function parameters must be a list")
        for param in params:
            if not isinstance(param, str):
                raise ErrorHandler.runtime_error(f"Parameter names must be strings, got {type(param)}")

    def __call__(self, *args) -> Any:
        if len(args) != len(self.params):
            raise ErrorHandler.runtime_error(f"Function expects {len(self.params)} arguments, got {len(args)}")
        env = Environment(self.env)
        for param, arg in zip(self.params, args):
            env.define(param, arg)
        return self.interpreter.eval(self.body, env)

class Token:
    def __init__(self, kind: str, value: str, pos: int):
        self.kind = kind
        self.value = value
        self.pos = pos

class TokenFactory:
    TOKEN_REGEX = re.compile(r'''
        (?P<STRING>"(?:[^"\\]|\\.)*")           |  # Strings with escape sequences
        (?P<COMMENT>;[^\n]*)                    |  # Comments
        (?P<QUOTE>')                            |  # Quote shorthand
        (?P<PAREN>[()[\]])                      |  # Parentheses and brackets
        (?P<NUMBER>-?(?:\d*\.\d+([eE][+-]?\d+)?|\d+))  |  # Numbers (int, float, scientific)
        (?P<SYMBOL>[^\s()[\]'"`;]+)             |  # Symbols
        (?P<WHITESPACE>\s+)                        # Whitespace
    ''', re.VERBOSE)

    @classmethod
    def create_tokens(cls, text: str) -> List[Token]:
        tokens = []
        for match in cls.TOKEN_REGEX.finditer(text):
            kind = match.lastgroup
            value = match.group()
            pos = match.start()
            if kind == 'WHITESPACE' or kind == 'COMMENT':
                continue
            if kind == 'STRING' and not value.endswith('"'):
                raise ErrorHandler.parse_error("Unterminated string", value, pos)
            tokens.append(Token(kind, value, pos))
        return tokens

class Symbol:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Symbol({self.name})"

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

class ExpressionFactory:
    @staticmethod
    def create_atom(token: Token) -> Any:
        if token.kind == 'STRING':
            content = token.value[1:-1]
            return content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        try:
            if '.' in token.value or 'e' in token.value.lower():
                return float(token.value)
            return int(token.value)
        except ValueError:
            pass
        if token.value.lower() == 'true':
            return True
        if token.value.lower() == 'false':
            return False
        if token.value == 'nil':
            return None
        return Symbol(token.value)

    @staticmethod
    def create_list(elements: List[Any]) -> List[Any]:
        return elements

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.expr_factory = ExpressionFactory()

    def parse(self) -> Any:
        if self.pos >= len(self.tokens):
            raise ErrorHandler.parse_error("Unexpected end of input")
        return self._parse_expression()

    def _parse_expression(self) -> Any:
        if self.pos >= len(self.tokens):
            raise ErrorHandler.parse_error("Unexpected end of input")
        token = self.tokens[self.pos]
        if token.value == '(':
            return self._parse_list()
        elif token.value == '[':
            return self._parse_list(end_token=']')
        elif token.value == "'":
            self.pos += 1
            quoted_expr = self._parse_expression()
            return ['quote', quoted_expr]
        elif token.value in (')', ']'):
            raise ErrorHandler.parse_error(f"Unexpected closing '{token.value}'", token.value, self.pos)
        else:
            self.pos += 1
            return self.expr_factory.create_atom(token)

    def _parse_list(self, end_token: str = ')') -> List[Any]:
        self.pos += 1
        elements = []
        while self.pos < len(self.tokens) and self.tokens[self.pos].value != end_token:
            elements.append(self._parse_expression())
        if self.pos >= len(self.tokens):
            expected = ']' if end_token == ']' else ')'
            raise ErrorHandler.parse_error(f"Missing closing '{expected}'")
        self.pos += 1
        return self.expr_factory.create_list(elements)

class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        pass

class QuoteEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) != 2:
            raise ErrorHandler.runtime_error("quote requires exactly 1 argument")
        return expr[1]

class IfEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) < 3 or len(expr) > 4:
            raise ErrorHandler.runtime_error("if requires 2 or 3 arguments")
        condition = interpreter.eval(expr[1], env)
        if interpreter._is_truthy(condition):
            return interpreter.eval(expr[2], env)
        return interpreter.eval(expr[3], env) if len(expr) == 4 else None

class CondEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        for clause in expr[1:]:
            if not isinstance(clause, list) or len(clause) != 2:
                raise ErrorHandler.runtime_error("cond clauses must be lists of length 2")
            condition, result = clause
            if (isinstance(condition, Symbol) and condition.name == 'else') or condition == 'else' or interpreter._is_truthy(interpreter.eval(condition, env)):
                return interpreter.eval(result, env)
        return None

class AndEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        for sub_expr in expr[1:]:
            result = interpreter.eval(sub_expr, env)
            if not interpreter._is_truthy(result):
                return False
        return True

class OrEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        for sub_expr in expr[1:]:
            result = interpreter.eval(sub_expr, env)
            if interpreter._is_truthy(result):
                return result
        return False

class DefineEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) != 3:
            raise ErrorHandler.runtime_error("define requires exactly 2 arguments")
        target = expr[1]
        if isinstance(target, list):
            if not target:
                raise ErrorHandler.runtime_error("define: function name cannot be empty")
            func_name = target[0]
            params = target[1:]
            body = expr[2]
            param_names = [param.name if isinstance(param, Symbol) else str(param) for param in params]
            procedure = Procedure(param_names, body, env, interpreter)
            return env.define(func_name.name if isinstance(func_name, Symbol) else str(func_name), procedure)
        elif isinstance(target, Symbol):
            value = interpreter.eval(expr[2], env)
            return env.define(target.name, value)
        else:
            raise ErrorHandler.runtime_error("define: first argument must be a symbol or list")

class SetEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) != 3:
            raise ErrorHandler.runtime_error("set! requires exactly 2 arguments")
        var_name = expr[1]
        if isinstance(var_name, Symbol):
            var_name = var_name.name
        elif not isinstance(var_name, str):
            raise ErrorHandler.runtime_error("set!: first argument must be a symbol")
        value = interpreter.eval(expr[2], env)
        return env.set(var_name, value)

class LambdaEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) != 3:
            raise ErrorHandler.runtime_error("lambda requires exactly 2 arguments")
        params = expr[1]
        body = expr[2]
        if not isinstance(params, list):
            raise ErrorHandler.runtime_error("lambda: parameters must be a list")
        param_names = [param.name if isinstance(param, Symbol) else str(param) for param in params]
        return Procedure(param_names, body, env, interpreter)

class LetEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) < 3:
            raise ErrorHandler.runtime_error("let requires at least 2 arguments")
        bindings = expr[1]
        body_exprs = expr[2:]
        if not isinstance(bindings, list):
            raise ErrorHandler.runtime_error("let: bindings must be a list")
        new_env = Environment(env)
        for binding in bindings:
            if not isinstance(binding, list) or len(binding) != 2:
                raise ErrorHandler.runtime_error("let: each binding must be a list of length 2")
            var_name, value_expr = binding
            if isinstance(var_name, Symbol):
                var_name = var_name.name
            elif not isinstance(var_name, str):
                raise ErrorHandler.runtime_error("let: variable names must be symbols")
            value = interpreter.eval(value_expr, env)
            new_env.define(var_name, value)
        return interpreter._eval_begin(body_exprs, new_env)

class BeginEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        return interpreter._eval_begin(expr[1:], env)

class WhileEvaluator(Evaluator):
    def evaluate(self, expr: List[Any], env: Environment, interpreter: 'Lisp') -> Any:
        if len(expr) < 3:
            raise ErrorHandler.runtime_error("while requires a condition and at least one body expression")
        condition_expr = expr[1]
        body_exprs = expr[2:]
        result = None
        while interpreter._is_truthy(interpreter.eval(condition_expr, env)):
            result = interpreter._eval_begin(body_exprs, env)
        return result

class BuiltInCommand(ABC):
    @abstractmethod
    def execute(self, *args: Any) -> Any:
        pass

class AddCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        return sum(args)

class SubtractCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        if not args:
            return 0
        if len(args) == 1:
            return -args[0]
        return args[0] - sum(args[1:])

class MultiplyCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        return functools_reduce(lambda x, y: x * y, args, 1)

class DivideCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        if not args:
            raise ErrorHandler.runtime_error("divide requires at least 1 argument")
        if len(args) == 1:
            if args[0] == 0:
                raise ErrorHandler.runtime_error("Division by zero")
            return 1.0 / args[0]
        result = args[0]
        for arg in args[1:]:
            if arg == 0:
                raise ErrorHandler.runtime_error("Division by zero")
            result /= arg
        return result

class ModCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a % b

class AbsCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return abs(x)

class MaxCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        return max(args)

class MinCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        return min(args)

class EqualCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a == b

class NotEqualCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a != b

class LessCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a < b

class GreaterCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a > b

class LessEqualCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a <= b

class GreaterEqualCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return a >= b

class NotCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return not x

class ConsCommand(BuiltInCommand):
    def execute(self, a: Any, b: Any) -> Any:
        return [a] + (b if isinstance(b, list) else [b])

class CarCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return x[0] if x else None

class CdrCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return x[1:] if len(x) > 1 else []

class ListCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        return list(args)

class AppendCommand(BuiltInCommand):
    def execute(self, *lists: Any) -> Any:
        return sum(lists, [])

class LengthCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return len(x)

class ReverseCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return list(reversed(x))

class NullCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return x is None or x == []

class EmptyCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return len(x) == 0 if hasattr(x, '__len__') else False

class NumberCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return isinstance(x, (int, float))

class StringCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return isinstance(x, str)

class SymbolCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return isinstance(x, Symbol)

class ListPredCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return isinstance(x, list)

class ProcedureCommand(BuiltInCommand):
    def execute(self, x: Any) -> Any:
        return callable(x)

class MapCommand(BuiltInCommand):
    def execute(self, func: Callable, lst: List[Any]) -> Any:
        if not isinstance(lst, list):
            raise ErrorHandler.runtime_error("map: second argument must be a list")
        return [func(x) for x in lst]

class FilterCommand(BuiltInCommand):
    def execute(self, func: Callable, lst: List[Any]) -> Any:
        if not isinstance(lst, list):
            raise ErrorHandler.runtime_error("filter: second argument must be a list")
        return [x for x in lst if func(x)]

class ReduceCommand(BuiltInCommand):
    def execute(self, func: Callable, lst: List[Any], *initial: Any) -> Any:
        if not isinstance(lst, list):
            raise ErrorHandler.runtime_error("reduce: second argument must be a list")
        if not lst and not initial:
            raise ErrorHandler.runtime_error("reduce: empty list with no initial value")
        if initial:
            return functools_reduce(func, lst, initial[0])
        return functools_reduce(func, lst)

class ApplyCommand(BuiltInCommand):
    def execute(self, func: Callable, args: List[Any]) -> Any:
        if not isinstance(args, list):
            raise ErrorHandler.runtime_error("apply: second argument must be a list")
        return func(*args)

class PrintCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        formatted_args = [arg.name if isinstance(arg, Symbol) else arg for arg in args]
        print(*formatted_args)
        return None

class DisplayCommand(BuiltInCommand):
    def execute(self, *args: Any) -> Any:
        formatted_args = [arg.name if isinstance(arg, Symbol) else arg for arg in args]
        print(*formatted_args, end='')
        return None

class ResultFormatter:
    def format(self, result: Any) -> str:
        return self.visit(result)

    def visit(self, result: Any) -> str:
        if isinstance(result, str):
            return f'"{result}"'
        elif isinstance(result, Symbol):
            return result.name
        elif isinstance(result, list):
            formatted_items = [self.visit(item) for item in result]
            return f"({' '.join(formatted_items)})"
        else:
            return str(result)

class Lisp:
    def __init__(self):
        self.global_env = Environment()
        self.special_forms: Dict[str, Evaluator] = {}
        self.formatter = ResultFormatter()
        self._setup_special_forms()
        self._setup_builtins()

    def _setup_special_forms(self):
        self.special_forms = {
            'quote': QuoteEvaluator(),
            'if': IfEvaluator(),
            'cond': CondEvaluator(),
            'and': AndEvaluator(),
            'or': OrEvaluator(),
            'define': DefineEvaluator(),
            'set!': SetEvaluator(),
            'lambda': LambdaEvaluator(),
            'let': LetEvaluator(),
            'begin': BeginEvaluator(),
            'while': WhileEvaluator(),
        }

    def _setup_builtins(self):
        env = self.global_env
        env.define('+', AddCommand())
        env.define('-', SubtractCommand())
        env.define('*', MultiplyCommand())
        env.define('/', DivideCommand())
        env.define('mod', ModCommand())
        env.define('abs', AbsCommand())
        env.define('max', MaxCommand())
        env.define('min', MinCommand())
        env.define('=', EqualCommand())
        env.define('==', EqualCommand())
        env.define('!=', NotEqualCommand())
        env.define('<', LessCommand())
        env.define('>', GreaterCommand())
        env.define('<=', LessEqualCommand())
        env.define('>=', GreaterEqualCommand())
        env.define('not', NotCommand())
        env.define('cons', ConsCommand())
        env.define('car', CarCommand())
        env.define('cdr', CdrCommand())
        env.define('list', ListCommand())
        env.define('append', AppendCommand())
        env.define('length', LengthCommand())
        env.define('reverse', ReverseCommand())
        env.define('null?', NullCommand())
        env.define('empty?', EmptyCommand())
        env.define('number?', NumberCommand())
        env.define('string?', StringCommand())
        env.define('symbol?', SymbolCommand())
        env.define('list?', ListPredCommand())
        env.define('procedure?', ProcedureCommand())
        env.define('map', MapCommand())
        env.define('filter', FilterCommand())
        env.define('reduce', ReduceCommand())
        env.define('apply', ApplyCommand())
        env.define('print', PrintCommand())
        env.define('display', DisplayCommand())
        env.define('true', True)
        env.define('false', False)
        env.define('nil', None)

    def parse(self, text: str) -> Any:
        try:
            tokens = TokenFactory.create_tokens(text)
            if not tokens:
                raise ErrorHandler.parse_error("Empty input")
            parser = Parser(tokens)
            return parser.parse()
        except Exception as e:
            raise ErrorHandler.parse_error(str(e))

    def eval(self, expr: Any, env: Optional[Environment] = None) -> Any:
        if env is None:
            env = self.global_env
        try:
            return self._eval_expr(expr, env)
        except Exception as e:
            if isinstance(e, (RuntimeError, LispError)):
                raise
            raise ErrorHandler.runtime_error(str(e))

    def _eval_expr(self, expr: Any, env: Environment) -> Any:
        if isinstance(expr, (int, float, str, bool)) or expr is None:
            return expr
        if isinstance(expr, Symbol):
            return env.get(expr.name)
        if isinstance(expr, list):
            return self._eval_list(expr, env)
        raise ErrorHandler.runtime_error(f"Cannot evaluate expression of type {type(expr)}: {expr}")

    def _eval_list(self, expr: List[Any], env: Environment) -> Any:
        if not expr:
            return []
        first = expr[0]
        first_name = first.name if isinstance(first, Symbol) else first
        if first_name in self.special_forms:
            return self.special_forms[first_name].evaluate(expr, env, self)
        func = self.eval(first, env)
        args = [self.eval(arg, env) for arg in expr[1:]]
        if isinstance(func, BuiltInCommand):
            return func.execute(*args)
        if callable(func):
            return func(*args)
        raise ErrorHandler.runtime_error(f"'{first}' is not a function: {type(func)} {func}")

    def _eval_begin(self, exprs: List[Any], env: Environment) -> Any:
        if not exprs:
            return None
        result = None
        for expr in exprs:
            result = self.eval(expr, env)
        return result

    def _is_truthy(self, value: Any) -> bool:
        return value is not False and value is not None

    def run(self, source: str) -> Any:
        try:
            expr = self.parse(source)
            return self.eval(expr)
        except (ParseError, RuntimeError, LispError) as e:
            raise e
        except Exception as e:
            raise ErrorHandler.runtime_error(f"Unexpected error: {e}")

class LispREPL:
    def __init__(self):
        self.lisp = Lisp()
        self.multiline_buffer = []
        self.paren_count = 0

    def start(self):
        print("Design Pattern Lisp REPL")
        print("Type 'exit', 'quit', or press Ctrl+C to quit")
        print("Multi-line expressions are supported")
        print()
        while True:
            try:
                prompt = ".. " if self.multiline_buffer else ">> "
                line = input(prompt).strip()
                if line.lower() in ("exit", "quit"):
                    break
                if not line:
                    continue
                self.multiline_buffer.append(line)
                self.paren_count += line.count('(') + line.count('[')
                self.paren_count -= line.count(')') + line.count(']')
                if self.paren_count == 0:
                    source = ' '.join(self.multiline_buffer)
                    self.multiline_buffer = []
                    try:
                        result = self.lisp.run(source)
                        if result is not None:
                            print(self.lisp.formatter.format(result))
                    except (ParseError, RuntimeError, LispError) as e:
                        print(f"Error: {e}")
                elif self.paren_count < 0:
                    print("Error: Unmatched closing parenthesis")
                    self.multiline_buffer = []
                    self.paren_count = 0
            except (KeyboardInterrupt, EOFError):
                print("\nBye!")
                break

if __name__ == '__main__':
    repl = LispREPL()
    repl.start()

