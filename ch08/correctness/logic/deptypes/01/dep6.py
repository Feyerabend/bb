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
class Bool(Type):
    def __str__(self): return "Bool"

@dataclass(frozen=True)
class Unit(Type):
    def __str__(self): return "Unit"

@dataclass(frozen=True)
class Pi(Type):
    var: str
    domain: Type
    codomain: Callable[[str], Type]
    def __str__(self): return f"(Π {self.var} : {self.domain}). {self.codomain(self.var)}"

@dataclass(frozen=True)
class Sigma(Type):
    fst_type: Type
    snd_type: Callable[[Term], Type]
    def __str__(self): return f"Sigma({self.fst_type}, {self.snd_type('x')})"

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

# Additional Terms for Bool, Unit, Sigma
@dataclass(frozen=True)
class TrueTerm(Term):
    def __str__(self): return "True"

@dataclass(frozen=True)
class FalseTerm(Term):
    def __str__(self): return "False"

@dataclass(frozen=True)
class UnitTerm(Term):
    def __str__(self): return "()"

@dataclass(frozen=True)
class Pair(Term):
    fst: Term
    snd: Term
    def __str__(self): return f"({self.fst}, {self.snd})"

@dataclass(frozen=True)
class Fst(Term):
    pair: Term
    def __str__(self): return f"fst({self.pair})"

@dataclass(frozen=True)
class Snd(Term):
    pair: Term
    def __str__(self): return f"snd({self.pair})"

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
    
    elif isinstance(term, TrueTerm):
        return Bool()
    
    elif isinstance(term, FalseTerm):
        return Bool()

    elif isinstance(term, UnitTerm):
        return Unit()

    elif isinstance(term, Pair):
        fst_type = type_check(ctx, term.fst)
        snd_type = type_check(ctx, term.snd)
        return Sigma(fst_type, lambda _: snd_type)
    
    elif isinstance(term, Fst):
        pair_type = type_check(ctx, term.pair)
        if isinstance(pair_type, Sigma):
            return pair_type.fst_type
        raise TypeError(f"Trying to take fst of a non-pair: {pair_type}")

    elif isinstance(term, Snd):
        pair_type = type_check(ctx, term.pair)
        if isinstance(pair_type, Sigma):
            return pair_type.snd_type(term.pair)
        raise TypeError(f"Trying to take snd of a non-pair: {pair_type}")

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

# Beta Reduction

def beta_reduce(term: Term) -> Term:
    if isinstance(term, Lam):
        # Lambda terms don't reduce on their own,
        # but the body can be reduced when applied.
        return term
    elif isinstance(term, App):
        # Beta reduction: (λx.M) N → M[x := N]
        if isinstance(term.func, Lam):
            return substitute(term.func.body, term.func.var, term.arg)
        else:
            return App(beta_reduce(term.func), beta_reduce(term.arg))
    elif isinstance(term, TrueTerm):
        return term  # True is already in normal form
    
    elif isinstance(term, FalseTerm):
        return term  # False is already in normal form

    elif isinstance(term, UnitTerm):
        return term  # Unit is already in normal form

    elif isinstance(term, Pair):
        return Pair(beta_reduce(term.fst), beta_reduce(term.snd))

    elif isinstance(term, Fst):
        return Fst(beta_reduce(term.pair))  # No reduction for projections yet

    elif isinstance(term, Snd):
        return Snd(beta_reduce(term.pair))  # No reduction for projections yet

    elif isinstance(term, Refl):
        return term  # Refl is already in normal form
    
    elif isinstance(term, Sym):
        return Sym(beta_reduce(term.proof))  # Reduce the proof term

    elif isinstance(term, Trans):
        return Trans(beta_reduce(term.p), beta_reduce(term.q))  # Reduce both proof terms

    else:
        return term

def substitute(term: Term, var: str, value: Term) -> Term:
    if isinstance(term, Var):
        if term.name == var:
            return value
        else:
            return term
    elif isinstance(term, Lam):
        # if the variable is the same as the one
        # we're substituting, no need to do anything
        if term.var == var:
            return term
        else:
            # Recursively substitute in the body
            return Lam(term.var, term.var_type, substitute(term.body, var, value))
    elif isinstance(term, App):
        return App(substitute(term.func, var, value), substitute(term.arg, var, value))
    elif isinstance(term, Refl):
        return Refl(substitute(term.term, var, value))
    elif isinstance(term, Sym):
        return Sym(substitute(term.proof, var, value))
    elif isinstance(term, Trans):
        return Trans(substitute(term.p, var, value), substitute(term.q, var, value))
    elif isinstance(term, Pair):
        return Pair(substitute(term.fst, var, value), substitute(term.snd, var, value))
    elif isinstance(term, Fst):
        return Fst(substitute(term.pair, var, value))
    elif isinstance(term, Snd):
        return Snd(substitute(term.pair, var, value))
    else:
        return term



if __name__ == "__main__":
    # Some basic variables
    x = Var("x")
    y = Var("y")
    z = Var("z")

    # Example 1: Identity function
    id_term = Lam("x", Nat(), Var("x"))
    app_term = App(id_term, Var("y"))

    print("Before beta reduction:")
    print(app_term)
    
    reduced_term = beta_reduce(app_term)
    print("\nAfter beta reduction:")
    print(reduced_term)
    
    # Example 2: Reflexive identity proof
    refl_term = Lam("x", Nat(), Refl(Var("x")))
    app_refl_term = App(refl_term, Var("y"))

    print("\nBefore beta reduction on refl term:")
    print(app_refl_term)

    reduced_refl_term = beta_reduce(app_refl_term)
    print("\nAfter beta reduction on refl term:")
    print(reduced_refl_term)

    # Example 3: Boolean values
    true_term = TrueTerm()
    false_term = FalseTerm()

    print("\nTrue Term Type:")
    print(type_check({}, true_term))  # Should return Bool()

    print("\nFalse Term Type:")
    print(type_check({}, false_term))  # Should return Bool()

    # Example 4: Sigma pairs and projections
    pair_term = Pair(Var("x"), Var("y"))
    print("\nPair Term Type:")
    print(type_check({"x": Nat(), "y": Nat()}, pair_term))  # Should return Sigma(Nat, Nat)

    # Beta reduction example
    reduced_pair = beta_reduce(pair_term)
    print("\nReduced Pair Term:")
    print(reduced_pair)  # Should output (x, y)

    # Example 5: Unit term
#    unit_term = UnitTerm()
#    print("\nUnit Term Type:")
#    print(type_check({}, unit_term))  # Should return Unit()
#    print("\nReduced Unit Term:")
#    print(beta_reduce(unit_term))  # Should output ()

    # Example 6: Fst and Snd
#    pair = Pair(Var("x"), Var("y"))
#    fst_term = Fst(pair)
#    snd_term = Snd(pair)
#    print("\nFst Term Type:")
#    print(type_check({"x": Nat(), "y": Nat()}, fst_term))  # Should return Nat()
#    print("\nSnd Term Type:")
#    print(type_check({"x": Nat(), "y": Nat()}, snd_term))  # Should return Nat()
#    print("\nReduced Fst Term:")
#    print(beta_reduce(fst_term))  # Should output x
#    print("\nReduced Snd Term:")
#    print(beta_reduce(snd_term))  # Should output y

