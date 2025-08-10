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


# Vectors

@dataclass(frozen=True)
class Vector(Type):
    length: Term  # A term of type Nat
    elem_type: Type
    def __str__(self): return f"Vector[{self.length}]({self.elem_type})"

@dataclass(frozen=True)
class Nil(Term):
    elem_type: Type
    def __str__(self): return f"nil[{self.elem_type}]"

@dataclass(frozen=True)
class Cons(Term):
    head: Term
    tail: Term
    def __str__(self): return f"cons({self.head}, {self.tail})"

@dataclass(frozen=True)
class VLength(Term):
    vector: Term
    def __str__(self): return f"length({self.vector})"

@dataclass(frozen=True)
class VIndex(Term):
    vector: Term
    index: Term
    def __str__(self): return f"{self.vector}[{self.index}]"


# Natural Numbers

@dataclass(frozen=True)
class Zero(Term):
    def __str__(self): return "0"

@dataclass(frozen=True)
class Succ(Term):
    pred: Term
    def __str__(self): return f"succ({self.pred})"


# Matrix

@dataclass(frozen=True)
class Matrix(Type):
    rows: Term    # Number of rows (Nat)
    cols: Term    # Number of columns (Nat)
    elem_type: Type
    def __str__(self): return f"Matrix[{self.rows},{self.cols}]({self.elem_type})"

@dataclass(frozen=True)
class MNil(Term):
    rows: Term    # Number of rows (should be Zero)
    cols: Term    # Number of columns
    elem_type: Type
    def __str__(self): return f"mnil[{self.rows},{self.cols}]({self.elem_type})"

@dataclass(frozen=True)
class MEmpty(Term):
    elem_type: Type
    def __str__(self): return f"mempty[{self.elem_type}]"

@dataclass(frozen=True)
class MCons(Term):
    row: Term     # A vector of length cols
    rest: Term    # The rest of the matrix (rows-1 x cols)
    def __str__(self): return f"mcons({self.row}, {self.rest})"

@dataclass(frozen=True)
class MMult(Term):
    a: Term
    b: Term
    def __str__(self): return f"mmult({self.a}, {self.b})"

@dataclass(frozen=True)
class MGet(Term):
    matrix: Term
    row: Term
    col: Term
    def __str__(self): return f"mget({self.matrix}, {self.row}, {self.col})"


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

    elif isinstance(term, Nil):
        return Vector(Zero(), term.elem_type)
    
    elif isinstance(term, Cons):
        head_type = type_check(ctx, term.head)
        tail_type = type_check(ctx, term.tail)
        if not isinstance(tail_type, Vector):
            raise TypeError("Cons tail must be a Vector")
        # Check if head type matches vector element type
        if head_type != tail_type.elem_type:
            raise TypeError(f"Head type {head_type} doesn't match vector element type {tail_type.elem_type}")
        # The new vector's length is succ(tail.length)
        return Vector(Succ(tail_type.length), tail_type.elem_type)
    
    elif isinstance(term, VLength):
        vec_type = type_check(ctx, term.vector)
        if not isinstance(vec_type, Vector):
            raise TypeError("length expects a Vector")
        return Nat()
    
    elif isinstance(term, VIndex):
        vec_type = type_check(ctx, term.vector)
        idx_type = type_check(ctx, term.index)
        if not isinstance(vec_type, Vector):
            raise TypeError("Indexing requires a Vector")
        if idx_type != Nat():
            raise TypeError("Index must be a Nat")
        # Here you'd want to verify the index is less than the length
        # This would require more advanced dependent type checking
        return vec_type.elem_type

    elif isinstance(term, Zero):
        return Nat()
    
    elif isinstance(term, Succ):
        pred_type = type_check(ctx, term.pred)
        if pred_type != Nat():
            raise TypeError("succ expects a Nat")
        return Nat()

    elif isinstance(term, MEmpty):
        return Matrix(Zero(), Zero(), term.elem_type)

    elif isinstance(term, MNil):
        if not isinstance(term.rows, Zero):
            raise TypeError("MNil rows must be Zero")
        return Matrix(term.rows, term.cols, term.elem_type)
    
    elif isinstance(term, MCons):
        row_type = type_check(ctx, term.row)
        rest_type = type_check(ctx, term.rest)
        
        if not isinstance(row_type, Vector):
            raise TypeError("MCons row must be a Vector")
        if not isinstance(rest_type, Matrix):
            raise TypeError("MCons rest must be a Matrix")
        
        # For the first row being added, rest_type.cols should be Zero
        # After that, check column counts match
        if not (isinstance(rest_type.cols, Zero) or row_type.length == rest_type.cols):
            raise TypeError(f"Row length {row_type.length} doesn't match matrix cols {rest_type.cols}")
        
        # Check element types match
        if row_type.elem_type != rest_type.elem_type:
            raise TypeError(f"Row element type {row_type.elem_type} doesn't match matrix element type {rest_type.elem_type}")
        
        # If this is the first row, cols becomes row length
        new_cols = row_type.length if isinstance(rest_type.cols, Zero) else rest_type.cols
        return Matrix(Succ(rest_type.rows), new_cols, rest_type.elem_type)
    
    elif isinstance(term, MMult):
        a_type = type_check(ctx, term.a)
        b_type = type_check(ctx, term.b)
        
        if not (isinstance(a_type, Matrix) and isinstance(b_type, Matrix)):
            raise TypeError("MMult requires two matrices")
        
        # Check if columns of A match rows of B
        if a_type.cols != b_type.rows:
            raise TypeError(f"Cannot multiply {a_type.rows}x{a_type.cols} by {b_type.rows}x{b_type.cols}")
        
        # Check element types are compatible (could add numeric type checking)
        if a_type.elem_type != Nat() or b_type.elem_type != Nat():
            raise TypeError("Matrix multiplication requires numeric elements")
        
        return Matrix(a_type.rows, b_type.cols, Nat())
    
    elif isinstance(term, MGet):
        mat_type = type_check(ctx, term.matrix)
        row_type = type_check(ctx, term.row)
        col_type = type_check(ctx, term.col)
        
        if not isinstance(mat_type, Matrix):
            raise TypeError("MGet requires a matrix")
        if row_type != Nat() or col_type != Nat():
            raise TypeError("Matrix indices must be Nats")
        
        # Here you'd want to verify the indices are in bounds
        # This would require more advanced dependent type checking
        return mat_type.elem_type


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

# Type-safe matrix multiplication
def matrix_mult_type(rows_a: Term, cols_a: Term, cols_b: Term) -> Type:
    """Returns the type of a matrix multiplication function"""
    return Pi("a", Matrix(rows_a, cols_a, Nat()),
           Pi("b", Matrix(cols_a, cols_b, Nat()),
           Matrix(rows_a, cols_b, Nat())))



if __name__ == "__main__":


    # Natural number helpers
    zero = Zero()
    one = Succ(zero)
    two = Succ(one)
    three = Succ(two)

    # Vector helpers
    def vec(*elements):
        if not elements:
            return Nil(Nat())
        return Cons(elements[0], vec(*elements[1:]))

    # Matrix helpers
    def matrix(cols: Term, *rows):
        if not rows:
            return MNil(zero, cols, Nat())
        first_row = rows[0]
        rest_matrix = matrix(cols, *rows[1:])
        return MCons(first_row, rest_matrix)

    # Example 1: Create a 2x3 matrix
    row1 = vec(one, zero, one)    # [1, 0, 1]
    row2 = vec(zero, one, one)    # [0, 1, 1]
    mat_a = matrix(three, row1, row2)  # Specify expected columns (3) upfront

    # Check its type
    mat_a_type = type_check({}, mat_a)
    print(f"Matrix A type: {mat_a_type}")  # Should be Matrix[2,3](Nat)

    # Example 2: Create a 3x2 matrix
    row1 = vec(one, zero)         # [1, 0]
    row2 = vec(zero, one)         # [0, 1]
    row3 = vec(one, one)          # [1, 1]
    mat_b = matrix(two, row1, row2, row3)

    # Check its type
    mat_b_type = type_check({}, mat_b)
    print(f"Matrix B type: {mat_b_type}")  # Should be Matrix[3,2](Nat)

    # Example 3: Matrix multiplication
    mat_mult = MMult(mat_a, mat_b)
    mat_mult_type = type_check({}, mat_mult)
    print(f"Matrix multiplication type: {mat_mult_type}")  # Should be Matrix[2,2](Nat)

    # Example 4: Invalid matrix construction (rows with different lengths)
    bad_row1 = vec(one, zero)     # [1, 0]
    bad_row2 = vec(one)           # [1] - wrong length
    try:
        bad_mat = matrix(two, bad_row1, bad_row2)  # Should fail
        type_check({}, bad_mat)
    except TypeError as e:
        print(f"\nExpected type error: {e}")

    # Test 1: Verify 1×1 matrix
    mat_1x1 = matrix(one, vec(one))
    print(type_check({}, mat_1x1))  # Should print: Matrix[succ(0),succ(0)](Nat)

    # Test 2: Verify invalid multiplication
    mat_2x2 = matrix(two, vec(one, zero), vec(zero, one))
    try:
        bad_mult = MMult(mat_a, mat_2x2)  # 2×3 × 2×2 - invalid!
        type_check({}, bad_mult)
    except TypeError as e:
        print(f"Correctly caught: {e}")  # Should catch dimension mismatch

    # Test 3: Verify element access
    get_ok = MGet(mat_1x1, zero, zero)
    print(type_check({}, get_ok))  # Should be Nat

    try:
        get_bad = MGet(mat_1x1, one, zero)  # Out of bounds
        type_check({}, get_bad)
    except TypeError as e:
        print(f"Correctly caught out of bounds: {e}")

