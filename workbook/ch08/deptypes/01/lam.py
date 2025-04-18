
from dataclasses import dataclass
from typing import Union, Callable, Optional

# expression types
@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Abs:
    param: str
    body: 'Expr'

@dataclass(frozen=True)
class App:
    func: 'Expr'
    arg: 'Expr'

Expr = Union[Var, Abs, App]

def substitute(expr: Expr, var: str, value: Expr) -> Expr:
    if isinstance(expr, Var):
        return value if expr.name == var else expr
    elif isinstance(expr, Abs):
        if expr.param == var:
            return expr  # no substitution under same-named binder
        else:
            return Abs(expr.param, substitute(expr.body, var, value))
    elif isinstance(expr, App):
        return App(substitute(expr.func, var, value), substitute(expr.arg, var, value))

# eval (beta reduction, normal order)
def is_reducible(expr: Expr) -> bool:
    if isinstance(expr, App):
        if isinstance(expr.func, Abs):
            return True
        return is_reducible(expr.func) or is_reducible(expr.arg)
    elif isinstance(expr, Abs):
        return is_reducible(expr.body)
    else:
        return False

def step(expr: Expr) -> Expr:
    if isinstance(expr, App):
        if isinstance(expr.func, Abs):
            return substitute(expr.func.body, expr.func.param, expr.arg)
        elif is_reducible(expr.func):
            return App(step(expr.func), expr.arg)
        elif is_reducible(expr.arg):
            return App(expr.func, step(expr.arg))
    elif isinstance(expr, Abs):
        return Abs(expr.param, step(expr.body))
    return expr

def evaluate(expr: Expr, max_steps: int = 1000) -> Expr:
    for i in range(max_steps):
        if not is_reducible(expr):
            break
        expr = step(expr)
    return expr

# pprinting
def pretty(expr: Expr) -> str:
    if isinstance(expr, Var):
        return expr.name
    elif isinstance(expr, Abs):
        return f"(λ{expr.param}.{pretty(expr.body)})"
    elif isinstance(expr, App):
        return f"({pretty(expr.func)} {pretty(expr.arg)})"

# Church numerals
def church(n: int) -> Expr:
    f = Var('f')
    x = Var('x')
    body = x
    for _ in range(n):
        body = App(f, body)
    return Abs('f', Abs('x', body))


def to_int(expr: Expr) -> Optional[int]:
    expr = evaluate(expr)
    if isinstance(expr, Abs) and isinstance(expr.body, Abs):
        counter = 0
        body = expr.body.body
        while isinstance(body, App):
            if isinstance(body.func, Var) and body.func.name == 'f':
                counter += 1
                body = body.arg
            else:
                return None
        if isinstance(body, Var) and body.name == 'x':
            return counter
    return None

# Church-encoded booleans
# true: λx.λy.x  (selects first argument)
true = Abs('x', Abs('y', Var('x')))
# false: λx.λy.y  (selects second argument)
false = Abs('x', Abs('y', Var('y')))

# Conditional: λp.λa.λb.p a b
# Simply applies the predicate to the two branches
cond = Abs('p', Abs('a', Abs('b', App(App(Var('p'), Var('a')), Var('b')))))

# Logical operators
# not: λp.λa.λb.p b a  (flips the arguments)
not_op = Abs('p', Abs('a', Abs('b', App(App(Var('p'), Var('b')), Var('a')))))

# and: λp.λq.p q p  (if p then q else p)
and_op = Abs('p', Abs('q', App(App(Var('p'), Var('q')), Var('p'))))

# or: λp.λq.p p q  (if p then p else q)
or_op = Abs('p', Abs('q', App(App(Var('p'), Var('p')), Var('q'))))

# Successor: λn.λf.λx.f (n f x)
succ = Abs('n', Abs('f', Abs('x', App(Var('f'), App(App(Var('n'), Var('f')), Var('x'))))))

# Addition: λm.λn.λf.λx.m f (n f x)
add = Abs('m', Abs('n', Abs('f', Abs('x',
        App(App(Var('m'), Var('f')), App(App(Var('n'), Var('f')), Var('x')))
))))

# Multiplication: λm.λn.λf.m (n f)
mult = Abs('m', Abs('n', Abs('f', App(Var('m'), App(Var('n'), Var('f'))))))

# Church-encoded pairs
# pair: λx.λy.λf.f x y
pair = Abs('x', Abs('y', Abs('f', App(App(Var('f'), Var('x')), Var('y')))))
# fst: λp.p (λx.λy.x)
fst = Abs('p', App(Var('p'), Abs('x', Abs('y', Var('x')))))
# snd: λp.p (λx.λy.y)
snd = Abs('p', App(Var('p'), Abs('x', Abs('y', Var('y')))))

# Predecessor helper: λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)
# This creates a pair (0,0), then iterates n times the operation (m,n) -> (n,n+1)
# After n iterations, we get the pair (n-1,n) and we take the first element
shift = Abs('p', App(App(pair, App(snd, Var('p'))), 
                       App(succ, App(snd, Var('p')))))

pred = Abs('n', App(
    App(App(Var('n'), shift), App(App(pair, church(0)), church(0))),
    Abs('x', Abs('y', Var('x')))
))

# Zero test: λn.n (λx.false) true
# Apply n to a function that always returns false, starting with true
# If n = 0, result is true. If n > 0, result is false.
iszero = Abs('n', App(App(Var('n'), Abs('x', false)), true))

# Y combinator: λf.(λx.f (x x)) (λx.f (x x))
Y = Abs('f', App(
    Abs('x', App(Var('f'), App(Var('x'), Var('x')))),
    Abs('x', App(Var('f'), App(Var('x'), Var('x'))))
))


#
def to_bool(expr: Expr) -> Optional[bool]:
    expr = evaluate(expr)
    if pretty(expr) == pretty(true):
        return True
    elif pretty(expr) == pretty(false):
        return False
    return None

if __name__ == "__main__":

    one = church(1)
    two = church(2)
    three = evaluate(App(succ, two))

    print("Church numeral 2:", to_int(two))
    print("Successor of 2:", to_int(three))

    five = evaluate(App(App(add, two), three))
    print("2 + 3 =", to_int(five))

    # pairs
    p = evaluate(App(App(pair, two), three))
    first = evaluate(App(fst, p))
    second = evaluate(App(snd, p))

    print("First of pair (2,3):", to_int(first))
    print("Second of pair (2,3):", to_int(second))
    
    # boolean
    print("\n--- Boolean Tests ---")
    print("true:", to_bool(true))
    print("false:", to_bool(false))
    
    not_true = evaluate(App(not_op, true))
    print("not true:", to_bool(not_true))
    
    and_true_false = evaluate(App(App(and_op, true), false))
    print("true and false:", to_bool(and_true_false))
    
    or_true_false = evaluate(App(App(or_op, true), false))
    print("true or false:", to_bool(or_true_false))
    
    # conditional
    cond_test = evaluate(App(App(App(cond, true), church(1)), church(2)))
    print("if true then 1 else 2:", to_int(cond_test))
    
    # number
    print("\n--- Number Tests ---")
    is_zero_test = evaluate(App(iszero, church(0)))
    print("is_zero(0):", to_bool(is_zero_test))
    
    is_zero_test = evaluate(App(iszero, church(1)))
    print("is_zero(1):", to_bool(is_zero_test))
    
    pred_test = evaluate(App(pred, church(5)))
    print("pred(5):", to_int(pred_test))
    
    mult_test = evaluate(App(App(mult, church(3)), church(4)))
    print("3 * 4 =", to_int(mult_test))
    
    # Y combinator test for factorial
    print("\n--- Y Combinator Test: Factorial ---")
    
    # The factorial function
    # fact = λn. if (iszero n) 1 (mult n (fact (pred n)))
    # Using Y combinator: Y (λf.λn. if (iszero n) 1 (mult n (f (pred n))))
 
    fact_body = Abs('f', Abs('n', 
        App(App(App(cond, App(iszero, Var('n'))),
            church(1)),  # then branch: return 1
            App(App(mult, Var('n')),  # else branch: n * f(pred n)
                App(Var('f'), App(pred, Var('n'))))
        )
    ))
    
    # Create factorial function using Y combinator
    fact = App(Y, fact_body)
    
    # Calculate factorial of 0, 1, 2, 3, 4
    for i in range(5):
        result = evaluate(App(fact, church(i)), max_steps=10000)
        print(f"factorial({i}) =", to_int(result))
