"""
Categorical Compilation Pipeline

Pipeline stages:
1. High-level categorical language (Surface Language)
2. Categorical IR (preserves structure)
3. Optimisation using categorical laws
4. Code generation to simple VM

Category theory is a *design tool* for the compiler,
not something the VM needs to understand.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


# STAGE 1: SURFACE LANGUAGE (Categorical)

class Type(ABC):
    """Types as objects in a category"""
    pass

@dataclass
class IntType(Type):
    def __repr__(self): return "Int"

@dataclass
class BoolType(Type):
    def __repr__(self): return "Bool"

@dataclass
class UnitType(Type):
    def __repr__(self): return "Unit"

@dataclass
class ProductType(Type):
    """Categorical product A x B"""
    left: Type
    right: Type
    def __repr__(self): return f"({self.left} × {self.right})"

@dataclass
class SumType(Type):
    """Categorical coproduct A + B"""
    left: Type
    right: Type
    def __repr__(self): return f"({self.left} + {self.right})"

@dataclass
class FunctionType(Type):
    """Exponential object B^A (A → B)"""
    domain: Type
    codomain: Type
    def __repr__(self): return f"({self.domain} → {self.codomain})"


class Expr(ABC):
    """Surface language expressions (arrows in category)"""
    @abstractmethod
    def type_of(self, ctx: Dict[str, Type]) -> Type:
        """Type inference"""
        pass


@dataclass
class Var(Expr):
    """Variable reference"""
    name: str
    
    def type_of(self, ctx):
        return ctx[self.name]
    
    def __repr__(self):
        return self.name


@dataclass
class Lit(Expr):
    """Literal value"""
    value: int
    
    def type_of(self, ctx):
        return IntType()
    
    def __repr__(self):
        return str(self.value)


@dataclass
class BinOp(Expr):
    """Binary operation"""
    op: str
    left: Expr
    right: Expr
    
    def type_of(self, ctx):
        # Type checking
        lt = self.left.type_of(ctx)
        rt = self.right.type_of(ctx)
        if not (isinstance(lt, IntType) and isinstance(rt, IntType)):
            raise TypeError(f"BinOp requires Int, got {lt} and {rt}")
        return IntType()
    
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


@dataclass
class Pair(Expr):
    """Categorical product introduction"""
    fst: Expr
    snd: Expr
    
    def type_of(self, ctx):
        return ProductType(self.fst.type_of(ctx), self.snd.type_of(ctx))
    
    def __repr__(self):
        return f"⟨{self.fst}, {self.snd}⟩"


@dataclass
class Fst(Expr):
    """First projection (product elimination)"""
    expr: Expr
    
    def type_of(self, ctx):
        t = self.expr.type_of(ctx)
        if not isinstance(t, ProductType):
            raise TypeError(f"fst requires product type, got {t}")
        return t.left
    
    def __repr__(self):
        return f"fst({self.expr})"


@dataclass
class Snd(Expr):
    """Second projection (product elimination)"""
    expr: Expr
    
    def type_of(self, ctx):
        t = self.expr.type_of(ctx)
        if not isinstance(t, ProductType):
            raise TypeError(f"snd requires product type, got {t}")
        return t.right
    
    def __repr__(self):
        return f"snd({self.expr})"


@dataclass
class InL(Expr):
    """Left injection (coproduct introduction)"""
    expr: Expr
    right_type: Type
    
    def type_of(self, ctx):
        return SumType(self.expr.type_of(ctx), self.right_type)
    
    def __repr__(self):
        return f"inl({self.expr})"


@dataclass
class InR(Expr):
    """Right injection (coproduct introduction)"""
    expr: Expr
    left_type: Type
    
    def type_of(self, ctx):
        return SumType(self.left_type, self.expr.type_of(ctx))
    
    def __repr__(self):
        return f"inr({self.expr})"


@dataclass
class Case(Expr):
    """Case analysis (coproduct elimination)"""
    scrutinee: Expr
    left_var: str
    left_branch: Expr
    right_var: str
    right_branch: Expr
    
    def type_of(self, ctx):
        scrut_type = self.scrutinee.type_of(ctx)
        if not isinstance(scrut_type, SumType):
            raise TypeError(f"case requires sum type, got {scrut_type}")
        
        # Check both branches return same type
        left_ctx = {**ctx, self.left_var: scrut_type.left}
        right_ctx = {**ctx, self.right_var: scrut_type.right}
        
        left_type = self.left_branch.type_of(left_ctx)
        right_type = self.right_branch.type_of(right_ctx)
        
        if type(left_type) != type(right_type):
            raise TypeError(f"case branches must have same type: {left_type} vs {right_type}")
        
        return left_type
    
    def __repr__(self):
        return f"case {self.scrutinee} of inl({self.left_var}) → {self.left_branch} | inr({self.right_var}) → {self.right_branch}"


@dataclass
class Let(Expr):
    """Let binding"""
    var: str
    value: Expr
    body: Expr
    
    def type_of(self, ctx):
        val_type = self.value.type_of(ctx)
        new_ctx = {**ctx, self.var: val_type}
        return self.body.type_of(new_ctx)
    
    def __repr__(self):
        return f"let {self.var} = {self.value} in {self.body}"


# STAGE 2: CATEGORICAL IR (Intermediate Representation)

class CatIR(ABC):
    """Categorical IR - explicit categorical structure"""
    pass


@dataclass
class IRLit(CatIR):
    """Literal"""
    value: int
    def __repr__(self): return f"#{self.value}"


@dataclass
class IRVar(CatIR):
    """Variable (de Bruijn index)"""
    index: int
    def __repr__(self): return f"${self.index}"


@dataclass
class IRBinOp(CatIR):
    """Binary operation"""
    op: str
    left: CatIR
    right: CatIR
    def __repr__(self): return f"({self.left} {self.op} {self.right})"


@dataclass
class IRPair(CatIR):
    """Product (categorical)"""
    fst: CatIR
    snd: CatIR
    def __repr__(self): return f"⟨{self.fst}, {self.snd}⟩"


@dataclass
class IRFst(CatIR):
    """First projection"""
    expr: CatIR
    def __repr__(self): return f"π₁({self.expr})"


@dataclass
class IRSnd(CatIR):
    """Second projection"""
    expr: CatIR
    def __repr__(self): return f"π₂({self.expr})"


@dataclass
class IRInL(CatIR):
    """Left injection"""
    expr: CatIR
    def __repr__(self): return f"ι₁({self.expr})"


@dataclass
class IRInR(CatIR):
    """Right injection"""
    expr: CatIR
    def __repr__(self): return f"ι₂({self.expr})"


@dataclass
class IRCase(CatIR):
    """Case analysis"""
    scrutinee: CatIR
    left_branch: CatIR
    right_branch: CatIR
    def __repr__(self): return f"case({self.scrutinee}, {self.left_branch}, {self.right_branch})"



# STAGE 3: CATEGORICAL OPTIMISATIONS

class CategoricalOptimizer:
    """Optimise using categorical laws"""
    
    @staticmethod
    def optimize(ir: CatIR) -> CatIR:
        """Apply categorical optimisation laws"""
        # Apply laws recursively
        ir = CategoricalOptimizer.apply_laws(ir)
        
        # Recurse into subexpressions
        if isinstance(ir, IRBinOp):
            return IRBinOp(ir.op, 
                          CategoricalOptimizer.optimize(ir.left),
                          CategoricalOptimizer.optimize(ir.right))
        elif isinstance(ir, IRPair):
            return IRPair(CategoricalOptimizer.optimize(ir.fst),
                         CategoricalOptimizer.optimize(ir.snd))
        elif isinstance(ir, IRFst):
            return IRFst(CategoricalOptimizer.optimize(ir.expr))
        elif isinstance(ir, IRSnd):
            return IRSnd(CategoricalOptimizer.optimize(ir.expr))
        elif isinstance(ir, IRCase):
            return IRCase(CategoricalOptimizer.optimize(ir.scrutinee),
                         CategoricalOptimizer.optimize(ir.left_branch),
                         CategoricalOptimizer.optimize(ir.right_branch))
        
        return ir
    
    @staticmethod
    def apply_laws(ir: CatIR) -> CatIR:
        """Apply categorical laws for optimization"""
        
        # Law: fst(⟨a, b⟩) = a (Product β-reduction)
        if isinstance(ir, IRFst) and isinstance(ir.expr, IRPair):
            return ir.expr.fst
        
        # Law: snd(⟨a, b⟩) = b (Product β-reduction)
        if isinstance(ir, IRSnd) and isinstance(ir.expr, IRPair):
            return ir.expr.snd
        
        # Law: ⟨fst(p), snd(p)⟩ = p (Product η-reduction)
        if isinstance(ir, IRPair):
            if (isinstance(ir.fst, IRFst) and isinstance(ir.snd, IRSnd) and
                isinstance(ir.fst.expr, IRVar) and isinstance(ir.snd.expr, IRVar) and
                ir.fst.expr.index == ir.snd.expr.index):
                return ir.fst.expr
        
        # Law: case(inl(x), f, g) = f(x) (Sum β-reduction left)
        if isinstance(ir, IRCase) and isinstance(ir.scrutinee, IRInL):
            return ir.left_branch
        
        # Law: case(inr(x), f, g) = g(x) (Sum β-reduction right)
        if isinstance(ir, IRCase) and isinstance(ir.scrutinee, IRInR):
            return ir.right_branch
        
        return ir



# STAGE 4: SIMPLE TARGET VM (No category theory needed!)

class Opcode(Enum):
    """Simple VM opcodes - no categorical concepts here"""
    PUSH = "PUSH"
    LOAD = "LOAD"      # Load from environment
    STORE = "STORE"    # Store to environment
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    PAIR = "PAIR"      # Create tuple
    FST = "FST"        # Get first element
    SND = "SND"        # Get second element
    TAG = "TAG"        # Tag value (0=left, 1=right)
    BRANCH = "BRANCH"  # Branch on tag


@dataclass
class Instruction:
    """VM instruction"""
    opcode: Opcode
    arg: Any = None
    
    def __repr__(self):
        if self.arg is not None:
            return f"{self.opcode.value} {self.arg}"
        return self.opcode.value


class SimpleVM:
    """Simple stack VM - no category theory, just efficient execution"""
    
    def __init__(self):
        self.stack: List[Any] = []
        self.env: Dict[int, Any] = {}
    
    def execute(self, instructions: List[Instruction]):
        """Execute instructions"""
        ip = 0
        while ip < len(instructions):
            instr = instructions[ip]
            
            if instr.opcode == Opcode.PUSH:
                self.stack.append(instr.arg)
            
            elif instr.opcode == Opcode.LOAD:
                self.stack.append(self.env[instr.arg])
            
            elif instr.opcode == Opcode.STORE:
                self.env[instr.arg] = self.stack[-1]
            
            elif instr.opcode == Opcode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            
            elif instr.opcode == Opcode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            
            elif instr.opcode == Opcode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            
            elif instr.opcode == Opcode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a // b)
            
            elif instr.opcode == Opcode.PAIR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append((a, b))
            
            elif instr.opcode == Opcode.FST:
                pair = self.stack.pop()
                self.stack.append(pair[0])
            
            elif instr.opcode == Opcode.SND:
                pair = self.stack.pop()
                self.stack.append(pair[1])
            
            elif instr.opcode == Opcode.TAG:
                val = self.stack.pop()
                self.stack.append((instr.arg, val))
            
            elif instr.opcode == Opcode.BRANCH:
                tagged = self.stack.pop()
                tag, val = tagged
                self.stack.append(val)
                if tag == 1:  # right branch
                    ip = instr.arg
                    continue
            
            ip += 1
    
    def top(self):
        return self.stack[-1] if self.stack else None


# STAGE 4: CODE GENERATION

class CodeGen:
    """Generate VM code from categorical IR"""
    
    @staticmethod
    def compile(ir: CatIR) -> List[Instruction]:
        """Compile IR to VM instructions"""
        if isinstance(ir, IRLit):
            return [Instruction(Opcode.PUSH, ir.value)]
        
        elif isinstance(ir, IRVar):
            return [Instruction(Opcode.LOAD, ir.index)]
        
        elif isinstance(ir, IRBinOp):
            code = []
            code.extend(CodeGen.compile(ir.left))
            code.extend(CodeGen.compile(ir.right))
            
            if ir.op == '+':
                code.append(Instruction(Opcode.ADD))
            elif ir.op == '-':
                code.append(Instruction(Opcode.SUB))
            elif ir.op == '*':
                code.append(Instruction(Opcode.MUL))
            elif ir.op == '/':
                code.append(Instruction(Opcode.DIV))
            
            return code
        
        elif isinstance(ir, IRPair):
            code = []
            code.extend(CodeGen.compile(ir.fst))
            code.extend(CodeGen.compile(ir.snd))
            code.append(Instruction(Opcode.PAIR))
            return code
        
        elif isinstance(ir, IRFst):
            code = CodeGen.compile(ir.expr)
            code.append(Instruction(Opcode.FST))
            return code
        
        elif isinstance(ir, IRSnd):
            code = CodeGen.compile(ir.expr)
            code.append(Instruction(Opcode.SND))
            return code
        
        elif isinstance(ir, IRInL):
            code = CodeGen.compile(ir.expr)
            code.append(Instruction(Opcode.TAG, 0))
            return code
        
        elif isinstance(ir, IRInR):
            code = CodeGen.compile(ir.expr)
            code.append(Instruction(Opcode.TAG, 1))
            return code
        
        elif isinstance(ir, IRCase):
            code = []
            code.extend(CodeGen.compile(ir.scrutinee))
            
            # Compile branches
            left_code = CodeGen.compile(ir.left_branch)
            right_code = CodeGen.compile(ir.right_branch)
            
            # Branch instruction
            code.append(Instruction(Opcode.BRANCH, len(code) + len(left_code) + 1))
            code.extend(left_code)
            code.extend(right_code)
            
            return code
        
        return []


# COMPILER PIPELINE

class Compiler:
    """Full compilation pipeline"""
    
    @staticmethod
    def compile_expr(expr: Expr, show_stages: bool = False) -> List[Instruction]:
        """Compile expression through all stages"""
        
        # Stage 1: Type check
        ctx = {}
        try:
            typ = expr.type_of(ctx)
            if show_stages:
                print(f"  Type: {typ}")
        except TypeError as e:
            print(f"  Type error: {e}")
            return []
        
        # Stage 2: Convert to IR
        ir = Compiler.to_ir(expr, {})
        if show_stages:
            print(f"  IR (before): {ir}")
        
        # Stage 3: Optimize using categorical laws
        optimized = CategoricalOptimizer.optimize(ir)
        if show_stages:
            print(f"  IR (after):  {optimized}")
        
        # Stage 4: Generate code
        code = CodeGen.compile(optimized)
        if show_stages:
            print(f"  Code: {len(code)} instructions")
        
        return code
    
    @staticmethod
    def to_ir(expr: Expr, env: Dict[str, int]) -> CatIR:
        """Convert surface language to IR (with de Bruijn indices)"""
        if isinstance(expr, Lit):
            return IRLit(expr.value)
        
        elif isinstance(expr, Var):
            return IRVar(env[expr.name])
        
        elif isinstance(expr, BinOp):
            return IRBinOp(expr.op, 
                          Compiler.to_ir(expr.left, env),
                          Compiler.to_ir(expr.right, env))
        
        elif isinstance(expr, Pair):
            return IRPair(Compiler.to_ir(expr.fst, env),
                         Compiler.to_ir(expr.snd, env))
        
        elif isinstance(expr, Fst):
            return IRFst(Compiler.to_ir(expr.expr, env))
        
        elif isinstance(expr, Snd):
            return IRSnd(Compiler.to_ir(expr.expr, env))
        
        elif isinstance(expr, InL):
            return IRInL(Compiler.to_ir(expr.expr, env))
        
        elif isinstance(expr, InR):
            return IRInR(Compiler.to_ir(expr.expr, env))
        
        elif isinstance(expr, Case):
            scrut = Compiler.to_ir(expr.scrutinee, env)
            
            # Extend environment for branches
            left_env = {**env, expr.left_var: 0}
            right_env = {**env, expr.right_var: 0}
            
            left = Compiler.to_ir(expr.left_branch, left_env)
            right = Compiler.to_ir(expr.right_branch, right_env)
            
            return IRCase(scrut, left, right)
        
        elif isinstance(expr, Let):
            val_ir = Compiler.to_ir(expr.value, env)
            new_env = {**env, expr.var: len(env)}
            body_ir = Compiler.to_ir(expr.body, new_env)
            # Simplified: just inline for now
            return body_ir
        
        return IRLit(0)



# EXAMPLES

def example_basic_optimization():
    """Show how categorical laws enable optimisation"""
    print("\n" + "-"*70)
    print("EXAMPLE 1: Categorical Optimisation")
    print("-"*70)
    print("\nExpression: fst(⟨3 + 4, 10 * 2⟩)")
    print("\nThis demonstrates the product β-law: fst(⟨a, b⟩) = a")
    print("The optimiser eliminates the unnecessary pair construction!\n")
    
    # Create expression: fst(⟨3 + 4, 10 * 2⟩)
    expr = Fst(Pair(
        BinOp('+', Lit(3), Lit(4)),
        BinOp('*', Lit(10), Lit(2))
    ))
    
    print(f"Surface: {expr}")
    code = Compiler.compile_expr(expr, show_stages=True)
    
    print(f"\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"  {i}: {instr}")
    
    # Execute
    vm = SimpleVM()
    vm.execute(code)
    print(f"\n Result: {vm.top()}")
    print(f"  (Notice: no PAIR or FST in optimized code!)")


def example_sum_type():
    """Sum types with case analysis"""
    print("\n" + "-"*70)
    print("EXAMPLE 2: Sum Types (Either)")
    print("-"*70)
    print("\nExpression: case(inl(42), x → x * 2, y → 0)")
    print("\nThis demonstrates the sum β-law: case(inl(x), f, g) = f(x)")
    print("The optimiser eliminates the unnecessary case analysis!\n")
    
    # Create: case(inl(42), x → x * 2, y → 0)
    expr = Case(
        InL(Lit(42), IntType()),
        "x", BinOp('*', Var("x"), Lit(2)),
        "y", Lit(0)
    )
    
    print(f"Surface: {expr}")
    
    # Need to provide context for type checking
    ctx = {}
    code = Compiler.compile_expr(expr, show_stages=True)
    
    print(f"\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"  {i}: {instr}")
    
    # Execute
    vm = SimpleVM()
    vm.execute(code)
    print(f"\n  Result: {vm.top()}")
    print(f"  (Notice: case was optimised away!)")


def example_nested_products():
    """Nested products"""
    print("\n" + "-"*70)
    print("EXAMPLE 3: Nested Products")
    print("-"*70)
    print("\nExpression: snd(fst(⟨⟨1, 2⟩, 3⟩))")
    print()
    
    expr = Snd(Fst(Pair(
        Pair(Lit(1), Lit(2)),
        Lit(3)
    )))
    
    print(f"Surface: {expr}")
    code = Compiler.compile_expr(expr, show_stages=True)
    
    print(f"\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"  {i}: {instr}")
    
    vm = SimpleVM()
    vm.execute(code)
    print(f"\n  Result: {vm.top()}")


def example_computation():
    """More complex computation"""
    print("\n" + "-"*70)
    print("EXAMPLE 4: Complex Expression")
    print("-"*70)
    print("\nExpression: (3 + 4) * (10 - 2)")
    print()
    
    expr = BinOp('*',
        BinOp('+', Lit(3), Lit(4)),
        BinOp('-', Lit(10), Lit(2))
    )
    
    print(f"Surface: {expr}")
    code = Compiler.compile_expr(expr, show_stages=True)
    
    print(f"\nGenerated code:")
    for i, instr in enumerate(code):
        print(f"  {i}: {instr}")
    
    vm = SimpleVM()
    vm.execute(code)
    print(f"\n  Result: {vm.top()}")




def main():
    """Run all examples"""
    example_basic_optimization()
    example_sum_type()
    example_nested_products()
    example_computation()
    
    print("\n" + "-"*70)
    print("SUMMARY")
    print("-"*70)
    print("""
Category theory should be applied EARLY in the pipeline:

✓ Type system design (products, sums, exponentials)
✓ IR structure (preserve categorical laws)
✓ Optimisation (use laws for correctness)
✗ Runtime VM (too late, just execute!)

The categorical structure enables:
- Type safety
- Correct optimisations
- Compositional reasoning
- Modular compilation

But the final VM is simple and efficient!
""")


if __name__ == "__main__":
    main()
