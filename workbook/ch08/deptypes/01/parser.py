import re


class Expr:
    pass

class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var({self.name!r})"

class Abs(Expr):
    def __init__(self, param, body):
        self.param = param
        self.body = body

    def __repr__(self):
        return f"Abs({self.param!r}, {self.body!r})"

class App(Expr):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f"App({self.func!r}, {self.arg!r})"

class Binding:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f"Binding(name={self.name!r}, expr={self.expr!r})"


TOKEN_SPEC = [
    ('LAMBDA', r'λ|\\|lambda'),
    ('DOT',    r'\.'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('EQUAL',  r'='),
    ('IDENT',  r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('SKIP',   r'[ \t\n]+'),
]

TOKEN_RE = re.compile('|'.join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC))

def tokenize(code):
    tokens = []
    for match in TOKEN_RE.finditer(code):
        kind = match.lastgroup
        if kind == 'SKIP':
            continue
        value = match.group()
        tokens.append((kind, value))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_kind=None):
        kind, value = self.peek()
        if expected_kind and kind != expected_kind:
            raise SyntaxError(f"Expected {expected_kind}, got {kind}")
        self.pos += 1
        return value

    def parse_binding(self):
        name = self.consume('IDENT')
        self.consume('EQUAL')
        expr = self.parse_expr()
        return Binding(name, expr)

    def parse_expr(self):
        exprs = []
        while True:
            if self.pos >= len(self.tokens):
                break
            kind, _ = self.peek()
            if kind in ('RPAREN', 'EQUAL'):
                break
            exprs.append(self.parse_atom())
        return self.fold_applications(exprs)

    def parse_atom(self):
        kind, val = self.peek()
        if kind == 'IDENT':
            self.consume()
            return Var(val)
        elif kind == 'LAMBDA':
            return self.parse_lambda()
        elif kind == 'LPAREN':
            self.consume()
            e = self.parse_expr()
            self.consume('RPAREN')
            return e
        else:
            raise SyntaxError(f"Unexpected token: {kind}")

    def parse_lambda(self):
        self.consume('LAMBDA')
        param = self.consume('IDENT')
        self.consume('DOT')
        body = self.parse_expr()
        return Abs(param, body)

    def fold_applications(self, exprs):
        if not exprs:
            raise SyntaxError("Empty application")
        result = exprs[0]
        for e in exprs[1:]:
            result = App(result, e)
        return result

def parse(code):
    tokens = tokenize(code)
    parser = Parser(tokens)
    if any(tok[0] == 'EQUAL' for tok in tokens):
        return parser.parse_binding()
    else:
        return parser.parse_expr()


if __name__ == "__main__":
    print(parse("true = λx.λy.x"))
    print(parse("λx.(x x)"))
    print(parse("(λx.λy.x) a b"))

# project: adjust and extend the parser to go with lam.py
