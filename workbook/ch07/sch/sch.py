#!/usr/bin/env python3
#https://gist.github.com/wwbrannon/9386c40a832a1a6ac26b8310f7db9084

import math
import operator as op
from functools import reduce

#
# Errors
#

class LispException(Exception):
    """Base class for all Lisp exceptions."""
    pass

class LispParseException(LispException):
    """Exception raised during parsing."""
    pass

class LispEvalException(LispException):
    """Exception raised during evaluation."""
    pass

#
# Types
#

class LispType:
    """Base class for all Lisp types."""
    pass

class List(LispType, list):
    """Represents a Lisp list."""
    pass

class Atom(LispType):
    """Base class for Lisp atoms."""
    pass

class Symbol(Atom, str):
    """Represents a Lisp symbol."""
    pass

class Literal(Atom):
    """Base class for Lisp literals."""
    pass

class Number(Literal):
    """Base class for Lisp numbers."""
    pass

class Int(Number, int):
    """Represents a Lisp integer."""
    pass

class Float(Number, float):
    """Represents a Lisp floating-point number."""
    pass

class Function(LispType):
    """Base class for Lisp functions."""
    pass

class UserFunction(Function):
    """Represents a user-defined Lisp function."""
    def __init__(self, params, body, frame):
        self.params = params
        self.body = body
        self.frame = frame

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise LispEvalException(f"Arity mismatch: expected {len(self.params)} arguments, got {len(args)}")
        new_frame = Frame(self.frame, **dict(zip(self.params, args)))
        return eval(self.body, new_frame)

class BuiltinFunction(Function):
    """Represents a built-in Lisp function."""
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        return self.fn(*args)

#
# Symbol tables / stack frames
#

class Frame:
    """Represents a Lisp environment frame."""
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.bindings = kwargs

    def resolve(self, name):
        """Resolve a symbol in the current or parent frame."""
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent is not None:
            return self.parent.resolve(name)
        else:
            raise LispEvalException(f"Unbound symbol: {name}")

    def set(self, name, value):
        """Bind a symbol to a value in the current frame."""
        if not isinstance(name, Symbol):
            raise LispEvalException(f"Invalid binding: {name} is not a symbol")
        self.bindings[name] = value

#
# Parsing
#

def tokenize(text):
    """Tokenize a Lisp expression."""
    return text.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(tokens):
    """Parse a list of tokens into a Lisp expression."""
    if not tokens:
        raise LispParseException("Unexpected end of input")

    token = tokens.pop(0)

    if token == '(':
        expr = List()
        while tokens[0] != ')':
            expr.append(parse(tokens))
        tokens.pop(0)  # Remove ')'
        return expr
    elif token == ')':
        raise LispParseException("Unexpected )")
    else:
        return to_atom(token)

def to_atom(token):
    """Convert a token to a Lisp atom."""
    try:
        return Int(token)
    except ValueError:
        try:
            return Float(token)
        except ValueError:
            return Symbol(token)

#
# Evaluation
#

def eval(expr, frame):
    """Evaluate a Lisp expression in the given frame."""
    if isinstance(expr, Literal):
        return expr
    elif isinstance(expr, Symbol):
        return frame.resolve(expr)
    elif isinstance(expr, List):
        if not expr:
            return expr
        car, *cdr = expr
        if car == 'quote':
            return cdr[0]
        elif car == 'if':
            test, conseq, alt = cdr
            return eval(conseq if eval(test, frame) else alt, frame)
        elif car == 'define':
            name, value = cdr
            frame.set(name, eval(value, frame))
        elif car == 'lambda':
            params, body = cdr
            return UserFunction(params, body, frame)
        else:
            fn = eval(car, frame)
            args = [eval(arg, frame) for arg in cdr]
            return fn(*args)
    else:
        raise LispEvalException(f"Invalid expression: {expr}")

#
# Standard Library
#

def default_frame():
    """Create a frame with the standard library functions."""
    frame = Frame()

    # Basic arithmetic
    frame.set(Symbol('+'), BuiltinFunction(lambda *args: reduce(op.add, args)))
    frame.set(Symbol('-'), BuiltinFunction(lambda *args: reduce(op.sub, args)))
    frame.set(Symbol('*'), BuiltinFunction(lambda *args: reduce(op.mul, args)))
    frame.set(Symbol('/'), BuiltinFunction(lambda *args: reduce(op.truediv, args)))

    # Comparison
    frame.set(Symbol('>'), BuiltinFunction(op.gt))
    frame.set(Symbol('<'), BuiltinFunction(op.lt))
    frame.set(Symbol('>='), BuiltinFunction(op.ge))
    frame.set(Symbol('<='), BuiltinFunction(op.le))
    frame.set(Symbol('='), BuiltinFunction(op.eq))
    frame.set(Symbol('!='), BuiltinFunction(op.ne))

    # Math functions
    frame.set(Symbol('abs'), BuiltinFunction(abs))
    frame.set(Symbol('max'), BuiltinFunction(max))
    frame.set(Symbol('min'), BuiltinFunction(min))
    frame.set(Symbol('expt'), BuiltinFunction(op.pow))
    frame.set(Symbol('round'), BuiltinFunction(round))

    # List operations
    frame.set(Symbol('car'), BuiltinFunction(lambda x: x[0]))
    frame.set(Symbol('cdr'), BuiltinFunction(lambda x: x[1:]))
    frame.set(Symbol('cons'), BuiltinFunction(lambda x, y: [x] + y))
    frame.set(Symbol('length'), BuiltinFunction(len))
    frame.set(Symbol('list'), BuiltinFunction(List))

    return frame

#
# REPL
#

def repl():
    """Run the Lisp REPL."""
    frame = default_frame()
    while True:
        try:
            text = input("> ")
            if not text:
                continue
            expr = parse(tokenize(text))
            print(eval(expr, frame))
        except (LispParseException, LispEvalException) as e:
            print(f"Error: {e}")
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    repl()
