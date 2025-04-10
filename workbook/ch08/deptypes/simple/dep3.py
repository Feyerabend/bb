
from dataclasses import dataclass
from typing import Dict, Callable, Union


# Base Classes

class Type:
    pass

class Term:
    pass


# Types

@dataclass(frozen=True)
class Nat(Type):
    def __str__(self): return "Nat"

@dataclass(frozen=True)
class Pi(Type):
    var: str
    domain: Type
    codomain: Callable[[str], Type]
    def __str__(self): return f"(Π {self.var} : {self.domain}). {self.codomain(self.var)}"

@dataclass(frozen=True)
class Id(Type):
    typ: Type
    lhs: Term
    rhs: Term
    def __str__(self): return f"Id({self.typ}, {self.lhs}, {self.rhs})"


# Terms

@dataclass(frozen=True)
class Var(Term):
    name: str
    def __str__(self): return self.name

@dataclass(frozen=True)
class Lam(Term):
    var: str
    var_type: Type
    body: Term
    def __str__(self): return f"(λ {self.var} : {self.var_type}. {self.body})"

@dataclass(frozen=True)
class App(Term):
    func: Term
    arg: Term
    def __str__(self): return f"({self.func} {self.arg})"

@dataclass(frozen=True)
class Refl(Term):
    term: Term
    def __str__(self): return f"refl({self.term})"


# Typing Context

Context = Dict[str, Type]


# Typechecker

def type_check(ctx: Context, term: Term) -> Type:
    if isinstance(term, Var):
        if term.name in ctx:
            return ctx[term.name]
        raise TypeError(f"Unbound variable: {term.name}")
    
    elif isinstance(term, Lam):
        new_ctx = ctx.copy()
        new_ctx[term.var] = term.var_type
        body_type = type_check(new_ctx, term.body)
        return Pi(term.var, term.var_type, lambda _: body_type)
    
    elif isinstance(term, App):
        func_type = type_check(ctx, term.func)
        arg_type = type_check(ctx, term.arg)
        if isinstance(func_type, Pi):
            if arg_type != func_type.domain:
                raise TypeError(f"Argument type mismatch: expected {func_type.domain}, got {arg_type}")
            # We simplify by not actually substituting term.arg into the codomain
            return func_type.codomain(term.arg.name if isinstance(term.arg, Var) else "_")
        raise TypeError(f"Trying to apply a non-function: {func_type}")
    
    elif isinstance(term, Refl):
        t_type = type_check(ctx, term.term)
        return Id(t_type, term.term, term.term)
    
    else:
        raise NotImplementedError(f"Unknown term: {term}")



if __name__ == "__main__":
    # Example: id = λx : Nat. x
    id_term = Lam("x", Nat(), Var("x"))
    print("Term:")
    print(id_term)
    print("Type:")
    print(type_check({}, id_term))  # Should be: (Π x : Nat). Nat

    # Example: refl_id = λx : Nat. refl x
    id_eq = Lam("x", Nat(), Refl(Var("x")))
    print("\nProof Term:")
    print(id_eq)
    print("Proof Type:")
    print(type_check({}, id_eq))  # Should be: (Π x : Nat). Id(Nat, x, x)
