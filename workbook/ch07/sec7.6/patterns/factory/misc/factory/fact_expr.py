from abc import ABC, abstractmethod
from typing import Any

class Expr(ABC):
    @abstractmethod
    def evaluate(self) -> float:
        pass

class Number(Expr):
    def __init__(self, value: float):
        self.value = value

    def evaluate(self) -> float:
        return self.value

class Add(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self) -> float:
        return self.left.evaluate() + self.right.evaluate()

class Mul(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def evaluate(self) -> float:
        return self.left.evaluate() * self.right.evaluate()


# Factory Method style – each creator decides the concrete node types
# (you could also make separate factories for different dialects)

class ExprFactory(ABC):
    @abstractmethod
    def create_number(self, value: float) -> Expr:
        pass

    @abstractmethod
    def create_add(self, left: Expr, right: Expr) -> Expr:
        pass

    @abstractmethod
    def create_mul(self, left: Expr, right: Expr) -> Expr:
        pass


class StandardExprFactory(ExprFactory):
    def create_number(self, value: float) -> Expr:
        return Number(value)

    def create_add(self, left: Expr, right: Expr) -> Expr:
        return Add(left, right)

    def create_mul(self, left: Expr, right: Expr) -> Expr:
        return Mul(left, right)


class LoggingExprFactory(ExprFactory):  # toy example – could log evaluations etc.
    def create_number(self, value: float) -> Expr:
        print(f"Created number node: {value}")
        return Number(value)

    def create_add(self, left: Expr, right: Expr) -> Expr:
        print("Created ADD node")
        return Add(left, right)

    def create_mul(self, left: Expr, right: Expr) -> Expr:
        print("Created MUL node")
        return Mul(left, right)


# Usage – client code does not depend on concrete classes
def build_sample_expression(factory: ExprFactory) -> Expr:
    #  (3 + 4) * 2 + 5
    three   = factory.create_number(3)
    four    = factory.create_number(4)
    sum_    = factory.create_add(three, four)
    two     = factory.create_number(2)
    product = factory.create_mul(sum_, two)
    five    = factory.create_number(5)
    result  = factory.create_add(product, five)
    return result


# Try different factories
std_factory = StandardExprFactory()
expr = build_sample_expression(std_factory)
print("Result:", expr.evaluate())          # 19.0

log_factory = LoggingExprFactory()
expr2 = build_sample_expression(log_factory)
print("Result:", expr2.evaluate())         # also 19.0, but with logs
