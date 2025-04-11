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
    var: str  # Add a variable name for clarity
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
    """Base type for logical propositions"""
    name: str  # Add a name field for better identification
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

# New Terms for Natural Deduction
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
    def __str__(self): return f"∧E({'left' if self.left else 'right'}, {self.pair})"

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

# Helper function to collect free variables in a term
def free_vars(term: Term) -> set:
    """Return the set of free variables in a term."""
    if isinstance(term, Var):
        return {term.name}
    
    elif isinstance(term, Lam) or isinstance(term, ImpliesIntro):
        # Remove the bound variable from the free variables of the body
        body_free = free_vars(term.body)
        return body_free - {term.var}
    
    elif isinstance(term, App):
        return free_vars(term.func) | free_vars(term.arg)
    
    elif isinstance(term, (TrueTerm, FalseTerm, UnitTerm)):
        return set()  # No free variables
    
    elif isinstance(term, Pair):
        return free_vars(term.fst) | free_vars(term.snd)
    
    elif isinstance(term, (Fst, Snd)):
        return free_vars(term.pair)
    
    elif isinstance(term, Refl):
        return free_vars(term.term)
    
    elif isinstance(term, Sym):
        return free_vars(term.proof)
    
    elif isinstance(term, Trans):
        return free_vars(term.p) | free_vars(term.q)
    
    elif isinstance(term, Assume):
        body_free = free_vars(term.body)
        return body_free - {term.var}
    
    elif isinstance(term, ImpliesElim):
        return free_vars(term.impl) | free_vars(term.antecedent)
    
    elif isinstance(term, AndIntro):
        return free_vars(term.left) | free_vars(term.right)
    
    elif isinstance(term, AndElim):
        return free_vars(term.pair)
    
    else:
        return set()  # Default case


# Fixed substitute function
def substitute(term: Term, var: str, value: Term) -> Term:
    """Substitute value for var in term."""
    if isinstance(term, Var):
        if term.name == var:
            return value
        else:
            return term
    
    elif isinstance(term, Lam):
        # Alpha renaming logic to avoid variable capture
        if term.var == var:
            # If the lambda binds the same variable, don't substitute in the body
            return term
        elif term.var in free_vars(value) and var in free_vars(term.body):
            # Avoid variable capture by renaming the bound variable
            new_var = generate_fresh_var(term.var, free_vars(value) | free_vars(term.body))
            new_body = substitute(term.body, term.var, Var(new_var))
            return Lam(new_var, term.var_type, substitute(new_body, var, value))
        else:
            # Safe to substitute
            return Lam(term.var, term.var_type, substitute(term.body, var, value))
    
    elif isinstance(term, App):
        return App(substitute(term.func, var, value), substitute(term.arg, var, value))
    
    elif isinstance(term, (TrueTerm, FalseTerm, UnitTerm)):
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
    
    elif isinstance(term, Assume):
        if term.var == var:
            return term
        elif term.var in free_vars(value) and var in free_vars(term.body):
            # Handle variable capture
            new_var = generate_fresh_var(term.var, free_vars(value) | free_vars(term.body))
            new_body = substitute(term.body, term.var, Var(new_var))
            return Assume(new_var, term.prop, substitute(new_body, var, value))
        else:
            return Assume(term.var, term.prop, substitute(term.body, var, value))
    
    elif isinstance(term, ImpliesIntro):
        if term.var == var:
            return term
        elif term.var in free_vars(value) and var in free_vars(term.body):
            # Handle variable capture
            new_var = generate_fresh_var(term.var, free_vars(value) | free_vars(term.body))
            new_body = substitute(term.body, term.var, Var(new_var))
            return ImpliesIntro(new_var, term.var_type, substitute(new_body, var, value))
        else:
            return ImpliesIntro(term.var, term.var_type, substitute(term.body, var, value))
    
    elif isinstance(term, ImpliesElim):
        return ImpliesElim(substitute(term.impl, var, value), substitute(term.antecedent, var, value))
    
    elif isinstance(term, AndIntro):
        return AndIntro(substitute(term.left, var, value), substitute(term.right, var, value))
    
    elif isinstance(term, AndElim):
        return AndElim(substitute(term.pair, var, value), term.left)
    
    else:
        return term  # Default case

def generate_fresh_var(base_var: str, avoid_vars: set) -> str:
    """Generate a fresh variable name based on base_var that's not in avoid_vars."""
    if base_var not in avoid_vars:
        return base_var
    
    i = 1
    while f"{base_var}_{i}" in avoid_vars:
        i += 1
    return f"{base_var}_{i}"


# Improved beta reduction
def beta_reduce(term: Term) -> Term:
    """Apply beta reduction to a term."""
    if isinstance(term, Var):
        return term  # Variables are already in normal form
    
    elif isinstance(term, (TrueTerm, FalseTerm, UnitTerm)):
        return term  # Constants are already in normal form
    
    elif isinstance(term, Lam):
        # Reduce the body of the lambda
        return Lam(term.var, term.var_type, beta_reduce(term.body))
    
    elif isinstance(term, App):
        # First reduce the function and argument
        func = beta_reduce(term.func)
        arg = beta_reduce(term.arg)
        
        # If the function is a lambda, apply beta reduction
        if isinstance(func, Lam):
            return beta_reduce(substitute(func.body, func.var, arg))
        else:
            return App(func, arg)
    
    elif isinstance(term, Pair):
        return Pair(beta_reduce(term.fst), beta_reduce(term.snd))
    
    elif isinstance(term, Fst):
        pair = beta_reduce(term.pair)
        if isinstance(pair, Pair):
            return beta_reduce(pair.fst)
        return Fst(pair)
    
    elif isinstance(term, Snd):
        pair = beta_reduce(term.pair)
        if isinstance(pair, Pair):
            return beta_reduce(pair.snd)
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
        
        if isinstance(p, Refl):
            return q  # trans(refl(t), q) = q
        
        if isinstance(q, Refl):
            return p  # trans(p, refl(t)) = p
        
        return Trans(p, q)
    
    elif isinstance(term, Assume):
        return Assume(term.var, term.prop, beta_reduce(term.body))
    
    elif isinstance(term, ImpliesIntro):
        return ImpliesIntro(term.var, term.var_type, beta_reduce(term.body))
    
    elif isinstance(term, ImpliesElim):
        impl = beta_reduce(term.impl)
        ant = beta_reduce(term.antecedent)

        # Apply modus ponens if impl is a lambda abstraction
        if isinstance(impl, ImpliesIntro):
            return beta_reduce(substitute(impl.body, impl.var, ant))
        
        return ImpliesElim(impl, ant)
    
    elif isinstance(term, AndIntro):
        return AndIntro(beta_reduce(term.left), beta_reduce(term.right))
    
    elif isinstance(term, AndElim):
        pair = beta_reduce(term.pair)
        
        if isinstance(pair, AndIntro):
            return beta_reduce(pair.left if term.left else pair.right)
        
        return AndElim(pair, term.left)
    
    else:
        return term


# Improved cut elimination
def apply_cut_elimination(term: Term) -> Term:

    # First beta-reduce the term
    reduced = beta_reduce(term)
    
    # Base cases: atomic terms don't need cut elimination
    if isinstance(reduced, (Var, TrueTerm, FalseTerm, UnitTerm)):
        return reduced
    
    # Recursively normalize subterms
    if isinstance(reduced, Lam):
        body = apply_cut_elimination(reduced.body)
        return Lam(reduced.var, reduced.var_type, body)
    
    elif isinstance(reduced, App):
        func = apply_cut_elimination(reduced.func)
        arg = apply_cut_elimination(reduced.arg)
        
        # If func is a lambda, apply beta reduction
        if isinstance(func, Lam):
            return apply_cut_elimination(substitute(func.body, func.var, arg))
        
        return App(func, arg)
    
    elif isinstance(reduced, Pair):
        return Pair(apply_cut_elimination(reduced.fst), apply_cut_elimination(reduced.snd))
    
    elif isinstance(reduced, Fst):
        pair = apply_cut_elimination(reduced.pair)
        if isinstance(pair, Pair):
            return apply_cut_elimination(pair.fst)
        return Fst(pair)
    
    elif isinstance(reduced, Snd):
        pair = apply_cut_elimination(reduced.pair)
        if isinstance(pair, Pair):
            return apply_cut_elimination(pair.snd)
        return Snd(pair)
    
    elif isinstance(reduced, Refl):
        return Refl(apply_cut_elimination(reduced.term))
    
    elif isinstance(reduced, Sym):
        proof = apply_cut_elimination(reduced.proof)
        if isinstance(proof, Refl):
            return proof  # sym(refl(t)) = refl(t)
        elif isinstance(proof, Sym):
            return apply_cut_elimination(proof.proof)  # sym(sym(p)) = p
        return Sym(proof)
    
    elif isinstance(reduced, Trans):
        p = apply_cut_elimination(reduced.p)
        q = apply_cut_elimination(reduced.q)
        
        # Simplification rules for transitivity
        if isinstance(p, Refl):
            return q  # trans(refl(a), q) = q
        
        if isinstance(q, Refl):
            return p  # trans(p, refl(b)) = p
        
        # Associativity of transitivity
        if isinstance(p, Trans):
            return apply_cut_elimination(Trans(p.p, Trans(p.q, q)))
        
        return Trans(p, q)
    
    # Handle logical connectives
    
    elif isinstance(reduced, ImpliesElim):
        impl = apply_cut_elimination(reduced.impl)
        ant = apply_cut_elimination(reduced.antecedent)
        
        # Key cut elimination rule: directly substitute in ImpliesIntro
        if isinstance(impl, ImpliesIntro):
            return apply_cut_elimination(substitute(impl.body, impl.var, ant))
        
        return ImpliesElim(impl, ant)
    
    elif isinstance(reduced, ImpliesIntro):
        body = apply_cut_elimination(reduced.body)
        
        # η-reduction for implications
        if isinstance(body, ImpliesElim) and isinstance(body.antecedent, Var) and body.antecedent.name == reduced.var:
            if reduced.var not in free_vars(body.impl):
                return body.impl
        
        return ImpliesIntro(reduced.var, reduced.var_type, body)
    
    elif isinstance(reduced, AndIntro):
        left = apply_cut_elimination(reduced.left)
        right = apply_cut_elimination(reduced.right)
        return AndIntro(left, right)
    
    elif isinstance(reduced, AndElim):
        pair = apply_cut_elimination(reduced.pair)
        
        # Direct extraction from AndIntro
        if isinstance(pair, AndIntro):
            return apply_cut_elimination(pair.left if reduced.left else pair.right)
        
        return AndElim(pair, reduced.left)
    
    elif isinstance(reduced, Assume):
        body = apply_cut_elimination(reduced.body)
        return Assume(reduced.var, reduced.prop, body)
    
    else:
        return reduced


# Main normalization function
def normalize(term: Term) -> Term:

    # Apply beta reduction first
    reduced = beta_reduce(term)
    
    # Then apply cut elimination
    eliminated = apply_cut_elimination(reduced)
    
    # If the term has changed, continue normalizing
    if str(eliminated) != str(term):
        return normalize(eliminated)
    
    return eliminated


if __name__ == "__main__":
    # Define propositions P and Q
    P = Proposition("P")
    Q = Proposition("Q")
    R = Proposition("R")

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
            AndElim(Var("pq"), False),  # Extract Q from P∧Q
            AndElim(Var("pq"), True)    # Extract P from P∧Q
        )
    )
    
    print(conj_comm)
    
    print("\nType checking conjunction commutativity...")
    conj_type = type_check(ctx, conj_comm)
    print("Result type:")
    print(conj_type)
    
    # Example showing cut elimination
    print("\n\nCut Elimination Example:")
    print("P → Q, Q → R, P ⊢ R")
    
    # Create complex term with cuts
    # First create proofs of P → Q and Q → R
    p_implies_q = Var("p_implies_q")  # Assume we have P → Q
    q_implies_r = Var("q_implies_r")  # Assume we have Q → R
    p_var = Var("p")                  # Assume we have P
    
    # Derive Q using modus ponens
    q_proof = ImpliesElim(p_implies_q, p_var)
    
    # Derive R using Q and Q → R
    r_proof = ImpliesElim(q_implies_r, q_proof)
    
    # Extended context with our assumptions
    ext_ctx = {
        "p": P,
        "p_implies_q": Implies(P, Q),
        "q_implies_r": Implies(Q, R)
    }
    
    print("\nBefore normalization:")
    print(r_proof)
    print("Type:", type_check(ext_ctx, r_proof))
    
    # Normalize the proof to eliminate the cut
    normalized_proof = normalize(r_proof)
    
    print("\nAfter normalization:")
    print(normalized_proof)
    print("Type:", type_check(ext_ctx, normalized_proof))
    
    # Example showing cut elimination with explicit lambda terms
    print("\n\nCut Elimination with Lambda Terms:")
    
    # Create a proof of P → Q with a concrete function body
    proof_p_to_q = ImpliesIntro("p1", P, Var("q_var"))  # A concrete implication
    ext_ctx["q_var"] = Q  # Add Q to context for typechecking
    
    # Then use this proof to prove P using a detour through Q
    detour_proof = ImpliesIntro(
        "p2", P,
        ImpliesElim(
            proof_p_to_q,  # P → Q
            Var("p2")      # P
        )                  # This gives Q, but should simplify
    )
    
    print("\nProof with detour:")
    print(detour_proof)
    print("Type:", type_check(ext_ctx, detour_proof))
    
    # Normalize to eliminate the unnecessary detour
    normalized_detour = normalize(detour_proof)
    
    print("\nNormalized proof:")
    print(normalized_detour)
    print("Type:", type_check(ext_ctx, normalized_detour))