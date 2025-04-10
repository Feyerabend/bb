
from dataclasses import dataclass
from typing import Union, Callable, Dict, Optional


# Types and Terms

@dataclass(frozen=True)
class Type:
    pass

@dataclass(frozen=True)
class NatType(Type):
    pass

@dataclass(frozen=True)
class PiType(Type):
    var: str
    domain: Type
    codomain: Callable[[str], Type]

@dataclass(frozen=True)
class IdType(Type):
    typ: Type
    lhs: 'Term'
    rhs: 'Term'


# Terms

@dataclass(frozen=True)
class Term:
    pass

@dataclass(frozen=True)
class Var(Term):
    name: str

@dataclass(frozen=True)
class Lam(Term):
    var: str
    typ: Type
    body: Term

@dataclass(frozen=True)
class App(Term):
    func: Term
    arg: Term

@dataclass(frozen=True)
class Refl(Term):
    term: Term


# Context and Typechecking

Context = Dict[str, Type]

def type_check(ctx: Context, term: Term) -> Type:
    if isinstance(term, Var):
        return ctx[term.name]

    elif isinstance(term, Lam):
        new_ctx = ctx.copy()
        new_ctx[term.var] = term.typ
        codomain = type_check(new_ctx, term.body)
        return PiType(term.var, term.typ, lambda x: codomain)

    elif isinstance(term, App):
        func_type = type_check(ctx, term.func)
        if not isinstance(func_type, PiType):
            raise TypeError("Function application to non-function")
        arg_type = type_check(ctx, term.arg)
        if arg_type != func_type.domain:
            raise TypeError(f"Argument type mismatch: expected {func_type.domain}, got {arg_type}")
        return func_type.codomain(term.arg.name if isinstance(term.arg, Var) else "arg")

    elif isinstance(term, Refl):
        term_type = type_check(ctx, term.term)
        return IdType(term_type, term.term, term.term)

    else:
        raise NotImplementedError("Unknown term type")


# The term: λx : Nat. refl x
ctx = {}
term = Lam("x", NatType(), Refl(Var("x")))

typ = type_check(ctx, term)
print(typ)
