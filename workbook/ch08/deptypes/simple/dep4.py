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

@dataclass(frozen=True)
class Sym(Term):
    proof: Term
    def __str__(self): return f"sym({self.proof})"

@dataclass(frozen=True)
class Trans(Term):
    p: Term
    q: Term
    def __str__(self): return f"trans({self.p}, {self.q})"

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
            return func_type.codomain(term.arg.name if isinstance(term.arg, Var) else "_")
        raise TypeError(f"Trying to apply a non-function: {func_type}")
    
    elif isinstance(term, Refl):
        t_type = type_check(ctx, term.term)
        return Id(t_type, term.term, term.term)

    elif isinstance(term, Sym):
        proof_type = type_check(ctx, term.proof)
        if not isinstance(proof_type, Id):
            raise TypeError("sym expects a proof of an identity")
        return Id(proof_type.typ, proof_type.rhs, proof_type.lhs)

    elif isinstance(term, Trans):
        p_type = type_check(ctx, term.p)
        q_type = type_check(ctx, term.q)
        if not isinstance(p_type, Id) or not isinstance(q_type, Id):
            raise TypeError("trans expects two identity proofs")
        if p_type.typ != q_type.typ:
            raise TypeError("Mismatched types in trans")
        if p_type.rhs != q_type.lhs:
            raise TypeError(f"Middle terms don't match in trans: {p_type.rhs} vs {q_type.lhs}")
        return Id(p_type.typ, p_type.lhs, q_type.rhs)

    else:
        raise NotImplementedError(f"Unknown term: {term}")



if __name__ == "__main__":
    x = Var("x")
    y = Var("y")
    z = Var("z")

    ctx = {
        "x": Nat(),
        "y": Nat(),
        "z": Nat(),
        "p": Id(Nat(), x, y),
        "q": Id(Nat(), y, z)
    }

    id_term = Lam("x", Nat(), Var("x"))
    print("Term:")
    print(id_term)
    print("Type:")
    print(type_check({}, id_term))  # (Π x : Nat). Nat

    refl_term = Lam("x", Nat(), Refl(Var("x")))
    print("\nProof Term:")
    print(refl_term)
    print("Type:")
    print(type_check({}, refl_term))  # (Π x : Nat). Id(Nat, x, x)

    sym_p = Sym(Var("p"))
    print("\nsym(p):")
    print(sym_p)
    print("Type:")
    print(type_check(ctx, sym_p))  # Id(Nat, y, x)

    trans_pq = Trans(Var("p"), Var("q"))
    print("\ntrans(p, q):")
    print(trans_pq)
    print("Type:")
    print(type_check(ctx, trans_pq))  # Id(Nat, x, z)
