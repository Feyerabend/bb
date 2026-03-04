class Expr:
    def evaluate(self):
        raise NotImplementedError

class Number(Expr):
    def __init__(self, value): self.value = value
    def evaluate(self): return self.value

class BinOp(Expr):
    def __init__(self, left, op, right):
        self.left, self.op, self.right = left, op, right

    def evaluate(self):
        l = self.left.evaluate()
        r = self.right.evaluate()
        if self.op == '+': return l + r
        if self.op == '*': return l * r
        raise ValueError("Unknown op")

class ExprBuilder:
    def __init__(self):
        self.stack = []

    def number(self, value):
        self.stack.append(Number(value))
        return self

    def add(self):
        right = self.stack.pop()
        left  = self.stack.pop()
        self.stack.append(BinOp(left, '+', right))
        return self

    def mul(self):
        right = self.stack.pop()
        left  = self.stack.pop()
        self.stack.append(BinOp(left, '*', right))
        return self

    def build(self):
        return self.stack.pop()

# Usage — reverse Polish / postfix style construction (algorithmic feel)
b = (ExprBuilder()
     .number(3)
     .number(4)
     .add()           # 3 + 4
     .number(2)
     .mul()           # (3 + 4) * 2
     .number(5)
     .add())          # (3 + 4) * 2 + 5

expr = b.build()
print(expr.evaluate())          # = 19
