from dataclasses import dataclass
from typing import Dict, Callable, Union, Optional

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
    var: str  # variable name for clarity
    fst_type: Type
    snd_type: Callable[[Term], Type]
    def __str__(self): return f"(Σ {self.var} : {self.fst_type}). {self.snd_type(Var(self.var))}"

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

# New Types
@dataclass(frozen=True)
class Proposition(Type):
    name: str  # name field
    def __str__(self): return self.name

@dataclass(frozen=True)
class Implies(Type):
    """P → Q"""
    antecedent: Type
    consequent: Type
    def __str__(self): return f"({self.antecedent} → {self.consequent})"

@dataclass(frozen=True)
class And(Type):
    """P ∧ Q"""
    left: Type
    right: Type
    def __str__(self): return f"({self.left} ∧ {self.right})"

# Terms for Natural Deduction
@dataclass(frozen=True)
class Assume(Term):
    """Assume P to prove Q (for → introduction)"""
    var: str  # Variable name for the assumption
    prop: Type  # The proposition being assumed
    body: Term  # Proof of Q under assumption P
    def __str__(self): return f"assume {self.var} : {self.prop} {{ {self.body} }}"

@dataclass(frozen=True)
class ImpliesIntro(Term):
    """Given a proof of Q under assumption P, conclude P → Q"""
    var: str  # Variable name for the assumption
    var_type: Type  # The type of the assumption
    body: Term  # Proof of Q under assumption P
    def __str__(self): return f"→I({self.var} : {self.var_type}.{self.body})"

@dataclass(frozen=True)
class ImpliesElim(Term):
    """From P → Q and P, conclude Q (modus ponens)"""
    impl: Term  # P → Q
    antecedent: Term  # P
    def __str__(self): return f"→E({self.impl}, {self.antecedent})"

@dataclass(frozen=True)
class AndIntro(Term):
    """From P and Q, conclude P ∧ Q"""
    left: Term
    right: Term
    def __str__(self): return f"∧I({self.left}, {self.right})"

@dataclass(frozen=True)
class AndElim(Term):
    """From P ∧ Q, conclude P (or Q)"""
    pair: Term
    left: bool  # True for left elim, False for right
    def __str__(self): return f"∧E({'l' if self.left else 'r'}, {self.pair})"

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
        # Using a placeholder var name, which should be improved in practice
        return Sigma("x", fst_type, lambda _: snd_type)
    
    elif isinstance(term, Fst):
        pair_type = type_check(ctx, term.pair)
        if isinstance(pair_type, Sigma):
            return pair_type.fst_type
        raise TypeError(f"Trying to take fst of a non-pair: {pair_type}")

    elif isinstance(term, Snd):
        pair_type = type_check(ctx, term.pair)
        if isinstance(pair_type, Sigma):
            # Create a First projection term to substitute in the second component's dependent type
            fst_proj = Fst(term.pair)
            return pair_type.snd_type(fst_proj)
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
            raise TypeError(f"Mismatched types in trans: {p_type.typ} vs {q_type.typ}")
        if p_type.rhs != q_type.lhs:
            raise TypeError(f"Middle terms don't match in trans: {p_type.rhs} vs {q_type.lhs}")
        return Id(p_type.typ, p_type.lhs, q_type.rhs)

    elif isinstance(term, Assume):
        new_ctx = ctx.copy()
        new_ctx[term.var] = term.prop  # Add assumption to context with its variable name
        body_type = type_check(new_ctx, term.body)
        return body_type  # Return the type of the body
    
    elif isinstance(term, ImpliesIntro):
        new_ctx = ctx.copy()
        new_ctx[term.var] = term.var_type  # Add the assumption with its proper type
        body_type = type_check(new_ctx, term.body)
        return Implies(term.var_type, body_type)  # Properly track the type
    
    elif isinstance(term, ImpliesElim):
        impl_type = type_check(ctx, term.impl)
        ant_type = type_check(ctx, term.antecedent)
        if not isinstance(impl_type, Implies):
            raise TypeError(f"Expected implication, got {impl_type}")
        if ant_type != impl_type.antecedent:
            raise TypeError(f"Antecedent mismatch: {ant_type} vs {impl_type.antecedent}")
        return impl_type.consequent
    
    elif isinstance(term, AndIntro):
        left_type = type_check(ctx, term.left)
        right_type = type_check(ctx, term.right)
        return And(left_type, right_type)
    
    elif isinstance(term, AndElim):
        pair_type = type_check(ctx, term.pair)
        if not isinstance(pair_type, And):
            raise TypeError(f"Expected conjunction, got {pair_type}")
        return pair_type.left if term.left else pair_type.right

    else:
        raise NotImplementedError(f"Unknown term: {term}")

# Beta Reduction

def beta_reduce(term: Term) -> Term:
    if isinstance(term, Var):
        return term  # Variables are already in normal form
    
    elif isinstance(term, Lam):
        # Reduce the body of the lambda
        reduced_body = beta_reduce(term.body)
        return Lam(term.var, term.var_type, reduced_body)
    
    elif isinstance(term, App):
        # Beta reduction: (λx.M) N → M[x := N]
        func = beta_reduce(term.func)
        arg = beta_reduce(term.arg)
        
        if isinstance(func, Lam):
            return beta_reduce(substitute(func.body, func.var, arg))
        else:
            return App(func, arg)
    
    elif isinstance(term, TrueTerm) or isinstance(term, FalseTerm) or isinstance(term, UnitTerm):
        return term  # Already in normal form

    elif isinstance(term, Pair):
        return Pair(beta_reduce(term.fst), beta_reduce(term.snd))

    elif isinstance(term, Fst):
        pair = beta_reduce(term.pair)
        if isinstance(pair, Pair):
            return beta_reduce(pair.fst)  # Return the first component of the pair
        return Fst(pair)

    elif isinstance(term, Snd):
        pair = beta_reduce(term.pair)
        if isinstance(pair, Pair):
            return beta_reduce(pair.snd)  # Return the second component of the pair
        return Snd(pair)
    
    elif isinstance(term, Refl):
        return Refl(beta_reduce(term.term))
    
    elif isinstance(term, Sym):
        proof = beta_reduce(term.proof)
        if isinstance(proof, Refl):
            return proof  # sym(refl(t)) = refl(t)
        return Sym(proof)
    
    elif isinstance(term, Trans):
        p = beta_reduce(term.p)
        q = beta_reduce(term.q)
        
        if isinstance(p, Refl) and isinstance(q, Refl):
            return Refl(p.term)  # trans(refl(t), refl(t)) = refl(t)
        
        return Trans(p, q)
    
    # Handle the new logical operations
    elif isinstance(term, Assume):
        return Assume(term.var, term.prop, beta_reduce(term.body))
    
    elif isinstance(term, ImpliesIntro):
        return ImpliesIntro(term.var, term.var_type, beta_reduce(term.body))
    
    elif isinstance(term, ImpliesElim):
        impl = beta_reduce(term.impl)
        ant = beta_reduce(term.antecedent)
        
        if isinstance(impl, ImpliesIntro):
            # (λx:A.M) N → M[x := N]
            return beta_reduce(substitute(impl.body, impl.var, ant))
        
        return ImpliesElim(impl, ant)
    
    elif isinstance(term, AndIntro):
        return AndIntro(beta_reduce(term.left), beta_reduce(term.right))
    
    elif isinstance(term, AndElim):
        pair = beta_reduce(term.pair)
        
        if isinstance(pair, AndIntro):
            # Extract the component from the conjunction
            return beta_reduce(pair.left if term.left else pair.right)
        
        return AndElim(pair, term.left)
    
    else:
        return term  # Default case for unhandled terms

def substitute(term: Term, var: str, value: Term) -> Term:
    """Substitute value for var in term."""
    if isinstance(term, Var):
        if term.name == var:
            return value
        else:
            return term
    
    elif isinstance(term, Lam):
        # If the lambda binds the same variable, don't substitute in the body
        if term.var == var:
            return term
        else:
            # Make sure value doesn't capture any free variables in term.body
            # (A proper implementation would check for variable capture)
            return Lam(term.var, term.var_type, substitute(term.body, var, value))
    
    elif isinstance(term, App):
        return App(substitute(term.func, var, value), substitute(term.arg, var, value))
    
    elif isinstance(term, TrueTerm) or isinstance(term, FalseTerm) or isinstance(term, UnitTerm):
        return term  # Constants don't contain variables
    
    elif isinstance(term, Pair):
        return Pair(substitute(term.fst, var, value), substitute(term.snd, var, value))
    
    elif isinstance(term, Fst):
        return Fst(substitute(term.pair, var, value))
    
    elif isinstance(term, Snd):
        return Snd(substitute(term.pair, var, value))
    
    elif isinstance(term, Refl):
        return Refl(substitute(term.term, var, value))
    
    elif isinstance(term, Sym):
        return Sym(substitute(term.proof, var, value))
    
    elif isinstance(term, Trans):
        return Trans(substitute(term.p, var, value), substitute(term.q, var, value))
    
    # Handle substitution for the new logical operations
    elif isinstance(term, Assume):
        # If the assumption binds the same variable, don't substitute in the body
        if term.var == var:
            return term
        else:
            return Assume(term.var, term.prop, substitute(term.body, var, value))
    
    elif isinstance(term, ImpliesIntro):
        # If the introduction binds the same variable, don't substitute in the body
        if term.var == var:
            return term
        else:
            return ImpliesIntro(term.var, term.var_type, substitute(term.body, var, value))
    
    elif isinstance(term, ImpliesElim):
        return ImpliesElim(substitute(term.impl, var, value), substitute(term.antecedent, var, value))
    
    elif isinstance(term, AndIntro):
        return AndIntro(substitute(term.left, var, value), substitute(term.right, var, value))
    
    elif isinstance(term, AndElim):
        return AndElim(substitute(term.pair, var, value), term.left)
    
    else:
        return term  # Default case for unhandled terms


if __name__ == "__main__":

    # Define propositions P and Q
    P = Proposition("P")
    Q = Proposition("Q")

    # Context: empty, no assumptions at the top level
    ctx: Context = {}

    # Build the term for the proof of P → (Q → P)
    # This corresponds to: λp:P. λq:Q. p
    proof_term = ImpliesIntro(
        "p", P, ImpliesIntro("q", Q, Var("p"))
    )

    print("Proof term:")
    print(proof_term)

    print("\nType checking...")
    result_type = type_check(ctx, proof_term)
    print("Result type:")
    print(result_type)
    
    # Additional example: conjunction commutativity (P ∧ Q → Q ∧ P)
    print("\n\nProof of P ∧ Q → Q ∧ P:")
    
    # Build the term for the proof of P ∧ Q → Q ∧ P
    conj_comm = ImpliesIntro(
        "pq", And(P, Q), 
        AndIntro(
            AndElim(Var("pq"), False),  # q from p∧q
            AndElim(Var("pq"), True)    # p from p∧q
        )
    )
    
    print(conj_comm)
    
    print("\nType checking conjunction commutativity...")
    conj_type = type_check(ctx, conj_comm)
    print("Result type:")
    print(conj_type)
